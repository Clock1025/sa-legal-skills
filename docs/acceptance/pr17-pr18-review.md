# PR #17／#18 工具比較與整併建議

讀取GitHub實際PR、程式、文件與測試，並在獨立/tmp快照跑封裝與完整unit；未合併或關閉任一PR。
比較固定HEAD：#17 `2873040dc39c9f3c5f922a3b4f1ee1a63956a578`；#18 `737e9f05a8e06499a848a5c6e7a37e1cfa2274b5`。
兩PR均OPEN、base=develop，GitHub CI均SUCCESS。本地#17為78/78，#18為91/91，封裝皆通過；測試數量本身不是品質結論。

**建議以 #18 的 acceptance_assistant.py 作唯一正式驗收整理CLI，吸收 #17 的有用功能後由維護者處理重複PR。**
本批DOCX分支只從develop開始，不引入任何一套驗收CLI，不把兩個入口都合進正式樹；PR採用／合併／關閉仍由維護者決定。

| 面向 | #17 acceptance_assist.py | #18 acceptance_assistant.py | 評估 |
| --- | --- | --- | --- |
| 來源與架構 | 載入目前工作目錄matrix/template；Commit只檢查40字元格式 | 由指定SHA讀canonical、Skill、矩陣、判準；配方與工具bytes另索引 | #18可重建候選材料，避免未提交或不同分支內容冒充指定版本 |
| 操作易用性 | 命令短，抽取steps引號作提示片段，明說不是完整prompt | 一／多案操作卡與逐輪輸入配方，含DOCX六fixture全文；setup仍需人工 | #18較能減少查找；成本是人工配方需隨矩陣維護。#17引號摘錄不可當完整可執行prompt |
| 證據處理 | 保留TXT/hash，所有TXT標PLATFORM_EXPORT；來源及呼叫由人工後填 | 原始BOM／CRLF不改，可宣告來源種類、輸入及Skill原檔；預設SELF_REPORTED，讀取不升FULL | #18更能區分來源未知、合成與原始匯出；仍無法證明平台真實性 |
| 防護 | 拒絕ID穿越、輸入／run symlink及重複bytes；root.resolve容許root是symlink，忽略壞JSON再去重 | 固定ignored目錄、拒絕父層symlink、匯入鎖、先核對既有hash/schema再去重；跳脫Markdown metadata | #18邊界較完整；仍非抗同帳號惡意並行改檔的安全隔離，鎖中斷後需處理 |
| 摘要 | 所有矩陣案例含未有run的NOT TESTED，另列壞紀錄，可新建output | 逐run的執行／判定與一致性分欄，可唯讀指定舊record，顯示版本／缺口 | #17未測case可見性值得吸收；#18保留舊紀錄位置較方便 |
| 維護 | 218行CLI、5項新測試；動作集中，配方較少 | 314行CLI、18項新測試；Git/temp fixture覆蓋更多，配方有維護成本 | 不靠行數判定；建議維護一套來源／匯入實作，避免修復與規則漂移分叉 |

## 建議吸收，先不在本DOCX PR改另一套工具

1. #17「所有未測case都出現在摘要」：加入 #18 的矩陣視圖，保留逐run與原判定，不以紀錄數當有效覆蓋。
2. #17 CI 的PR `git diff --check`：可另行納入既有CI，仍須核對完整fetch及base比較方式；不需第二套CLI。
3. #17 的實務案例之公布／公告／生效疑義、未確認電子送達：作補充材料，保留局部全文限制，不重複複製schema或命令。
4. 保留 #18 的候選SHA材料固定、來源分類、原始bytes與既有checker相容；輸入配方需標示版本適用性，未來可減少不必要的工具原碼副本。

## 核對發現與待處理

#17根目錄symlink、預設PLATFORM_EXPORT與摘要Markdown連結未完整跳脫，從原碼可見；既有五項測試未覆蓋這些邊界，不把未測情況寫成已重現模型FAIL。
#18摘要目前不列無run案例、配方讀工具版本而非候選版本；文件有揭露後者，需要維護者核對舊候選仍適用，不能自動視為候選規則改動。
兩套都不呼叫模型／自動判分；沒有底層工具日誌可列能力限制，不否定可觀察文字。原P0及歷史結果保持不變。
整併應只留下單一正式CLI與入口文件；舊紀錄直接沿用schema/checker，不刪原FAIL或為遷移重寫原始TXT。
