# Student Association Legal Skills

本 repository 提供學生自治組織使用的法規審查與修法輔助 Agent Skills。核心分工是：人負責制度與政策選擇；AI 協助整理想法、檢查漏洞與連動影響，並轉寫為正式法規文字及提案文件。

## Skills

- **`regulation-review`**：審查現行法規、制度、程序或行為。核實適用規範與有效版本，分析位階衝突、權限、程序、法律時點及條文一致性，並依據資料說明結論與不確定之處。
- **`amendment-drafting`**：在制度方向已確認或足以草擬時，製作修正、制定或刪除條文、案由、修正總說明、修正條文對照表、提案 Email 草稿，並在執行環境支援時產生可編輯 DOCX。
- **`large-scale-reform`**：管理整部章程、組織法規或多個相連制度的大規模改革；整理制度架構與問題、追蹤決策狀態、保留決策紀錄、處理暫緩事項及法規連動，再將已足夠明確的部分交由 `amendment-drafting`。

## 典型組合

`large-scale-reform` → `regulation-review` → `amendment-drafting`

以上是可搭配的典型組合，不是強制或固定流程：

- 單純法規審查可以只使用 `regulation-review`。
- 小型且制度方向已定的修法可以直接使用 `amendment-drafting`。
- 大型改革或仍有大量制度未決問題時，使用 `large-scale-reform` 管理制度分析、決策及議題；可視需要搭配 `regulation-review` 審查特定現行規則或行為。
- 大型改革中，已充分確認的制度部分可以逐部分交由 `amendment-drafting` 草擬，其他部分可繼續保持待決或暫緩。

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
