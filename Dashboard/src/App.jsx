import { useEffect, useMemo, useState } from "react";
import accountListMarkdown from "../AccountList.md?raw";
import accountsListMarkdown from "../AccountsList.md?raw";
import rfpMarkdown from "../RFPStatus.md?raw";

const serviceLines = ["DE", "QEA", "ADM"];
const otherServiceLines = ["CIS", "AIA", "Moment", "Others"];
const documentsApi =
  "https://api.github.com/repos/CognizantCodex/ProposalResponseOrchestration/contents/Customer%20RFP%20Documentation?ref=develop";

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileType(name) {
  return name.split(".").pop()?.toUpperCase() || "FILE";
}

function matchesAccount(name, account) {
  const normalizedName = name.toLowerCase().replace(/[^a-z0-9]/g, "");
  const normalizedAccount = account.toLowerCase().replace(/[^a-z0-9]/g, "");
  return normalizedAccount && normalizedName.includes(normalizedAccount);
}

function parseList(markdown) {
  return markdown
    .split("\n")
    .map((line) => line.match(/^\s*\d+\.\s+(.+?)\s*$/)?.[1])
    .filter(Boolean);
}

function parseTable(markdown) {
  const lines = markdown
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("|"));
  if (lines.length < 3) return [];

  const cells = (line) =>
    line
      .slice(1, -1)
      .split("|")
      .map((cell) => cell.trim());

  const headers = cells(lines[0]);
  return lines.slice(2).map((line, index) => {
    const values = cells(line);
    return headers.reduce(
      (record, header, column) => ({ ...record, [header]: values[column] || "" }),
      { id: index + 1 },
    );
  });
}

function StatusPill({ status }) {
  return <span className={`status status--${status.toLowerCase().replaceAll(" ", "-")}`}>{status}</span>;
}

function RfpCard({ rfp, selection, onChange }) {
  const selected = selection?.serviceLines || [];
  const selectedOther = selection?.otherServiceLines || [];
  const toggle = (line) => {
    const next = selected.includes(line)
      ? selected.filter((item) => item !== line)
      : [...selected, line];
    onChange({ ...selection, serviceLines: next });
  };
  const toggleOther = (line) => {
    const next = selectedOther.includes(line)
      ? selectedOther.filter((item) => item !== line)
      : [...selectedOther, line];
    onChange({ ...selection, otherServiceLines: next });
  };

  return (
    <article className="rfp-card">
      <div className="rfp-card__head">
        <div>
          <span className="eyebrow">RFP {String(rfp.id).padStart(2, "0")}</span>
          <h3>{rfp["RFP Name"]}</h3>
        </div>
        <StatusPill status={rfp.Status} />
      </div>

      <p className="description">{rfp["RFP Description"]}</p>

      <dl className="rfp-facts">
        <div><dt>TCV value</dt><dd>{rfp["TCV Value"]}</dd></div>
        <div><dt>Primary SLS POC</dt><dd>{rfp["Primary SLS POC"]}</dd></div>
        <div><dt>Primary CRM POC</dt><dd>{rfp["Primary CRM POC"]}</dd></div>
      </dl>

      <div className="service-grid">
        <fieldset>
          <legend>SEG service lines</legend>
          <div className="checkboxes">
            {serviceLines.map((line) => (
              <label className="check" key={line}>
                <input
                  type="checkbox"
                  checked={selected.includes(line)}
                  onChange={() => toggle(line)}
                />
                <span>{line}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend>Other service lines</legend>
          <div className="checkboxes checkboxes--wrap">
            {otherServiceLines.map((line) => (
              <label className="check" key={line}>
                <input
                  type="checkbox"
                  checked={selectedOther.includes(line)}
                  onChange={() => toggleOther(line)}
                />
                <span>{line}</span>
              </label>
            ))}
          </div>
        </fieldset>
      </div>
    </article>
  );
}

export default function App() {
  const accounts = useMemo(
    () => [...new Set([...parseList(accountListMarkdown), ...parseList(accountsListMarkdown)])],
    [],
  );
  const rfps = useMemo(() => parseTable(rfpMarkdown), []);
  const [account, setAccount] = useState(accounts[0] || "");
  const [winzoneId, setWinzoneId] = useState("");
  const [query, setQuery] = useState("");
  const [choices, setChoices] = useState({});
  const [notice, setNotice] = useState("");
  const [documents, setDocuments] = useState([]);
  const [documentsState, setDocumentsState] = useState("loading");

  useEffect(() => {
    const controller = new AbortController();
    setDocumentsState("loading");

    fetch(documentsApi, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Repository documents could not be loaded.");
        return response.json();
      })
      .then((items) => {
        const matches = items
          .filter((item) => item.type === "file" && item.name !== ".gitkeep")
          .filter((item) => matchesAccount(item.name, account));
        setDocuments(matches);
        setDocumentsState("ready");
      })
      .catch((error) => {
        if (error.name !== "AbortError") {
          setDocuments([]);
          setDocumentsState("error");
        }
      });

    return () => controller.abort();
  }, [account]);

  const visibleRfps = rfps.filter((rfp) =>
    [rfp["RFP Name"], rfp["RFP Description"], rfp.Status]
      .join(" ")
      .toLowerCase()
      .includes(query.toLowerCase()),
  );

  const saveDraft = () => {
    const payload = { account, winzoneId, choices, savedAt: new Date().toISOString() };
    localStorage.setItem("bcm-sls-rfp-draft", JSON.stringify(payload));
    setNotice("Draft saved in this browser.");
    window.setTimeout(() => setNotice(""), 2800);
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#main" aria-label="BCM SLS dashboard home">
          <span className="brand-mark" aria-hidden="true"><i /><i /></span>
          <span>cognizant</span>
        </a>
        <nav aria-label="Primary navigation">
          <a className="active" href="#overview">RFP Dashboard</a>
          <a href="#opportunities">Opportunities</a>
          <a href="#resources">Resources</a>
        </nav>
        <div className="avatar" aria-label="Signed in user">SLS</div>
      </header>

      <section className="hero" id="overview">
        <div>
          <p className="hero-kicker">Sales lifecycle workspace</p>
          <h1>BCM SLS RFP Dashboard</h1>
          <p>Keep account context, proposal ownership, and service-line coverage in one focused view.</p>
        </div>
        <div className="hero-stat">
          <strong>{rfps.length}</strong>
          <span>active RFP records</span>
        </div>
      </section>

      <main id="main">
        <section className="panel account-panel" aria-labelledby="account-heading">
          <div className="section-heading">
            <div>
              <span className="step">01</span>
              <div><p className="eyebrow">Primary group</p><h2 id="account-heading">Account</h2></div>
            </div>
            <span className="required-note">Required fields</span>
          </div>

          <div className="account-fields">
            <label className="field">
              <span>Account name</span>
              <select value={account} onChange={(event) => setAccount(event.target.value)} required>
                {accounts.map((name) => <option key={name}>{name}</option>)}
              </select>
              <small>Loaded from AccountList.md / AccountsList.md</small>
            </label>

            <label className="field">
              <span>Winzone ID</span>
              <input
                type="number"
                inputMode="numeric"
                min="0"
                step="1"
                value={winzoneId}
                onChange={(event) => setWinzoneId(event.target.value)}
                placeholder="Enter integer ID"
              />
              <small>Validation will be connected in a later release.</small>
            </label>
          </div>
        </section>

        <section className="documents-section panel" aria-labelledby="documents-heading">
          <div className="section-heading">
            <div>
              <span className="step">02</span>
              <div>
                <p className="eyebrow">Repository documents</p>
                <h2 id="documents-heading">{account} files</h2>
              </div>
            </div>
            <a
              className="folder-link"
              href="https://github.com/CognizantCodex/ProposalResponseOrchestration/tree/develop/Customer%20RFP%20Documentation"
              target="_blank"
              rel="noreferrer"
            >
              Open repository folder
            </a>
          </div>

          {documentsState === "loading" && <p className="document-message">Loading files for {account}…</p>}
          {documentsState === "error" && (
            <p className="document-message document-message--error">
              Files could not be loaded. Open the repository folder to view them directly.
            </p>
          )}
          {documentsState === "ready" && documents.length === 0 && (
            <p className="document-message">No customer RFP documentation is available for {account}.</p>
          )}
          {documentsState === "ready" && documents.length > 0 && (
            <div className="document-list">
              {documents.map((document) => (
                <article className="document-row" key={document.sha}>
                  <span className="file-badge">{fileType(document.name)}</span>
                  <div className="document-copy">
                    <strong>{document.name}</strong>
                    <span>{formatBytes(document.size)} · Customer RFP Documentation</span>
                  </div>
                  <a href={document.html_url} target="_blank" rel="noreferrer">View file</a>
                  <a className="download-link" href={document.download_url} target="_blank" rel="noreferrer">Download</a>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="rfp-section" id="opportunities" aria-labelledby="rfp-heading">
          <div className="section-heading section-heading--plain">
            <div>
              <span className="step">03</span>
              <div><p className="eyebrow">Secondary group</p><h2 id="rfp-heading">RFP portfolio</h2></div>
            </div>
            <label className="search">
              <span className="sr-only">Search RFPs</span>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search RFPs" />
            </label>
          </div>

          <div className="rfp-list">
            {visibleRfps.map((rfp) => (
              <RfpCard
                key={rfp.id}
                rfp={rfp}
                selection={choices[rfp.id]}
                onChange={(value) => setChoices((current) => ({ ...current, [rfp.id]: value }))}
              />
            ))}
            {!visibleRfps.length && <p className="empty-state">No RFPs match your search.</p>}
          </div>
        </section>
      </main>

      <footer id="resources">
        <span>BCM SLS · Internal proposal workspace</span>
        <button type="button" onClick={saveDraft}>Save draft</button>
        <span className="save-notice" role="status">{notice}</span>
      </footer>
    </div>
  );
}
