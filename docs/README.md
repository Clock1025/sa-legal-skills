# 文件導覽：正式版使用者

本頁是 GitHub 預設分支 `main` 的使用指南入口。**最新的使用說明可能記錄 Beta／新版模型的實測觀察，但不代表 `v0.1.3` 的 Skill 已更新或重新發布。** 要固定 Skill 內容，請使用正式 Release 的附件或指定版本 Tag。

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

## 版本與驗證說明

- **正式版：**[v0.1.3 Release](https://github.com/Clock1025/sa-legal-skills/releases/tag/v0.1.3)。既有 Tag 與 Release ZIP 不會因本頁更新而改變。
- **Beta 實測紀錄：**[v0.1.4-beta.1 Release Notes](https://github.com/Clock1025/sa-legal-skills/releases/tag/v0.1.4-beta.1)，尚未完成 RC／正式版驗收。使用這些記錄時，請區分首輪模型觀察、文件檢查與程式 CI。
- **歷史回歸：**[v0.1.3 紀錄](regression/v0.1.3.md)，包含模型行為、格式與證據限制。
- **開發者／Beta 專用文件：**[develop 分支的文件導覽](https://github.com/Clock1025/sa-legal-skills/blob/develop/docs/README.md)。該分支含尚未納入正式主線的離線驗收工具、開發紀錄及操作說明；**不是正式版附件的一部分**。

### 哪些內容在 Release ZIP？

正式版 ZIP 固定只有 `START-HERE.md`、`LICENSE` 及三份 `skills/*/SKILL.md`。這些網頁指南與開發者工具不在 ZIP 內。

[返回專案首頁](../README.md)
