# 在 Gemini 使用

以下為使用者回報的 **2026-10-02** 實測紀錄：**Gemini 3.1 Pro** 直接讀取 GitHub repository 失敗，模型有明確告知無法讀取；手動提供完整 `SKILL.md` 後可使用，且 `large-scale-reform` 已進行實際案件測試。這是當次人工實測回報，不是本輪自動化測試；本輪未重新執行。平台、模型與工具能力可能更新，不代表 Gemini 永久不支援 GitHub。

## 先開新對話

開啟 [Gemini](https://gemini.google.com)，登入後選擇目前介面的「新對話／New chat」。把提示詞貼到平常輸入訊息的文字框。第一次使用可先貼[START-HERE 的唯一可複製提示詞](../../START-HERE.md#可複製提示詞)，讓 AI 判斷要用哪份 Skill；無法讀 GitHub 時，依下面方式提供檔案。

## 方法 A：開啟 → 全選 → 複製 → 貼入

1. 從下方入口選擇本次需要的 Skill。Raw 是只有文字的頁面，較方便完整複製；電腦可用全選快捷鍵，手機依瀏覽器方式全選。
2. 複製整份內容，從開頭 `---` 到最後一段，不只複製標題或描述。
3. 貼入 Gemini 文字框，附上「請先完整閱讀以上 SKILL.md，再依其中規則處理；若文字被截斷請告知，不要依記憶補完」。送出後再提供案件資料。

| 本次需求 | GitHub 檔案頁 | Raw 純文字 |
| --- | --- | --- |
| 查現行規定、權限、程序或合規問題 | [regulation-review](https://github.com/Clock1025/sa-legal-skills/blob/main/skills/regulation-review/SKILL.md) | [開啟全文](https://raw.githubusercontent.com/Clock1025/sa-legal-skills/main/skills/regulation-review/SKILL.md) |
| 制度設計與未決事項追蹤 | [large-scale-reform](https://github.com/Clock1025/sa-legal-skills/blob/main/skills/large-scale-reform/SKILL.md) | [開啟全文](https://raw.githubusercontent.com/Clock1025/sa-legal-skills/main/skills/large-scale-reform/SKILL.md) |
| 制度已定，要起草正式文件 | [amendment-drafting](https://github.com/Clock1025/sa-legal-skills/blob/main/skills/amendment-drafting/SKILL.md) | [開啟全文](https://raw.githubusercontent.com/Clock1025/sa-legal-skills/main/skills/amendment-drafting/SKILL.md) |

只需貼本次使用的 Skill，不必每次貼三份。這些入口指向原始檔案，不另維護一份 Gemini 版 Skill。

## 方法 B：上傳檔案

取得本次需要的 `SKILL.md`（也可從 Release ZIP 解壓取得），使用文字框附近的「新增檔案／Add files」及上傳功能提供。若當前介面或帳號不接受 `.md`，改用方法 A。按鈕名稱與支援格式依當前版本為準。

接著同樣上傳正式 PDF／DOCX，或直接貼入法規文字，並提供版本／生效資訊、必要事實及想解決的問題。解析能力依環境而定；要求 Gemini 明確告知讀取限制，不把「已讀完」視為 PDF 每頁完整性驗證。

## 要正式 Word 文件時

制度方向確認後，再完整提供 `amendment-drafting`，要求可編輯 DOCX、Word 原生表格、真正底線、中文字型與法規段落縮排。若 Gemini 當前環境不能直接產生 DOCX，請其明確告知並提供完整結構化內容；不要把文字回覆或其他格式文件稱為已完成的 DOCX。

操作參考：[Google 官方檔案上傳說明](https://support.google.com/gemini/answer/14903178?hl=zh-Hant)。官方文件描述的 GitHub 匯入等功能是否可用，仍須在你的帳號確認；本指南優先提供本次已成功實測的貼入路徑。
