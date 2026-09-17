from hashlib import sha256
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from .document_reader import extract_text
from .models import RfpMetadata, utc_now
from .tracker import ExcelTracker


class DuplicateRfpError(RuntimeError):
    def __init__(self, metadata: RfpMetadata):
        super().__init__(f"Duplicate file; first registered by run {metadata.duplicate_of}")
        self.metadata = metadata


class ReceiverAgent:
    WORKSPACE_SUBFOLDERS = ("Case Study and Reference", "Customer Documents", "Pricing", "Questionnaire", "Response", "TO")

    def __init__(self, tracker: ExcelTracker, customer_rfp_root: Path | str = Path("Customer RFP Documentation")):
        self.tracker = tracker
        self.customer_rfp_root = Path(customer_rfp_root)

    def run(self, *, run_id: str, account: str, source_path: Path | str) -> tuple[RfpMetadata, str]:
        source_ref = str(source_path)
        temporary: Path | None = None
        original_file_name: str | None = None
        if source_ref.startswith(("https://", "http://")):
            url = self._raw_github_url(source_ref)
            original_file_name = Path(unquote(urlparse(url).path)).name
            request = Request(url, headers={"User-Agent": "ProposalResponseOrchestration/1.0"})
            with urlopen(request, timeout=30) as response:
                data = response.read()
            suffix = Path(unquote(urlparse(url).path)).suffix.lower()
            if not suffix:
                raise ValueError("Remote RFP URL must include a supported file extension")
            with NamedTemporaryFile(prefix="rfp-", suffix=suffix, delete=False) as handle:
                handle.write(data)
                temporary = Path(handle.name)
            source_path = temporary
        else:
            source_path = Path(source_ref)
            if not source_path.is_file():
                raise FileNotFoundError(source_path)
            data = source_path.read_bytes()
        digest = sha256(data).hexdigest()
        text, unit_count = extract_text(Path(source_path))
        if not text.strip():
            raise ValueError("The RFP contains no extractable text")
        duplicate_of = self.tracker.find_by_hash(digest)
        metadata = RfpMetadata(run_id, account, source_ref, original_file_name or Path(source_path).name, Path(source_path).suffix.lower().lstrip("."), len(data), digest, unit_count, len(text.split()), utc_now(), duplicate_of)
        if duplicate_of:
            # The first intake row is the immutable registration for this file.
            # Replays are rejected without appending a second row.
            if temporary:
                temporary.unlink(missing_ok=True)
            raise DuplicateRfpError(metadata)
        self.tracker.insert({"Run ID": run_id, "Account": account, "File Name": metadata.file_name, "Source Path": source_ref, "SHA-256": digest, "Received At": metadata.ingested_at, "Status": "VALIDATED", "Current Agent": "receiver", "Duplicate Of": "", "Error": ""})
        self.create_customer_workspace(account=account, metadata=metadata)
        if temporary:
            temporary.unlink(missing_ok=True)
        return metadata, text

    def create_customer_workspace(self, *, account: str, metadata: RfpMetadata) -> Path | None:
        """Create the per-RFP collaboration folders for Bank 1 after intake."""
        normalized = re.sub(r"\s+", "", account).casefold()
        if normalized != "bank1":
            return None
        folder_name = re.sub(r'[<>:"/\\|?*]', "-", Path(metadata.file_name).stem).strip(" .") or "Untitled RFP"
        workspace = self.customer_rfp_root / "Bank 1" / folder_name
        workspace.mkdir(parents=True, exist_ok=True)
        for child in self.WORKSPACE_SUBFOLDERS:
            (workspace / child).mkdir(exist_ok=True)
        return workspace

    @staticmethod
    def _raw_github_url(url: str) -> str:
        parsed = urlparse(url)
        parts = [unquote(part) for part in parsed.path.split("/") if part]
        if parsed.netloc == "github.com" and len(parts) >= 5 and parts[2] == "blob":
            owner, repo, branch = parts[0], parts[1], parts[3]
            return "https://raw.githubusercontent.com/{}/{}/{}/{}".format(owner, repo, branch, "/".join(parts[4:]))
        return url

