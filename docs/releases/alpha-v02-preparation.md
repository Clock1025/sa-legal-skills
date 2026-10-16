# v0.2.0-alpha.2 發布準備紀錄

2026-10-16 核對：PR #33 已合併；develop-0.2 實際 HEAD 為 b52851e741052c1da009cb23068df73100b146b2，與使用者提供的 merge commit 一致。Alpha.2 Tag／Release 尚不存在；Latest 為 v0.1.4，正式 Tag 指向 6aa5c775d8ea011ea4b2380ef467591a6966070a。

本準備 PR 加入獨立 Alpha workflow、來源 gate／附件產生腳本及測試、繁中 notes 和發布前後皆成立的 START-HERE 發布狀態說明。三份核心 Skill 不變。完整操作與預設不發布行為見 [CI/CD](../ci-cd.md#v020-alpha2-專用流程發布準備)。

待使用者審查：流程的 PR 僅準備、日後精確 Alpha Tag push 才發布的條件及另行授權；準備 PR 不自行合併。PR 整合後須再次核對 develop-0.2 HEAD，選最終來源 SHA、重建並審查附件／SHA256SUMS.txt，再決定實際發布。現在對 b52851e 產生的候選只證明目前已整合內容可封裝，不是尚未合併的準備 PR 已成為發布來源；入口修正整合後 ZIP hash 會改變。

Google Docs 人工回報依 PR #33 及驗收索引記錄，未在本機重做；真正跨對話恢復、多人競爭、長篇全部頁面／不同裝置字型及跨模型表現尚未完整驗證，限封閉 Alpha。完整 Tag／Release 寫入流程尚未實測。

## 記憶庫待寫回摘要

本環境沒有 Google Drive 讀寫工具，無法讀取或更新「學聯會 AI 專案記憶庫｜三 Repo 共用」。以下是供授權環境寫回的交接摘要，並非宣稱記憶庫已更新：

- Repo：Clock1025/sa-legal-skills；PR #33 已合併到 develop-0.2（b52851e）；v0.2.0-alpha.2 本輪只準備，尚未建立 Tag／Release，未改 main／develop 或既有正式版。
- 新專用流程於 PR 只產生／驗證附件；只接受已整合 develop-0.2 的完整 SHA；Alpha 與 v0.1 Beta 的 origin/develop gate 分開。精確 Alpha Tag push 必須另獲明確授權，不標 Latest、不覆寫既有 Tag／Release。
- Notes、固定五檔 ZIP／SHA256SUMS 與人工驗收範圍一併審查；最終來源與 hash 在準備 PR 整合後重新確認。Google Docs 已知風險仍限封閉 2～3 人試用，沒有寄出邀請。
- 本次 PR 連結、commit、附件 hash 與實際測試／CI 結果以對應 GitHub 準備 PR 紀錄為準；讀取／寫回記憶庫仍待有權限的環境完成。


## 本地驗證結果

- 目前已整合的 b52851e：於獨立乾淨 checkout 透過新腳本成功跑完 Validator 與既有 121 tests，產出五檔 ZIP、SHA256SUMS.txt、SOURCE_COMMIT.txt、候選 notes；sha256sum --check 成功。此來源 ZIP hash 為 `e1681ea77d907d62784a00e7c39350c43eddf6dd577a6e70acbb68f9e60398f5`。
- 發布準備工作樹：Validator、全部 127 tests（原 121 加 6 個發布來源／觸發條件測試）及 diff check 通過；工作流程 YAML、各 shell step 的 bash -n 檢查通過。Alpha 不改既有 Beta／Stable workflow 或核心 Skill。
- 因修正入口發布狀態，準備工作樹 ZIP 預覽 hash 為 `4ef8bc273e535484a3cd1578ca10dd0b1fb40403b664e48ac3eed02410959829`。這是尚待整合／審查的候選內容，不把 feature SHA 當作已整合來源；合併準備 PR 後須再次核對最終來源及附件。
- 新流程 PR CI 會讀取其 develop-0.2 base 生成可下載的候選 artifact；PR 不進 publish job。Tag 發布／上傳等真實寫入未執行，沒有建 Tag 或 Release。後續另獲授權的精確 Alpha Tag push 才是發布觸發。
