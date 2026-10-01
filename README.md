# Student Association Legal Skills

本 repository 提供學生自治組織使用的法規審查與修法輔助 Agent Skills。核心分工是：人負責制度與政策選擇；AI 協助整理想法、檢查漏洞與連動影響，並轉寫為正式法規文字及提案文件。

## 安裝與使用

`sa-legal-skills` 是供 AI Agent 使用的一組 Agent Skills，不是獨立 App，也沒有需要執行的安裝程式。Skills 是指引文件；取得 repository 後，依你使用的 Agent 支援方式提供這些 Skill，並在對話中交代要處理的任務及相關法規資料。

### 方法一：Clone repository

```bash
git clone https://github.com/Clock1025/sa-legal-skills.git
cd sa-legal-skills
```

此 repository 的 owner 為 `Clock1025`。可在支援 Agent Skills 的環境中，依該環境的說明將 `skills/` 加入可使用的 Skills；也可以在測試對話中提供本 repository 路徑，並指定讀取相關 Skill 的 `SKILL.md`。各 Agent 的 Skills 安裝方式與自動載入行為不同，Clone repository 本身不會替 Agent 安裝或啟用 Skills。

### 方法二：GitHub Codespaces

1. 開啟本 repository。
2. 選擇 `Code`。
3. 選擇 `Codespaces`。
4. 建立新的 Codespace。
5. 在 workspace 中使用可讀取 repository 檔案的 AI Agent。

Codespaces 不是必要條件，只是方便使用 repository 的方式；也可以在本機 Clone 後，依 Agent 的支援方式使用 Skills。

### 開始測試

先提供要審查或修改的正式法規文本、版本及相關事實，再明確指定 Skill。

### 怎麼選 Skill

#### 想知道現在規定是什麼

使用 `regulation-review`，例如：

- 誰有某項權限？
- 有沒有期限？
- 某程序是否合法？
- 條文是否衝突？

#### 已經知道要怎麼改

使用 `amendment-drafting`，例如：

- 起草修正條文。
- 製作修正條文對照表。
- 撰寫案由與修正說明。
- 在執行環境支援時產生 DOCX。

重大政策仍未決時，不要要求 Agent 自行補完；可先用 `large-scale-reform` 整理選項與待決事項。

#### 還在設計整套制度

使用 `large-scale-reform`，例如：

- 全面修章。
- 行政、立法、評議制度改革。
- 任免、缺位、看守等連動制度。
- 需要追蹤已決與未決事項。

第一次測試可先從單一條文或一個制度問題開始。若 Agent 無法讀取 repository 路徑，請依該 Agent 的 Skills 說明安裝或提供對應的 `SKILL.md` 內容。不要只靠 AI 記憶重建現行法規；審查或製作對照表時，應提供可核對的正式文本及版本資訊。

### 提供文件時的建議

- 優先提供正式現行版本及其版本或生效資訊。
- PDF、DOCX、純文字均可；實際解析能力依 Agent 環境而定。
- PDF 若可使用工具，請確認實際頁數，並檢查是否有無法提取文字的頁面。
- 不要只因 Agent 自稱「已讀完整份文件」，就視為文件完整性已驗證。
- 若法規引用其他法規，最好一併提供相關文本。
- 不要要求 Agent 憑記憶重建現行條文。

## Skills

- **`regulation-review`**：審查現行法規、制度、程序或行為。核實適用規範與有效版本，分析位階衝突、權限、程序、法律時點及條文一致性，並依據資料說明結論與不確定之處。
- **`amendment-drafting`**：在制度方向已確認或足以草擬時，製作修正、制定或刪除條文、案由、修正總說明、修正條文對照表、提案 Email 草稿，並在執行環境支援時產生可編輯 DOCX。
- **`large-scale-reform`**：管理整部章程、組織法規或多個相連制度的大規模改革；整理制度架構與問題、追蹤決策狀態、保留決策紀錄、處理暫緩事項及法規連動，再將已足夠明確的部分交由 `amendment-drafting`。

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
