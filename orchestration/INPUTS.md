# Inputs Required to Run the Agents

## Required for the hackathon MVP

1. OpenAI project credentials: `OPENAI_API_KEY` and access to the model named by `OPENAI_MODEL`.
2. At least one RFP under `RFP/<Account>/`. Supported formats are PDF, DOCX, PPTX, TXT, and Markdown.
3. The account name passed to the CLI, such as `WellsFargo`, `JPMC`, `Truist`, or `M&T`.
4. Writable locations for the Excel tracker and JSON run-state files.

## Strongly recommended knowledge inputs

1. `knowledge/category.md`: approved category names, descriptions, synonyms, and routing rules. Initial examples include application modernization, cloud migration, QEA automation, AI and analytics, infrastructure, security, ERP, CRM, and process automation.
2. `knowledge/SLS point of contact.md`: service line, practice/function, named owner, role, skills, email, escalation owner, and active/inactive status. If absent, the agent can read `knowledge/Synthetic_Service_Line_Employee_Master.xlsx`.
3. Approved prior RFP responses and capability evidence with owner, approval status, source date, expiry date, customer restrictions, and reusable/non-reusable status.
4. Per-account lookup Markdown containing aliases, folder path, CRM/pursuit identifiers, contacts, confidentiality rules, and approved knowledge scope.

## Needed for production integrations after the MVP

- CRM/email event contract and credentials
- SharePoint site, library, `Customer RFP Documentation` folder path, and application permissions
- ODS schema or API contract for RFP state
- Teams destination and approval workflow
- Identity, client-separation, retention, audit, legal, finance, and submission policies
- Retry limits, service-level objectives, and human approval gates


