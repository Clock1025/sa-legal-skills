# Beta 前驗收清單（建議，不是發布授權）

本清單為維護者建議判準，最終scope、限制接受與是否發布由使用者決定。
**不新增發布機制、不自動讀本清單放行或建立Tag。** 沿用 [ci-cd.md](../ci-cd.md) 的既有Beta workflow：
完整合法既存Beta tag、checkout=tag commit、完整origin/develop歷史、來源/封裝/全部unit通過，
才由publish job建Pre-release且Latest=false、拒絕覆寫。人工清單並非GitHub技術權限guard。

每次候選記：完整SHA、profile/surface/model/effort/工具能力、操作範圍、run IDs、
已驗證/未驗證/例外、使用者最終決定（PENDING或真正明確授權），不得因CI成功推定授權。

## 自動 CI 項目

- [ ] 候選PR指develop，該head的實際Actions run完成SUCCESS，紀錄URL/SHA；不沿用別commit／舊main run。
- [ ] scripts/validate.py、全部unit、git diff --check通過；正式ZIP固定五成員及bytes/CRC/獨立雙次hash。
- [ ] P0/Feedback/DOCX參考契約測試仍可執行；靜態/模擬/reference結果分開，不記為模型或visual PASS。
- [ ] 維持三Skill/START-HERE gate、沒有main修改或另一套發布流程。

## 必須真人模型與人工證據

- [ ] 先由維護者決定本Beta要宣稱支援／推薦的profile集合；[21案矩陣](model-regression.md)逐格實際執行，
  未測平台不宣稱已驗。建議每個宣稱profile至少一輪有效fresh-context；高風險gate/決策案再獨立fresh重複一輪，兩次分run，不承諾兩次代表普遍成功。
- [ ] A讀取/gate/版本與八個P0、C分案/移列/原文、D回報/完整性/無ZIP分支都有原始輸入/輸出、實際模型呼叫及可核對來源。
- [ ] 狀態、verifier、依據與evidence anchors清楚；NOT TESTED不當PASS；FAIL不被其他通過項目抵銷。
- [ ] 完整性／紅刪／敏感資料最小必要、附件授權人工確認；離線checker不證明真實性。

## DOCX／視覺人工項目

- [ ] 對本次**模型實際產物**核對各欄原文、說明／版本、縮排與底線，不以reference檔替代。
- [ ] 在要宣稱的renderer/font組合實際生成PDF/頁面並查看；記所有已看頁、長列續頁、標題、欄位、溢出及字型。
- [ ] 未看的頁面／Word／平台保持NOT TESTED，局部PARTIAL；第三批的reference LibreOffice記錄不能當本次模型visual結果。

## 可明確揭露的限制（仍需使用者接受）

- 非目標profile未測、模型版本UI僅有限資訊、特定平台無DOCX／ZIP工具但誠實文字回退。
- 未完成Word／正式楷體／跨平台一致性、部分style繼承、未做每字視覺核對；不得宣稱相關能力PASS。
- prompt-only gate為規範沒有runtime guarantee；歷史模型差異保留，不能由靜態PASS推一般成功率。
- 完整原始證據受平台export能力限制；如缺核心判定證據不是可偷偷接受的PASS，列待補／scope受限。

## 建議阻擋 Beta 的重大問題

- 可重現的未讀Skill正式/暫擬工作、捏造來源或版本、未確認政策升格、範圍擴張、原文改寫／遺失，且影響本Beta宣稱scope。
- 發布工序越過develop/Tag/read-write邊界、改stable/Latest、ZIP源內容不一致、必要CI失敗。
- 可證明的真人DOCX遺失/截斷/錯欄/版本混用，或把有缺失／紅刪回報造為完整；用造假證據做放行。
- 宣稱已驗profile的核心真人證據／必要視覺項目未完成，沒有清楚的scope縮限與使用者決定。

以上是**建議判準**，不是新增政策決定或新CI gate。若使用者決定接受已知問題，
保存明確決定、範圍、風險與Release Notes措辭，不默默把FAIL改PASS；必要時縮限宣稱scope。
重大問題與例外由獨立審查／使用者判定，不由程式或助手發布。

## 本批結論

- 原始基準：b98a95a1c27c0b3eb8821dbed82785b49d098c8c；準備文件/工具本身待PR審查。
- 真人覆蓋0/84，全部NOT TESTED；本批未驗模型DOCX頁面，VISUAL QA: NOT TESTED（第三批reference紀錄不重命名）。
- 沒有新真人證據足以確認或排除v0.1.4重大行為問題；歷史v0.1.3 gate FAIL不是本批新版重測結論。
- **待人工驗收與發布決定；不能聲稱已可放行。** 建議若尚未完成宣稱scope的核心真人證據，暫緩Beta。
- 本批不Merge、不修改main、不建立v0.1.4-beta.1、不發布Pre-release/Stable。
