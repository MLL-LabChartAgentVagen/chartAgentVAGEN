# 失败样本分析

一个解析器在 ParseBench chart 分片上跑完之后，这里回答一个问题：**它剩下的失败是什么形态，据此生成流水线该多出什么能力**。归因用的六类形态定在 [../data/failure_cases/README.md](../data/failure_cases/README.md)。

与 [../reports/](../reports/INDEX.md) 的分工：那一份读的是**基准页面本身**长什么样（组件、类型、标题维度），一次跑 192 页，不涉及任何模型输出；这一份读的是**某个解析器在这些页面上失败在哪**，一次跑一整个运行目录。第二节把两者交叉起来——「哪种画法要付代价」只有把页面描述和失败结果放在一起才问得出来。**本目录不写 `../reports/` 下的任何文件。**

## 一个运行一个子目录

```
failures/
└── <运行名>/
    ├── INDEX.md      四节：失败形态 · 什么图更容易失败 · 翻成流水线改动 · 能不能信
    ├── view.html     同一份内容的图示版，每个案例配整页原图
    ├── cases/        逐页实例，一页一目录（page.png 是软链，不入库）
    └── assets/       view.html 读的降采样页面图（不入库，重跑即生成）
```

机读汇总写在 `../data/stats/failures_<运行名>.json`（入库），给 D 组的改造前后对比用。

## 加一个新运行

```bash
unzip -q <运行>.zip -x "__MACOSX/*" -d parsebench/data/runs/
python parsebench/tools/failures/analyze_failures.py --run <运行名>
```

`data/runs/<运行名>/chart/` 里要有 parse-bench 留下的 `<页面>.result.json` 与 `_evaluation_report.json`；页面 PNG 与 PDF 取自 `data/raw/` 与 `data/pages/`。不调模型，不重判分数，重跑是零成本的。

代码在 [../tools/failures/](../tools/failures/)：`run` 读运行目录 · `tables` 按度量的方式在输出里找格子 · `taxonomy` 给失败命名 · `profile` 与页面描述对齐 · `stats` 一次算完 · `index`/`viewer`/`cases` 渲染。
