# sa-legal-skills 快速上手

本專案提供學生自治組織使用的法規審查與修法 Agent Skills。它不是獨立 App，不必會 Git，也不需要安裝程式。

## 選擇 Skill

- 想確認現行規定、權限、程序、期限或合規問題：選 `regulation-review`。
- 正在設計或改革整部章程／制度，並要追蹤已決與未決事項：選 `large-scale-reform`。
- 制度方向已決定，要起草正式修正條文、對照表、說明或 DOCX：選 `amendment-drafting`。

1. **AI 能讀 GitHub 時：**直接提供 https://github.com/Clock1025/sa-legal-skills 與需要的 Skill 路徑，例如 `skills/regulation-review/SKILL.md`，要求 AI 先實際讀取檔案再工作。
2. **AI 不能讀 GitHub 時：**從下載或解壓縮的資料夾找到 `skills/<Skill 名稱>/SKILL.md`，上傳或貼入 ChatGPT 或其他 AI。AI 若讀取失敗，應明確告知，不得宣稱已讀取。
3. **再提供案件資料：**提供正式現行法規文本、版本或生效資訊及必要事實；若引用其他法規，也一併提供相關文本。

可複製以下提示詞開始：

> 請先實際讀取我指定或提供的 SKILL.md，再依其中的工作流程與限制處理案件。若讀取失敗，請明確告知，讓我提供檔案；不得宣稱已讀取。不得自行補充我尚未決定的制度政策，也不得依記憶重建現行法規。

請接著說明要處理的問題，並上傳相關正式文件。不同 AI 模型對長文件、規則遵循及 DOCX 產生或格式驗證的能力可能不同；請核對輸出內容與正式來源。使用本專案不需要 GitHub Codespaces。
