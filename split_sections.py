import os
import re
import subprocess
import sys

# ==========================================
# [設定區] 絕對路徑設定
# ==========================================

# 1. Pandoc 路徑
PANDOC_PATH = "/usr/local/bin/pandoc" 

# 2. MiKTeX 執行檔路徑 (都在您的 bin 資料夾下)
# 請確認這個路徑是正確的 (根據您之前的回報)
BIN_DIR = "/Users/limchinkun/bin"
LATEXMK_PATH = os.path.join(BIN_DIR, "latexmk")

# ==========================================

SOURCE_MD = "paper.md"
OUTPUT_DIR = "sections"
METADATA_FILE = os.path.join(OUTPUT_DIR, "metadata.tex")
BODY_FILE = os.path.join(OUTPUT_DIR, "body.tex")
PANDOC_ARGS = ["-f", "markdown", "-t", "latex", "--biblatex"]

FORMAT_MAPPING = {
    "cjp": "main_cjp.tex",
    "apa": "main_apa.tex"
}

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def transform_figures(content):
    pattern = re.compile(r'!\[(.*?)\]\((.*?)\)\{#(.*?)\}\s*\n\s*\[Fig_Note\]\s*(.*?)(?=\n|$)', re.MULTILINE)
    def replacer(match):
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

def parse_yaml_to_latex(content):
    latex_lines = ["% Auto-generated metadata"]
    yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not yaml_match: return "", None
    yaml_block = yaml_match.group(1)
    
    format_match = re.search(r'^output_format:\s*["\']?(.*?)["\']?\s*$', yaml_block, re.MULTILINE)
    target_format = format_match.group(1).strip().lower() if format_match else None

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

    for lang in ["zh", "en"]:
        key = f"abstract_{lang}"
        cmd = f"MyAbstract{lang.capitalize()}"
        match = re.search(rf'^{key}:\s*\|\s*\n(.*?)(?=^\w+:|\Z)', yaml_block, re.DOTALL | re.MULTILINE)
        val = match.group(1).strip() if match else ""
        latex_lines.append(f"\\newcommand\\{cmd}{{{val}}}")

    return "\n".join(latex_lines), target_format

def compile_pdf(tex_file):
    print(f"\n🚀 正在編譯 PDF ({tex_file})...")
    
    if not os.path.exists(LATEXMK_PATH):
        print(f"❌ 錯誤: 找不到 Latexmk。請確認 {LATEXMK_PATH} 存在。")
        return

    # [關鍵修正] 使用 -pdfxe 參數，這是 latexmk 指定使用 XeLaTeX 的標準方式
    cmd = [
        LATEXMK_PATH, 
        "-g",           # 強制重編
        "-pdfxe",       # <--- 重點：強制使用 XeLaTeX 引擎產生 PDF
        "-synctex=1", 
        "-interaction=nonstopmode", 
        "-file-line-error", 
        tex_file
    ]
    
    # [額外保險] 設定環境變數，確保 latexmk 找得到同資料夾下的 xelatex
    env = os.environ.copy()
    env["PATH"] = f"{BIN_DIR}:{env.get('PATH', '')}"

    try:
        subprocess.run(cmd, check=True, env=env)
        print(f"✅ 成功生成: {tex_file.replace('.tex', '.pdf')}")
    except Exception as e:
        print(f"❌ 編譯失敗: {e}")

def main():
    print(f"--- 讀取 {SOURCE_MD} ---")
    if not os.path.exists(SOURCE_MD):
        print(f"❌ 錯誤: 找不到 {SOURCE_MD}")
        sys.exit(1)

    with open(SOURCE_MD, "r", encoding="utf-8") as f:
        full_content = f.read()

    ensure_dir(OUTPUT_DIR)

    latex_meta, target_format = parse_yaml_to_latex(full_content)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        f.write(latex_meta)

    processed_content = transform_figures(full_content)

    print("轉換 Markdown 內文...")
    try:
        result = subprocess.run([PANDOC_PATH] + PANDOC_ARGS, input=processed_content,
                                capture_output=True, text=True, encoding='utf-8', check=True)
        latex_body = result.stdout
    except Exception as e:
        print(f"Pandoc 錯誤: {e}"); sys.exit(1)

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
    
    with open(BODY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(body_content))

    if target_format and target_format in FORMAT_MAPPING:
        compile_pdf(FORMAT_MAPPING[target_format])
    else:
        print(f"⚠️ 未指定格式或格式錯誤 (目前設定: {target_format})，僅完成轉換。")

if __name__ == "__main__":
    main()