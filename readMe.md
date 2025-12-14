# Markdown 自動化論文寫作系統 (CJP & APA)

這是一個基於 **Markdown** 的自動化學術寫作流程。透過 Python 腳本與 LaTeX 模版，實現「單一寫作來源 (`paper.md`)」，並一鍵編譯成符合 **《中華心理學刊》(CJP)** 或 **APA 7th** 格式的 PDF 論文。

## ✨ 特色 (Features)

* **單一來源**：只需維護一份 `paper.md`，無需手動調整 Word 格式。
* **雙格式輸出**：支援一鍵切換 CJP (中文期刊) 與 APA (國際期刊) 格式。
* **自動化編號**：圖片 (`Figure X`) 與表格 (`Table X`) 自動分離編號。
* **學術規範**：支援三線表、APA 文獻引用 (Biber)、自動目錄生成。
* **macOS 優化**：針對 macOS 環境 (MiKTeX + XeLaTeX) 進行最佳化設定。

## 🛠 系統需求 (Prerequisites)

本專案主要在 macOS 環境下開發與測試。使用前請確保安裝以下工具：

1.  **Python 3.x**
2.  **Pandoc** (文件轉換核心)
    * 建議下載官方安裝檔 (.pkg) 安裝。
3.  **MiKTeX** (LaTeX 發行版)
    * 需安裝 `latexmk` 與 `xecjk` 等套件 (首次執行會自動詢問安裝)。
    * 需在 MiKTeX Console 完成 "Finish Private Setup"。
4.  **VS Code** (建議編輯器)
    * 建議安裝 `LaTeX Workshop` 擴充套件。

## ⚙️ 安裝與設定 (Installation)

1.  **複製專案 (Clone)**
    ```bash
    git clone [https://github.com/您的帳號/markdown-thesis-cjp-apa.git](https://github.com/您的帳號/markdown-thesis-cjp-apa.git)
    cd markdown-thesis-cjp-apa
    ```

2.  **配置路徑 (關鍵步驟！)**
    打開 `split_sections.py`，根據您的電腦環境修改頂部的路徑設定：
    ```python
    # split_sections.py 頂部
    PANDOC_PATH = "/usr/local/bin/pandoc"        # 您的 Pandoc 路徑
    BIN_DIR = "/Users/您的使用者名稱/bin"          # 您的 MiKTeX bin 路徑
    ```
    * *提示：可在終端機使用 `which pandoc` 或 `which latexmk` 查詢路徑。*

3.  **字體設定 (Font)**
    本專案預設使用 macOS 內建的 **「PingFang TC (蘋方體)」**。
    * 若在 Windows 執行，請至 `cjpsych.sty` 與 `main_apa.tex` 修改為 `PMingLiU` 或其他系統字體。

## 🚀 使用方法 (Usage)

### 1. 撰寫論文
打開 **`paper.md`** 開始寫作。
* **檔頭設定 (YAML)**：設定標題、作者、摘要、關鍵詞。
* **圖片插入**：
    ```markdown
    ![圖片標題](Figure/img.png){#fig:label}
    [Fig_Note] 註：這裡是圖片下方的註解。
    ```
* **表格插入**：建議直接使用 LaTeX 三線表語法以獲得最佳效果。

### 2. 切換輸出格式
在 `paper.md` 的第一行設定 `output_format`：

* **輸出中華心理學刊格式**：
    ```yaml
    output_format: "cjp"
    ```
* **輸出 APA 7th 格式**：
    ```yaml
    output_format: "apa"
    ```

### 3. 一鍵編譯 (Build)
在 VS Code 中：
1.  按下快捷鍵 **`Ctrl + Shift + B`** (執行預設建置工作)。
2.  觀察終端機輸出，等待顯示 `✅ 成功生成: main_cjp.pdf`。

*(首次執行時，MiKTeX 可能會跳出視窗要求安裝套件，請全部按 Install。)*

## 📂 檔案結構 (File Structure)

```text
.
├── paper.md              # [核心] 唯一的寫作檔案
├── split_sections.py     # [引擎] 自動化處理腳本 (含路徑設定)
├── cjpsych.sty           # [樣式] 中華心理學刊樣式定義
├── main_cjp.tex          # [模版] CJP LaTeX 主檔
├── main_apa.tex          # [模版] APA LaTeX 主檔
├── references.bib        # [資料] 參考文獻資料庫
├── Figure/               # [資料] 圖片存放區
└── sections/             # [自動生成] 切割後的章節 (勿手動修改)