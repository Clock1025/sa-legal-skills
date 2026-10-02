# 在 ChatGPT 使用

不必安裝 Skills。下面是提供指引和案件文件的操作方式；按鈕名稱、檔案支援及工具能力會隨帳號、模型和介面版本改變。

## 開始對話並提供 Skill

1. 開啟 [ChatGPT](https://chatgpt.com)，登入後選擇「新對話／New chat」（或目前介面的新增對話按鈕）。
2. 在平常輸入訊息的文字框貼入[START-HERE 的唯一可複製提示詞](../../START-HERE.md#可複製提示詞)。只說明你想解決的問題即可，AI 可協助判斷本次 Skill。
3. 若已知要用哪份 Skill，直接送出以下文字，並依需求替換路徑：

   ```text
   請實際讀取 https://github.com/Clock1025/sa-legal-skills 的
   skills/regulation-review/SKILL.md，再依其中規則處理案件。
   若不能讀取，請明確告知，讓我提供檔案；不要宣稱已讀取。
   ```

以下為使用者回報的 **2026-10-02** 實測紀錄：在 **ChatGPT 對話環境**中，GitHub zero-install 成功，指定 `regulation-review` 的描述性分析與合規分析實測成功；**模型版本未記錄**。詳見[v0.1.1 紀錄](../regression/v0.1.1.md)。這是當次人工實測回報，不是本輪自動化測試；本輪未重新執行。平台、模型與工具能力可能更新，不代表所有 ChatGPT 對話都能讀 GitHub。

## 讀不到 GitHub 或要提供文件時

從[三份 Skill 清單](generic-agent.md#取得本次需要的-skill)開啟本次需要的檔案，完整複製並貼入文字框；或下載 `SKILL.md`，用目前介面提供的附件／新增檔案功能上傳。只需本次使用的 Skill。若檔案格式被拒絕，改貼全文，不必安裝。

再以附件提供正式 PDF／DOCX，或把法規全文貼入訊息，並說明法規名稱、版本／生效資訊、案件事實與問題。先要求 AI 回報讀取限制；「已讀取」的文字回覆不代表 PDF 每頁都已核對。

## 要正式 Word 文件時

制度方向確認後，要求「請依 `amendment-drafting` 產生可編輯 DOCX，保留原生 Word 表格、底線、中文字型與法規段落縮排；如有正式範本，請沿用」。需要切換 Skill 時，讓 AI 實際讀取或提供對應檔案。若目前環境不能建立 DOCX，要求明確告知並提供完整結構化內容，不把純文字回覆視為已產生 Word 檔案。

官方操作參考：[ChatGPT 網頁版使用說明](https://learn.chatgpt.com/docs/web)。以目前帳號可見功能為準。
