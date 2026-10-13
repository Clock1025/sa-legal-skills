# 半自動驗收工具（離線）

此工具延用 model-matrix.json、run-template.json 及 check_acceptance_evidence.py。僅使用 Python 標準庫，不呼叫模型、不使用付費 API、不更改既有 P0 判準或歷史 FAIL。

## 準備操作包

執行：

    python3 scripts/acceptance_assist.py prepare P0-CASE-03

預設輸出在 test-output/acceptance/plans/P0-CASE-03/：

- operator.md：原矩陣的操作順序和 Skill 需求，僅供操作者參考。
- prompt-fragments.md：**僅摘錄原始步驟引號中的輸入片段，不是完整可直接送給模型的提示詞**。需依 START-HERE 的 canonical prompt、原始 Skill 及虛構材料補上上下文。
- evaluator-PRIVATE.md：預期及禁止行為，與模型輸入隔離。P0 判定仍以原案為準。

禁止直接將 operator.md 或 evaluator-PRIVATE.md 貼給受測模型。本工具不自動推斷哪段敘述是完整使用者輸入；避免提前透露參考答案。不會覆寫既存的操作包。

## 匯入 UTF-8 TXT

先在實際平台取得已授權的 UTF-8 TXT（無私人資料及憑證），於本機執行：

    python3 scripts/acceptance_assist.py import-txt P0-CASE-03 gpt6-p003-r1 /path/to/export.txt --commit <完整40字元SHA> --platform ChatGPT --surface Chat --model GPT-6

輸出 test-output/acceptance/gpt6-p003-r1/evidence/original.txt 與 record.json。完整保存原始 bytes，索引 SHA-256 和 byte_size；拒絕無效 UTF-8、空檔、含 NUL、重複 run ID、同雜湊檔案與不安全路徑。所有版號和平台由操作者聲明，工具只查驗 SHA 字串格式與檔案一致性，**不查證**真實模型或版本。

新匯入仍是 NOT TESTED / PLANNED，沒有預先填造任何模型回覆、tool receipt、隔離證據或人工判定。保存 TXT 只是證據整理的開始。模型輸出若能在可見聊天介面直接觀察，人工可依真正輸入／輸出判斷該行為；缺底層日誌則註明無法驗證 Skill 完整讀取或 fresh-context，而不是否定已可觀察的行為。

人工確認後，依 record-guide.md 建立有來源錨點的 inputs、outputs、execution、adjudication，並使用：

    python3 scripts/check_acceptance_evidence.py test-output/acceptance/gpt6-p003-r1/record.json

此檢查器仍僅驗證宣告與檔案相符，不是法規或模型正確性驗收。不要覆寫既有 FAIL，重測須另建 run。

## 產生報告

    python3 scripts/acceptance_assist.py summary --output test-output/acceptance/summary.md

列出各案例、模型／平台、候選 SHA 前綴、個別 run、狀態與缺證據。沿用既有完整性檢查器；無效紀錄另外列示，不混算成 PASS。沒有 run 的案例維持 NOT TESTED。不提供自動發布或 RC 決策。

## 隱私、使用界線

- 本機 test-output/ 應保持 Git ignore；不得將真實對話、未授權文件、憑證、私密提示或學生資料提交 repository。
- 工具不能連線取用 ChatGPT／Claude／Gemini 私人歷史，也不能自動核實 TXT 是否為完整平台匯出；不以缺資料補造對話。
- 不處理平台專屬二進位匯出，不推論是否關閉 memory，也不假裝完成真人模型、DOCX 渲染或法律正確性測試。
- 參考實務型案例：practical-cases/operator.md 及獨立的 practical-cases/evaluator-PRIVATE.md。
