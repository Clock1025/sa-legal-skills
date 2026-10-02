# sa-legal-skills 快速上手

本專案提供學生自治組織使用的法規審查與修法 Agent Skills。它不是獨立 App，不必會 Git，也不需要安裝程式。

## 選擇 Skill

- 想確認現行規定、權限、程序、期限或合規問題：選 `regulation-review`。
- 現在要規劃整體改革、協調多個制度或追蹤大量待決事項：選 `large-scale-reform`。
- 制度方向已決定，要起草正式修正條文、對照表、說明或 DOCX：選 `amendment-drafting`。

目前只是檢查現行制度時，即使涉及整套規章或未來可能修法，也先選 `regulation-review`；不要只因範圍大就選 `large-scale-reform`。

## 可複製提示詞

```text
請用一般學生看得懂的文字帶我開始。
Skill 來源：https://github.com/Clock1025/sa-legal-skills

根據我現在要做的事選擇本次 Skill：如果目前主要是檢查現行規定，即使涉及整套規章、未來可能大改或想法尚未整理，也先選 regulation-review；只有現在要規劃整體改革、協調多個制度或追蹤大量待決事項，才選 large-scale-reform；制度方向大致確定並要寫正式修正條文、修正總說明或對照表時，才選 amendment-drafting。

請先實際完整讀取本次所需的 Skill。若不能讀 GitHub，請告訴我如何提供該 SKILL.md；不得宣稱已讀取。

在取得並完整讀取本次所需 Skill 前，只能協助我辨識大致需求、選擇 Skill，或取得、貼上、上傳該 Skill。不得索取現行法規文本、版本、生效日期、修正日期、案件事實、具體爭議資料或其他正式工作材料，也不得開始正式法規分析、合規判斷、制度設計或修法起草。此時唯一必要的下一步是取得並完整讀取本次所需 Skill；讀完後才依 Skill 要求逐步取得案件材料。

一次只問一個必要問題，必要時最多一次兩個。未決制度或政策不要替我選方案。

正式分析或起草前，先簡短整理：我想解決什麼、已確認事項、尚未確認事項，以及本次要使用的 Skill。接著依照該 Skill 的流程與限制處理。
```

1. **AI 能讀 GitHub 時：**直接提供 https://github.com/Clock1025/sa-legal-skills 與需要的 Skill 路徑，例如 `skills/regulation-review/SKILL.md`，要求 AI 先實際讀取檔案再工作。
2. **AI 不能讀 GitHub 時：**從下載或解壓縮的資料夾找到 `skills/<Skill 名稱>/SKILL.md`，上傳或貼入 ChatGPT 或其他 AI。AI 若讀取失敗，應明確告知，不得宣稱已讀取。
3. **讀完 Skill 後再提供案件資料：**依該 Skill 要求，逐步提供正式現行法規文本、版本或生效資訊及必要事實；若引用其他法規，也一併提供相關文本。

請接著簡述要處理的問題；待 AI 完整讀取 Skill 後，再依其要求上傳相關正式文件。不同 AI 模型對長文件、規則遵循及 DOCX 產生或格式驗證的能力可能不同；請核對輸出內容與正式來源。使用本專案不需要 GitHub Codespaces。

需要更多操作說明，可在線閱讀[新手引導](https://github.com/Clock1025/sa-legal-skills/blob/main/docs/first-time-user.md)與[平台指南](https://github.com/Clock1025/sa-legal-skills/tree/main/docs/platforms)。這些指南未包含在 ZIP 中；上面的步驟已可獨立使用。
