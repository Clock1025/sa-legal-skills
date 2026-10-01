# 學生自治法規審查與修法 Skills

本 repository 提供學生自治組織使用的法規審查與修法輔助 Agent Skills。核心分工是：人負責制度與政策選擇；AI 協助整理想法、檢查漏洞與連動影響，並轉寫為正式法規文字及提案文件。

## 快速開始

不需要會 Git，也不需要執行安裝程式；可依 AI 的讀取能力選擇使用方式：

1. **最快：能讀取 GitHub 的 Agent。**提供 repository URL：https://github.com/Clock1025/sa-legal-skills，再指定 Skill 路徑，例如 `skills/regulation-review/SKILL.md`。Agent 應先實際讀取檔案；若無法讀取 GitHub 或該檔案，必須明確告知，不得宣稱已讀取。
2. **最通用：直接提供 `SKILL.md`。**取得需要的檔案，上傳或貼入 ChatGPT 或其他 AI，再提供法規文件與案件資料。
3. **長期／進階：**Clone repository、使用 GitHub Codespaces，或依 Agent 支援方式安裝到 Skills 目錄；詳見下方進階使用方式。

選擇 Skill：現行規定與合規問題用 `regulation-review`；整體制度設計及未決事項追蹤用 `large-scale-reform`；制度方向已定、要起草正式文件用 `amendment-drafting`。相關檔案見下方 Skills 說明。

可直接複製以下提示詞：

```text
請讀取 GitHub repository：
https://github.com/Clock1025/sa-legal-skills

以 skills/regulation-review/SKILL.md 為本次主要 Skill，
先完整閱讀其內容，再依照其中的工作流程與限制處理我接下來提供的案件。

不得依記憶重建現行法規，也不得自行補完未決制度政策。
若無法實際讀取該檔案，請明確告知，讓我提供 SKILL.md；
不要宣稱已讀取。
```

正式 Release 發布後，預計提供固定名稱為 `sa-legal-skills.zip` 的下載包。Release asset 尚未發布前，請直接從 repository 取得需要的 `SKILL.md`；目前不提供未驗證的固定下載連結。

## 進階使用方式

若想取得完整 repository，或在可讀取 workspace 的 Agent 環境中工作，可使用以下方式。Codespaces 不是必要條件。

### 方法一：Clone repository

```bash
git clone https://github.com/Clock1025/sa-legal-skills.git
cd sa-legal-skills
```

此 repository 的 owner 為 `Clock1025`。可在支援 Agent Skills 的環境中，依該環境的說明將 `skills/` 加入可使用的 Skills；也可以在對話中提供 repository 路徑，並指定讀取相關 Skill 的 `SKILL.md`。各 Agent 的 Skills 安裝方式與自動載入行為不同，Clone repository 本身不會替 Agent 安裝或啟用 Skills。

### 方法二：GitHub Codespaces

1. 開啟本 repository。
2. 選擇 `Code`。
3. 選擇 `Codespaces`。
4. 建立新的 Codespace。
5. 在 workspace 中使用可讀取 repository 檔案的 AI Agent。

Codespaces 不是必要條件，只是方便使用 repository 的方式；也可以在本機 Clone 後，依 Agent 的支援方式使用 Skills。

## 提供文件時的建議

- 優先提供正式現行版本及其版本或生效資訊。
- PDF、DOCX、純文字均可；實際解析能力依 Agent 環境而定。
- PDF 若可使用工具，請確認實際頁數，並檢查是否有無法提取文字的頁面。
- 不要只因 Agent 自稱「已讀完整份文件」，就視為文件完整性已驗證。
- 若法規引用其他法規，最好一併提供相關文本。
- 不要要求 Agent 憑記憶重建現行條文。

## Skills

- **[`regulation-review`](skills/regulation-review/SKILL.md)**：審查現行法規、制度、程序或行為。核實適用規範與有效版本，分析位階衝突、權限、程序、法律時點及條文一致性，並依據資料說明結論與不確定之處。
- **[`amendment-drafting`](skills/amendment-drafting/SKILL.md)**：在制度方向已確認或足以草擬時，製作修正、制定或刪除條文、案由、修正總說明、修正條文對照表、提案 Email 草稿，並在執行環境支援時產生可編輯 DOCX。
- **[`large-scale-reform`](skills/large-scale-reform/SKILL.md)**：管理整部章程、組織法規或多個相連制度的大規模改革；整理制度架構與問題、追蹤決策狀態、保留決策紀錄、處理暫緩事項及法規連動，再將已足夠明確的部分交由 `amendment-drafting`。

## 典型組合

```text
large-scale-reform
        ↓
regulation-review
        ↓
amendment-drafting
```

以上是可搭配的典型組合，不是強制或固定流程：

- 單純法規審查可以只使用 `regulation-review`。
- 小型且制度方向已定的修法可以直接使用 `amendment-drafting`。
- 大型改革或仍有大量制度未決問題時，使用 `large-scale-reform` 管理制度分析、決策及議題；可視需要搭配 `regulation-review` 審查特定現行規則或行為。
- 大型改革中，已充分確認的制度部分可以逐部分交由 `amendment-drafting` 草擬，其他部分可繼續保持待決或暫緩。

## DOCX 輸出

`amendment-drafting` 在執行環境支援 DOCX 產生時，可依需求提供：

- 可編輯的 Word 文字及 Word 原生表格。
- 固定欄序的修正條文對照表：`修正條文｜現行條文｜說明`。
- 真正的 Word underline formatting。
- 精確的法規結構位置：`條 → 項 → 款 → 目`。
- 整條新增時，現行條文欄填「（本條新增）」；整條刪除時，修正條文欄填「（刪除）」。這些標記本身不加底線。
- 有既有正式文件或機關範本時，沿用其格式；否則依環境可用字型選用標楷體、全字庫正楷體或繁體中文 fallback。

DOCX 能力與實際字型渲染依執行環境而定；字型來源與安裝方式見[正式文件字型](#正式文件字型)。

## 程序邊界

AI 可以分析、提出建議及草擬條文、提案文件與 Email 草稿；在執行環境支援時，可產生可編輯 DOCX。AI 不會代表使用者寄信、正式提案、簽署、公告或執行任免等制度行為，也不會宣稱議案已送件、通過或法規已公布、生效。制度與政策決定由人作成，未確認的 AI 建議不得當作使用者決定。

本專案目前只提供 Agent Skills，不包含正式資訊系統、MCP、Plugin 或後端服務。

## 正式文件字型

本專案不內附字型檔。若要產生或渲染本會慣用的楷體正式文件，可安裝「標楷體」或「全字庫正楷體」；全字庫官方字型名稱為「正楷體」。請只從[政府資料開放平臺 — CNS11643中文標準交換碼全字庫](https://data.gov.tw/dataset/5961)下載；該資料集頁提供「全字庫楷體字型檔」ZIP。請勿使用非官方鏡像、字型下載站或重新打包的檔案。

### Windows

1. 從[官方資料集頁](https://data.gov.tw/dataset/5961)下載「全字庫楷體字型檔」ZIP。
2. 解壓縮。
3. 找到其中的 `.ttf` 字型檔。
4. 選取字型檔，使用 Windows 的「安裝」或「為所有使用者安裝」。
5. 關閉並重新開啟 Word 或其他使用字型的應用程式。
6. 在 Word 或系統字型清單確認字型已出現。

### macOS

1. 從[官方資料集頁](https://data.gov.tw/dataset/5961)下載並解壓縮全字庫楷體字型 ZIP。
2. 開啟 `.ttf`。
3. 使用「字體簿（Font Book）」安裝。
4. 重新開啟使用字型的應用程式。
5. 確認系統可辨識該字型。

### Linux / Codespaces

不需要 root 權限，可安裝至使用者字型目錄：

```bash
mkdir -p ~/.local/share/fonts
# 將下載並解壓縮後的 .ttf 複製至 ~/.local/share/fonts/
fc-cache -f
fc-list | grep -i -E 'CNS|Kai|楷'
```

## 更新

若已 Clone repository，可在 repository 目錄中執行：

```bash
git pull
```

若 Agent 使用的是已複製到其他位置的 Skill 檔案，更新 repository 後也要依該 Agent 的使用方式重新載入或更新 Skill。

## 授權

本專案採用 [Mozilla Public License 2.0](LICENSE) 授權。
