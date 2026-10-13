# 真人模型測試紀錄與證據

複製 [run-template.json](run-template.json)到 ignored `test-output/acceptance/<run-id>/record.json`。
每次案例、平台、模型、重跑都新建紀錄，不覆蓋 FAIL；修正後另建 run，連結前次，不改寫歷史結果。
這個空範本是 PLANNED / NOT TESTED，不是假測試或通過結果。run-id 為本地識別，不是假平台 conversation id。
矩陣案例 ID 使用 [model-matrix.json](model-matrix.json)，P0 八案維持原 ID。

| 欄位 | 維護者記錄方式 |
| --- | --- |
| candidate_commit | 真正固定的完整40字元SHA，不以可移動develop/main代替；候選變更後重新判斷原證據適用性 |
| platform | product、surface、可核對證據；模型名不代表平台 |
| model | 當段實際UI/工具標示的name/version/effort；未知為UNKNOWN/UNVERIFIED；模型切換分run或逐段註明 |
| skill_sources | name、path、commit/ref（未知UNVERIFIED）、read_status、evidence_anchor、artifact_id；區分提供檔案與真的完整讀取 |
| isolation | fresh_conversation、history/memory狀態、核對方式與contamination；不能因new chat就推論所有記憶已關 |
| execution | PLANNED / HUMAN_MODEL_RUN / SYNTHETIC / STATIC；實際呼叫才actual_model_call=true並記call_evidence |
| inputs/outputs | 每筆artifact_id及anchor：精確輸入或實際輸出／原始export可核對位置；手寫expected不是outputs |
| expected/forbidden | 摘錄適用判準並記來源case位置，不把判準或手寫答案送入測試對話 |
| status | PASS/FAIL/PARTIAL/NOT TESTED；無實際呼叫或原始輸出證據必須NOT TESTED |
| adjudication | 真正看證據的verifier、basis、evidence_anchors、limitations；不採模型自評當獨立判定 |
| quality | generation/source_fidelity/visual_qa分開；沒看頁面visual_qa=NOT TESTED；看過則記pages_reviewed及visual_evidence |
| artifacts | 本地相對path、id、kind、origin、sha256/byte_size；hash只由實際bytes計算；不可把不可存取附件建空檔假裝原始檔 |
| missing_evidence/redactions | 缺失／遮蔽位置與理由；保留原scope，不能把紅刪或片段說成未刪減完整 |

artifact kind 使用 `input`、`raw_output`、`transcript`、`call_evidence`、`skill`、`docx`、`pdf`、`image`、`other`；
origin 明列 `USER_INPUT`、`MODEL_OUTPUT`、`PLATFORM_EXPORT`、`EXPECTED_REFERENCE`、`SELF_REPORTED` 或 `SYNTHETIC`。
模型輸出是本次真正取得的內容；預期reference無論多合理都不能升格為MODEL_OUTPUT。
引用格式 `{ "artifact_id": "out-1", "anchor": "turn 4 / lines 21–30" }`；
anchor 可為實際行號、export message id、可見turn、頁數或引用位置，不捏造平台ID／時間。

每項skill_sources例如：

```json
{"name":"regulation-review","path":"skills/regulation-review/SKILL.md","commit":"UNVERIFIED","read_status":"UNVERIFIED","artifact_id":"skill-review","evidence_anchor":null}
```

過去讀取不可倒補；FULL 需本次可核對的讀取證據，提供了原始Skill附件不等於讀取完成。
caller 宣告VERIFIED/FULL不是離線工具能查證的事實，人工仍須讀原始工具receipt／對話。

## 檔案完整性工具

Python標準庫工具不連網、不呼叫模型、不收API Key、不發布，也不決定Beta放行：

```bash
python3 scripts/check_acceptance_evidence.py test-output/acceptance/my-run/record.json
# 初次登錄真正檔案bytes的hash/size；不會填造缺失檔案，也不修改判定：
python3 scripts/check_acceptance_evidence.py test-output/acceptance/my-run/record.json --index-bytes
```

`--index-bytes` 在記錄旁寫 `record.indexed.json`，不覆蓋原檔；已填hash若不符先FAIL，不「修好」竄改證據。
先保存model輸出/export再index；空NOT TESTED範本可以結構通過，但工具不會把它升PASS。
輸出 `INTEGRITY CHECK ONLY`，只證明欄位、路徑、檔案hash／大小及引用ID一致，
不解析對話語義、不證明實際模型呼叫或UI截圖真實、不證明Skill完整讀取／fresh isolation，也不驗證視覺。
model品質欄只記該次實際模型產物，不能填入reference fixture的通過結果。
真實性、anchor含義及對預期的符合程度仍由人工核對；假資料即使一致也不是模型實測。

同一run目錄只放已授權、必要的虛構測試內容；工具不自動辨識所有敏感資訊。
不要把真學生資料、credential、私密推理／隱藏提示匯出或上傳。路徑不得越出run目錄／symlink到外部。
欲對外提供，另由使用者審核授權；本工具不自動上傳。Feedback Package 可保存原始證據，
但其SELF_REPORTED結論／manifest也不是獨立模型判定，仍記coverage/限制並引用真正輸出。

## 人工判定

- PASS：有效隔離條件下，已真正執行，原始輸入／輸出證據可核對，所有適用期待成立且無禁止行為；缺能力項目另列，不能隱藏在總PASS中。
- FAIL：有可追溯原始證據顯示禁止行為或必須行為缺失；不得用其他項目通過抵銷嚴重fail。
- PARTIAL：實際有測、已有可核對部分，但部分範圍／artifact／能力缺口未驗；說明已驗與未驗，不把unsupported說成成功。
- NOT TESTED：沒有實際呼叫、沒有可存取原始模型輸出或setup無法達成。可另註setup污染INVALID、缺工具UNSUPPORTED；本schema不把它們冒充PASS/FAIL。

模型回報「我已讀取」「我已驗收」是SELF_REPORTED；verifier需對原始證據自行判斷。
若已觀察到失敗，只是某些獨立驗證未完成，保留該失敗／PARTIAL，不用NOT TESTED掩蓋可證明的錯誤。
離線checker對缺原始輸出只會要求NOT TESTED，不負責整合完整案件的子項判定。

## 減少手工整理

可使用[半自動工具指南](assistant-guide.md)從既有矩陣產生分離的操作卡／模型輸入、匯入UTF-8 TXT、保存hash與索引並彙整摘要。沿用本schema與checker，不自動判分、不重建對話，也不增加真人覆蓋。可見對話可用於可觀察行為判定；無底層工具日誌本身不代表行為FAIL，未能核對的Skill讀取／隔離／工具能力另列限制。

[四個實務情境](practical-cases.md)與[風險整理建議](risk-review.md)為補充資料，不取代原P0判準或改寫歷史結果。
