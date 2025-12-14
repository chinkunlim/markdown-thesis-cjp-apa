import os
import re
import subprocess
import sys

# --- 設定 ---
SOURCE_MD = "paper.md"
OUTPUT_DIR = "sections"
METADATA_FILE = os.path.join(OUTPUT_DIR, "metadata.tex")
BODY_FILE = os.path.join(OUTPUT_DIR, "body.tex")
PANDOC_ARGS = ["-f", "markdown", "-t", "latex", "--biblatex"]

# 格式對應表
FORMAT_MAPPING = {
    "cjp": "main_cjp.tex",
    "apa": "main_apa.tex"
}

def ensure_dir(directory):
    if not os.path.exists(directory): os.makedirs(directory)

# === 1. 圖表語法轉換 (處理 [Fig_Note]) ===
def transform_figures(content):
    # Regex: 抓取 ![Title](Path){#Label} 下方的 [Fig_Note]
    pattern = re.compile(r'!\[(.*?)\]\((.*?)\)\{#(.*?)\}\s*\n\s*\[Fig_Note\]\s*(.*?)(?=\n|$)', re.MULTILINE)
    def replacer(match):
        # 轉換為 LaTeX figure 環境，強制標題在上方 (CJP規範)，註解在下方
        return (
            f"\n\\begin{{figure}}[htbp]\n"
            f"    \\centering\n"
            f"    \\caption{{{match.group(1)}}}\\label{{{match.group(3)}}}\n"
            f"    \\includegraphics[width=0.8\\textwidth]{{{match.group(2)}}}\n"
            f"    \\par\\raggedright\\footnotesize\n"
            f"    {match.group(4)}\n"
            f"\\end{{figure}}\n"
        )
    return pattern.sub(replacer, content)

# === 2. Metadata 解析 ===
def parse_yaml_to_latex(content):
    latex_lines = ["% Auto-generated metadata"]
    yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not yaml_match: return "", None
    yaml_block = yaml_match.group(1)
    
    # 抓取 output_format
    format_match = re.search(r'^output_format:\s*["\']?(.*?)["\']?\s*$', yaml_block, re.MULTILINE)
    target_format = format_match.group(1).strip().lower() if format_match else None

    # 抓取論文資訊
    mappings = [
        ("title_zh", "MyTitleZh"), ("title_en", "MyTitleEn"), ("short_title", "MyShortTitle"),
        ("author_zh", "MyAuthorZh"), ("author_en", "MyAuthorEn"),
        ("affiliation_zh", "MyAffiliationZh"), ("affiliation_en", "MyAffiliationEn"),
        ("keywords_zh", "MyKeywordsZh"), ("keywords_en", "MyKeywordsEn"),
    ]
    for key, cmd in mappings:
        match = re.search(rf'^{key}:\s*["\']?(.*?)["\']?\s*$', yaml_block, re.MULTILINE)
        val = match.group(1).strip() if match else ""
        latex_lines.append(f"\\newcommand\\{cmd}{{{val}}}")

    # 抓取多行摘要
    for lang in ["zh", "en"]:
        key = f"abstract_{lang}"
        cmd = f"MyAbstract{lang.capitalize()}"
        match = re.search(rf'^{key}:\s*\|\s*\n(.*?)(?=^\w+:|\Z)', yaml_block, re.DOTALL | re.MULTILINE)
        val = match.group(1).strip() if match else ""
        latex_lines.append(f"\\newcommand\\{cmd}{{{val}}}")

    return "\n".join(latex_lines), target_format

# === 3. 編譯 PDF ===
def compile_pdf(tex_file):
    print(f"\n🚀 正在編譯 PDF ({tex_file})...")
    # 使用 latexmk 自動處理編譯次數與文獻
    cmd = ["latexmk", "-xelatex", "-synctex=1", "-interaction=nonstopmode", "-file-line-error", "-pdf", tex_file]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 成功生成: {tex_file.replace('.tex', '.pdf')}")
    except Exception as e:
        print(f"❌ 編譯失敗: {e}")
        print("請確認已安裝 LaTeX 環境 (TeX Live/MacTeX) 且 latexmk 指令可用。")

def main():
    print(f"--- 讀取 {SOURCE_MD} ---")
    with open(SOURCE_MD, "r", encoding="utf-8") as f: full_content = f.read()

    ensure_dir(OUTPUT_DIR)

    # 1. 處理 Metadata
    latex_meta, target_format = parse_yaml_to_latex(full_content)
    with open(METADATA_FILE, "w", encoding="utf-8") as f: f.write(latex_meta)

    # 2. 預處理圖表
    processed_content = transform_figures(full_content)

    # 3. Pandoc 轉換內文
    print("轉換 Markdown 內文...")
    try:
        result = subprocess.run(["pandoc"] + PANDOC_ARGS, input=processed_content,
                                capture_output=True, text=True, encoding='utf-8', check=True)
        latex_body = result.stdout
    except Exception as e:
        print(f"Pandoc Error: {e}"); sys.exit(1)

    # 4. 切割章節 & 生成 body.tex
    pattern = re.compile(r'(\\section\{([^}]+)\}.*?)(?=\\section\{|$)', re.DOTALL)
    matches = pattern.findall(latex_body)
    
    body_content = []
    if not matches:
        with open(os.path.join(OUTPUT_DIR, "content.tex"), "w", encoding="utf-8") as f: f.write(latex_body)
        body_content.append(f"\\input{{sections/content}}")
    else:
        for content, title in matches:
            slug = re.sub(r'[^\w]', '_', title.lower().strip())
            fname = f"{slug}.tex"
            with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as f: f.write(content)
            body_content.append(f"\\input{{sections/{slug}}}")
    
    with open(BODY_FILE, "w", encoding="utf-8") as f: f.write("\n".join(body_content))

    # 5. 自動編譯
    if target_format and target_format in FORMAT_MAPPING:
        compile_pdf(FORMAT_MAPPING[target_format])
    else:
        print(f"⚠️ 未指定格式或格式錯誤 (目前設定: {target_format})，僅完成轉換。")

if __name__ == "__main__":
    main()