# 文件導覽：正式版使用者

本頁是 GitHub 預設分支 `main` 的使用指南入口。**最新的使用說明可能記錄 Beta／新版模型的實測觀察，但不代表 `v0.1.3` 的 Skill 已更新或重新發布。** 要固定 Skill 內容，請使用正式 Release 的附件或指定版本 Tag。

依使用目的整理既有文件，不在本頁複製 Skill 規則或維護第二份啟動提示詞。第一次使用通常只需要 [START-HERE](../START-HERE.md)，不用安裝程式、執行驗收工具或了解 GitHub 分支。

## v0.2 開發線

本分支的 [Google Docs 工作流程](google-docs-workflow.md)與 [v0.2.0-alpha.1 範圍及驗證](development/v0.2.0-alpha.1.md)屬於開發中規範，不表示正式版或平台整合已發布。

## 第一次使用

| 想做的事 | 文件 |
| --- | --- |
| 不確定用哪個 Skill，想開始對話 | [START-HERE：唯一可複製提示詞](../START-HERE.md#可複製提示詞) |
| 看三種常見提問情境，了解何時提供法規資料 | [新手引導](first-time-user.md) |
| 在 ChatGPT 使用，了解已知限制 | [ChatGPT 指南](platforms/chatgpt.md) |
| 在 Claude 使用，了解已知限制 | [Claude 指南](platforms/claude.md) |
| 在 Gemini 使用，了解無法讀 GitHub 時如何繼續 | [Gemini 指南](platforms/gemini.md) |
| 在其他 AI Agent 使用 | [其他 Agent 指南](platforms/generic-agent.md) |
| 查看已記錄的模型與平台觀察 | [模型與平台使用建議](platforms/model-compatibility.md) |
| 了解三份 Skill 的用途 | [專案 README](../README.md#skills) |

只需完整提供本次所需的 `SKILL.md`，不用一次提供三份。AI 無法讀取 GitHub 時，可自行下載並完整貼入或上傳該檔案。先完整讀取 Skill，再按其流程提供正式法規與案件資料；切換 Skill 時，先讀取新 Skill。

## 維護者：驗收與品質工具

| 需求 | 入口 |
| --- | --- |
| 產生真人測試操作卡、匯入 TXT、彙整有效測試缺口 | [半自動驗收工具](acceptance/assistant-guide.md) |
| 離線核對實際 AI DOCX 的原文、表格和底線 | [模型 DOCX 品質檢查](acceptance/model-docx-check.md) |
| 進行真人模型回歸、了解原定矩陣 | [真人模型驗收操作](acceptance/model-regression.md) |
| 保存證據並決定測試狀態 | [驗收紀錄指南](acceptance/record-guide.md)・[Beta 前清單](acceptance/beta-checklist.md) |
| 選擇虛構案例、區分規則與實際風險 | [實務案例](acceptance/practical-cases.md)・[風險審查](acceptance/risk-review.md) |
| 匯出可取得的對話與附件記錄 | [Skill 完整回報包](feedback-package.md) |
| 維護分支、CI 和 Beta 發布 | [CI/CD 與 Beta Pre-release](ci-cd.md) |

這些離線工具不是新的法律 Skill，也不是一般使用者的必要安裝項目。程式不自動呼叫模型或替模型評分；CI／參考文件／DOCX 結構檢查不能取代真人模型、法律內容或實際 Word 視覺驗收。

## 版本與驗證說明

- **歷史正式版：** [v0.1.3 Release](https://github.com/Clock1025/sa-legal-skills/releases/tag/v0.1.3)。既有 Tag 與 Release ZIP 不會因本頁更新而改變。
- **Beta 實測紀錄：** [v0.1.4-beta.1 Release Notes](https://github.com/Clock1025/sa-legal-skills/releases/tag/v0.1.4-beta.1)，記錄當時尚未完成 RC／正式版驗收的首輪觀察。使用這些記錄時，請區分首輪模型觀察、文件檢查與程式 CI。
- **歷史回歸：** [v0.1.3 紀錄](regression/v0.1.3.md)，包含模型行為、格式與證據限制。
- **開發與回歸文件：** [v0.1.4 P0 案例](regression/v0.1.4-p0-cases.md)・[DOCX 品質回歸](regression/v0.1.4-docx-quality.md)。參考及模擬驗證紀錄不能當成整體真人測試通過；離線驗收工具及操作說明見上方維護者導覽，**不是正式版附件的一部分**。

- [v0.1.1](regression/v0.1.1.md)・[v0.1.2](regression/v0.1.2.md)：其他歷史觀察與限制。
- [GitHub Releases](https://github.com/Clock1025/sa-legal-skills/releases)：已發布版本與附件。要固定版本，使用 Tag 或完整 Commit，不以會移動的 `main`／`develop` 代替。

### 哪些內容在 Release ZIP？

正式版 ZIP 固定只有 `START-HERE.md`、`LICENSE` 及三份 `skills/*/SKILL.md`。這些網頁指南與開發者工具不在 ZIP 內。

[返回專案首頁](../README.md)
