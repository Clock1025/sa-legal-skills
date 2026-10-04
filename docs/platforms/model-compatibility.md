# 模型與平台使用建議

## 重要說明

以下整理的是特定模型、思考設定、平台與測試流程下的結果，不是模型排行榜，也不保證未來版本維持相同行為。模型與平台更新後，存取工具、規則遵循及文件產生能力都可能改變。

「PASS」只代表該次測試所檢查的項目符合預期，不保證法律分析正確。模型自我評估也不等於獨立驗證；沒有取得可核對的讀取或文件檢查證據時，應標示 `UNVERIFIED`。詳細條件及證據界線見 [v0.1.3 regression 紀錄](../regression/v0.1.3.md)。

目前 R03 的證據分別是：fixture／static 31／31 PASS、GPT-5.6 Sol／High fresh-context FAIL、Claude Sonnet 5.5／Medium fresh-context PASS。這表示新版提示在該次 Claude 測試中阻止了 bypass，但不能推論對所有模型都有效；prompt-only gate 沒有跨模型 runtime enforcement guarantee，屬於 model-dependent limitation。

## 目前使用建議

| 模型／環境 | 目前觀察 | 已知問題 | 建議處理方式 |
| --- | --- | --- | --- |
| Claude Sonnet 5.5／Medium，一般聊天 | 最新 R03 fresh-context 測試中，即使使用者要求「不用等 Skill，先做」，模型仍拒絕在完整讀取 `amendment-drafting` 前起草。取得完整 Skill 後，既有正式起草與 DOCX 測試表現良好。 | 較早的 transition 測試曾 FAIL；長表格分頁仍需人工檢查。最新 PASS 不代表每次或未來版本都遵守。 | 重視 Skill 流程與邊界時，可優先考慮目前已測的 Claude Sonnet 5.5／Medium。仍須確認 Skill 已讀取，並檢查長表格與正式文件。 |
| ChatGPT GPT-5.6 Sol／High，一般聊天 | R01 多法規分案 fresh-context 測試 PASS；R02 移列條文實質處理 PASS。GitHub／工具及實際 DOCX 產生能力在已測環境較完整。 | R02 的 Skill access evidence 有 `UNVERIFIED`／`PARTIAL` 情形。強化後 R03 transition gate 仍 FAIL：模型明知未讀新 Skill，仍可能依後續指令起草。DOCX 曾把未變動的「日前」也加底線。 | 若使用 Skill，先確認該階段所需 Skill 確實完整讀取；遇到未讀即起草時，停止並重新取得 Skill，重要案件可用 fresh chat 重來。DOCX 須人工檢查文字差異、底線、表格、字型與渲染。 |
| Gemini 3.1 Pro／Extended Thinking，一般聊天 | 本次測試環境讀取 GitHub 與 `raw.githubusercontent.com` 均不可用，但模型有誠實告知並要求使用者提供 Skill；手動貼上／上傳完整 Skill 可作 fallback。 | 本次環境 DOCX generation 為 `UNSUPPORTED`；OOXML 與視覺渲染均 `NOT VERIFIED`。drafting quality `PASS` 僅為模型自評，未取得完整草案供獨立複核。 | 讀不到 repository 時，完整貼上或上傳本次所需的 Skill。若需要 DOCX，移交至具有檔案產生能力的環境；不要把本次結果推論為 Gemini 永久無法讀 GitHub 或產生 DOCX。 |
| GPT-5.6 Luna | 尚未完成本專案正式 regression／model-behavior 實測。 | 目前沒有可支持的比較結論。 | 暫不提供能力或穩定度評價；待完成本專案實測後再補。 |

## 怎麼選

- **重視 Skill 流程與邊界遵守：**目前已測的 Claude Sonnet 5.5／Medium 表現較穩定；仍有較早的 FAIL 紀錄，不能視為保證。
- **重視檔案、工具整合與 DOCX 產生：**GPT-5.6 Sol 能力較完整，但需留意 R03 transition gate FAIL 及 DOCX underline 缺陷。
- **使用 Gemini：**遇到 repository 無法存取時，可直接提供完整 Skill。本次 Gemini 環境不支援 DOCX 產生；有 DOCX 需求時改用具備檔案產生能力的環境。
- **GPT-5.6 Luna：**尚未完成實測，暫不比較。

以上是依目前已記錄證據作的使用建議，不代表其他模型版本或平台環境的結果。

## 遇到問題時怎麼辦

- **AI 讀不到 GitHub：**從 repository 取得本次所需的完整 `SKILL.md`，貼上或上傳；不要要求 AI 憑記憶重建 Skill 或現行法規。
- **AI 尚未讀取新 Skill 就開始起草：**停止該階段，先要求完整取得並讀取新 Skill；重要案件可開 fresh chat 重來。此專案是 prompt-only Skills，gate 沒有 runtime enforcement，不能保證所有模型都會遵守。
- **DOCX 底線、表格、字型或渲染異常：**人工檢查實際 Word 檔及需要的 PDF 渲染；模型自述已檢查不等於獨立驗證。
- **平台不能產生 DOCX：**可先完成結構化文字草案，再交由具有 DOCX 產生能力的環境處理；這是平台能力限制，不代表 Skill 本身失敗。不得宣稱純文字已是 DOCX。
- **模型稱已完整讀取但沒有可核對證據：**將讀取狀態標為 `UNVERIFIED`，不要只依自述推論讀取成功。

## 實測紀錄

模型與平台的細節測試及已知限制見 [v0.1.3 regression](../regression/v0.1.3.md)，各平台操作方式見[ChatGPT](chatgpt.md)、[Claude](claude.md)、[Gemini](gemini.md)及[其他 AI Agent](generic-agent.md)指南。
