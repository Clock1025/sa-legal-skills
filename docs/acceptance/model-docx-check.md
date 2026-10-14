# 模型 DOCX 產物品質檢查（Draft）

使用 `scripts/check_model_docx.py` 比對你實際取得的DOCX與可核對的原始條文、已確認修正全文。
核心使用Python標準庫；重用既有docx_reference的欄名／文字diff底線計算，以及docx_pdf_probe的可選頁面預覽。
不使用reference的固定欄寬、字型、direct-format validator去拒絕不同模型風格；不建立文件生成引擎。
不呼叫模型、不修正原檔、不自動授權政策或判法律正確性，也不依賴PR #17／#18任何一套新CLI。

## 提供核對基準

依 [虛構source範例](../../tests/fixtures/docx/source-example.json) 建UTF-8 JSON：

- schema_version=1.0；source的name／version／location是你核對的來源，未知明記UNVERIFIED。
- 每列有穩定id、source_anchor、confirmation_basis，及current（原文）、amended（已確認目標全文）各自段落字串陣列，按照對照表邏輯列的順序。
- reason是修正說明基準段落陣列；沒有基準用null，工具明列說明欄未核對，不猜法律理由。
- 每項／款／目保留真實段落，正文／標點／空白逐字保真。先依既有法制格式核對條號及單一U+3000；網站UI形式與canonical排版轉換由人核對，工具不偷偷刪空白或改字。
- 新增列的current可為「（本條新增）」；刪除列的amended可為「（刪除）」，依既有Skill處理文字底線、排除marker及空白。

這不是讓模型自行編核對答案。current必須來自原始來源，amended由可追溯使用者確認及核對後的目標全文建立。
confirmation_basis是你提供的引用，不是工具認證決策；來源與確認是否真實、是否涵蓋該範圍仍需人工確認。
原始DOCX／source JSON保存bytes、SHA-256及大小；在JSON引用原始文件位置方便查核，**工具不會自動下載該位置或證明法律效力**。

## 執行

```bash
python3 scripts/check_model_docx.py \
  --docx /path/to/actual-model-output.docx \
  --source /path/to/checked-source.json \
  --run-id model-case01-attempt01 --origin MODEL_OUTPUT \
  --generation-evidence /path/to/actual-generation-record.txt --render
```

路徑是佔位，請用真正檔案。不確定生成來源維持預設UNVERIFIED；reference／合成測試明記REFERENCE／SYNTHETIC。
即使宣告MODEL_OUTPUT且附生成記錄，模型來源仍為UNVERIFIED，須人工比對此次對話、下載鏈及文件hash，不能只信模型自述。
生成記錄可為已授權的可見文字／截圖原始bytes，不取得hidden prompts；本工具不解析證據真實性。

若文件有多個比較表，用 `--table 2` 明確選文件頂層第二張表；不將不同法規混成一個提案或自動猜對應。
原生表格的三個欄名須可辨識為「修正條文」「現行條文」「說明」；若只是順序不同，按欄名核對、另列格式項。
無可辨識原生表／圖片表會產生未核對報告，不OCR重建。合併儲存格、巢狀表、未知欄名需人工映射；不宣稱已完全支援。

輸出固定在 ignored `test-output/model-docx-quality/<run-id>/`，拒絕覆寫、symlink與穿越路徑：

- input.docx、source.json：真正輸入bytes，沒有改寫或接受追蹤修訂。
- generation-evidence.bin：有提供才保存，無則明列缺失。
- report.json／report.md：hash、來源宣告、所選表／列／欄anchor、抽取段落、實際新舊差異、底線及風險發現。
- preview/：有請求且工具可用時保存PDF、PNG及renderer資訊；所有檔案留本地，不上傳公開Repo。

來源、回報或模型對話可能敏感；ignored不是存取控制，公開前仍需使用者授權，不把真實學生資料加進Git。

## 判定界線與風險

| 自動項目 | 能說明的結果 | 人工仍需做的事 |
| --- | --- | --- |
| 文字／段落逐列比對 | 與給定current／amended／reason是否相同，列數不符、漏段、重複或錯欄可能性 | 核對source真實性、版本、原本的法律結構及確認範圍；差異不等於自動判法律錯誤 |
| 原生表格 | 有Word表格與文字節點；圖片、合併／巢狀或文件保護另列 | 在Word確認實際可編輯、條文及圖中內容；原生結構PASS不是Word操作實測 |
| 實際文字diff與底線 | 使用字符級新舊變化比對已解析底線；新增／刪除marker及空白分開 | 確認變化是已授權的修正，不以底線匹配替代政策確認 |
| 樣式底線 | 解析document defaults、paragraph／character basedOn及direct override；未能解析記UNVERIFIED | 條件table styles、未知樣式／版本、所有有效格式不作全面保證 |
| 生成來源 | 保存來源宣告、證據檔bytes及hash | 真正查核是不是該次模型產物；沒有證據不虛構生成歷史 |
| PDF／PNG | 真正產生頁面預覽、頁數、已生成頁、embedded fonts名稱及renderer版本 | 實際看每頁、底線、分頁、空白、欄位與字型；沒有看圖VISUAL QA: NOT TESTED |

HIGH優先：原文／目標文字或段落結構差異、列數不符、無法安全對應、未決追蹤修訂／非文字物件等需核對可能內容風險。
MEDIUM：缺變動底線、欄序／保護或未知樣式需人工處理；依真實影響調整，不把格式本身稱法律效果錯誤。
LOW：例如「七日」兩字都畫底線但實際只改「七」；文字一致性可以PASS，底線格式仍FAIL，風險不等同漏字／擅改政策。
多餘空段落與非空正文完全一致時另列LOW；不能拿低風險項目抵銷已觀察的HIGH差異。

退出碼0只代表成功產生報告，即使報告有FAIL；輸入不合法／映射需明確選擇時退出非0。
這不是CI放行閘門，不自動修改run判定、歷史結果或模型驗收覆蓋；可將report作為既有回報包的產物索引附件。

## 可選渲染與安全限制

`--render` 使用已安裝的soffice與既有可用的PyMuPDF；不自動安裝依賴、連付費API或索Key。
使用隔離LibreOffice profile並設定高MacroSecurityLevel，先拒絕外部relationships、嵌入物件／macro payload及altChunk的渲染。
ZIP不解壓到文件系統，檢查CRC、成員重複／路徑、總解壓大小及XML DTD；這不是完整惡意文件沙箱。
外部普通超連結也會使本工具暫不渲染，記能力限制而非法律內容FAIL；必要時由維護者在合適的受控環境看頁。
未安裝工具／預覽失敗保持NOT TESTED／PARTIAL與原因，不捏造PDF。最多輸出100頁PNG，超出的未生成頁如實列範圍。
字型只回報觀察到的PDF名稱，不能由名稱證明已正確fallback，也不保證Word、Windows／Mac版面一致。

本批測試只用既有六個reference案例及虛構mutation，無實際模型DOCX或正式法律案件，模型回歸／視覺驗收皆NOT TESTED。
原reference生成成功或自動比對PASS不升格為真人產物驗收；舊DOCX視覺紀錄不冒充本批重跑。
