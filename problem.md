---
associate: "Gaurav Saxena"
case_study: "AI Assisted RFP and RFI Response Orchestration"
---

# Hackathon Theme & Idea

## THEME
Use agentic AI to turn customer RFP and RFI documents into a traceable requirements brief, ownership plan, and managed questionnaire workflow with human review.

## IDEA
Build an AI-assisted proposal response orchestrator for account teams, pursuit managers, architects, and service-line specialists. For the hackathon MVP, it reads an RFP from an account-specific folder on the `develop` branch, validates and registers the file, extracts requirements and response themes, recommends owners, and maintains open questions through a visible workflow. The design improves requirement coverage and specialist coordination while keeping capability claims, assignments, and final response decisions under human control.

## HOW_IT_WORKS
The Receiver reads files from `RFP/<Account>/` for accounts such as Wells Fargo, JPMC, Truist, and M&T; validates supported type, required metadata, file hash, and duplicates; and adds or updates one row in an Excel RFP progress tracker. The production source is the SharePoint folder `Customer RFP Documentation`, while repository folders replace CRM email intake and SharePoint ingestion for today's MVP. The Orchestrator manages agent state, routing, retries, and status updates; the Classifier and Parser extracts scope, deliverables, dates, evaluation criteria, commercial questions, categories, and candidate winning themes from the current request and approved prior responses. The Requirements Agent produces a source-linked requirement brief, ownership map, and SLS mapping from the synthetic employee master, and the Questionnaire Agent creates and updates open questions, collates specialist responses, and returns the consolidated state to the Orchestrator.

## WHAT_MAKES_IT_DIFFERENT
The solution connects every requirement to its source, category, proposed owner, evidence, open questions, and review status instead of producing an untraceable summary. It exposes duplicates, missing evidence, unsupported claims, and ownership uncertainty, records human corrections, and uses lightweight hackathon substitutes that can later connect to CRM, SharePoint, ODS, Teams, and approved knowledge sources.

## MEASURED_RESULTS
Not yet measured. Hackathon evaluation targets are at least 90% requirement recall on a manually annotated sample, no missed designated mandatory requirement, source references for every extracted requirement and proposed factual claim, correct duplicate detection, correct flagging of a seeded unsupported claim, and lower preparation time at comparable reviewer-rated quality. Pending actions are to add a separate account lookup Markdown file, upload and refine `category.md`, create `SLS point of contact.md` from the synthetic employee master, confirm mappings for CIS, SEG and ADM, IDE, QEA, IPM, Moments, and other required teams, and replace the MVP Excel and repository intake mechanisms with ODS, CRM email, SharePoint, and collaboration integrations after the hackathon.

## WHY_IT_FITS
The solution addresses a recurring proposal-response problem: teams spend substantial time interpreting customer documents, finding the right specialists, gathering approved evidence, and coordinating unanswered questions. The MVP is feasible in one hackathon day because it demonstrates the complete request-to-reviewed-plan flow with synthetic mappings and controlled local inputs, while its source traceability, exception handling, and human approval points support the evaluation criteria for innovation, desirability, feasibility, technical quality, and responsible AI.
