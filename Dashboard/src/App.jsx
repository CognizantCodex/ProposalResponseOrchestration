import { useMemo, useState } from "react";
import accountListMarkdown from "../AccountList.md?raw";
import accountsListMarkdown from "../AccountsList.md?raw";
import rfpMarkdown from "../RFPStatus.md?raw";

const serviceLines = ["DE", "QEA", "ADM"];
const otherServiceLines = ["CIS", "IPM", "AIA"];

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
  const toggle = (line) => {
    const next = selected.includes(line)
      ? selected.filter((item) => item !== line)
      : [...selected, line];
    onChange({ ...selection, serviceLines: next });
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

        <label className="field">
          <span>Other service line</span>
          <select
            value={selection?.other || ""}
            onChange={(event) => onChange({ ...selection, other: event.target.value })}
          >
            <option value="">Select a service line</option>
            {otherServiceLines.map((line) => <option key={line}>{line}</option>)}
          </select>
        </label>
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

        <section className="rfp-section" id="opportunities" aria-labelledby="rfp-heading">
          <div className="section-heading section-heading--plain">
            <div>
              <span className="step">02</span>
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
