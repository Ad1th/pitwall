# PITWALL — Autonomous Agent Handoff & Development Workflow

`docs/AGENT_WORKFLOW.md`

---

## 1. Operating Instructions for Future Coding Agents

You are acting as a specialized software engineer assigned to implement specific stages of **PITWALL**. To ensure strict architectural integrity, code quality, and competition readiness, you MUST follow this operational protocol:

### Step 1: Context Assimilation
Before writing any code or modifying existing files:
1. Read `docs/PRD.md` to understand core requirements and non-negotiables.
2. Read `docs/ARCHITECTURE.md` to understand system component boundaries.
3. Read `docs/DEVELOPMENT_PLAN.md` and identify your assigned stage.
4. Read `docs/DECISIONS.md` to check existing Architectural Decision Records.

### Step 2: Strict Scope Enforcement
- Implement **ONLY** the requirements specified for your current assigned stage.
- Do NOT skip ahead or implement partial features from future stages unless explicitly instructed.
- Do NOT alter core database schemas or API contracts defined in `docs/DATABASE.md` or `docs/API.md` without documenting the change in `docs/DECISIONS.md`.

### Step 3: Verification & Quality Gate
- Every stage must include automated unit/integration tests located in `tests/`.
- Run tests before concluding your turn:
  - Python: `pytest`
  - Frontend: `npm run build`
- Ensure all tests pass with **0 errors**.

### Step 4: Mandatory Stage Completion Report
When finishing your turn, provide a structured completion report containing:
1. **Stage Completed**: Stage number and title.
2. **Files Created / Modified**: List of exact relative file paths.
3. **Requirements Fulfilled**: Unique requirement IDs completed (e.g., `FR-001`, `MODEL-002`).
4. **Verification Results**: Command output summary confirming all tests pass.
5. **Decisions / Deviations**: Any ADR logged in `docs/DECISIONS.md`.
6. **Next Stage Prompt**: Exact copy-paste prompt for the user to invoke the next agent.

---

## 2. Standardized Next Agent Prompt Template

```text
Build according to the PITWALL PRD. Next stage: implement Stage [N]: [Stage Name].
First read docs/PRD.md, docs/ARCHITECTURE.md, docs/DEVELOPMENT_PLAN.md, and docs/AGENT_WORKFLOW.md.
```
