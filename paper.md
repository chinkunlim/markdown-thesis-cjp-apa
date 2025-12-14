---
# === 輸出設定 (Output Control) ===
# 選項: "cjp" (中華心理學刊) 或 "apa" (APA 7th)
output_format: "cjp"

# === 論文基本資訊 ===
title_zh: "自動化學術寫作流程之效率研究"
title_en: "Efficiency of Automated Academic Writing Workflows"
short_title: "Automated Writing"

# === 作者資訊 ===
author_zh: "王小明"
author_en: "Wang, Xiao-Ming"
affiliation_zh: "國立台灣大學心理學系"
affiliation_en: "Department of Psychology, National Taiwan University"

# === 摘要與關鍵詞 ===
abstract_zh: |
  本研究旨在探討 Markdown 轉 LaTeX 的自動化流程。
  結果顯示，此流程能有效解決格式切換的困擾。
keywords_zh: "自動化、LaTeX、學術寫作"

abstract_en: |
  This study investigates the automation workflow from Markdown to LaTeX.
  Results indicate significant efficiency improvements.
keywords_en: "Automation, LaTeX, Academic Writing"
---

# 緒論

這是第一章。自動化流程可以減少重複勞動 [@huang2005]。

# 方法

## 研究對象

本研究招募了 30 位受試者。

## 實驗材料 (圖片範例)

系統會自動編號為「圖 X」，且標題在上方。

![實驗流程示意圖](Figure/example.png){#fig:exp_flow}
[Fig_Note] 註：受試者需先完成前測。

# 結果

## 描述性統計 (表格範例)

表格會自動編號為「表 X」。建議使用 LaTeX 語法以符合三線表規範：

\begin{table}[htbp]
    \centering
    \caption{各組反應時間描述性統計} \label{tbl:rt_stats}
    \begin{tabular}{lcc}
        \toprule
        組別 & 平均數 ($M$) & 標準差 ($SD$) \\
        \midrule
        實驗組 & 450.2 & 35.1 \\
        控制組 & 510.5 & 42.8 \\
        \bottomrule
    \end{tabular}
    \par \raggedright \footnotesize
    \textit{註}：$N=60$。單位為毫秒 (ms)。
\end{table}

如表 \ref{tbl:rt_stats} 所示，實驗組反應較快。

# 討論

本研究證實了 Markdown 結合 Python 自動化的可行性。