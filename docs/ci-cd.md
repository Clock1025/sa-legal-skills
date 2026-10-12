# 自動驗證與 Beta Pre-release

本流程只驗證來源與封裝契約，不判斷法律正確性、真人模型行為或 DOCX 視覺品質。

## PR CI 與本機開發

PR 指向 `main`（包含 fork PR）以及 push 到 `main` 會執行 `.github/workflows/ci.yml`。
CI 僅有 `contents: read`，不使用 `pull_request_target`，不發布任何 Release。
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

## Beta 發布閘門

經獨立審查合併到 main、確認想測試的版本與人工驗收範圍後，維護者才另外授權建立 Beta tag。
本次 CI/CD 導入不建立 tag、不發布 Beta、不修改正式 `v0.1.3`。
只接受 `v<major>.<minor>.<patch>-beta.<n>`，各數字不接受多餘前導零，例如 `v0.1.4-beta.1`。
不支援 `workflow_dispatch`，不自動生成 tag，不接受 rc 或 stable。

Beta tag push 觸發 `.github/workflows/beta-release.yml`。GitHub 的 tag glob 只是初步篩選；
read-only validation job 再以完整正規式拒絕非法名稱，確認 checkout HEAD 等於 tag commit、
且 commit 已在 `origin/main` 歷史，然後在該 commit 重跑上述兩個指令的全部檢查。
任何失敗都不進入 publish job。main 歷史需完整，checkout 使用 `fetch-depth: 0`。

只有 publish job 使用 `contents: write`。它下載本次驗證產物，重驗 SHA-256，
使用既存 tag 建立明確 `--prerelease --latest=false` 的 Release。
Actions 使用內建 `GITHUB_TOKEN`，不需要另外提供個人 token。
同 tag 工作流以 concurrency 序列化；若 Release 已存在，明確 FAIL 並拒絕覆寫。
若 API 檢查失敗也停止，不把查詢錯誤誤認為 Release 不存在。
若建立 Release 或上傳附件中途失敗，需人工檢查及清理該 Beta Release 後再重跑；
不得刪改 stable Release。這是保守的失敗策略，不能把重跑拒絕當成成功。

## 附件與失敗重跑

在 Actions 的 run/jobs 查看全部 validation 通過後，到 Releases 確認版本顯示 **Pre-release**，
沒有標為 Latest，附件包含 `sa-legal-skills.zip` 與 `SHA256SUMS.txt`。下載兩份到同一目錄後執行：

```bash
sha256sum --check SHA256SUMS.txt
```

預期 ZIP 內容固定為 START-HERE.md、LICENSE 與三份 `skills/<name>/SKILL.md`。
失敗時先閱讀該 job log，修正可重現問題。PR 修改後 push 會觸發新 CI；暫時性 runner 問題可在
Actions run 選 **Re-run failed jobs**。Beta 如需程式修正，先送 PR 合併，再由維護者另行授權新 Beta tag；
不要移動既存 tag。驗證產物保存 7 天，逾期需重新執行完整 workflow。

Release Notes 明列 `AUTOMATED CHECKS: PASS` 與具體檢查，以及
`REAL-MODEL BEHAVIOR: NOT TESTED / UNVERIFIED`。
歷史 v0.1.3 的 5/5、17/17、31/31 不屬於這次 executable tests，也沒有被 Actions 重跑。
靜態或封裝 PASS 不代表模型、法律內容、DOCX 或字型／視覺品質 PASS。
穩定版仍需另外人工核准與發布，不由這套 workflow 建立。

實際 GitHub Release 建立、附件上傳、Latest 狀態及重跑拒絕行為在本次交付為
**NOT LIVE-TESTED**；未建立任何專案 Beta tag 或 Release。
