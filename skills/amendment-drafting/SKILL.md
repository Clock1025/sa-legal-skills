---
name: amendment-drafting
description: Turn a sufficiently settled student association or student self-governance policy direction into formal legislative drafting materials. Use for drafting new provisions, amending provisions, deleting provisions, preparing amendment reasons and proposal documents, an amendment comparison table, a proposal email draft, or editable DOCX content. Do not use to decide unresolved policy choices or to manage a whole-charter reform project.
---

# Amendment Drafting

Translate the user's chosen institutional direction into precise, internally consistent legal text and proposal materials. The user owns policy choices. Clarify ambiguity that affects substance; do not silently change a choice to make drafting easier. When a large-scale reform record is supplied, treat its confirmed decisions as authoritative and exclude open, deferred, or unconfirmed proposals from the clean formal version.

## Intake and source control

1. Identify the intended instrument, provisions, policy direction, scope, audience, and requested deliverables.
2. Obtain the authoritative current text and verify its version and relevant effective dates. Never recreate current wording from memory. If it is unavailable, request it or clearly label any working text as unverified and do not present a definitive comparison.
3. Before drafting or preparing a comparison table, identify the precise provision level and location affected: **條 → 項 → 款 → 目**. Do not substitute vague descriptions such as 「一段」、「一項文字」, or 「增列內容」 for an identifiable legal structure. Within an article, separate paragraphs are 項 in order (第一項、第二項、第三項, etc.), whether or not the text labels them explicitly; for example, adding a third paragraph after two existing paragraphs is 「增訂第三項」. Recognize 款 as typically numbered 一、二、三…… and 目 as （一）、（二）、（三）……; do not call a 款 an 項 or a 目 a 款.
4. Separate confirmed policy from drafting choices. The user owns policy choices. Do not silently change a choice to make drafting easier. Ask the user only about ambiguity that would change substantive institutional content, including rights, powers, duties, procedures, qualifications, timing, or legal effect. Resolve purely legal-language, sentence-structure, formatting, and other editorial choices consistently without interrupting the user when they do not alter institutional meaning. Identifying the correct article, paragraph, subparagraph, or item is legal drafting precision, not a policy decision.
5. Check adjacent provisions, definitions, references, institutional names, hierarchy, and consequential rules. Flag dependencies that require a decision or additional amendment, including cross-references to any article, paragraph, subparagraph, or item whose numbering or content changes. Carry forward every article, paragraph, subparagraph, or item identified in earlier review as potentially affected. During drafting, recheck each one and record exactly one disposition:
   - **MODIFY** — rechecked and confirmed to require amendment; include it in the draft.
   - **NO_CHANGE** — rechecked and confirmed not to require amendment; state the specific reason for leaving it unchanged.
   - **UNRESOLVED** — rechecked and found to have a consequential link, but necessary policy, procedure, or other matter remains undecided, so it cannot safely be drafted yet; do not supply the missing policy yourself.

   Do not let a previously identified related provision silently disappear when drafting begins. If an item has not been rechecked, do not imply that the consequential review is complete. Tracking these dispositions is a drafting and review completeness requirement, not a policy decision.

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
- **修正條文對照表**, using exactly these columns and order: **修正條文｜現行條文｜說明**. The 說明欄 ordinarily serves as that article's 逐條修正理由. Do not create a separate, duplicative 逐條修正理由 section unless the user or applicable formal procedure requires one.
- **正式提案 Email 草稿** with an appropriate subject, recipient placeholder if unknown, concise submission text, and attachments or enclosures as applicable. It remains a draft for the user to send.

- **DOCX**: when the execution environment supports editable DOCX generation, DOCX is the preferred output format for a formal document. Use actual editable Word text, native Word tables, and genuine underline formatting; never convert provisions or tables into images. For formal Chinese rules, proposals, and amendment comparison tables, follow an existing formal document or institutional template's fonts and layout when supplied. Otherwise, this project's preferred Kai-style font order is **標楷體** (if available in the execution environment), then **全字庫正楷體** (if available), then a fallback font that displays Traditional Chinese correctly. Clearly report any fallback. Do not claim a font was used unless it exists in the execution/rendering environment. If the DOCX specifies a font family but rendering could not be verified, distinguish that it was **specified** from whether it was **verified**. When generating DOCX through OOXML, `python-docx`, or similar tools, set the Chinese font correctly in the East Asian font property (`w:eastAsia`) and any other required font properties; setting only the Western font property is insufficient and may cause Word to substitute another font. Use the actual font family name recognized by the execution environment for 標楷體 or 全字庫正楷體; verify it with available system font tools or font metadata instead of assuming an internal name. When rendering/preview QA is available, check that Chinese text uses the expected font without fallback, bold and underline remain correct, table text renders correctly, and font changes have not caused unwanted page breaks, overflow, or clipping. Font selection is a presentation/document-formatting requirement, not an institutional or policy decision. Do not add font files to the repository or copy third-party or government font files into this Skill package; point users to official download sources instead. Provide a working version with review annotations or alternatives when useful, and a separate clean formal proposal containing only confirmed choices. If the environment cannot create DOCX, provide complete, structured formal document content and clearly say DOCX could not be created in this environment; never claim that a DOCX was created when it was not.

### Proposal separation across instruments

Each formal proposal must target **one legal instrument or regulation**. When one policy package requires amendments, enactments, or repeals across multiple instruments:

- Treat each affected instrument as a **separate formal proposal**, even when the policy purpose is shared or the proposals are intended to move together. Each proposal must have its own 案由, 修正／制定／廢止總說明 as applicable, comparison table or repeal materials, and any required attachments.
- By default, when file generation is available, output each instrument's formal proposal as a **separate file**.
- If separate files would materially increase generation cost, token use, or operational burden, ask the user whether they prefer a consolidated working file. Do not choose consolidation solely for convenience or token savings without the user's agreement.
- A consolidated file may contain multiple independent proposals for convenience, but each proposal must remain structurally complete and clearly separated. Do not collapse multiple instruments into one 案由, one comparison table, or a single formal proposal merely because they are related.
- Related proposals may cross-reference one another in explanations or consequential notes. This does not merge their legal or procedural identity.
- Even if an authoritative institutional template or applicable procedure permits joint submission or a consolidated document, retain each instrument as a complete, independent formal proposal. Permission to submit or collect proposals together does not authorize merging them into a single multi-instrument proposal. Any change to this principle requires an explicit user decision; mark it **NEEDS_USER_DECISION** rather than introducing an exception yourself.

The comparison table's **現行條文** column must faithfully preserve the verified source's provision wording, punctuation, and the substantive text and structure of its 項、款、目. Do not correct typos, change punctuation, standardize terminology, modernize wording, or rewrite sentence structure. Formal Word layout may normalize the article number and join it with the first paragraph as specified below; source website UI formatting or HTML block separation does not define the formal document layout. This formatting treatment does not authorize merging or changing any later 項、款、目.

### 法規段落與 Word 縮排

「項」通常沒有編號符號，段落界線與縮排本身就是法規結構資訊。不得因重新排版而合併不同項，或使其看起來像同一段。有機關／正式範本時，優先沿用其條、項、款、目縮排及字級、行距、段前段後格式。無範本時，使用一致、可讀且不破壞法規層級的格式，不預設固定字級；行距與段落間距依下列規則，縮排採以下預設：

C = 該段落實際正文所使用的中文字型與字級之一個全形中文字寬（約 1 em）的版面基準。以下僅為無正式範本時的 fallback，不得凌駕使用者提供的正式範本：

- 無正式範本另有規定時，法規正文及修正條文對照表中的條文段落，段前與段後間距均設為 0 pt，行距設為 single／1.0；不得預設 1.5 倍行距或用空白行製造段落距離。此處 0 pt 指 paragraph spacing before／after，不等於強制單行距；但本 fallback 的行距為 single／1.0。正式範本優先。表格儲存格內的條文段落也適用此規則。
- 無正式範本另有規定時，正式法規條號使用中文數字，條號文字內不得插入空白；例如「第一條」、「第二十三條」、「第一百八十四條」、「第一千零五十二條」。不得用字元間距模擬排版。
- 正式條文中的「條號＋第一項正文」置於同一 Word paragraph，預設為「第一百八十四條　第一項正文……」；條號與第一項正文之間使用一個全形空白 U+3000，不得以冒號、Tab 或多個空白代替。此規則適用於修正條文欄、現行條文欄及一般正式條文正文。條號＋第一項基本左縮排 C、首行使用凸排 C，因此段落首行起始位置為 0、自動換行後為 C。第二項及其後各項仍各自使用獨立 paragraph，基本左縮排 C、首行再增加 C，因此首行 2C、續行 C。
- 款、目保留清楚可辨識的階層與編號對齊。修正條文對照表儲存格內也保留同樣的條、項、款、目結構，除非正式範本另有規定。表格內以儲存格內容區左界為縮排原點；C 仍為正文的一字寬，不把儲存格內距算入 C。
- 無正式範本另有規定時，Word 原生修正條文對照表的可見格線使用黑色（`#000000`）；OOXML 應明確指定 `w:color="000000"`，不得依賴 theme color 或應用程式預設灰色。正式範本優先。
- 優先使用 Word／OOXML 原生 paragraph indentation。環境支援時可用 character-based indentation；若工具只能使用 points／twips，依有效字級換算近似一個 em，並以實際渲染結果驗證。不得同時疊加互相衝突的 hanging、first-line、character 或 twips 設定；應確認 paragraph style 的繼承縮排與最終有效格式。
- 不得堆疊全形空白、半形空白或 Tab 字元模擬整個段落縮排，也不得用空白行、額外空白字元或 Tab 取代段落間距控制。C 是版面基準，不是插入方塊或空白字元的指令。
- 現行條文欄與直接引文的法規正文文字、標點及項、款、目內容須忠實保留原文；條號轉為正式文件所需的中文數字格式，以及條號和第一項間單一 U+3000，依前述排版規則處理。來源網站的 UI 顯示（例如「第 184 條」）或 HTML 將條號與第一項分成不同區塊，不代表正式 Word 文件也應照其形式呈現。不得因此合併第二項、款、目或其他具有法律結構意義的段落。除此明定的條號格式及分隔外，原文沒有空白、Tab 或其他字元時，不得僅為排版自行新增；優先以 paragraph formatting、tab stop、表格配置或其他不改變原文字元的方法處理。若工具無法同時維持指定版面與正文原文完整性，保留正文原文並揭露版面限制。
- 新擬文字可依正式範本或預設法制格式安排必要的條號與正文間隔；這不等於用大量空白模擬段落縮排。

DOCX QA 若環境支援，核對條文段落 paragraph spacing before／after 為 0 pt、fallback line spacing 為 single／1.0；渲染後檢查不同項仍可區分、首行與續行縮排正確、款目階層未消失、表格內格式正常、換頁未破壞法規結構，以及新設縮排未以新增前置空白字元假裝實現。同時核對 underline、bold、East Asian font 與既有字型規則；若無法渲染，明確說明版面尚未驗證。既有原文含有的空白不得僅為 QA 而刪改。

## Comparison table markup

Apply underlining in Word formatting, not underscore characters or markup symbols in the final DOCX:

- Deleted wording: underline it in **現行條文**.
- Added wording: underline it in **修正條文**.
- Replaced wording: underline the old wording in **現行條文** and the replacement in **修正條文**.
- Unchanged wording: do not underline it.
- Entirely new provision:
  - 修正條文欄：新增條文全文加底線。
  - 現行條文欄：填「（本條新增）」；「（本條新增）」本身不加底線。
  - 說明欄：填具體增訂理由。
- When wording is moved or copied **from another instrument into the target instrument**, judge the 現行條文欄 only against the verified current text of the **target instrument**. If the target instrument does not already contain that provision at the corresponding location, it is an entirely new provision in the target instrument: 現行條文欄 must be 「（本條新增）」, not 「○○法第 X 條」 or the source instrument's text. Record the source instrument, original article number, and migration relationship in the 說明欄 or a working-version source map. Source text may be reproduced separately for traceability, but it must not be presented as the target instrument's 現行條文.
- Entirely deleted provision:
  - 修正條文欄：填「（刪除）」；「（刪除）」本身不加底線。
  - 現行條文欄：原條文全文加底線。
  - 說明欄：填具體刪除理由。
- Renumbering alone, where the substance is unchanged: show the appropriate provision locations, explain the renumbering in 說明, and do not mark the entire text as amended.

If adding or deleting a 項, 款, or 目 changes later numbering, distinguish pure sequential renumbering from substantive textual change. Mark differences by actual text additions and deletions: do not mark otherwise unchanged text as substantively amended merely because a preceding paragraph, subparagraph, or item caused its number to shift. Check and update cross-references to affected locations where necessary, and identify consequential reference amendments separately.

Before delivery, compare each table row against the verified source and final draft. Confirm that each underlined span corresponds to a real addition, deletion, or replacement and that no unchanged text is underlined.

## Reasons and language

In the 說明欄 and any required reasons, identify the exact affected location using its legal structure, such as 「修正第三條第二項」、「增訂第三條第三項」、「修正第十條第一項第二款」, or 「增訂第十條第一項第二款第三目」. Avoid imprecise descriptions such as 「修正本條部分文字」 when the affected level can be identified. Explain each amendment in concrete terms:

**現行規定／現況 → 存在的問題 → 本次如何修改 → 修改後的制度效果**

Ground each link in the supplied facts and source text. Avoid generic reasons such as 「為使規範更加明確，爰予修正。」、「為符實際需要，爰予修正。」、「為臻周延，爰予修正。」 and 「酌作文字修正。」 unless the reason truly is that narrow and the specific clarification or editorial change is identified. Do not invent a problem or effect to fill out the pattern.

Convert the user's conversational explanation into clear, formal, consistent legal language while preserving the user's substantive choice. Use defined terms consistently; distinguish authority, duty, discretion, procedure, legal effect, and timing. Do not add a common institutional mechanism merely because it is customary. Flag unresolved choices instead of hiding them in legal wording.

中文法規、修正條文、修正說明、案由、正式提案文字及其他正式中文法制文件，原則上使用逗號、句號、分號、冒號、全形括號及中文引號等全形中文標點。本規則適用於新擬文字；現行條文欄及直接引文應忠實保留原文，不得僅為統一標點而改寫。正式中文法制文字不得無必要混用半形標點。技術識別字、網址、檔名、版本號、程式碼、Git 指令、Skill 名稱等確有必要時，得使用半形符號。本規則屬文件格式與法制作業要求，不是制度或政策決定。

## Final consistency review

Check article, paragraph, subparagraph, and item numbering; amendments and repeals; cross-references to affected locations; instrument and body names; defined terms; titles; authority; procedural steps; legal effects; effective dates; and any transitional or consequential amendments. Distinguish pure sequential renumbering from substantive change. Before completing the formal draft, perform a coverage check: compare the full list of related provisions identified in earlier review against the recorded **MODIFY**, **NO_CHANGE**, and **UNRESOLVED** dispositions, one by one, and confirm that none is missing. Include unresolved items and the reasons for no-change dispositions in the review record; do not imply complete coverage for any item not rechecked. Identify residual issues plainly. Ensure the reasons match the final text and that the clean proposal contains no drafting notes, alternatives, AI proposals, or unconfirmed defaults.

## Formal procedure boundary

AI may analyze, draft provisions and proposal materials, and generate an email draft; it may create a DOCX only when the execution environment supports it. It must not send the email, formally submit or sign the proposal, promulgate a rule, appoint or remove anyone, resign, adjudicate, or claim that a proposal was formally submitted or passed, or that a rule was promulgated or effective.

For current-law compliance analysis, use `regulation-review`. For a long-running charter, organizational-rule, or multi-system redesign with unresolved decisions and dependencies, use `large-scale-reform` to track choices and dependencies; draft a coherent portion once its policy choices are sufficiently clear, even if other portions remain open or deferred.
