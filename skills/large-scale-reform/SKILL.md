---
name: large-scale-reform
description: Manage a long-running redesign or large-scale amendment of a student association charter, organizational regulations, or multiple connected institutional systems. Use when the work requires mapping the current framework, identifying gaps and conflicts, tracking policy decisions and deferred issues, discussing choices incrementally, or tracing cross-instrument dependencies. Do not jump directly to a full rewrite; hand sufficiently settled choices to amendment-drafting for formal proposal documents.
---

# Large-Scale Reform

Treat large-scale reform as a staged institutional design project. The human decides institutional policy. Your role is to structure the work, expose gaps and consequences, maintain decision integrity, and prepare confirmed choices for drafting. Do not turn an unresolved framework into a purportedly complete rewrite.

## Skill Feedback Package

Recognize: 「請產生完整 Skill 回報包，包含可取得的完整對話紀錄。」 Follow the single [feedback-package contract](../../docs/feedback-package.md) when accessible. This is retrospective archiving, not a new legal-work stage: do not block it with the Skill-switch read gate or use it to perform unread-Skill work. Existing policy statuses, scope, source fidelity and formal-work read gates still apply.

Even with only the Release ZIP and no docs, export only actually available user-visible user/assistant turns in order, preserving verbatim text and separating summaries/redactions. Never reconstruct lost dialogue, hidden prompts/private reasoning, unavailable tools or attachments. Record platform product/surface separately from model segments (E1/E2), actual stage-specific Skill paths/reads/versions (unknown: UNVERIFIED), D/I/SRC references, attachments/outputs and evidence anchors; distinguish OBSERVED, SELF_REPORTED and UNVERIFIED. Use transcript_completeness COMPLETE only for a declared, checked user-visible scope without gaps/redactions; known missing/truncated/summarized/redacted content is PARTIAL, unknown coverage UNVERIFIED. Disclose endpoints, evidence, omissions and verification limits; never turn static checks or self-assessment into model/quality PASS.

Reuse a recorded 8-character conversation ID (canonical platform code + six lowercase letters/digits); if platform/surface or its canonical code cannot be checked use UU and disclose the uncertainty, not a guess from model name. Keep model/Skill changes segmented; when ID persistence is unavailable disclose it and let the user supply an existing ID. Use report_<conversation-id>_<YYMMDD>_<4-character-alphanumeric-suffix>.zip, checking collisions; use a reliable or explicitly supplied date, never invent a timestamp or claim secure randomness without a tool call. Produce manifest.json (schema_version, conversation_id/report_id/generated_at, platform/model_segments/skill_reads, transcript coverage, sources, attachments/outputs, limitations/redactions, actual file index), report.md, transcript.md, sources-index.md and attachments/INDEX.md plus outputs/INDEX.md even when empty. If canonical docs are unavailable, disclose that limit and leave unknown fields null/UNKNOWN/UNVERIFIED rather than inventing the schema's details.

Copy raw files only when accessible, explicitly authorized and minimally necessary; no automatic external upload. Compute SHA-256/byte sizes only from actual bytes. Provide a real downloadable ZIP only after creating and checking it. Without file/ZIP capability, provide copyable text sections for manifest/report/transcript and all indexes, disclose omitted files/features and manual save/pack steps, and never give a nonexistent download link. A feedback export does not verify legal sources, user decisions, model obedience or DOCX quality.

## Stage provenance and incomplete input

At the start or resumption of a work stage, when switching Skills, or before reusing old work materials, record the active Skill file and source path, the verifiable version/commit/ref (if available), and whether its complete contents were actually read in this turn. Distinguish a prior read from a current read; never claim to have read an unread version. Reacquire and fully read the applicable Skill for a new or resumed stage before formal work. If a version or source cannot be checked, mark it **UNVERIFIED** and explicitly request the source needed to verify it; do not invent a commit or rely on model memory. A readable supplied Skill with an unknown ref remains version-UNVERIFIED, not falsely verified.

When switching Skills, fully read the new Skill before any formal or provisional work in that stage. If it cannot be obtained and fully read, stop at obtaining/pasting/uploading that Skill. Earlier materials, confirmed policy, urgency, or a request to draft first do not bypass the START-HERE read gate.

If an instruction or proposed legal text is ambiguous, truncated, or missing words that could change legal effect, identify the exact incomplete fragment and ask one necessary clarification question before acting on it. Never silently supply a legally substantive completion, including a clause ending in 「由」. Continue only independent work whose meaning does not depend on the missing text. Pure formatting or an obvious typo with no effect on legal meaning may follow existing editorial rules; never use “technical correction” to hide a change in meaning or alter a faithful quotation.

## Project workflow

### 1. Read and verify the current framework

Collect authoritative current copies of the charter, relevant rules, resolutions, and related materials. Record instrument names, versions, amendment and promulgation dates, effective dates, and source locations where available. Never reconstruct current text from memory. Mark missing, unofficial, or unverified material and avoid treating it as settled law.

### 2. Map institutional architecture

Describe the existing bodies, roles, powers, duties, procedures, timelines, legal effects, and relationships among instruments based on the sources. Keep this descriptive map separate from proposed changes. Identify which provisions create, limit, or depend on each arrangement.

### 3. Diagnose design issues

Identify gaps, contradictions, ambiguous assignments, unfinished procedures, unclear effects, and dependencies. Do not assume that a perceived gap should be filled in one particular way. Record each matter as an issue with its source, known facts, consequence, questions to resolve, and linked provisions or instruments.

### 4. Maintain an issue register and decision log

Do not assume chat context will be permanently available. If the execution environment supports persistent files or workspace storage, maintain suitable structured records for the individual reform case, such as `decisions.md` and `issues.md`. These case records may contain decision IDs, status, confirmed and unresolved points, dependencies, superseded decisions, and affected provisions or instruments; they are project work products and must not be written into this general skill. If persistent files are unavailable, keep the same structured decision and issue records in the current work product or conversation and make their limits clear. Use stable decision, issue, and source IDs independent of article numbers (for example, `D-001`, `I-001`, and `SRC-001`); never use an old article number as an immutable identity. Do not silently overwrite a prior decision: mark it **SUPERSEDED** and link the later decision.

For each source record, retain its original instrument/document, verifiable version and source location, and whether it is current law or a proposal. Never fabricate sources, versions, text, or simulated document provenance. Link decisions and issues to those source IDs. Each decision record must include its content, status, affected instruments and scope, the user's confirmation context (if any), and later changes or supersession links. When renumbering, preserve the stable IDs and an old-to-new provision mapping with instrument and version on both sides; keep earlier mappings rather than overwriting history. If a record cannot be persisted, include the same traceable fields in the working material and disclose that limitation.

### 5. Trace cross-rule dependencies

Map provisions affected by a choice, including authority, procedures, appointments, terms, assumption and leaving office, acting service, publication, effective dates, and connected regulations. Record the direction of the dependency and the affected source provisions. Do not assume that a policy decision automatically settles its procedural or technical implementation.

### 6. Discuss decisions incrementally

Present a manageable issue or connected set of issues at a time. Explain the practical and institutional consequences of available choices without choosing for the user. The user may answer one complex issue at a time and may explicitly defer others. Continue work on sufficiently settled areas while keeping dependencies and unresolved points visible; do not block all progress because other issues remain OPEN or DEFERRED.

### 7. Draft coherent portions when ready

Do not require a linear project sequence or resolution of every issue before drafting begins. When the choices for one coherent portion are sufficiently clear, provide its decision record and verified source text to `amendment-drafting`, even while other parts remain OPEN or DEFERRED. That skill prepares formal provisions, reasons, comparison tables, proposal materials, and, when the environment supports it, DOCX. Do not let a temporary drafting assumption migrate into a clean formal proposal.

## Decision Integrity

Assign a state to each important institutional decision. Use these exact status labels:

- **CONFIRMED** — the user has explicitly decided this point.
- **DIRECTION** — the user has expressed a clear preference or direction, but material details remain unsettled.
- **OPEN** — the issue has been identified, but the user has not decided it.
- **DEFERRED** — the user has explicitly asked to address it later.
- **ASSISTANT_PROPOSAL** — the assistant has suggested an option that the user has not confirmed.
- **SUPERSEDED** — a later user decision has replaced this earlier decision; link the replacement where possible.

Apply these safeguards:

- Never record an assistant recommendation, common practice, implication, or convenient drafting assumption as the user's decision. Only **CONFIRMED** policy within its recorded scope may enter a clean formal draft. DIRECTION, OPEN, DEFERRED, SUPERSEDED, and ASSISTANT_PROPOSAL must remain outside it; discuss them only in clearly labeled, separate working candidates.
- 「比較傾向 C」 is DIRECTION unless the conversation explicitly completes that decision. 「加上去」 or 「照這個」 confirms only the specific option, scope, and policy consequences clearly presented at that time and traceable to that reply. If the referent is unclear, ask what was agreed; never promote the whole surrounding context.
- Confirmation is bound to the specified instruments, offices, and institutional scope. A later-added instrument or source is not automatically covered: separate previously confirmed policy from the new scope still needing confirmation. If the new source changes the proposal's premises, ask again before extending or implementing the affected decision. Do not confuse proposal text with effective current law.
- A change to the legal subject, regulated persons, powers, legal effects, periods, mandatory procedures, or exceptions is a **possible substantive change**, even if only a few words change. Explain the possible effect and obtain user confirmation for that change before adopting it; existing confirmation suffices only when it explicitly covers this change. For example, changing 「該會議」 to 「其出席之會議」 may alter scope and must not be treated as mere editing.
- A high-level institutional issue may contain principles that the user has confirmed and details that remain undecided. Split these into atomic decisions and assign each its own status. Do not downgrade an explicitly confirmed principle to DIRECTION or OPEN merely because some details are unresolved. The overall issue may remain OPEN while its confirmed atomic decisions remain CONFIRMED.
- Replies such as 「都可以」、「都行」、「沒差」 do not by themselves confirm an option. Record that there is no strong current preference, keep the decision OPEN (or DIRECTION only if the user has stated an actual direction), and ask only if a choice is needed to progress.
- If drafting must proceed temporarily on one option, label it **「暫定方案（未確認）」**, state who proposed it and what depends on it, and keep it out of the clean formal proposal unless the user later confirms it.
- Record the user's actual words or a faithful concise summary, the date/context when available, and affected decisions when this helps prevent later confusion.
- When the user changes a choice, preserve the history as SUPERSEDED; update dependent issues and identify which draft text must change.

Example record (fictional demonstration, not actual case evidence):

The following examples contain stipulated fictional user statements only. Their SRC records make those statements traceable within each example; they are not real user decisions or verified legal sources. Legal text has not been supplied, so its version/location is UNVERIFIED and must be obtained before legal comparison or a definitive formal proposal. In real work, replace demonstration evidence with actual, checkable user records; never copy these decisions into a case.

```json
{
  "example_type": "FICTIONAL_DEMONSTRATION",
  "sources": [
    {"id": "SRC-001", "type": "fictional_user_statement", "document": "本範例內的虛構對話，非真實使用者紀錄", "version": "example-1", "location": "message-1", "text": "我確認：僅《組織規則》的正職部門首長由會長提名，任命須經議會同意。免職程序我比較傾向也經議會同意，尚未決定。"},
    {"id": "SRC-002", "type": "legal_text_not_provided", "document": "示意《組織規則》（非真實法規來源）", "version": "UNVERIFIED", "location": "UNVERIFIED", "text": null}
  ],
  "issue": {"id": "I-001", "title": "人事任免制度", "status": "OPEN", "decision_ids": ["D-001", "D-002", "D-003", "D-004"]},
  "decisions": [
    {"id": "D-001", "issue_id": "I-001", "content": "正職部門首長由會長提名", "status": "CONFIRMED", "scope": {"instrument": "示意《組織規則》", "offices": ["部門首長"], "limits": "僅正職部門首長；不含代理人或其他職務"}, "source_ids": ["SRC-001", "SRC-002"], "confirmation_basis": {"source_id": "SRC-001", "location": "message-1", "quote": "我確認：僅《組織規則》的正職部門首長由會長提名，任命須經議會同意。"}, "superseded_by": null},
    {"id": "D-002", "issue_id": "I-001", "content": "正職部門首長任命須經議會同意", "status": "CONFIRMED", "scope": {"instrument": "示意《組織規則》", "offices": ["部門首長"], "limits": "僅正職部門首長；不含代理人或其他職務"}, "source_ids": ["SRC-001", "SRC-002"], "confirmation_basis": {"source_id": "SRC-001", "location": "message-1", "quote": "我確認：僅《組織規則》的正職部門首長由會長提名，任命須經議會同意。"}, "superseded_by": null},
    {"id": "D-003", "issue_id": "I-001", "content": "傾向正職部門首長免職也須經議會同意，尚未決定", "status": "DIRECTION", "scope": {"instrument": "示意《組織規則》", "offices": ["部門首長"], "limits": "僅正職部門首長；不含代理人或其他職務"}, "source_ids": ["SRC-001", "SRC-002"], "confirmation_basis": null, "superseded_by": null},
    {"id": "D-004", "issue_id": "I-001", "content": "代理人是否適用同一任免程序", "status": "OPEN", "scope": {"instrument": "示意《組織規則》", "offices": ["代理部門首長"], "limits": "只討論代理職務；未確認適用正職規則"}, "source_ids": ["SRC-002"], "confirmation_basis": null, "superseded_by": null}
  ]
}
```

Atomic-decision example (fictional demonstration):

```json
{
  "example_type": "FICTIONAL_DEMONSTRATION",
  "sources": [
    {"id": "SRC-003", "type": "fictional_user_statement", "document": "本範例內的虛構對話，非真實使用者紀錄", "version": "example-1", "location": "message-1", "text": "我確認《組織規則》的會長與副會長應有看守機制，但具體條件與權限還沒決定。"},
    {"id": "SRC-004", "type": "legal_text_not_provided", "document": "示意《組織規則》（非真實法規來源）", "version": "UNVERIFIED", "location": "UNVERIFIED", "text": null}
  ],
  "issue": {"id": "I-002", "title": "看守機制", "status": "OPEN", "decision_ids": ["D-005", "D-006", "D-007", "D-008", "D-009"]},
  "decisions": [
    {"id": "D-005", "issue_id": "I-002", "content": "會長與副會長應有看守機制的原則", "status": "CONFIRMED", "scope": {"instrument": "示意《組織規則》", "offices": ["會長", "副會長"], "limits": "僅看守原則；不含啟動、終止、人選、權限或其他職位"}, "source_ids": ["SRC-003", "SRC-004"], "confirmation_basis": {"source_id": "SRC-003", "location": "message-1", "quote": "我確認《組織規則》的會長與副會長應有看守機制，但具體條件與權限還沒決定。"}, "superseded_by": null},
    {"id": "D-006", "issue_id": "I-002", "content": "看守機制啟動條件", "status": "OPEN", "scope": {"instrument": "示意《組織規則》", "offices": ["會長", "副會長"], "limits": "僅該項待決細節；原則確認不等於細節確認"}, "source_ids": ["SRC-004"], "confirmation_basis": null, "superseded_by": null},
    {"id": "D-007", "issue_id": "I-002", "content": "看守機制終止條件", "status": "OPEN", "scope": {"instrument": "示意《組織規則》", "offices": ["會長", "副會長"], "limits": "僅該項待決細節；原則確認不等於細節確認"}, "source_ids": ["SRC-004"], "confirmation_basis": null, "superseded_by": null},
    {"id": "D-008", "issue_id": "I-002", "content": "看守人選", "status": "OPEN", "scope": {"instrument": "示意《組織規則》", "offices": ["會長", "副會長"], "limits": "僅該項待決細節；原則確認不等於細節確認"}, "source_ids": ["SRC-004"], "confirmation_basis": null, "superseded_by": null},
    {"id": "D-009", "issue_id": "I-002", "content": "看守權限限制", "status": "OPEN", "scope": {"instrument": "示意《組織規則》", "offices": ["會長", "副會長"], "limits": "僅該項待決細節；原則確認不等於細節確認"}, "source_ids": ["SRC-004"], "confirmation_basis": null, "superseded_by": null}
  ]
}
```

The I-level status describes the overall unresolved issue, not the status of every linked D-level decision. Each atomic decision keeps its own status, scope, and confirmation evidence: DIRECTION/OPEN records have no confirmation_basis. CONFIRMED records in these examples demonstrate only the explicitly stated scope in the fictional input; they do not confirm unprovided legal text or authorize new offices or implementation details.

## Policy / Implementation Separation

Track these as distinct decision layers:

1. **制度原則** — what the institutional rule should require or permit.
2. **法律／程序需求** — the process and legal effect required to carry out that principle.
3. **技術實作方式** — tools or operational systems used to perform the process.

Confirmation at one layer does not decide the others. For example, 「採法規公告型」 does not itself decide 「資訊系統自動公告」; 「任命應公告」 does not require a particular online system. Record each layer separately with its own decision state. Avoid introducing a technical implementation as if it were inherent in the policy choice.

Technical implementation choices must not automatically become blocking OPEN items for institutional reform. If a rule can be designed in a technology-neutral way, record whether to build an information system, which platform to use, or whether to automate as implementation-layer issues, not as unresolved policy itself. Unless the user explicitly says a technical option is necessary for the institution to function, do not block completion of formal institutional design because that technical option is undecided. For example:

```text
CONFIRMED：法規公告制度不得依賴特定資訊系統存在。
Layer: IMPLEMENTATION
Status: OPEN
Issue: 未來是否建置資訊系統、使用何種公告工具。
```

Do not infer 「資訊系統自動公告」 from a decision to adopt a 「法規公告型」制度.

## Completion review

Before treating a reform portion as ready for formal drafting, review at least:

- Article numbers for duplication, gaps, and intended renumbering.
- Every internal and external cross-reference for accuracy.
- Consistent names for bodies, offices, titles, and defined terms.
- Authority matched to duties; flag any actor with responsibility but no adequate authority (**有責無權**).
- Powers paired with necessary limits and procedures; flag power without a procedure (**有權但無程序**).
- Procedures connected to an explicit legal effect; flag process with no stated consequence (**程序但沒有法律效果**).
- Completeness of terms, assumption of office, and leaving office.
- Resignation, removal, and acting-service rules for gaps in authority or continuity.
- Consistency of promulgation/publication and effective-date rules.
- Need for transitional provisions and treatment of pending matters.
- Other instruments requiring consequential amendment.
- Which choices remain OPEN, DIRECTION, DEFERRED, or ASSISTANT_PROPOSAL and therefore must not appear as confirmed policy in a clean proposal.

Completion of the checklist does not authorize the assistant to decide unresolved matters. Report remaining decisions and limits to the user.

## Formal procedure boundary

AI may analyze, recommend, draft, and prepare proposal materials. It must not send an email, formally submit or sign a proposal, promulgate a rule, appoint, remove, resign, adjudicate, or claim a proposal was submitted or passed or a rule promulgated or effective. Only the responsible human and institutional process can take those actions.
