# 模型與平台使用建議

## 重要說明

以下整理的是特定模型、思考設定、平台與測試流程下的結果，不是模型排行榜，也不保證未來版本維持相同行為。模型與平台更新後，存取工具、規則遵循及文件產生能力都可能改變。

「PASS」只代表該次測試所檢查的項目符合預期，不保證法律分析正確。模型自我評估也不等於獨立驗證；沒有取得可核對的讀取或文件檢查證據時，應標示 `UNVERIFIED`。下列資料按版本／日期分開：歷史 v0.1.3 實測、Beta 首輪行為觀察、實際 DOCX 文件檢查各有不同範圍；CI／靜態／模擬測試不能當成真人模型驗收。

歷史 v0.1.3 R03 的證據分別是：fixture／static 31／31 PASS、GPT-5.6 Sol／High 全新對話重測 FAIL、Claude Sonnet 5.5／Medium 全新對話重測 PASS。前者是程式檢查，後兩者是不同模型的當次行為；不能互相取代，也不能保證之後每次都遵守。詳見 [v0.1.3 回歸](../regression/v0.1.3.md)。

## 歷史 v0.1.3：已記錄的使用觀察

| 模型／環境 | 當次觀察 | 已知問題 | 建議處理方式 |
| --- | --- | --- | --- |
| Claude Sonnet 5.5／Medium，一般聊天 | 2026-10-04 收錄的 R03 全新對話重測中，即使使用者要求「不用等 Skill，先做」，模型仍拒絕在完整讀取 `amendment-drafting` 前起草。完整提供 Skill 後的歷史起草與 DOCX 有多項 PASS，但長表格視覺分頁及整輪為 PARTIAL。 | 較早的 transition 測試曾 FAIL；長表格分頁仍需人工檢查。後來的 PASS 不抹除先前 FAIL，也不代表所有 Claude 模型都遵守。 | 新 Skill 讀不到時，先完整貼入或上傳再起草；取得 DOCX 後人工看頁，核對分頁與字型。 |
| ChatGPT GPT-5.6 Sol／High，一般聊天 | R01 多法規分案 fresh-context 測試 PASS；R02 移列條文實質處理 PASS。該次環境曾取得 GitHub 材料並產生實際 DOCX。 | R02 的 Skill access evidence 有 `UNVERIFIED`／`PARTIAL` 情形。2026-10-04 的強化後 R03 重測仍 FAIL：模型明知未讀新 Skill，仍可能依後續指令起草。DOCX 曾把未變動的「日前」也加底線。 | 若使用 Skill，先確認該階段所需 Skill 確實完整讀取；遇到未讀即起草時，停止並重新取得 Skill，重要案件可用 fresh chat 重來。DOCX 須人工檢查文字差異、底線、表格、字型與渲染。 |
| Gemini 3.1 Pro／Extended Thinking，一般聊天 | 2026-10-04 收錄的測試環境讀取 GitHub 與 `raw.githubusercontent.com` 均不可用，但模型有誠實告知並要求使用者提供 Skill；手動貼上／上傳完整 Skill 可作 fallback。 | 該次環境 DOCX generation 為 `UNSUPPORTED`；OOXML 與視覺渲染均 `NOT VERIFIED`。drafting quality `PASS` 僅為模型自評，未取得完整草案供獨立複核。 | 讀不到 repository 時，完整貼上或上傳本次所需的 Skill。若需要 DOCX，移交至具有檔案產生能力的環境；不要把本次結果推論為 Gemini 永久無法讀 GitHub 或產生 DOCX。 |
| Gemini Flash-Lite／extended thinking OFF | v0.1.3 短提示詞測試的規則遵循 FAIL；完整 START-HERE 的當次測試 PASS。 | 短提示詞曾讓模型未讀 Skill 就分析；改善不保證其他對話穩定。 | 使用完整 START-HERE，讀不到 Skill 時先貼入／上傳全文，不用短提示取代。 |
| GPT-5.6 Luna | 尚未完成本專案正式 regression／model-behavior 實測。 | 目前沒有可支持的比較結論。 | 暫不提供能力或穩定度評價；待完成本專案實測後再補。 |

## v0.1.4-beta.1：GPT-6 首輪行為觀察

[Beta Release Notes](https://github.com/Clock1025/sa-legal-skills/releases/tag/v0.1.4-beta.1) 記錄維護者回報的 **2026-10-12** 初步觀察：

| 案例 | 首輪觀察 |
| --- | --- |
| P0-CASE-03 | PASS |
| P0-CASE-04 | PARTIAL |
| P0-CASE-05 | 初判 FAIL |
| P0-CASE-08 | PASS |

CASE-04 的「加上去」可能未先釐清指涉；CASE-05 可能在不完整條文釐清前產生占位內容。使用者應明確說明同意範圍、補明原意，檢查定稿是否包含未確認政策。
這不是四項正式驗收完成，也不計算 GPT-6 整體通過率或可靠度排名；不能與 GPT-5.6 歷史結果混算。Beta 尚未通過 RC 驗收。

## 2026-10-13：兩份實際模型 DOCX 檢查

[第一份](https://github.com/Clock1025/sa-legal-skills/pull/19#issuecomment-6140830914) 原文符合基準，但「日、前」多畫底線，屬 LOW 格式風險；[第二份](https://github.com/Clock1025/sa-legal-skills/pull/19#issuecomment-6141051567) 為較長、多項款及兩列修正，文字、段落、原生表格及底線符合基準且無相關警示，另經 LibreOffice 渲染及人工看頁。Microsoft Word 跨平台表現未驗證，頁數可能因環境不同。

第一份自述讀 `main`，不算固定 Beta 的正式回歸 PASS；第二份自述讀固定 Beta，實際全文讀取及生成鏈仍未獨立證實。精確模型版本／設定與修正說明逐字核對也有證據限制。
以上依維護者匿名摘要整理，**是文件檢查結果，不證明 GPT-6 全面遵守 Skill**；本次未取得原始對話／DOCX重跑。使用者注意事項詳見 [ChatGPT 指南](chatgpt.md)。

## 怎麼選

依目前帳號能實際讀取的文件、網路與 DOCX 工具選擇；上面的少量觀察不足以作跨模型穩定度排名。
試用 Beta 時使用該 Release ZIP 或固定 Commit；能讀取 `main` 不等於使用了指定 Beta 版本。
沒有本專案實測的模型／Agent 不推定成功或失敗；先依各[平台指南](generic-agent.md)提供完整 Skill，產生正式文件後核對內容。
有 DOCX 需求但環境沒有檔案工具時，先取得完整結構化文字，再交由可產生 DOCX 的環境處理；仍須完整讀取當階段 Skill，不能跳過起草前置條件。

## 遇到問題時怎麼辦

- **AI 讀不到 GitHub：**從 repository 取得本次所需的完整 `SKILL.md`，貼上或上傳；不要要求 AI 憑記憶重建 Skill 或現行法規。
- **AI 尚未讀取新 Skill 就開始起草：**停止該階段，先要求完整取得並讀取新 Skill；重要案件可開 fresh chat 重來。此專案是 prompt-only Skills，gate 沒有 runtime enforcement，不能保證所有模型都會遵守。
- **DOCX 內容或格式異常：**先比對原文與已確認修正；漏字、錯欄或擅改內容優先處理。只多畫未修改文字的底線屬格式問題，另外修正；字型／分頁仍須看實際頁面，模型自述已檢查不等於獨立驗證。
- **平台不能產生 DOCX：**可先完成結構化文字草案，再交由具有 DOCX 產生能力的環境處理；這是平台能力限制，不代表 Skill 本身失敗。不得宣稱純文字已是 DOCX。
- **模型稱已完整讀取但沒有可核對證據：**將讀取狀態標為 `UNVERIFIED`，不要只依自述推論成功。一般聊天拿不到底層工具日誌是證據限制，不直接判為嚴重功能缺陷；已可觀察的文件內容可另行核對。

## 實測紀錄

歷史細節見 [v0.1.3 回歸](../regression/v0.1.3.md)，新版初步觀察與文件檢查見上方 Release／PR 證據；各平台操作方式見[ChatGPT](chatgpt.md)、[Claude](claude.md)、[Gemini](gemini.md)及[其他 AI Agent](generic-agent.md)指南。
