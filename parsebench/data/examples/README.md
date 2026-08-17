# 代表页样例

放**人工挑出**的 ParseBench chart 页面，用于后续逐张分析。全量 568 页已经在 `../raw/docs/chart/`（PDF）与 `../pages/`（PNG），本目录只放需要重点看的那些。

## 放法

一页一个子目录，目录名用 PDF 的 stem：

```
examples/
  She-figures_p115/
    page.png            必需，页面渲染
    page.pdf            可选，从 ../raw/docs/chart/ 复制
    rules.json          可选，该页的抽查规则，见下
    notes.md            可选，人工观察
```

`rules.json` 由下面这条命令生成：

```bash
python - <<'EOF'
import json, sys
stem = "She-figures_p115"
rows = [json.loads(l) for l in open("parsebench/data/raw/chart.jsonl")]
hit = [r | {"rule": json.loads(r["rule"])} for r in rows if stem in r["pdf"]]
json.dump(hit, open(f"parsebench/data/examples/{stem}/rules.json", "w"), indent=2, ensure_ascii=False)
EOF
```

## 已在 review 中引用的页

这几页已经在 [../../review/03_chart_characteristics.md](../../review/03_chart_characteristics.md) 里作为实例引用，若要重点看先看它们：

| stem | 为什么 |
|---|---|
| `She-figures_p115` | 三键索引；44 类目 × 2 × 4 = 352 个分段的高稠密堆叠条 |
| `2023-05-sigma-01-english_p24` | 一页两张独立图表；两面板共享系列定义；单面板 49 时间刻度 × 3 折线；参考虚线带独立图例项 |
| `05021ff2-en_p19` | 一图内左右两面板量纲不同；右面板是零线居中的分叉条形图，含负值 |
| `(Web_version)_E-Government_Survey_2024_1392024_p101` | 6 个面板的小倍数版面；条内白字数值标签；面板名充当标签 |
| `P505350-59c98ca8-0803-4f23-b470-17f3dab010ab_p49` | 堆叠 + 分组同图；x 轴两级标签；窄分段的数值标签移到外部 |
