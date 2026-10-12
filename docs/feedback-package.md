# Skill 完整回報包（Skill Feedback Package）

本文件是唯一 canonical 回報契約（schema_version `1.0`）。三個 Skill 使用相同契約；
它是回顧／歸檔功能，不是第四個法律 Skill，也不是平台 API 私有對話匯出器。

最簡使用方式：在已使用的任一 Skill 對話送出：

> 請產生完整 Skill 回報包，包含可取得的完整對話紀錄。

「完整」是請求範圍，不保證取得所有平台歷史。僅盤點當下實際可取得的內容；
不能重建已失去的原文、取得隱藏系統／開發者提示或私密推理，也不能冒稱過去讀過未讀 Skill。
回報不是切換法律工作階段，不能誤用新 Skill 讀取 gate 阻擋歸檔；
不藉此開始未讀 Skill 的正式或暫擬工作，也不替代原任務所需法規來源／政策確認。

## 檔案與離線工具

有檔案／ZIP 工具時，產出實際可下載且驗證過的檔案；只有生成成功才給實際檔案連結。
建議結構如下，空的附件／產物索引也必須存在：

```text
report_<conversation-id>_<YYMMDD>_<4-char-suffix>.zip
  manifest.json
  report.md
  transcript.md
  sources-index.md
  attachments/INDEX.md
  outputs/INDEX.md
  files/...                    # 只含可讀且明確授權的原始檔
```

Python 3.9+ 標準庫工具只接受已提供的逐字稿與 metadata，不連網、不登入平台、不上傳 GitHub。
先依[虛構輸入 fixture](../tests/fixtures/feedback/partial.json)準備 JSON；把真正要納入的檔案
放在 JSON 所在目錄下。不要用示範內容冒充實際對話或來源。

```bash
python3 scripts/feedback_package.py pack tests/fixtures/feedback/partial.json \
  --date 2026-10-12 --output-dir test-output/feedback
# --date 是明確提供的命名日期，不表示工具核實了對話日期。
python3 scripts/feedback_package.py validate test-output/feedback/report_<id>_<date>_<suffix>.zip
# 複製 pack 輸出的真正路徑；上列尖括號是占位，不是可直接執行的檔名。
```

來源位元組必須存在、位於輸入目錄內、在索引指定安全的 `local_path`，並設 `authorized: true`
及 `package_path: files/...` 才納入。不存在的指定檔案、越界路徑、未授權檔案直接 FAIL；
無法取得的附件仍可記 `UNAVAILABLE`、`package_path: null` 和原因，不捏造空白「原始檔」。
工具不自動偵測所有個資或憑證；操作者須先最小化資料、確認本地打包授權，不能因能讀就假定可公開。

## 欄位契約

manifest 是 UTF-8 JSON，不以 Markdown 代替。離線 input 由 manifest 的資料欄位組成；
`report_id`、`naming_date`、`delivery`、`files`、原始檔的 `sha256`／`byte_size` 由工具產生，禁止預填假值。
可填 `conversation_id: null` 讓工具生成；其餘欄位不能以省略代替缺失揭露。

| 欄位 | 內容及未知值 |
| --- | --- |
| `schema_version` | `1.0`；不支援版本明確拒絕 |
| `conversation_id`, `report_id` | 對話穩定 ID、此次回報唯一檔名 stem |
| `generated_at` | 有可靠來源才填帶時區 ISO-8601；無可靠時間填 null，limitations 記 UNVERIFIED |
| `naming_date` | 日期及來源：SUPPLIED_GENERATED_AT 或 USER_PROVIDED_NAMING_DATE；不是新造對話 timestamp |
| `platform` | `code/product/surface/evidence_status/evidence`；不能由模型名稱猜平台 |
| `model_segments` | `E1/E2/...`；各自 platform、model、reasoning_effort、起訖 T anchor、證據及狀態；未知 model/effort 為 UNKNOWN |
| `skill_reads` | name、path、source_id、stage、version/version_status、read_status、evidence/evidence_anchors；未知版本 UNVERIFIED；沒有 receipt 不記 FULL |
| `transcript` | completeness、coverage 與依時間／提供順序逐則的 turns，詳下節 |
| `sources` | SRC ID、原始 name、kind、version、location、visibility、evidence_status；kind 分 skill/current_law/proposal/case_material/export/other |
| `attachments`, `outputs` | ID/name、availability、authorized、reason、verification、evidence_status、package_path；bytes 未讀取不填 hashes/sizes |
| `report` | context/task/scope、confirmed_decisions、open_questions、events、validation_limits；confirmed_decisions 保留 D ID、CONFIRMED、scope、evidence_anchor；events 附可追溯 anchor 及證據標籤 |
| `limitations`, `redactions` | 驗證／功能缺失；每項紅刪記 location/reason，不重複放敏感原文 |
| `files` | 實際成員 path/hash/size；manifest 自身 hash/size 為 null 以避免自指 hash，不冒稱已計算 |
| `delivery` | ZIP 或 TEXT_FALLBACK；不宣稱本機檔案已上傳或在任何平台都可下載 |

`OBSERVED` 只代表可直接核對的觀察；`SELF_REPORTED` 是提供者／助手自行聲稱；
`UNVERIFIED` 是無足夠核對資料。工具驗證欄位、索引、位元組一致性，**不能證明輸入宣稱真實**。
可靠時間、平台資料、讀取 receipt、使用者確認、法律效力都須另附真實證據，不能用 schema PASS 代替。

report.md 須包含情境、任務、範圍、已確認決策、未確認問題、失敗與重大更正的
transcript turn／SRC evidence anchor、輸出清單和品質驗證層級；保持原有 D/I/SRC 身分與範圍。
未取得實際決策依據就不要填 confirmed_decisions；空列表可配 open_questions 描述缺失。
助手自評、封裝驗證或 GitHub Actions PASS 不等於真人模型／法律／DOCX 視覺 PASS。

## 逐字稿與完整性

按 user-visible 對話的時間先後逐則記 `role`、`text`、`representation`、`origin`。
逐字內容 VERBATIM 不改寫；摘要為 SUMMARY，紅刪內容為 REDACTED，不當成原文補齊。
真實 `message_id`、`timestamp` 已知才填；否則 UNKNOWN 或省略。
本工具的 T1/T2/... 是本回報本地順序／引用 anchor，**不是平台 message id 或時間**；
工具保持提供的順序，不推論未知時間。可見 tool output 僅依授權以來源記錄，
不可存取的工具內容、早期對話、平台 UI 和附件記在 coverage/limitations，不假裝讀取。

| transcript_completeness | 判準 |
| --- | --- |
| COMPLETE | 對明確宣告的 user-visible conversation scope 核對沒有缺漏，提供來源與核對證據；不能只因「看得到本回合」就完整。無紅刪／摘要／截斷 |
| PARTIAL | 已知缺少段落、截斷、摘要替代或紅刪；coverage 記 scope、start/end、evidence、missing、truncations、summary_substitutions，redactions 另列 |
| UNVERIFIED | 無法核對有無缺漏；不當作 COMPLETE；若已有明確缺失則改 PARTIAL |

離線工具要求 COMPLETE 的 `coverage.verification` 為 `CHECKED_USER_VISIBLE_SCOPE`，
起訖對得上逐字稿 anchors；這只是宣告一致性門檻，並不替操作者查證平台匯出是否完整。
使用者提供可讀的完整匯出檔時，可據此改善判定：sources 記匯出來源／版本／位置，
coverage 說明核對方式，turn.origin 指出由哪個匯出檔匯入。不可把局部 UI 截圖當全段對話證據。

敏感個資、法規文件、第三方聊天及憑證不預設向外上傳；只於可取得、經授權且最小必要時本地打包。
紅刪會讓逐字稿成為 PARTIAL，不能仍稱為未刪減 COMPLETE。請求回報包不等於授權公開散布原始附件。

## 對話 ID、版本與模型段落

Conversation ID = 2 字元平台／surface 代碼 + 6 字元小寫 a-z/0-9（例如 OC7m4q2x）。
以下為唯一代碼表；模型名字不足以確定產品與使用 surface：

| code | product | surface |
| --- | --- | --- |
| OC | ChatGPT | Chat |
| OX | Codex | Codex |
| OW | ChatGPT | Work |
| AC | Claude | Chat |
| AK | Claude | Code |
| GC | Gemini | Gemini |
| GS | Google AI Studio | Studio |
| GL | Gemini | CLI |
| GN | NotebookLM | NotebookLM |
| HI | Copilot | IDE |
| UU | UNKNOWN | UNKNOWN |

同一對話多次回報沿用初始 conversation_id，跨模型／surface 段落仍保留 ID，分別記 E1/E2 等。
離線工具不知不同 metadata 是否同一平台對話；首次 ID 會輸出在 manifest 與終端，
下次把它填入 input JSON 即可沿用。沒有自動平台持久化；沒有可持續保存能力時，須告知下次可能無法自動沿用，
請使用者保存／提供既有 ID。不要用目前模型或單一截圖推論整段模型與工具能力；能力變化可寫 segment.evidence 或 limitations。

工具實際呼叫 Python `secrets.choice` 產生 ID 與四字元小寫 alphanumeric suffix，
檢查輸出目錄中的碰撞：新 ID 碰撞重新生成；同一 ID 的 suffix 不跨日期重用。
唯一性僅能核對目前輸出目錄，刪除舊回報或換目錄後無法保證全域無碰撞，需記錄／人工核對。
無亂數工具的聊天不得聲稱使用安全亂數；可由使用者提供並檢查 ID/suffix，揭露未全域核對。

檔名 `report_<conversation-id>_<YYMMDD>_<suffix>.zip`；沒有可靠時間時保持 generated_at null，
由使用者明確提供命名日期，不憑空假造「今日」。模型／Skill／法律文件版本逐段只盤點已記錄事實；
沒有 commit/ref 就 UNVERIFIED，不能為回報倒補一個從未讀取的版本或捏造法律效力。

## 無 ZIP／無檔案工具的回退

ZIP 無法生成時（離線工具可用 `--text-only`），輸出可複製文字：manifest、report、transcript、
sources-index、attachments/INDEX、outputs/INDEX。逐段列明檔名；缺失功能與檔案仍列出。
不得給不存在的 sandbox/download 連結。離線文字回退不嵌入二進位附件，將其標 EXCLUDED、
package_path null 並說明原因；hash/size 不冒稱已打包。仍生成必要索引與 JSON。

```bash
python3 scripts/feedback_package.py pack tests/fixtures/feedback/partial.json \
  --date 2026-10-12 --text-only --output-dir test-output/feedback
```

聊天沒有檔案工具時，直接依本契約逐段貼文字即可，不要求先安裝腳本。
沒有真正計算位元組時，files 中的 sha256/byte_size 為 null，明列未驗證，不能用猜測填值。
人工把每段另存其指定名稱，以 UTF-8 保存；原始附件另行取得及確認授權後才放 files/，
重新用離線 packer 生成／validate ZIP，或用本機 ZIP 工具壓縮並核對成員／實際 hashes。
不要把分隔線或包裝文字算入逐字稿正文。離線 .txt 輸出提供各節 UTF-8 byte 長度以區分邊界；
人工複製後的完整性仍需另驗，不能只因有文字就自動標 COMPLETE。

## 驗收界線

可執行測試涵蓋 manifest/ID/coverage 一致性、ZIP 真正存在與內容、bytes/hash、
同對話 ID 沿用與 suffix 碰撞、段落不同 surface、未知 Skill provenance、紅刪／缺失不能 COMPLETE、
文字回退、不存在或未授權檔案拒絕。三個 Skill 的觸發文字與 fallback 最小規則另作靜態核對。
這些不是 ChatGPT/Claude/Gemini/其他平台真人實測；平台下載能力、歷史匯出、
模型遵守規則及法律／DOCX 品質均 NOT TESTED / UNVERIFIED。保留現有正式版 ZIP 的五個成員不變。
