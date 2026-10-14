# 自動驗證與 Beta Pre-release

本流程只驗證來源與封裝契約，不判斷法律正確性、真人模型行為或 DOCX 視覺品質。

## 分支策略與固定版本

- `main` 保持 GitHub 預設分支與穩定主線，供一般使用者讀取；正式發布準備的合併仍需真人測試與人工審查。
- `develop` 是下一版本開發與 Beta 整合主線；一般功能分支 `feature/*` 或 `feat/*` 從最新 develop 建立，PR base 必須選 develop。
- 一般開發 PR 不得指 main；只有維護者審查後的正式發布準備才送 develop → main。CI 同時驗證兩者，不以粗略分支名稱 guard 阻擋合法發布。

main 可有已核准的 CI／文件等非 Skill 工程內容，與 Latest 正式 Release 的快照不完全相同。
若要固定正式版本，請使用 [v0.1.3 Release](https://github.com/Clock1025/sa-legal-skills/releases/tag/v0.1.3)
附件或明確指定 [v0.1.3 Skill 路徑](https://github.com/Clock1025/sa-legal-skills/blob/v0.1.3/skills/regulation-review/SKILL.md)，
不要把可移動的 main 或 Latest 連結當成固定版本識別。

一般開發的操作範例（工作樹有修改時先妥善保存，不重設或丟棄）：

```bash
git fetch origin refs/heads/develop:refs/remotes/origin/develop
git switch -c feat/my-change origin/develop
# 修改並執行下列測試，commit 後：
git push -u origin feat/my-change
gh pr create --base develop
```

本 Issue 的 migration PR 先由使用者獨立審查，再人工合併至 develop。
Issue #5 / PR #6 已改 base develop，無需取消或重作；待這次 CI 調整合併後，
在 develop 基準上重新確認 PR #6 的差異與新 Actions run，不能沿用先前 main 的 PASS。
本 Issue 不合併 PR #6、不將其改回 main。

## PR CI 與本機開發

PR 指向 `main` 或 `develop`（包含 fork PR）以及 push 到這兩個分支會執行 `.github/workflows/ci.yml`。
CI 僅有 `contents: read`，不使用 `pull_request_target` 或 secrets，不發布任何 Release。
全新 checkout 僅需 Bash、Git、Python 3 標準庫，從 repository 根目錄執行：

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

驗證必要檔案、Skill name/description/heading、入口引用與唯一 canonical prompt 標題；
實際執行既有打包腳本，核對 ZIP 精確五個檔案、來源位元組、CRC 及解壓內容。
刪除前次 ZIP 後各自打包兩次，核對 SHA-256 一致。測試涵蓋缺 Skill、名稱或入口錯誤、
錯誤 ZIP 內容／檔案清單／格式、故障打包腳本、非法 tag、未合併 commit 及錯誤 checkout。
任何失敗皆 non-zero exit。ZIP 位於既有 ignored `sa-legal-skills.zip`；測試使用自動清理的暫存目錄。
Git 測試的 synthetic tags 只存在於暫存 Git fixture，不建立或推送專案版本 tag。

## Beta 前人工驗收

[驗收操作與矩陣](acceptance/model-regression.md)、[證據紀錄範本](acceptance/record-guide.md)及
[Beta 前清單](acceptance/beta-checklist.md)供維護者獨立驗收。離線檔案完整性／CI PASS 不等於真人模型或 DOCX 視覺 PASS。
這些是建議與證據管理，不新增自動發布閘門或授權；原有 workflow 不讀這些紀錄自動放行。
測試scope與限制接受、最終 Tag／Release 授權仍由使用者明確決定。

## Beta 發布閘門

經獨立審查合併到 develop、確認想測試的版本與人工驗收範圍後，維護者才另外授權建立 Beta tag。
Beta 必須取自包含本次新版 workflow 的 develop commit；main 上的舊 CI/CD 不由這個 PR 覆寫。
不必先將功能合併到 main。本次分支策略遷移不建立 tag、不發布 Beta、不修改正式 `v0.1.3`。
只接受 `v<major>.<minor>.<patch>-beta.<n>`，各數字不接受多餘前導零，例如 `v0.1.4-beta.1`。
不支援 `workflow_dispatch`，不自動生成 tag，不接受 rc 或 stable。

Beta tag push 觸發 `.github/workflows/beta-release.yml`。GitHub 的 tag glob 只是初步篩選；
read-only validation job 再以完整正規式拒絕非法名稱，確認 checkout HEAD 等於 tag commit、
且 commit 已在 `origin/develop` 可核對歷史，然後在該 commit 重跑上述兩個指令的全部檢查。
任何失敗都不進入 publish job。develop 歷史需完整，checkout 使用 `fetch-depth: 0` 取得完整歷史與遠端分支 refs。
缺少或無效的 `origin/develop` ref、shallow checkout 都明確 FAIL；不退回 main 或跳過 gate。

只有 publish job 使用 `contents: write`。它下載本次驗證產物，重驗 SHA-256，
使用既存 tag 建立明確 `--prerelease --latest=false` 的 Release。
Actions 使用內建 `GITHUB_TOKEN`，不需要另外提供個人 token。
同 tag 工作流以 concurrency 序列化；若 Release 已存在，明確 FAIL 並拒絕覆寫。
若 API 檢查失敗也停止，不把查詢錯誤誤認為 Release 不存在。
若建立 Release 或上傳附件中途失敗，需人工檢查及清理該 Beta Release 後再重跑；
不得刪改 stable Release。這是保守的失敗策略，不能把重跑拒絕當成成功。

建立 Beta tag 的步驟只供維護者在未來另行授權後操作，本次不執行：先 fetch 最新 develop，
選定已整合且包含新版 workflow 的 commit，人工確認版本名稱與測試範圍；建立
`vM.m.p-beta.n` tag 指向該 commit，再只推送該 tag。不要使用未整合 feature commit，
不要移動、刪除或覆寫既存版本 tag。tag push 才執行發布 workflow，分支 PR 不會發布。

## 人工正式發布與建議保護

真人模型測試、必要 DOCX 驗收及人工審查完成後，維護者才將 develop 中已核准內容
送 PR 合併到 main，另經人工授權建立正式版本 tag／Release。本流程不實作自動 stable release。
保留預設分支 main；現有 v0.1.3 tag、Release 與附件不動。

本 PR **未設定或驗證啟用** GitHub Rulesets、Branch Protection 或 Tag Protection。
上述 PR base 約定是流程約束，不是實質 GitHub 權限保護。
建議維護者另行檢閱設定：main/develop 要求 PR 審查與必要 CI、限制繞過與 force push，
main 限制未經審查的合併；版本 tag 限授權維護者建立並禁止移動／刪除。
設定 required checks 前確認 develop 新版 CI 已會執行，以免要求不存在的 check。
這些是手動設定建議，本次不要求 admin 權限或修改 security settings。

## 附件與失敗重跑

在 Actions 的 run/jobs 查看全部 validation 通過後，到 Releases 確認版本顯示 **Pre-release**，
沒有標為 Latest，附件包含 `sa-legal-skills.zip` 與 `SHA256SUMS.txt`。下載兩份到同一目錄後執行：

```bash
sha256sum --check SHA256SUMS.txt
```

預期 ZIP 內容固定為 START-HERE.md、LICENSE 與三份 `skills/<name>/SKILL.md`。
失敗時先閱讀該 job log，修正可重現問題。PR 修改後 push 會觸發新 CI；暫時性 runner 問題可在
Actions run 選 **Re-run failed jobs**。Beta 如需程式修正，先送 PR 至 develop 並經人工合併，再由維護者另行授權新 Beta tag；
不要移動既存 tag。驗證產物保存 7 天，逾期需重新執行完整 workflow。

Release Notes 明列 `AUTOMATED CHECKS: PASS` 與具體檢查，以及
`REAL-MODEL BEHAVIOR: NOT TESTED / UNVERIFIED`。
歷史 v0.1.3 的 5/5、17/17、31/31 不屬於這次 executable tests，也沒有被 Actions 重跑。
靜態或封裝 PASS 不代表模型、法律內容、DOCX 或字型／視覺品質 PASS。
穩定版仍需另外人工核准與發布，不由這套 workflow 建立。

實際 GitHub Release 建立、附件上傳、Latest 狀態及重跑拒絕行為在本次交付為
**NOT LIVE-TESTED**；未建立任何專案 Beta tag 或 Release。

## v0.1.4 Stable：手動發布（固定來源）

`.github/workflows/stable-release.yml` 僅接受 `workflow_dispatch`，且只允許在本 repository
的 `main` 執行；一般 push、PR 或 Tag 不會觸發。這是一次性 v0.1.4 發布機制，不接受任意版本輸入。
Beta workflow 的行為不變。

審查並合併發布機制 PR 後，維護者到 **Actions → v0.1.4 Stable Release (manual) → Run workflow**，
選擇 `main`，再手動執行。CLI 等效命令（本 PR 交付時尚未執行）：

```bash
gh workflow run stable-release.yml --repo Clock1025/sa-legal-skills --ref main
```

Workflow 程式與繁體中文說明取自觸發時的 main Commit；**Skill 套件與既有測試始終取自
`6aa5c775d8ea011ea4b2380ef467591a6966070a`**，不使用合併 Workflow 後的新 main 內容。
五個檔案固定不變，封裝沿用候選 Commit 的 `scripts/package-release.sh`／`validate.py`。
唯讀 validate job 執行候選的 115 項 unittest、發布工具離線安全測試，以及封裝驗證；
重新計算 SHA-256，必須符合
`ee933fe8fd06f50a6d7ea42d5a5164586cf08a825b1a3fb68d6f33c17a34152b`。
產物保存 7 天，publish job 重新核對固定來源、成員、CRC 與 checksum。

只有 publish job 取得 `contents: write`，以內建 `GITHUB_TOKEN` 建立固定 Commit 的 lightweight Tag
`v0.1.4`，先建立 Draft Release（非 Pre-release、非 Latest），上傳兩個附件並實際下載核對，
才將 Draft 公開且設為 Latest。公開後再次下載核對，確認 Latest、Tag 及既有 v0.1.3／RC Tag 未變。
不使用長期 Token、不 force push、不移動或覆寫 Tag。

任何同名 Tag 或 Release（包括草稿）都會保守停止，查詢權限錯誤不當作不存在。
上傳／草稿驗證失敗會留下 Tag 與未公開草稿供維護者檢查，不自動刪除、覆寫或續傳；
**不可直接重跑期待自動恢復**。先檢查 Actions 失敗步驟與 Releases 草稿，再另行決定處理方式。
公開後驗證若失敗，工作流回報失敗並保留現狀，不自動刪除已公開版本。

Release Notes 位於 `docs/releases/v0.1.4.md`，保留 CASE-05、C05 版面 PARTIAL／預設直式未模型複驗、
Microsoft Word 及完整真實案件端到端試用限制。程式／模擬測試成功不代表真人模型或法律品質驗收。
本機與 PR CI 可核對離線程式及安全測試；手動 Workflow、GitHub 草稿上傳、公開與下載流程在本次 PR
交付為 **NOT LIVE-TESTED**，必須等維護者審查合併後才執行。
