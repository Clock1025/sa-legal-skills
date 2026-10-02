# 在 Claude 使用

不必先懂 GitHub，也不必把三份 Skill 全部上傳。介面與檔案能力可能更新；下面的實測結果只代表當次環境。

## 開始對話並提供 Skill

1. 開啟 [Claude](https://claude.ai)，登入後從首頁或側欄建立「新對話／New chat」；名稱與位置以目前介面為準。
2. 在平常輸入訊息的文字框貼入[START-HERE 的唯一可複製提示詞](../../START-HERE.md#可複製提示詞)，再用自己的話說明問題。
3. 已知 Skill 時，可直接貼入：

   ```text
   請實際讀取 https://github.com/Clock1025/sa-legal-skills 的
   skills/regulation-review/SKILL.md，再依其中規則處理案件。
   無法讀取時請明確告知，讓我提供全文；不得宣稱已讀取。
   ```

以下為使用者回報的 **2026-10-02** 實測紀錄：**Claude Sonnet 5.5 Medium** 的 GitHub zero-install 成功，指定單一 `SKILL.md` 讀取成功，不需全部上傳。這是當次人工實測回報，不是本輪自動化測試；本輪未重新執行。平台、模型與工具能力可能更新，不是對所有 Claude 模型或未來版本的能力保證。

## 讀不到 GitHub 或要提供文件時

從[Skill 清單](generic-agent.md#取得本次需要的-skill)開啟需要的 `SKILL.md`，完整複製全文貼入文字框；或取得檔案後，用訊息框旁的「＋／Add files or photos」或目前附件功能上傳。若附件不接受 `.md`，改貼全文。只提供本次使用的 Skill 即可。

用相同附件方式提供 PDF／DOCX，或貼入正式法規文字，再交代版本／生效資訊與必要事實。要求 Claude 說明哪些內容無法讀取；掃描頁與長文件的解析須另外核對，不能只憑「已讀完」就認定完整。

## 要正式 Word 文件時

制度方向確認後，請 Claude 先讀取 `amendment-drafting`，再要求「產生可編輯 DOCX，使用原生 Word 表格、真正底線、中文字型與法規縮排；依我提供的正式範本排版」。能否產生可下載檔案依目前工具與帳號功能而定；不能產生時，請其明確說明並提供完整文件內容。

附件操作參考：[Claude 官方檔案上傳說明](https://support.claude.com/en/articles/8241126-upload-files-to-claude)。功能以當前介面為準。
