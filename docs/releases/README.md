# Release Notes 編輯規範

正式版本的 GitHub Release 以 [v0.1.2](https://github.com/Clock1025/sa-legal-skills/releases/tag/v0.1.2) 的閱讀體驗為範本。

- **Release Title** 使用 [titles.json](titles.json) 對應的「版本號 — 簡短更新摘要」；版本說明內文不可再放同名 Markdown H1／重複標題。
- **Description** 優先依序呈現一段簡短介紹、「重點更新：」及「已知限制：」，必要時補充原始驗收紀錄與下載方式。可使用簡短 Markdown，避免將整份技術驗收報告貼在首頁。
- 實際模型測試必須精確區分 PASS、PARTIAL、FAIL、未驗證與回歸測試範圍；靜態檢查不代表真人模型、法律內容或視覺驗收通過。
- 歷史敘述使用「發布當時」等明確時間界線，避免過時的 Latest 或模型狀態看起來像現況。
- 詳細技術證據及驗收紀錄以對應 Tag 下的 Repository 文件連結提供；不得捏造、擴大或改寫歷史結果。
- 調整既有 Release 文字只修改 Title 和 Description，不應修改 Tag、Commit、附件、雜湊、Pre-release、Latest、發布日期或來源程式碼。執行前後均須核對上述資訊。
- `v0.1.2.md` 保留公開原文（僅換行格式統一）；`v0.1.0` 歷史 Release 沒有 ZIP 附件，不得為了外觀一致而虛構附件。

## 版本說明來源

各版 `v*.md` 是待套用於 GitHub Release Description 的正文，`titles.json` 是 Release Title 的單一來源。已公開的 Release metadata 不會因本目錄變更而自動更新；需維護者透過 GitHub 另外核准執行。

未來建立新版本時，先新增版本檔與 titles.json 對應項，確認 CI 檢查通過，再於正式 Release 發布流程引用。現有 `stable-release-v0.1.4.yml` 為版本專用工作流，不會因更新此目錄自動重發 v0.1.4。


## v0.2 Alpha 發布準備

[v0.2.0-alpha.2 notes](v0.2.0-alpha.2.md) 為候選稿，不代表已發布；[準備紀錄與待確認事項](alpha-v02-preparation.md)及 [專用 CI/CD 流程](../ci-cd.md)供審查。實際 Tag／Release 須另行授權。
