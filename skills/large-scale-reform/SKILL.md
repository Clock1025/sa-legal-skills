---
name: large-scale-reform
description: Manage a long-running redesign or large-scale amendment of a student association charter, organizational regulations, or multiple connected institutional systems. Use when the work requires mapping the current framework, identifying gaps and conflicts, tracking policy decisions and deferred issues, discussing choices incrementally, or tracing cross-instrument dependencies. Do not jump directly to a full rewrite; hand sufficiently settled choices to amendment-drafting for formal proposal documents.
---

# Large-Scale Reform

Treat large-scale reform as a staged institutional design project. The human decides institutional policy. Your role is to structure the work, expose gaps and consequences, maintain decision integrity, and prepare confirmed choices for drafting. Do not turn an unresolved framework into a purportedly complete rewrite.

## Project workflow

### 1. Read and verify the current framework

Collect authoritative current copies of the charter, relevant rules, resolutions, and related materials. Record instrument names, versions, amendment and promulgation dates, effective dates, and source locations where available. Never reconstruct current text from memory. Mark missing, unofficial, or unverified material and avoid treating it as settled law.

### 2. Map institutional architecture

Describe the existing bodies, roles, powers, duties, procedures, timelines, legal effects, and relationships among instruments based on the sources. Keep this descriptive map separate from proposed changes. Identify which provisions create, limit, or depend on each arrangement.

### 3. Diagnose design issues

Identify gaps, contradictions, ambiguous assignments, unfinished procedures, unclear effects, and dependencies. Do not assume that a perceived gap should be filled in one particular way. Record each matter as an issue with its source, known facts, consequence, questions to resolve, and linked provisions or instruments.

### 4. Maintain an issue register and decision log

Do not assume chat context will be permanently available. If the execution environment supports persistent files or workspace storage, maintain suitable structured records for the individual reform case, such as `decisions.md` and `issues.md`. These case records may contain decision IDs, status, confirmed and unresolved points, dependencies, superseded decisions, and affected provisions or instruments; they are project work products and must not be written into this general skill. If persistent files are unavailable, keep the same structured decision and issue records in the current work product or conversation and make their limits clear. Use stable IDs where helpful. Do not silently overwrite a prior decision: mark it **SUPERSEDED** and link the later decision.

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

- Never record an assistant recommendation, common practice, implication, or convenient drafting assumption as the user's decision.
- A high-level institutional issue may contain principles that the user has confirmed and details that remain undecided. Split these into atomic decisions and assign each its own status. Do not downgrade an explicitly confirmed principle to DIRECTION or OPEN merely because some details are unresolved. The overall issue may remain OPEN while its confirmed atomic decisions remain CONFIRMED.
- Replies such as 「都可以」、「都行」、「沒差」 do not by themselves confirm an option. Record that there is no strong current preference, keep the decision OPEN (or DIRECTION only if the user has stated an actual direction), and ask only if a choice is needed to progress.
- If drafting must proceed temporarily on one option, label it **「暫定方案（未確認）」**, state who proposed it and what depends on it, and keep it out of the clean formal proposal unless the user later confirms it.
- Record the user's actual words or a faithful concise summary, the date/context when available, and affected decisions when this helps prevent later confusion.
- When the user changes a choice, preserve the history as SUPERSEDED; update dependent issues and identify which draft text must change.

Example record:

```text
DEC-012 人事任免制度
狀態：DIRECTION

已確認：
- 部門首長由會長提名
- 須經議會同意

尚待確認：
- 免職是否須經議會同意
- 被否決後是否可再次提名同一人
- 代理人是否適用相同程序

連動影響：
- 會長職權
- 議會職權
- 人事程序
- 就任
- 代理
- 公告
```

Atomic-decision example:

```text
ISSUE 看守機制
總體議題狀態：OPEN

CONFIRMED：重要職務原則上應設看守機制。
OPEN：適用職位、啟動條件、終止條件、代理人選、權限限制。
```

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
