# sa-legal-skills 快速上手

本專案提供學生自治組織使用的法規審查與修法 Agent Skills。它不是獨立 App，不必會 Git，也不需要安裝程式。

## 封閉 Alpha 試用：先從這裡開始

你收到 v0.2.0-alpha.2 試用邀請時，請使用下方固定版本；不需要會 Git 或看開發流程。**目前尚未建立 Alpha.2 Tag／Release**，試用的是 [PR #33](https://github.com/Clock1025/sa-legal-skills/pull/33) 已驗證的 Skill，固定版本為 `c07803e57d70ead05d9b5bdc5fdbf86e05ad1fb2`。這不是已發布的正式版，請勿改用專案首頁的 main 或「最新正式 Release」附件。

| 這次想做什麼 | 點這裡取得固定版本 Skill |
| --- | --- |
| 試做 Google Docs 修法草案 | [amendment-drafting：完整檔案](https://github.com/Clock1025/sa-legal-skills/blob/c07803e57d70ead05d9b5bdc5fdbf86e05ad1fb2/skills/amendment-drafting/SKILL.md) |
| 核對現行規定或程序 | [regulation-review：完整檔案](https://github.com/Clock1025/sa-legal-skills/blob/c07803e57d70ead05d9b5bdc5fdbf86e05ad1fb2/skills/regulation-review/SKILL.md) |
| 規劃整體改革、整理待決事項 | [large-scale-reform：完整檔案](https://github.com/Clock1025/sa-legal-skills/blob/c07803e57d70ead05d9b5bdc5fdbf86e05ad1fb2/skills/large-scale-reform/SKILL.md) |

只需取得這次要用的一份：把連結交給 AI，請它完整讀取；讀不到時，開啟檔案頁面的 **Raw**，複製完整內容貼入或儲存後上傳，不要只貼檔名或截圖。下方唯一提示詞已指定同一固定版本；讀完 Skill 才提供案件資料。Google Docs 第一次操作可照[新手操作卡](docs/first-time-user.md#google-docs-首次試用操作卡)逐步進行。若你只拿到 ZIP 而沒有 docs，可在線看[同一份操作卡](https://github.com/Clock1025/sa-legal-skills/blob/feature/v0.2-google-docs-template/docs/first-time-user.md#google-docs-首次試用操作卡)；指引可更新，試用 Skill 仍固定為上述版本。

## 選擇 Skill

- 想確認現行規定、權限、程序、期限或合規問題：選 `regulation-review`。
- 現在要規劃整體改革、協調多個制度或追蹤大量待決事項：選 `large-scale-reform`。
- 制度方向已決定，要起草正式修正條文、對照表、說明或 DOCX：選 `amendment-drafting`。

目前只是檢查現行制度時，即使涉及整套規章或未來可能修法，也先選 `regulation-review`；不要只因範圍大就選 `large-scale-reform`。

## 文件模式（v0.2.0-alpha.2 開發中）

Google Docs 優先，DOCX 完整保留。讀完本次 Skill 後，AI 應依實際工具及文件權限確認能否安全操作 Google Docs，不能只看模型名稱。有既有文件就先讀現況並局部修改；每項已確認修改及時寫入、再讀回核對，保護人工修改。Google Docs 建立、讀取、寫入失敗、缺少權限或版本衝突無法安全解決時，停止相關操作並保留現況，回報原因、已完成部分與未確認結果；不得擅自建立替代 Google Docs、DOCX 或覆蓋其他文件。只有使用者明確選擇 DOCX 時，才使用完整、獨立的 DOCX 流程。這不改變下方完整讀取 Skill 與政策確認的前置要求。

母版模式須由你提供並授權使用當次母版；AI 先驗證讀取／複製及安全編輯能力，僅修改經身分核對的副本，原母版不動。已有工作文件時優先續寫原文件；沒有母版或不支援時停止詢問，不擅建替代文件或轉 DOCX。逐條原生填表及擴列、真正底線與格式讀回規範已內嵌 Skill，無 docs 的 ZIP 也可使用；真人視覺仍須另驗收。

## 可複製提示詞

```text
請用一般學生看得懂的文字帶我開始。
Skill 來源：https://github.com/Clock1025/sa-legal-skills/tree/c07803e57d70ead05d9b5bdc5fdbf86e05ad1fb2
本次是尚未發布的 v0.2.0-alpha.2 封閉試用；請從上述固定版本讀取所選 Skill，不要改用 main 或最新正式 Release。

根據我現在要做的事選擇本次 Skill：如果目前主要是檢查現行規定，即使涉及整套規章、未來可能大改或想法尚未整理，也先選 regulation-review；只有現在要規劃整體改革、協調多個制度或追蹤大量待決事項，才選 large-scale-reform；制度方向大致確定並要寫正式修正條文、修正總說明或對照表時，才選 amendment-drafting。

請先實際完整讀取本次所需的 Skill。若不能讀 GitHub，請告訴我如何提供該 SKILL.md；不得宣稱已讀取。

在取得並完整讀取本次所需 Skill 前，只能協助我辨識大致需求、選擇 Skill，或取得、貼上、上傳該 Skill。不得索取現行法規文本、版本、生效日期、修正日期、案件事實、具體爭議資料或其他正式工作材料，也不得開始正式法規分析、合規判斷、制度設計或修法起草。此時唯一必要的下一步是取得並完整讀取本次所需 Skill；讀完後才依 Skill 要求逐步取得案件材料。

如果工作進行中從一個 Skill 切換到另一個 Skill（例如從 regulation-review 進入 amendment-drafting），只要我仍要求使用或切換該 Skill，新階段開始前就必須先實際完整讀取新 Skill，這是不可跳過的前置條件。先前已讀取其他 Skill、案件材料完整、政策已確認、前階段已完成、時間緊迫，或後續要求先用已有材料／不用等 Skill，都不構成跳過讀取的授權。若新 Skill 無法讀取，停在取得／貼上／上傳該 Skill，不得先產生任何屬於新階段的正式或暫擬內容。只有我明確撤回使用 Skill framework、改為一般非 Skill 工作時，才屬另一種情境；仍要求切換 Skill 卻要求不用讀，不是撤回。

一次只問一個必要問題，必要時最多一次兩個。未決制度或政策不要替我選方案。

正式分析或起草前，先簡短整理：我想解決什麼、已確認事項、尚未確認事項，以及本次要使用的 Skill。接著依照該 Skill 的流程與限制處理。
```

1. **AI 能讀 GitHub 時：**直接提供本頁封閉 Alpha 入口的固定版本連結與需要的 Skill 路徑，例如 `skills/regulation-review/SKILL.md`，要求 AI 先實際讀取檔案再工作。
2. **AI 不能讀 GitHub 時：**從下載或解壓縮的資料夾找到 `skills/<Skill 名稱>/SKILL.md`，上傳或貼入 ChatGPT 或其他 AI。AI 若讀取失敗，應明確告知，不得宣稱已讀取。
3. **讀完 Skill 後再提供案件資料：**依該 Skill 要求，逐步提供正式現行法規文本、版本或生效資訊及必要事實；若引用其他法規，也一併提供相關文本。

請接著簡述要處理的問題；待 AI 完整讀取 Skill 後，再依其要求上傳相關正式文件。不同 AI 模型對長文件、規則遵循及 DOCX 產生或格式驗證的能力可能不同；請核對輸出內容與正式來源。實際使用前，請另參閱 README 的「使用限制與免責聲明」。使用本專案不需要 GitHub Codespaces。

需要更多操作說明，可在線閱讀[新手引導](https://github.com/Clock1025/sa-legal-skills/blob/feature/v0.2-google-docs-template/docs/first-time-user.md)與[平台指南](https://github.com/Clock1025/sa-legal-skills/tree/c07803e57d70ead05d9b5bdc5fdbf86e05ad1fb2/docs/platforms)。平台指南含歷史紀錄，封閉 Alpha 的 Skill 來源仍以上方固定版本為準，不使用其中 main 的 Skill 連結。這些指南未包含在 ZIP 中；上面的步驟已可獨立使用。
