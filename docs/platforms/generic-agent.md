# 在其他 AI Agent 使用

開啟平常使用的 AI，建立一個新對話，把[START-HERE 的唯一可複製提示詞](../../START-HERE.md#可複製提示詞)貼到訊息框。若是讀取 workspace 的 Agent，提供檔案路徑；不確定時直接說明想解決的問題。各平台介面、網路讀取、附件與檔案產生能力不同，且可能更新。

## 取得本次需要的 Skill

- [regulation-review](https://github.com/Clock1025/sa-legal-skills/blob/main/skills/regulation-review/SKILL.md)：現行規定、權限、程序、期限與合規問題。
- [large-scale-reform](https://github.com/Clock1025/sa-legal-skills/blob/main/skills/large-scale-reform/SKILL.md)：整體制度設計及已決／未決事項追蹤。
- [amendment-drafting](https://github.com/Clock1025/sa-legal-skills/blob/main/skills/amendment-drafting/SKILL.md)：已確認制度方向的正式條文、對照表與提案文件。

能讀 GitHub 時，提供 https://github.com/Clock1025/sa-legal-skills 與其中一份 Skill 路徑，要求先實際完整讀取。不能讀時，開啟上面的檔案，完整複製內容貼入訊息框，或下載後以上傳附件提供。若附件不支援 `.md`，改貼全文。要求 Agent 明確說明讀取失敗，不得宣稱成功。

只需先提供本次要用的 Skill；切換工作時再提供對應檔案。三份規則各自以原始 `SKILL.md` 為準，網路讀取、上傳或完整貼入都能提供同一份規則。安裝到 Skills 目錄適合長期使用；若 Agent 支援自動發現，可減少每次指定的操作，但不是必要步驟。

## 提供案件資料與要求文件

在同一對話用附件提供正式 PDF／DOCX，或貼入法規文字，同時交代名稱、版本／生效資訊、必要事實和問題。實際支援格式與解析方式依 Agent 而定；讀不到的部分應要求其告知，而非以模型記憶補完。

制度方向確認後，可要求「請先完整讀取 amendment-drafting，依規則提供可編輯 DOCX，使用原生 Word 表格、真正底線、中文字型與法規縮排；如有正式範本請沿用」。無 DOCX 產生能力時，要求完整結構化文件內容並明確標示限制。若可渲染，還需檢查換頁與表格；不能只憑文字宣稱版面已驗證。
