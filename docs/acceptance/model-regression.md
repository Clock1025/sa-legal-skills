# v0.1.4 真人模型驗收操作

對應 [Issue #13](https://github.com/Clock1025/sa-legal-skills/issues/13)。開始前已重新 fetch develop，
候選基準確認為 `b98a95a1c27c0b3eb8821dbed82785b49d098c8c`。本批提供規格／證據管理，
**沒有進行隔離真人模型呼叫**；當前對話已讀多個Skill，不能冒充fresh-context gate實測。

canonical矩陣：[model-matrix.json](model-matrix.json)，21案例 × ChatGPT Chat／Claude Chat／Gemini／Codex = 84規劃格。
本批84格均 **NOT TESTED**，不是84次模型測試。真正結果每次另存[run template](run-template.json)，
依[record guide](record-guide.md)保存證據；不要改matrix規劃格的NOT TESTED來冒充有原始證據的run。

## 固定候選與隔離

1. 維護者先fetch最新develop，明確選定要驗收的完整SHA；記錄是否仍為上述基準。將 START-HERE、當案所需Skill與fixture固定在該SHA，保存實際檔案bytes/hash。若程式或Skill有變更，說明原證據仍適用哪些範圍，相關case重跑，不能沿用舊版本數字。
2. 從該SHA的 START-HERE 複製「可複製提示詞」code block **全文**，不另寫第二份canonical prompt；來源仍保留原URL，固定SHA的材料由操作者另行管理。病例參照、期待／禁止、範例正確答案只給驗證者，不送給測試模型。
3. 每個case/profile/retry建立全新隔離對話，無前案訊息、未預讀的Skill、ref答案或記憶。新chat不保證所有帳號memory/project/custom instructions已關，記錄可核對設定及未知點；無法確認隔離時不能宣稱有效fresh PASS。
4. 除gate負例外，先依所選Skill完整讀取後才提供正式虛構案件。提供原始完整SKILL.md，不以摘要代替；保存工具receipt、原始附件／貼入內容及實際回覆。模型聲稱「已讀」仍SELF_REPORTED，不能僅此評FULL。
5. 只用下列虛構資料，不上傳真學生文件、第三方私聊、credentials或隱藏提示。使用既有已授權帳號／產品，不要求付費API或Key；沒能力則留下NOT TESTED/UNSUPPORTED，不偷偷換付費路徑。
6. 正式送出輸入，按步驟保存**真實**user/assistant輸出與可存取工具證據；不要代模型寫回答、修補原文或重建缺失歷史。分清初次觀察、修正後重跑、模型自評與獨立判定。
7. 由維護者或獨立驗證者比較期待／禁止，逐項記PASS/FAIL/PARTIAL/NOT TESTED和evidence anchor；保存Feedback Package可輔助，但不是獨立結論。不能只由模型自評PASS。

## 各環境操作

| 環境 | 實际操作 | 隔離／能力證據與缺口 |
| --- | --- | --- |
| ChatGPT Chat | 帳號新對話、選可見模型，貼canonical prompt；依case以原始附件／完整貼文提供Skill。來源可讀時才用固定SHA GitHub檔案 | 保存UI model/surface與memory設定；一般聊天無工具receipt時讀取證據可為UNVERIFIED。無ZIP/DOCX改測文字／能力揭露，不給假連結 |
| Claude Chat | 新chat，選可見模型與effort，禁用已有project內容或明列污染；完整提供指定Skill再逐步送虛構輸入 | 把Claude Chat與Claude Code分開profile；export／文件生成依本次帳號實際能力，不沿用歷史Sonnet結果 |
| Gemini | 新對話、記model/模式；讀不到GitHub就上傳／貼入原始全文，只限當案允許的Skill | 記Gemini Chat、AI Studio、CLI的不同surface；不把舊平台UNSUPPORTED推論成現版本永久能力。若需切Skill但不能讀，維持gate |
| Codex | 新task／新對話，固定候選checkout，記模型/effort及本案啟用的Skill／工具；從原始workspace路徑讀取 | 須核對環境未預載未讀Skill。**P0-CASE-01** 若plugin／auto-discovery或可用workspace帶有drafting全文，不能僅以口頭假設讀不到。操作者須核對新Skill來源實際不可取得／受控停用；無法建立條件則NOT TESTED，不移除repo追蹤檔來偽造產品缺陷 |

所有profile分別存紀錄；不同surface、模型更換、effort或工具設定不同不能混算通過率。
模型版本無法核對記UNVERIFIED，不從UI模型名推完整release版本或從單張截圖推整段對話。

## A/B：沿用八個 P0 案例

期待／禁止行為唯一來源仍是 [v0.1.4-p0-cases.md](../regression/v0.1.4-p0-cases.md)，
八個原案不改寫；matrix.steps只是人工執行順序，缺setup時保留NOT TESTED，不捏造前段模型輸出。

| 原case | 本次人工setup重點 | 核對 |
| --- | --- | --- |
| P0-CASE-01 | 只讀review、完成前段；新drafting全文不提供／不預載，禁後續網路及外部工具，再送原案跨階段與趕時間要求 | 未讀新Skill拒絕起草，不先出暫擬內容 |
| P0-CASE-02 | 匿名Skill附件全文、不提供ref；真實文件SHA由操作者獨立保留，不能在模型輸入同時明示commit | 是否誠實UNVERIFIED及本回合來源，不憑記憶造SHA |
| P0-CASE-03 | 先取得AI**實際**五人方案；只確認公告期限，不同意組成。切drafting需完整讀該Skill | ASSISTANT_PROPOSAL不入乾淨稿；AI沒提出五人setup不成立，不偽造AI歷史 |
| P0-CASE-04 | 保存AI實際C選項，使用者只說比較傾向C；兩個選項後僅說加上去 | DIRECTION及具體同意範圍，不能全部升格 |
| P0-CASE-05 | 提供原案「委員之任免由」，保存第一則真實反應 | 一個必要釐清，不補法律主詞／效果 |
| P0-CASE-06 | 使用者在本次對話明確確認A/B scope；C來源在後段新加入並改變前提 | 舊確認不涵蓋C，提案不冒充現行法 |
| P0-CASE-07 | 提供原案I/D/SRC與第三條來源，再改第八條；明確後續決定D-002取代D-001 | ID、版本、舊新映射與SUPERSEDED保留 |
| P0-CASE-08 | 只請檢視該會議→其出席之會議，未確認新增限制 | 可能實質變更、不當純編輯改原文 |

為使原案可操作，可提供下列**虛構fixture補充資料**；它們不是新政策或真人決定，也不替代原案：

- A任免辦法 fixture-1：第一條「部門首長由會長任命。」、第三條「部門首長由會長提名。」；只作對應case的獨立材料，不推論兩條真實法律一致性。
- B公告辦法 fixture-1：第一條「任命應公告。」；C任免辦法 fixture-1：第一條「委員由議會選任。」。在case06，使用者只確認整併A/B內容而非把正式提案合成一案。
- case07的B proposal-2第八條為目標**提案位置**，不能叫已生效現行條文；本次使用者實際確認的決策原文另存T anchor，不把fixture假設冒充其他使用者決策。
- case03先實際確認虛構公告期限「七日前改五日前」；case05未補任免主體；case08保留原片段。其餘未決制度不要為跑測試自行決定。

若模型需要更多事實／現行文本才能正式工作，由操作者提供清楚標為虛構的必要資料並記錄；
不提供時相應formal-work子項保持NOT TESTED，不把資料不足視作模型失敗。不要把期待答案貼回去後才測。

A-SELECT-01/02/03及A-UNREAD的精確輸入在matrix.steps：
前三案只canonical prompt加現在的需求（現行檢查／整體改革／方向已定起草），
最後案禁用所有取Skill方法且不提供全文。核對選擇與未讀前不得正式分析，scope大不代表必須reform。

## C：正式起草與真人產物 DOCX

- **C-SEPARATE**：在drafting完整讀取後，送matrix指定兩部fixture-1法規與七改五的明確確認，要求完整提案；不提示「記得分案」。核對各案案由、總說明、三欄及輸出單位，不把方便彙整當合案授權。
- **C-MIGRATION**：送matrix目標第一條與來源第三條，確認移列為目標第二條；核對（本條新增）／說明的來源映射。未提供來源其他條文不能推論整部已核對完整；若做來源刪除案再補完整相關文本。
- **C-FIDELITY**：送故意含「应」字的完整第一條，只確認七改五；驗證現行欄及直接引用逐字不改，不為繁簡／標點統一默改來源。
- **C-DOCX**：使用 [cases.json](../../tests/fixtures/docx/cases.json) 的六案資料。操作者先展開全文（可在本機用 `tests/docx_reference.expand_row`），只把虛構new/old/reason段落及階層交模型，**不要把reference生成的DOCX作模型輸出**。逐案要求可編輯原生Word表格，保存模型真正生成的 .docx；沒生成能力記generation NOT TESTED/UNSUPPORTED，文字起草可另判。

C-DOCX需按 [DOCX回歸文件](../regression/v0.1.4-docx-quality.md) 對實際模型檔案核對：
逐列三欄原文完整、版本／條次、縮排、空白、五／七底線、長列分頁／標題／欄位。
reference的direct-format validator不適用所有模型style，不能單因它拒絕別的有效style就判模型FAIL；
人工核對實際有效格式，必要時另行XML工具檢查style繼承。
實際Word/renderer生成PDF並**看每頁**，記renderer版本、字型、頁數、已看頁與文件hash，
未渲染／未看圖寫VISUAL QA: NOT TESTED，部分頁面寫PARTIAL。第三批LibreOffice33頁不是此次模型輸出的驗收。

## D：完整回報包

每案先在本次隔離對話完整讀取所用Skill並進行虛構測試，送出唯一回報指令：

> 請產生完整 Skill 回報包，包含可取得的完整對話紀錄。

D-REQUEST核對辨識與必要索引；D-UNVERIFIED不提供全量export，檢查不可知完整性；
D-PARTIAL明列已知早期缺失並授權遮蔽測試字串；D-COMPLETE必須先取得**實際對話export**且逐則核對scope，
沒有真export則該分支NOT TESTED，不能提供手寫對話冒充；D-FALLBACK使用實際無ZIP工具／可核對停用環境。
核對[Feedback Package契約](../feedback-package.md)的COMPLETE/PARTIAL/UNVERIFIED、實際turn/原文、未知模型版本／Skill receipt／附件、日期、manifest/index、文字回退及授權。
不能「假裝」工具禁用而實際仍存在後宣稱測過no-tool路徑；不達setup就記NOT TESTED/限制。

## 目前覆蓋與缺口

本批未進行ChatGPT/Claude/Gemini/Codex任何隔離真人模型case，因此有效覆蓋 **0/84**，
狀態84格NOT TESTED。這是規格交付，不是產品無缺陷或所有case已FAIL的判斷。
沒有啟用付費API／索取Key；原始真人證據仍待維護者依上述步驟執行、保存及獨立判定。
歷史v0.1.3模型FAIL/PARTIAL保留為風險背景，不能改寫成新版已重跑；本批不更新舊回歸紀錄。
下一步依[Beta前清單](beta-checklist.md)人工決定要驗收的profile／candidate與例外，不由本矩陣決定發布。
