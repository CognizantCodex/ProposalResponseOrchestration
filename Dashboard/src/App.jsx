import { useEffect, useMemo, useState } from "react";
import accountListMarkdown from "../AccountList.md?raw";
import accountsListMarkdown from "../AccountsList.md?raw";
import rfpMarkdown from "../RFPStatus.md?raw";

const serviceLineOfferings = {
  SEG: ["Application Engineering", "Platform Engineering", "DevSecOps", "Cloud-Native Development", "Legacy Modernization"],
  AIA: ["Data Engineering", "AI/ML Engineering", "Business Intelligence", "Data Science", "Data Governance"],
  CIS: ["Cloud Operations", "Infrastructure Services", "Cybersecurity", "Modern Workplace", "Service Management"],
  IPM: ["ERP Delivery", "CRM Platforms", "Workflow Automation", "Enterprise Integration", "Process Transformation"],
  IOT: ["Connected Products", "Industrial IoT", "Embedded Engineering", "Product Engineering", "Digital Manufacturing"],
  ISG: ["Banking Solutions", "Insurance Solutions", "Healthcare Solutions", "Retail Solutions", "Industry Consulting"],
  QEA: ["Test Automation", "Performance Engineering", "Quality Governance", "SDET Engineering", "Test Data & Environment"],
};
const businessUnits = {
  "Financial Services": [
    "Banking & Capital Markets",
    "Cards & Payments",
    "Consumer Lending",
  ],
  Insurance: ["Life & Annuities", "Property & Casualty", "Insurance Operations"],
  Healthcare: ["Payer", "Provider", "Life Sciences"],
  "Consumer & Retail": ["Retail & Consumer Goods", "Travel & Hospitality"],
  "Communications & Technology": ["Communications", "Media", "Technology"],
};
const documentsApiBase =
  "https://api.github.com/repos/CognizantCodex/ProposalResponseOrchestration/contents/Customer%20RFP%20Documentation";
const documentsWebBase =
  "https://github.com/CognizantCodex/ProposalResponseOrchestration/tree/develop/Customer%20RFP%20Documentation";

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileType(name) {
  return name.split(".").pop()?.toUpperCase() || "FILE";
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

function RfpCard({ rfp, selection = {}, onChange }) {
  const serviceLines = (rfp["Service Lines"] || "")
    .split(";")
    .map((value) => value.trim())
    .filter(Boolean);
  const slsNames = (rfp["SLS Names"] || "")
    .split(";")
    .map((value) => value.trim());

  const updateServiceLine = (index, patch) => {
    const current = selection.serviceLineDetails || [];
    const next = serviceLines.map((_, rowIndex) => ({
      ...(current[rowIndex] || {}),
      ...(rowIndex === index ? patch : {}),
    }));
    onChange({ ...selection, serviceLineDetails: next });
  };

  const toggleOffering = (index, offering) => {
    const selected = selection.serviceLineDetails?.[index]?.offerings || [];
    const next = selected.includes(offering)
      ? selected.filter((item) => item !== offering)
      : [...selected, offering];
    updateServiceLine(index, { offerings: next });
  };

  return (
    <article className="rfp-card">
      <div className="rfp-card__head">
        <div>
          <span className="eyebrow">RFP {String(rfp.id).padStart(2, "0")}</span>
          <h3>{rfp["RFP Name"]}</h3>
          <span className="source-note">ReceiverAgent output</span>
        </div>
        <StatusPill status={rfp.Status} />
      </div>

      <p className="description">{rfp["RFP Description"]}</p>

      <div className="rfp-commercials">
        <label className="field tcv-field">
          <span>TCV value (USD millions)</span>
          <span className="money-input">
            <b>$</b>
            <input
              type="number"
              min="0"
              step="0.1"
              value={selection.tcv || ""}
              onChange={(event) => onChange({ ...selection, tcv: event.target.value })}
              placeholder="0.0"
            />
            <b>M</b>
          </span>
        </label>
        <div className="tracker-status">
          <span>Status</span>
          <strong>{rfp.Status}</strong>
          <small>RFP_Status_Tracker.xlsx</small>
        </div>
      </div>

      <div className="service-lines">
        <div className="service-lines__title">
          <h4>Service-line assignments</h4>
          <span>{serviceLines.length} line{serviceLines.length === 1 ? "" : "s"}</span>
        </div>
        {serviceLines.map((line, index) => {
          const detail = selection.serviceLineDetails?.[index] || {};
          const offerings = serviceLineOfferings[line] || [];
          return (
            <section className="service-line-row" key={`${line}-${index}`}>
              <div className="readonly-field">
                <span>Service Line</span>
                <strong>{line}</strong>
              </div>
              <div className="readonly-field">
                <span>SLS Name</span>
                <strong>{slsNames[index] || "Pending assignment"}</strong>
              </div>
              <label className="field">
                <span>SLS Email</span>
                <input
                  type="email"
                  value={detail.email || ""}
                  onChange={(event) => updateServiceLine(index, { email: event.target.value })}
                  placeholder="name@cognizant.com"
                />
              </label>
              <label className="field">
                <span>SLS Phone</span>
                <input
                  type="tel"
                  value={detail.phone || ""}
                  onChange={(event) => updateServiceLine(index, { phone: event.target.value })}
                  placeholder="+1"
                />
              </label>
              <fieldset className="offerings-field">
                <legend>Offerings</legend>
                <div className="offering-options">
                  {offerings.map((offering) => (
                    <label className="offering-check" key={offering}>
                      <input
                        type="checkbox"
                        checked={(detail.offerings || []).includes(offering)}
                        onChange={() => toggleOffering(index, offering)}
                      />
                      <span>{offering}</span>
                    </label>
                  ))}
                  {!offerings.length && <span className="pending-value">Pending category mapping</span>}
                </div>
              </fieldset>
            </section>
          );
        })}
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
  const [bu, setBu] = useState(Object.keys(businessUnits)[0]);
  const [sbu, setSbu] = useState(businessUnits[Object.keys(businessUnits)[0]][0]);
  const [account, setAccount] = useState(accounts[0] || "");
  const [cp, setCp] = useState("");
  const [crm, setCrm] = useState("");
  const [winzoneId, setWinzoneId] = useState("");
  const [query, setQuery] = useState("");
  const [choices, setChoices] = useState({});
  const [notice, setNotice] = useState("");
  const [documents, setDocuments] = useState([]);
  const [documentsState, setDocumentsState] = useState("loading");
  const [agentRuns, setAgentRuns] = useState({});
  const [receiverRun, setReceiverRun] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    setDocumentsState("loading");

    const selectedFolderApi = `${documentsApiBase}/${encodeURIComponent(account)}?ref=develop`;
    fetch(selectedFolderApi, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Repository documents could not be loaded.");
        return response.json();
      })
      .then((items) => {
        const files = items.filter(
          (item) => item.type === "file" && item.name !== ".gitkeep",
        );
        setDocuments(files);
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

  const handleBuChange = (event) => {
    const nextBu = event.target.value;
    setBu(nextBu);
    setSbu(businessUnits[nextBu][0]);
  };

  const visibleRfps = rfps.filter((rfp) =>
    [rfp["RFP Name"], rfp["RFP Description"], rfp.Status]
      .join(" ")
      .toLowerCase()
      .includes(query.toLowerCase()),
  );

  const runAgentReceiver = (document) => {
    setAgentRuns((current) => ({ ...current, [document.sha]: "started" }));
    setReceiverRun({
      account,
      documentName: document.name,
      documentSha: document.sha,
      startedAt: new Date().toISOString(),
    });
    window.dispatchEvent(
      new CustomEvent("agent-receiver:run", {
        detail: { account, document },
      }),
    );
  };

  const saveDraft = () => {
    const payload = { bu, sbu, account, cp, crm, winzoneId, choices, savedAt: new Date().toISOString() };
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
          <strong>{receiverRun ? rfps.length : 0}</strong>
          <span>{receiverRun ? "ReceiverAgent RFP records" : "RFP records awaiting ReceiverAgent"}</span>
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
              <span>BU</span>
              <select value={bu} onChange={handleBuChange} required>
                {Object.keys(businessUnits).map((name) => <option key={name}>{name}</option>)}
              </select>
            </label>

            <label className="field">
              <span>SBU</span>
              <select value={sbu} onChange={(event) => setSbu(event.target.value)} required>
                {businessUnits[bu].map((name) => <option key={name}>{name}</option>)}
              </select>
            </label>

            <label className="field">
              <span>Account name</span>
              <select value={account} onChange={(event) => setAccount(event.target.value)} required>
                {accounts.map((name) => <option key={name}>{name}</option>)}
              </select>
            </label>

            <label className="field">
              <span>CP</span>
              <input
                type="text"
                value={cp}
                onChange={(event) => setCp(event.target.value)}
                placeholder="Enter CP"
              />
            </label>

            <label className="field">
              <span>CRM</span>
              <input
                type="text"
                value={crm}
                onChange={(event) => setCrm(event.target.value)}
                placeholder="Enter CRM"
              />
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
                placeholder="Enter Winzone ID"
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
              href={`${documentsWebBase}/${encodeURIComponent(account)}`}
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
                    {agentRuns[document.sha] && (
                      <span className="agent-status" role="status">Agent Receiver started</span>
                    )}
                  </div>
                  <a className="download-link" href={document.download_url} target="_blank" rel="noreferrer">Download</a>
                  <button
                    className="agent-button"
                    type="button"
                    onClick={() => runAgentReceiver(document)}
                    disabled={Boolean(agentRuns[document.sha])}
                  >
                    {agentRuns[document.sha] ? "Agent Running" : "Run Agent Receiver"}
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>

        {receiverRun && (
          <section className="rfp-section" id="opportunities" aria-labelledby="rfp-heading">
          <div className="section-heading section-heading--plain">
            <div>
              <span className="step">03</span>
              <div>
                <p className="eyebrow">ReceiverAgent output</p>
                <h2 id="rfp-heading">RFP portfolio</h2>
                <span className="receiver-source">Created from {receiverRun.documentName}</span>
              </div>
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
        )}
      </main>

      <footer id="resources">
        <span>BCM SLS · Internal proposal workspace</span>
        <button type="button" onClick={saveDraft}>Save draft</button>
        <span className="save-notice" role="status">{notice}</span>
      </footer>
    </div>
  );
}
