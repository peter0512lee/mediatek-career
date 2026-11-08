# Engineering Fieldnotes

給 AI Software 背景工程師的 Modem 學習知識庫。繁體中文，從系統背景走向 C、Binary Logging 與除錯。

網站：[Engineering Fieldnotes](https://peter0512lee.github.io/mediatek-career/)

## 完整學習路線

1. **Modem 基礎**（`index.html`）：AP / Modem、UE / RAN / Core、協定分層、5G SA 概念流程、名詞搜尋。
2. **C 與記憶體**（`c-memory.html`）：編譯、pointer / length、ownership、生命週期、endianness、alignment、並行邊界、copy 實驗。
3. **Binary Logging**（`binary-logging.html`）：教學格式 LG v1、互動 hex decoder、stream parsing、ring buffer、版本與時間。
4. **Debugging 實作**（`debugging.html`）：證據與假設、排查矩陣、LLDB、sanitizers、錯誤注入與分析案例。

每篇附公開來源、查核日期、實作與自我檢查。進度儲存在瀏覽器 localStorage，各章獨立。純靜態頁面，不傳送練習輸入。

## 內容範圍與正確性

- 個人學習筆記，非 MediaTek 官方文件。不收錄內部程式碼、文件或 log。
- ICD、MDM、MTF、DHL 的內部定義未確認，不猜測對應關係。
- C 教材以 C11 為基準，使用 WG14 N1570 公開草案核對語言規則；另參考 LLVM、GCC、Linux、FreeRTOS 與 Zephyr 官方資料。
- LG v1 是自訂練習格式，不相容於任何廠商 modem trace；沒有 checksum、壓縮或 crash-durability 保證。
- Ring buffer 為單執行緒模型，不是可直接移植的 lock-free 實作。Host 測試不代表 firmware、ISR、DMA 或硬體效能已驗證。
- 3GPP Release 16 用於基礎架構學習，實際平台與規範版本須另確認。

## 編輯與預覽

無第三方 build 依賴。Python 3.9+ 與 Node.js 用於檢查，Clang 用於 C 練習。

```bash
python3 tools/build_site.py
python3 tools/check_site.py
node tools/test_labs.cjs
python3 -m http.server 8000
```

瀏覽 http://localhost:8000 。也可直接開啟 `index.html`；file URL 的進度儲存行為依瀏覽器而異。

- `content/modem.html`：第一篇原始頁面；build 會換成共用章節導覽。
- `content/c-memory.html`、`content/binary-logging.html`、`content/debugging.html`：各章正文。
- `tools/build_site.py`：共用頁面模板與路徑；輸出四個根目錄 HTML。
- `assets/style.css`、`assets/app.js`、`assets/labs.js`：版面、進度、搜尋與互動練習。
- `examples/`：C 程式與黑箱測試；網站也提供下載。

請修改 `content/` 後重新產生根目錄 HTML，不要只修改產物。新增章節時同步更新 build script、link checker 與 workflow 的部署清單。

## 執行 C 練習

```bash
mkdir -p build
clang -std=c11 -Wall -Wextra -Wpedantic -Werror -g -O1 \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  examples/log_lab.c -o build/log_lab
./build/log_lab self-test
./build/log_lab generate build/sample.bin
./build/log_lab decode build/sample.bin
./build/log_lab ring
python3 examples/test_lab.py build/log_lab
```

預期兩筆資料：MEASUREMENT 4660、STATE 1。Ring 預期 produced=6、queued=4、dropped=2。

Memory 練習另編譯 `examples/memory_demo.c`。Sanitizer 支援依平台而異；若 runtime 無法啟動，可先省略 sanitizer 旗標做一般執行，再於支援環境檢查。CI 使用 Ubuntu + Clang ASan / UBSan；未通過驗證不部署。

測試涵蓋正常與串接資料、所有非空截斷前綴、大小邊界、未知 ID、錯誤 magic／版本／level／schema、sequence wrap、ring 滿空與環繞。它們不是任意輸入安全性或真實硬體相容性的證明。

## GitHub Pages

在 Settings → Pages 將 Source 設為 **GitHub Actions**。Push 至 `main` 會先執行網站與 C 範例驗證，再部署；PR 只驗證。Workflow 也可手動執行。

僅四個根目錄 HTML、`assets/` 與 `examples/` 會發布；不打包 `.git`、build 產物或整個 repo。所有內部路徑為相對路徑，支援 repository Pages 子路徑。
