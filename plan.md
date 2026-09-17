# Evolution Plan: From Assisted Productivity to an Agentified Pursuit Value Chain

## Purpose

This plan evolves the Proposal Response Orchestration solution through three capability vectors:

- **Vector 1 — Assist the team:** the current MVP foothold.
- **Vector 2 — Embed in the process:** industrialize the workflow through governed integration APIs.
- **Vector 3 — Orchestrate the value chain:** enable specialized agents to collaborate through native MCP tools while humans retain control of commitments and risk.

The progression is intentional. Vector 1 proves usefulness, Vector 2 establishes repeatability and controls, and Vector 3 adds bounded autonomy only after the required trust, governance, and operating model are in place.

## Evolution summary

| Vector | Outcome | Technology emphasis | Primary gate |
| --- | --- | --- | --- |
| **Vector 1: Assist the Team** | Enable hyperproductivity for an individual pursuit team. | React dashboard, Python agents, structured outputs, local files, JSON state, and Excel tracking. | **Usefulness + human acceptance** |
| **Vector 2: Embed in the Process** | Standardize and govern the RFP workflow across SLS and accounts. | Enterprise integration APIs, reusable connectors, centralized state, evaluations, telemetry, and role-based controls. | **Repeatability + controls + adoption** |
| **Vector 3: Orchestrate the Value Chain** | Coordinate specialized pursuit agents across enterprise systems. | Native MCP servers/tools, policy-aware orchestration, dynamic routing, durable workflows, and approval checkpoints. | **Trust + autonomy boundaries + value** |

## Guiding principles

1. **Human accountability remains explicit.** Agents prepare, recommend, route, and execute only approved actions; humans approve customer commitments, commercials, legal language, and submission.
2. **Use approved sources only.** Outputs must be traceable to the RFP, approved knowledge, prior responses, or authoritative enterprise systems.
3. **Design for least privilege.** Every API and MCP tool receives only the permissions necessary for its defined task.
4. **Separate accounts and customers.** Retrieval, state, evidence, and generated content must respect account-level authorization and confidentiality boundaries.
5. **Persist before progressing.** Each workflow step records inputs, outputs, decisions, events, errors, and approvals before the next step begins.
6. **Measure quality and business value.** Adoption, cycle time, requirement coverage, evidence quality, rework, and win-process outcomes are tracked across all vectors.
7. **Version contracts.** Agent schemas, prompts, taxonomies, integration contracts, and MCP tools are versioned to keep runs reproducible.

---

## Vector 1 — Assist the Team

### Objective

Enable a pursuit team to analyze one RFP faster, structure requirements, recommend owners and evidence, and generate review-ready working artifacts.

### Current capability

The repository currently provides:

- A React/Vite dashboard for account context, RFP documents, lifecycle status, service-line selections, and local draft state.
- **AgentOrchestrator** for routing, durable state, retries, and error handling.
- **ReceiverAgent** for validation, text extraction, SHA-256 duplicate detection, and Excel tracking.
- **ClassifierAgent** for requirements, categories, commercial questions, and evidence-backed winning themes.
- **RequirementAgent** for requirement briefs, service-line ownership mapping, and evidence gaps.
- **QuestionnaireAgent** for open questions, proposed owners, and consolidated status.
- Strict JSON schemas for model-backed agent outputs.
- PDF, DOCX, PPTX, Markdown, and plain-text extraction.
- JSON run-state files and an Excel progress tracker.
- Automated orchestration and duplicate-detection testing.

### Vector 1 work remaining

1. Connect the dashboard's **Run Agent Receiver** action to an authenticated backend API.
2. Return a durable run ID to the UI and display live pipeline events and final outputs.
3. Add human review screens for:
   - Extracted requirements
   - Service-line and owner assignments
   - Evidence gaps
   - Commercial questions
   - Questionnaire status
4. Add artifact export for review-ready requirement and questionnaire packages.
5. Add tests for every supported file type, empty extraction, schema failures, retry exhaustion, and UI-to-API behavior.
6. Establish baseline metrics before industrialization.

### Vector 1 success measures

- RFP ingestion success rate
- Duplicate-detection accuracy
- Requirement coverage confirmed by reviewers
- Time from upload to first structured brief
- Percentage of suggested owners accepted
- Reduction in manual requirement triage
- User satisfaction and repeat usage

### Vector 1 exit gate

Proceed when the solution demonstrates **usefulness and human acceptance** through representative pursuits, review evidence, documented limitations, and an agreed backlog for production controls.

---

## Vector 2 — Embed in the Process

### Objective

Industrialize the MVP as a standard, governed operating capability across SLS teams and accounts.

### Target capabilities

- Standard workflow and status model across pursuits
- Governed requirement, category, service-line, evidence, and question taxonomies
- Reusable integration connectors
- Centralized durable workflow state
- Portfolio telemetry and service management
- Role-based access and account isolation
- Automated evaluations and release controls
- Human approval gates for sensitive or consequential actions

### Integration API layer

Vector 2 introduces an application integration layer between the UI, agents, and enterprise systems. Connectors should expose stable, versioned contracts while insulating agents from system-specific implementation details.

| Enterprise system | Planned role | Initial API capabilities |
| --- | --- | --- |
| **Winzone** | Authoritative opportunity and pursuit lifecycle context. | Read opportunity, account, stage, ownership, dates, identifiers, and approved status values; propose controlled status updates after approval. |
| **Wise** | Pursuit workflow, expertise, or approved operational context. | Search approved records, resolve relevant context, and link results to the active pursuit. Exact contracts must be confirmed with the Wise product owner. |
| **Cognizant Knowledge Base** | Approved reusable capability evidence and prior-response knowledge. | Search by category, service line, account scope, approval status, source date, and expiry; return citations and reuse restrictions. |
| **SharePoint** | Controlled RFP and artifact repository. | Read source documents, write versioned working artifacts, apply account paths and metadata, and preserve document links. |
| **Teams** | Collaboration, review, and approval notifications. | Create pursuit notifications, request reviews, post status summaries, and link users back to the governed workspace. |
| **BCM Buddy** | Banking and capital-markets domain assistance and contextual guidance. | Retrieve approved domain context and route domain questions using agreed API contracts. |

All connector behavior is subject to the target system's supported APIs, data ownership, identity model, and approval process. The plan does not assume write access until system owners approve the use case and scope.

### Vector 2 target architecture

    React dashboard
          |
          v
    Authenticated application API
          |
          +--> Workflow/job service
          |       |
          |       +--> AgentOrchestrator
          |       +--> durable state database
          |       +--> artifact store
          |       +--> evaluation and telemetry
          |
          +--> Enterprise connector layer
                  +--> Winzone API
                  +--> Wise API
                  +--> Knowledge Base API
                  +--> SharePoint API
                  +--> Teams API
                  +--> BCM Buddy API

### Vector 2 delivery increments

#### V2.1 — Standardize and govern

- Define the canonical pursuit, RFP, requirement, evidence, owner, question, approval, and artifact schemas.
- Align RFP stages with the approved lifecycle definitions in `Customer RFP Documentation/RFPStatus.md`.
- Define API contracts, error models, idempotency keys, correlation IDs, and versioning rules.
- Establish account-level access rules, retention, audit, and data-classification policies.
- Create golden RFP datasets and evaluation scorecards.
- Assign business and technical owners for every connector.

#### V2.2 — Connect read paths

- Read opportunity and account context from Winzone.
- Retrieve approved evidence from the Cognizant Knowledge Base.
- Read source RFPs and metadata from SharePoint.
- Retrieve approved Wise and BCM Buddy context.
- Display source citations, ownership, freshness, and reuse restrictions in the UI.
- Add connector health, latency, error, and authorization telemetry.

#### V2.3 — Operationalize the workflow

- Replace browser-only events with durable API-created jobs.
- Add asynchronous workers, status APIs, cancellation, safe retries, and resume behavior.
- Persist state in a transactional store and artifacts in an approved repository.
- Send Teams review requests and status notifications.
- Add approval workflows before any enterprise write action.
- Introduce service objectives, support ownership, incident procedures, and operational dashboards.

#### V2.4 — Scale adoption

- Roll out by controlled account and service-line cohorts.
- Train proposal, SLS, sales, legal, finance, and knowledge owners.
- Measure adoption, quality, rework, and cycle time.
- Use evaluation results and user feedback as release gates.
- Retire duplicate manual steps only after controlled validation.

### Vector 2 exit gate

Proceed when the workflow demonstrates **repeatability, controls, and adoption**:

- Standard process and schemas are approved.
- Connectors meet security and reliability requirements.
- Account isolation and audit evidence are verified.
- Human approvals are enforced.
- Evaluations meet agreed thresholds.
- Multiple teams use the capability consistently.
- Operations and support ownership are active.

---

## Vector 3 — Orchestrate the Value Chain

### Objective

Agentify the enterprise pursuit value chain so specialized agents can collaborate, dynamically route work, and execute approved actions across enterprise systems within explicit autonomy boundaries.

### Native MCP approach

Vector 3 exposes enterprise capabilities as governed native MCP servers and tools. The orchestrator acts as an MCP client and selects only allow-listed tools based on the workflow state, user role, account, and policy.

Proposed MCP domains:

| MCP server/domain | Example bounded tools |
| --- | --- |
| **Winzone MCP** | Get opportunity, get stage, validate transition, prepare approved update |
| **Wise MCP** | Search approved pursuit context, retrieve referenced record |
| **Knowledge MCP** | Search approved evidence, get citation, validate reuse eligibility |
| **SharePoint MCP** | Get RFP, list versions, save draft artifact, retrieve metadata |
| **Teams MCP** | Create approval request, post status update, resolve response |
| **BCM Buddy MCP** | Retrieve approved BCM context, route domain clarification |
| **Governance MCP** | Evaluate policy, request approval, record decision, retrieve audit event |

Tool names, inputs, outputs, permissions, and side effects must be explicit. Read tools and write tools should be separated, and write tools must support idempotency, audit metadata, and approval references.

### Specialized agent collaboration

The existing agents remain focused and are extended with additional roles as justified:

- **PursuitCoordinatorAgent** — maintains the end-to-end plan, dependencies, deadlines, and stage readiness.
- **EvidenceAgent** — retrieves approved evidence with citations, freshness, and reuse restrictions.
- **CommercialAgent** — identifies commercial inputs and routes them to authorized finance owners without making commitments.
- **RiskAndComplianceAgent** — checks confidentiality, policy, legal, security, and responsible-AI conditions.
- **ReviewAgent** — evaluates completeness, traceability, consistency, unsupported claims, and approval readiness.
- **CommunicationAgent** — prepares Teams updates and approval requests for human confirmation.
- Existing Receiver, Classifier, Requirement, and Questionnaire agents continue to own their bounded responsibilities.

Adding an agent requires a clear business responsibility, strict schema, approved tool set, evaluation suite, accountable human owner, and documented failure behavior.

### Dynamic orchestration

The Vector 3 orchestrator should:

1. Build a workflow plan from the opportunity, RFP, policy, and deadline.
2. Route tasks based on requirement category, service line, confidence, risk, and current stage.
3. Execute independent read-only tasks concurrently when safe.
4. Pause for human input when evidence, ownership, or policy is ambiguous.
5. Require approval before messages, repository writes, status changes, or commitments.
6. Retry only idempotent operations and route exceptions to named owners.
7. Record tool calls, source citations, model/schema versions, approvals, and outcomes.
8. Re-plan when upstream facts, deadlines, or approvals change.

### Autonomy boundaries

| Action class | Default policy |
| --- | --- |
| Read approved pursuit metadata | Automatic within user and account scope |
| Search approved knowledge | Automatic with citations and reuse checks |
| Analyze and draft | Automatic, clearly labeled as working draft |
| Assign or recommend owners | Recommendation only until human acceptance |
| Send Teams messages | Human approval unless an approved workflow explicitly delegates it |
| Write SharePoint artifacts | Human approval and versioned destination |
| Change Winzone stage or opportunity data | Human approval and authoritative validation |
| Make commercial, legal, delivery, or customer commitments | Human decision only |
| Submit a proposal | Human decision only |

### Vector 3 success measures

- End-to-end pursuit cycle-time reduction
- Percentage of requirements linked to approved evidence
- Approval turnaround time
- Exception and escalation rate
- Agent action acceptance/reversal rate
- Unsupported-claim rate
- Reuse rate of approved knowledge
- Workflow reliability and recovery time
- User trust and adoption
- Business value realized per pursuit

### Vector 3 exit gate

Vector 3 is successful when the solution demonstrates **trust, explicit autonomy boundaries, and measurable value**:

- Every action is attributable and auditable.
- High-impact actions require enforced approval.
- MCP tools are allow-listed, least-privilege, and evaluated.
- Dynamic routing handles expected exceptions safely.
- Users understand and trust agent recommendations.
- Quality and value metrics improve without increasing risk.

---

## Foundation across all vectors

### Approved data

- Authoritative source designation
- Account-level access control
- Citation and lineage
- Freshness and expiry
- Reuse restrictions
- Retention and deletion

### Identity and permissions

- Enterprise single sign-on
- Role- and attribute-based authorization
- Service identities for connectors and MCP servers
- Least-privilege scopes
- Segregation of duties for approvals
- Periodic access reviews

### Responsible AI

- Approved models and use cases
- Prompt and schema versioning
- Human review boundaries
- Bias, hallucination, and unsupported-claim testing
- Customer-data handling controls
- Incident and override procedures

### Observability and evaluation

- Correlation ID across UI, API, workflow, agents, and enterprise tools
- Structured events and audit logs
- Latency, failure, retry, and cost metrics
- Offline golden-set evaluations
- Online quality sampling
- Connector and MCP tool health
- Approval and override analytics

### Change adoption

- Named process owners
- Role-based training
- Pilot cohorts and champions
- Feedback and support channels
- Release notes and workflow documentation
- Adoption dashboards
- Controlled retirement of superseded manual processes

## Governance and ownership

| Area | Accountable owner |
| --- | --- |
| Pursuit process and stage definitions | Sales/pursuit operations |
| RFP content and customer commitments | Pursuit lead and authorized reviewers |
| Category and service-line taxonomy | SLS/process owner |
| Knowledge quality and reuse | Knowledge owner |
| Commercial decisions | Finance/commercial owner |
| Legal and confidentiality | Legal and compliance |
| Platform, APIs, and MCP servers | Engineering/platform owner |
| Identity and access | Security/IAM |
| Model and evaluation governance | Responsible AI/model owner |
| Production operations | Service owner |

Named individuals and escalation paths should be added before production rollout.

## Delivery controls

Each increment must include:

- Architecture and threat review
- Data-flow and permission review
- Versioned schemas and contracts
- Automated functional and security tests
- Agent and tool evaluations
- Rollback and recovery procedure
- Human-approval validation
- Operational runbook
- Pilot acceptance criteria
- Documented go/no-go decision

## Immediate next actions

1. Complete the Vector 1 UI-to-orchestrator API boundary.
2. Agree the canonical workflow and data contracts for Vector 2.
3. Confirm product owners, supported APIs, and permission models for Winzone, Wise, Cognizant Knowledge Base, Teams, SharePoint, and BCM Buddy.
4. Prioritize read-only integrations before write operations.
5. Define the evaluation scorecard and baseline Vector 1 metrics.
6. Select a controlled pilot account and representative RFP set.
7. Document approval gates and autonomy boundaries.
8. Prototype one native MCP read path after its API connector and governance controls are stable.
9. Review progress at each vector gate before expanding scope.

## Related documentation

- [Architecture](Architecture.md)
- [Orchestration setup](orchestration/README.md)
- [Required inputs and production dependencies](orchestration/INPUTS.md)
- [RFP stage definitions](Customer%20RFP%20Documentation/RFPStatus.md)
