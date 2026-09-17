from hashlib import sha256
from pathlib import Path

from .document_reader import extract_text
from .models import RfpMetadata, utc_now
from .tracker import ExcelTracker


class DuplicateRfpError(RuntimeError):
    def __init__(self, metadata: RfpMetadata):
        super().__init__(f"Duplicate file; first registered by run {metadata.duplicate_of}")
        self.metadata = metadata


class ReceiverAgent:
    def __init__(self, tracker: ExcelTracker):
        self.tracker = tracker

    def run(self, *, run_id: str, account: str, source_path: Path) -> tuple[RfpMetadata, str]:
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        data = source_path.read_bytes()
        digest = sha256(data).hexdigest()
        text, unit_count = extract_text(source_path)
        if not text.strip():
            raise ValueError("The RFP contains no extractable text")
        duplicate_of = self.tracker.find_by_hash(digest)
        metadata = RfpMetadata(run_id, account, str(source_path), source_path.name, source_path.suffix.lower().lstrip("."), len(data), digest, unit_count, len(text.split()), utc_now(), duplicate_of)
        self.tracker.insert({"Run ID": run_id, "Account": account, "File Name": source_path.name, "Source Path": str(source_path), "SHA-256": digest, "Received At": metadata.ingested_at, "Status": "DUPLICATE" if duplicate_of else "VALIDATED", "Current Agent": "receiver", "Duplicate Of": duplicate_of or "", "Error": ""})
        if duplicate_of:
            raise DuplicateRfpError(metadata)
        return metadata, text

