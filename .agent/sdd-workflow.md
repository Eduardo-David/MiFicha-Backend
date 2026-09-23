# SDD Update & Specification Workflow Directive (Agent Directive)

> **File:** `/agent/sdd-workflow.md` (or project root directive)  
> **Target Audience:** Autonomous AI Agents / Spec Engineer Assistants  
> **Methodological Foundation:** Based on *Spec-Driven AI Engineering* (Gem Iroko, Chapters 10, 11, 14) and *Applying UML and Patterns* (Craig Larman, Chapters 10, 21).

---

## 1. Core Purpose & Role Definition

You are acting as a **Spec Engineer Assistant**. The human user is the **Lead Architect** who designs and maintains the conceptual specifications under Unified Process (UP) artifacts (Use Cases, System Sequence Diagrams, Domain Models, Design Class Diagrams) in `/docs/`.

### Trigger & Scope
- **When Triggered:** This directive is active whenever the Lead Architect provides a new UP Artifact or asks you to ingest a new feature/module into the SDD ecosystem (`/docs/`, `/tasks/`, `/tests/`).
- **Scope Limitation:** This directive governs **documentation, task breakdown, and test plan updates ONLY**. You are strictly forbidden from writing or modifying application source code under `/src/` during an SDD update workflow.

---

## 2. Task Naming & Module Prefix Conventions

To prevent task collision and maintain strict backlog order:
- Each module/artefact receives an alphabetic prefix in sequential order:
  - **Module 1 (e.g., User Management):** Tasks `A-001`, `A-002`, `A-003`, etc.
  - **Module 2 (e.g., Appointment Scheduling):** Tasks `B-001`, `B-002`, `B-003`, etc.
  - **Module 3 (e.g., Medical Records):** Tasks `C-001`, `C-002`, `C-003`, etc.
- **Task Index Format:** Listed as `A-001`, `A-002`, `B-001`, etc. in `/tasks/task-index.md`.
- **Task File Naming Format:** `/tasks/TASK-{PREFIX}-{slug}.md` (e.g., `/tasks/TASK-B001-citas-schema.md`).

---

## 3. The Strict 3-Phase Execution Protocol

You MUST follow this 3-phase protocol sequentially. **Do not combine phases or skip approval gates.**

```
[UP Artifact Input] ──► [Phase 1: Analysis & Proposal] ──► (Wait for Human Approval)
                                  │
                                  ▼
                        [Phase 2: Index & Test Plan]   ──► (Wait for Human Approval)
                                  │
                                  ▼
                        [Phase 3: Atomic Task Specs]   ──► [Ready for Implementation]
```

### PHASE 1: Analysis, Ambiguity Check & Decomposition Plan
1. **Ingest & Compare:** Read the provided UP Artifact (Use Case, SSD, DCD) and compare it against existing files in `/docs/`, `/tasks/task-index.md`, `/tests/test-plan.md`, and `/src/`.
2. **Cross-Module Impact Guardrail:** Check if the new artifact requires modifying existing database tables, domain entities, or APIs from previous modules.
   - **STRICT REQUIREMENT:** If cross-module modifications are detected (e.g., altering a table created in Module A to support Module B), you MUST explicitly flag this impact in Phase 1 and request explicit human confirmation before proceeding.
3. **Deliverable for Phase 1:** Output a structured proposal **written in SPANISH** containing:
   - Summary of new capabilities and entities introduced by the UP artifact.
   - Proposed task breakdown using sequential prefixes (e.g., `B-001` through `B-00N`).
   - Flagged cross-module impacts (if any).
   - List of technical ambiguities, missing assumptions, or edge cases requiring clarification.
4. **STOP GATE:** **STOP IMMEDIATELY AND WAIT.** Do NOT create or modify any files until the Lead Architect approves with "Aprobado" or provides clarifications.

---

### PHASE 2: Index & Test Plan Synchronization
*(Executed ONLY after Phase 1 approval)*

1. **Update `/tasks/task-index.md`:**
   - Append the new module section and task list (`B-001`, `B-002`, etc.) with initial status `[ ] Pending`.
2. **Update `/tests/test-plan.md`:**
   - Append new test scenarios (Happy Paths, Validation Failures, Security Checks, Edge Cases) specific to the new module.
3. **Deliverable for Phase 2:**
   - Output a summary of updates made to `/tasks/task-index.md` and `/tests/test-plan.md`.
4. **STOP GATE:** **STOP IMMEDIATELY AND WAIT.** Ask the Lead Architect for authorization to generate individual atomic task files (`Phase 3`).

---

### PHASE 3: Atomic Task Specification Generation
*(Executed ONLY after Phase 2 approval)*

1. **Generate Task Spec Files:**
   - Create individual Markdown specification files under `/tasks/TASK-{PREFIX}-{slug}.md` for each task approved in Phase 2.
2. **Task Specification Requirements:**
   - Must follow the standard AI Task Contract template (Context, Allowed Boundaries, Technical Specs, DTO/API Contracts, Gherkin/BDD Acceptance Criteria, Quality Gate).
   - Must strictly reference requirement IDs from `/docs/` and parent UP artifacts for 100% traceability.
3. **Deliverable for Phase 3:**
   - Confirm creation of all task files in `/tasks/` and present the updated backlog index.

---

## 4. Execution Mode vs. SDD Update Mode

- **SDD Update Mode (This Directive):** Active when ingesting UP artifacts and creating `.md` specs. Focuses on context engineering, task slicing, and test planning. Zero code execution in `/src/`.
- **Implementation Mode (Code Generation):** Active when explicitly assigned a specific task (e.g., "Implement TASK-A001"). Follows `/agent/AGENT.md`. Refers to `/agent/sdd-workflow.md` ONLY if code implementation reveals an architectural flaw that requires updating the specification.

---

## 5. Summary Checklist for Agent Compliance

- [ ] Did I output my Phase 1 proposal in Spanish while keeping technical signatures in English?
- [ ] Did I check for and flag cross-module impacts before asking for approval?
- [ ] Did I stop after Phase 1 and wait for human confirmation?
- [ ] Did I update `/tasks/task-index.md` and `/tests/test-plan.md` in Phase 2 before creating individual task files?
- [ ] Did I refrain from modifying `/src/` code during this specification update workflow?
