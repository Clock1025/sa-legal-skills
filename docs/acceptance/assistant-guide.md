# 半自動驗收：操作卡、TXT 匯入及摘要

使用 `scripts/acceptance_assistant.py`，沿用既有 matrix、run-template 與 `check_acceptance_evidence.check`。
只需 Python 標準庫與本機 Git；不連網、不要求 Key、不呼叫或判分模型、不發布。
所有產物固定寫入 ignored `test-output/acceptance/assistant/`；不提供對外上傳功能。

## 先產生操作卡

```bash
# 可選已發布候選；不是移動 Tag 或改寫該版本。
python3 scripts/acceptance_assistant.py prepare \
  --commit 0b6df14e99ba57bcadfe43ead5fe0f079ef36680 \
  --bundle-id beta1-round1 \
  --case P0-CASE-03 --case P0-CASE-05 --case C-DOCX
# 不指定 --case 就整理該候選矩陣全部21案，不代表完成84格。
```

產物在 `plans/<bundle-id>/`：每案 `model/` 有逐字抽出的 canonical prompt、依序的使用者輸入、原始 Skill；
`reviewer/操作與判準.md` 有矩陣原步驟、setup 條件及原案判準。`index.json` 記來源與實際 hash/size。
**不要把 reviewer、index 或整個包上傳模型。** 只依階段送指定 model 檔，不能一次餵入所有 Skill 或所有 turns。
先選當階段 Skill、完整讀取，再提供案件；切換才提供新 Skill，未讀 gate 案不得提前提供新 Skill。
八個 P0 判準直接讀候選原文件，不改寫原判準、示範答案或歷史結果。

`case-inputs.json` 是工具版本附帶的人工整理輸入配方，引用既有 case ID，不另建判定矩陣。
模型輸入不從 expected/forbidden 或 operator steps 自動猜出來，避免將「核對是否釐清」等判準送入模型。
配方不是候選 Skill 原文；候選矩陣／Skill／canonical／判準從 `git show <完整SHA>` 取得，連未提交的本機修改也不混入。
index 另記配方與工具實際 bytes，方便核對配方版本；候選矩陣改動後需人工核對配方仍適用。

P0-CASE-03/04 需要真正的前段模型方案；未取得指定setup時，記未達，不手寫assistant回覆補歷史。
CASE-02 匿名 Skill 不帶 Commit 給模型，來源 SHA 只在操作者索引。不同平台每案另開隔離對話。
C-DOCX 只展開既有六個虛構 fixture 的 new/old/reason 及段落階層，每子案一新對話；**不生成reference DOCX**。
未實際測試的案例仍 NOT TESTED；兩子案完成也不是六案全通過。

## 匯入實際取得的 UTF-8 TXT

```bash
python3 scripts/acceptance_assistant.py import-txt \
  --commit 0b6df14e99ba57bcadfe43ead5fe0f079ef36680 \
  --run-id chatgpt-case05-attempt01 --case P0-CASE-05 \
  --transcript /path/to/actual-export.txt \
  --platform ChatGPT --surface Chat --model 'UI顯示的模型名稱' \
  --origin PLATFORM_EXPORT --observed-call \
  --inputs /path/to/actual-user-inputs.txt \
  --skill large-scale-reform=/path/to/actually-supplied-skill.md
```

路徑與模型名稱是佔位，須換成實際資料。模型完整版本能核對才提供 `--model-version`，否則保留 UNVERIFIED。
`--origin PLATFORM_EXPORT` 是匯入者宣告真的平台匯出；原始平台TXT匯出才用 PLATFORM_EXPORT；手工另存且已核對的實際assistant原始輸出可用 MODEL_OUTPUT，來源不確定用預設 SELF_REPORTED。不得把模型自行聲稱或重建的逐字稿標為平台匯出。
`--observed-call` 僅在操作者已核對真實執行時使用，是宣告而非工具認證。
合成資料必須 `--origin SYNTHETIC`，不能宣告真人呼叫。未指定平台／模型也可保存，不自動否定已有可觀察文字。

工具保留 TXT 原始bytes（含 BOM、CRLF）、hash/size，在 `runs/<run-id>/` 建 record、sources-index 及 summary。
不依「User:」「ChatGPT:」等內容猜分角色，不推論 timestamp、完整性、對話ID、可見附件或失去的段落。
原始TXT先作帶行號範圍的混合逐字稿，**整檔不是已核對的assistant回合**；由驗證者標出實際input/output anchors。
`--inputs` 僅保存真實使用者輸入，不能用準備好的尚未送出提示詞代替；沒有該檔仍可匯入，記缺口。
`--skill` 保存實際提供的原始檔；bytes 與候選相同才記來源SHA，否則 UNVERIFIED。保存附件不代表完整讀取，read_status 保持 UNVERIFIED。
來源與平台名稱由匯入者提供，不以模型自述核實。來源未知的 TXT 仍可供初步觀察，不憑此填正式 PASS。

新匯入紀錄一律 NOT TESTED（待獨立判定），不自動增加覆蓋或改 PASS/FAIL。
已核對且宣告的呼叫可記 HUMAN_MODEL_RUN；「執行宣告」與「行為判定」在摘要分欄保留。
若已有可證明 FAIL，驗證者應保存該判定與具體anchor，不因其他範圍缺證而抹去；這個初始狀態不強迫人工清除已觀察的缺陷。
可見對話／平台UI等證據可支持可觀察行為判定，**底層工具日誌不是所有聊天行為的必要條件**。
但全文讀取、工具實際停用／呼叫、fresh isolation 等無法確認的部分仍列限制；「我已讀」不等於獨立讀取證據。

同名run不覆寫；相同TXT SHA-256在本工具runs內拒絕再次匯入，即使換run-id，避免重複算覆蓋。
不同內容的重跑用新ID，舊FAIL保留；同一原檔的多項觀察在原run補anchors，不假裝多個fresh測試。
匯入鎖防止同時重複登錄；若程序遭強制終止留 `.import.lock`，確認沒有匯入程序後才手動移除。
去重只限目前本地runs，換目錄、刪除原run或跨工具紀錄不保證全域去重。

## 人工判定後再檢查與彙整

依 [record guide](record-guide.md) 填來源／隔離／實際回合、verifier、basis、anchors及各項限制；
未知保留未知。維護者可在原始可見文字上辨識行為，不由模型自評或本工具替代獨立審查。
修正 record 時同步更新已補齊的 missing_evidence；不要改原始TXT／既有hash來消除差異。

```bash
python3 scripts/check_acceptance_evidence.py \
  test-output/acceptance/assistant/runs/chatgpt-case05-attempt01/record.json
python3 scripts/acceptance_assistant.py summary \
  > test-output/acceptance/assistant/summary.md
```

既有其他資料夾的run可用 `summary --record test-output/acceptance/my-run/record.json`（可重複選不同檔案），直接唯讀彙整，不要求重新匯入或移動原紀錄。

若需要一眼看到**指定候選仍無有效 run 的所有案例**，加上固定的候選 SHA：

```bash
python3 scripts/acceptance_assistant.py summary \
  --commit 0b6df14e99ba57bcadfe43ead5fe0f079ef36680
```

新增清單只列該 SHA 下沒有通過檔案一致性檢查的 run 紀錄之案例，不會將其他 SHA 的紀錄算進來，也不會把「有 run」自動視為已 PASS。已觀察但未裁定的行為維持 NOT TESTED；壞檔會顯示原始一致性錯誤，不覆蓋原判定。

摘要檢查每份record/hash，列案例、模型、執行／原規則狀態、檔案一致性、缺漏及人工待辦。
檔案竄改或schema錯誤列一致性FAIL，**不改寫原行為判定**；模型版本／底層日誌不足不自動變行為FAIL。
摘要不含原始對話正文；metadata／人工備註仍可能含敏感資訊，公開前仍須使用者授權及適當處理。
不用新核准流程：按既有判定證據記錄即可，風險建議見 [risk-review.md](risk-review.md)。

限制：不自動解析各平台TXT格式、不核實export真實性、不自動裁定FAIL/PASS或法律效果；
準備配方需要人工依setup操作，無法無人值守跑模型。沒有實際看DOCX頁面就 VISUAL QA: NOT TESTED。
本工具讀寫本地檔案，不能全面識別個資／hidden prompts；只匯入你有權處理的必要可見資料，不提交真實對話到公開Repo。
