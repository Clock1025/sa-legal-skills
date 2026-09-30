---
name: amendment-drafting
description: Turn a sufficiently settled student association or student self-governance policy direction into formal legislative drafting materials. Use for drafting new provisions, amending provisions, deleting provisions, preparing amendment reasons and proposal documents, an amendment comparison table, a proposal email draft, or editable DOCX content. Do not use to decide unresolved policy choices or to manage a whole-charter reform project.
---

# Amendment Drafting

Translate the user's chosen institutional direction into precise, internally consistent legal text and proposal materials. The user owns policy choices. Clarify ambiguity that affects substance; do not silently change a choice to make drafting easier. When a large-scale reform record is supplied, treat its confirmed decisions as authoritative and exclude open, deferred, or unconfirmed proposals from the clean formal version.

## Intake and source control

1. Identify the intended instrument, provisions, policy direction, scope, audience, and requested deliverables.
2. Obtain the authoritative current text and verify its version and relevant effective dates. Never recreate current wording from memory. If it is unavailable, request it or clearly label any working text as unverified and do not present a definitive comparison.
3. Separate confirmed policy from drafting choices. The user owns policy choices. Do not silently change a choice to make drafting easier. Ask the user only about ambiguity that would change substantive institutional content, including rights, powers, duties, procedures, qualifications, timing, or legal effect. Resolve purely legal-language, sentence-structure, formatting, and other editorial choices consistently without interrupting the user when they do not alter institutional meaning.
4. Check adjacent provisions, definitions, references, institutional names, hierarchy, and consequential rules. Flag dependencies that require a decision or additional amendment.

## Drafting deliverables

For a complete amendment proposal, the default structure is:

1. **案由**
2. **修正總說明**
3. **修正條文對照表**
4. **必要配套或附帶說明**

Adjust this structure when the user or applicable formal procedure requires another format. Prepare only the deliverables requested or needed for the proposal. Depending on scope, include:

- **修正條文草案** for amendments to existing provisions.
- **制定條文草案** for new provisions or an entirely new instrument.
- **刪除條文** where repeal is intended, with consequential numbering and references checked.
- **案由** that identifies the proposed action and instrument concisely.
- **修正總說明** explaining the overall purpose and structure of the proposal.
- **修正條文對照表**, using exactly these columns and order: **現行條文｜修正條文｜說明**. “現行條文” must always be the leftmost column; the 說明欄 ordinarily serves as that article's 逐條修正理由. Do not create a separate, duplicative 逐條修正理由 section unless the user or applicable formal procedure requires one.
- **正式提案 Email 草稿** with an appropriate subject, recipient placeholder if unknown, concise submission text, and attachments or enclosures as applicable. It remains a draft for the user to send.
- **DOCX**: when the execution environment supports editable DOCX generation, DOCX is the preferred output format for a formal document. Use actual editable Word text, native Word tables, and genuine underline formatting; never convert provisions or tables into images. Provide a working version with review annotations or alternatives when useful, and a separate clean formal proposal containing only confirmed choices. If the environment cannot create DOCX, provide complete, structured formal document content and clearly say DOCX could not be created in this environment; never claim that a DOCX was created when it was not.

The comparison table's **現行條文** column must faithfully reproduce the text from the verified authoritative source. Do not correct typos, change punctuation, standardize terminology, modernize wording, or rewrite sentence structure in that column unless that exact change is part of the proposed amendment.

## Comparison table markup

Apply underlining in Word formatting, not underscore characters or markup symbols in the final DOCX:

- Deleted wording: underline it in **現行條文**.
- Added wording: underline it in **修正條文**.
- Replaced wording: underline the old wording in **現行條文** and the replacement in **修正條文**.
- Unchanged wording: do not underline it.
- Entirely new provision: put **無** in 現行條文 and underline the full provision in 修正條文.
- Entirely deleted provision: underline the full text in 現行條文 and put **刪除** in 修正條文.
- Renumbering alone, where the substance is unchanged: show the appropriate provision locations, explain the renumbering in 說明, and do not mark the entire text as amended.

Before delivery, compare each table row against the verified source and final draft. Confirm that each underlined span corresponds to a real addition, deletion, or replacement and that no unchanged text is underlined.

## Reasons and language

For each provision, explain in concrete terms:

**現行規定／現況 → 存在的問題 → 本次如何修改 → 修改後的制度效果**

Ground each link in the supplied facts and source text. Avoid generic reasons such as 「為使規範更加明確，爰予修正。」、「為符實際需要，爰予修正。」、「為臻周延，爰予修正。」 and 「酌作文字修正。」 unless the reason truly is that narrow and the specific clarification or editorial change is identified. Do not invent a problem or effect to fill out the pattern.

Convert the user's conversational explanation into clear, formal, consistent legal language while preserving the user's substantive choice. Use defined terms consistently; distinguish authority, duty, discretion, procedure, legal effect, and timing. Do not add a common institutional mechanism merely because it is customary. Flag unresolved choices instead of hiding them in legal wording.

## Final consistency review

Check article numbering, amendments and repeals, cross-references, instrument and body names, defined terms, titles, authority, procedural steps, legal effects, effective dates, and any transitional or consequential amendments. Identify residual issues plainly. Ensure the reasons match the final text and that the clean proposal contains no drafting notes, alternatives, AI proposals, or unconfirmed defaults.

## Formal procedure boundary

AI may analyze, draft provisions and proposal materials, and generate an email draft; it may create a DOCX only when the execution environment supports it. It must not send the email, formally submit or sign the proposal, promulgate a rule, appoint or remove anyone, resign, adjudicate, or claim that a proposal was formally submitted or passed, or that a rule was promulgated or effective.

For current-law compliance analysis, use `regulation-review`. For a long-running charter, organizational-rule, or multi-system redesign with unresolved decisions and dependencies, use `large-scale-reform` to track choices and dependencies; draft a coherent portion once its policy choices are sufficiently clear, even if other portions remain open or deferred.
