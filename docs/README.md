# 文件導覽

依使用目的整理既有文件，不在本頁複製 Skill 規則或維護第二份啟動提示詞。
第一次使用通常只需要 [START-HERE](../START-HERE.md)，不用安裝程式、執行驗收工具或了解 GitHub 分支。

## 第一次使用

| 需求 | 入口 |
| --- | --- |
| 不確定用哪個 Skill、想開始對話 | [START-HERE：唯一可複製提示詞](../START-HERE.md#可複製提示詞) |
| 準備法規來源、版本與案件資料 | [新手引導](first-time-user.md) |
| 在不同 AI 平台操作 | [ChatGPT](platforms/chatgpt.md)・[Claude](platforms/claude.md)・[Gemini](platforms/gemini.md)・[其他 AI Agent](platforms/generic-agent.md) |
| 了解各模型已記錄的測試與限制 | [模型與平台使用建議](platforms/model-compatibility.md) |
| 認識三個 Skill 的分工 | [專案 README：Skills](../README.md#skills) |

如果 AI 讀不到 GitHub，提供本次所需的一份 `SKILL.md` 全文或附件即可。先完整讀取 Skill，再依其工作流程取得案件材料。工作中切換 Skill 時，需要先完整讀取新 Skill。

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

## 回歸與版本資料

- [v0.1.1](regression/v0.1.1.md)・[v0.1.2](regression/v0.1.2.md)・[v0.1.3](regression/v0.1.3.md)：歷史觀察與限制。
- [v0.1.4 P0 案例](regression/v0.1.4-p0-cases.md)・[DOCX 品質回歸](regression/v0.1.4-docx-quality.md)：參考及模擬驗證紀錄，不能當成整體真人測試通過。
- [GitHub Releases](https://github.com/Clock1025/sa-legal-skills/releases)：已發布版本與附件。要固定版本，使用 Tag 或完整 Commit，不以會移動的 `main`／`develop` 代替。

**發行範圍：**正式 Release ZIP 固定只含 `START-HERE.md`、`LICENSE` 和三份 `skills/*/SKILL.md`。本頁、平台指南及驗收腳本沒有打包進 ZIP，請到 repository 網頁閱讀或取得。

[返回專案首頁](../README.md)
