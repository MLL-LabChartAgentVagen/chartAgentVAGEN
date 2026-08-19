# World_Inequality_Report_2026_p79

****表的形状完全正确**，4,000 个图元照样只对了一个点** · 数字读错了 · 该页 1 / 10 通过

![page](page.png)

## 这一页发生了什么

两个面板、9 条线、1800–2025，**4,000 个图元，一个数值都不写**。
解析器这次把表写成了长表：`Year | Panel | 九个地区`——**面板维进了表，正是 P2 想要的形状**。
十个点仍然只对了一个，剩下九个是数字本身落错了行或落错了列。

## 对流水线意味着什么

**这是唯一的反向证据：键写对了不等于能拿分。**
长表导出能解决 599 个「键对不上」，解决不了稠密度。两件事要分开验收——P3 / P2 看键，P1 / P5 看这一档的读数。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `25` | `Europe` · `1920` · `As % of regional GDP` | 0.1 | 数字读错了（表里是 30） | Value '25' not found in any table |
| **不通过** | `-25` | `North America & Oceania` · `2010` · `As % of regional GDP` | 0.1 | 读的是柱顶累计，不是这一段（表里是 -30） | Value '-25' not found in any table |
| **不通过** | `45` | `MENA` · `2010` · `As % of regional GDP` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (17, 2) missing labels: ['mena', '2010'] (data labels ['as % of regional gdp'] in table, title labels [] in cont |
| **不通过** | `40` | `East Asia` · `2010` · `As % of regional GDP` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (5, 7) missing labels: ['east asia', '2010'] (data labels ['as % of regional gdp'] in table, title labels [] in  |
| **不通过** | `-25` | `Sub-Saharan Africa` · `1980` · `As % of regional GDP` | 0.2 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (3, 3) missing labels: ['sub-saharan africa', '1980'] (data labels ['as % of regional gdp'] in table, title labe |
| **不通过** | `8` | `Europe` · `1920` · `As % of world GDP` | 0.2 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (3, 4) missing labels: ['europe', '1920', 'as % of world gdp'] (data labels [] in table, title labels [] in cont |
| **不通过** | `-5` | `North America & Oceania` · `2010` · `As % of world GDP` | 0.3 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (6, 5) missing labels: ['2010'] (data labels ['as % of world gdp'] in table, title labels ['north america & ocea |
| **不通过** | `9` | `East Asia` · `2010` · `As % of world GDP` | 0.05 | 数字读错了（表里是 12） | Value '9' not found in any table |
| 通过 | `8` | `North America & Oceania` · `1950` · `As % of world GDP` | 0.1 | — | Value '8' found with all labels at (12, 4) |
| **不通过** | `-4` | `South & Southeast Asia` · `1920` · `As % of world GDP` | 0.3 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (4, 5) missing labels: ['1920'] (data labels ['south & southeast asia', 'as % of world gdp'] in table, title lab |

## 解析器写下的整页 markdown

```markdown
Chapter 3. Regional Wealth Inequality

## Figure 3.4. Since the 1970s, North America &amp; Oceania has shifted into the largest net debtor

**Net foreign wealth across regions, 1800–2025**

**Net foreign assets, MER**

<table>
<thead>
<tr><th>Year</th><th>Panel</th><th>East Asia</th><th>Latin America</th><th>North America &amp; Oceania</th><th>South &amp; Southeast Asia</th><th>World</th><th>Europe</th><th>MENA</th><th>Russia &amp; Central Asia</th><th>Sub-Saharan Africa</th></tr>
</thead>
<tbody>
<tr><td>1800</td><td>As % of regional GDP</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td></tr>
<tr><td>1800</td><td>As % of world GDP</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td><td>0%</td></tr>
<tr><td>1830</td><td>As % of regional GDP</td><td>0%</td><td>-30%</td><td>10%</td><td>-30%</td><td>0%</td><td>30%</td><td>-30%</td><td>-20%</td><td>-30%</td></tr>
<tr><td>1830</td><td>As % of world GDP</td><td>0%</td><td>-1%</td><td>0%</td><td>-3%</td><td>0%</td><td>15%</td><td>-1%</td><td>-1%</td><td>-1%</td></tr>
<tr><td>1860</td><td>As % of regional GDP</td><td>-30%</td><td>-50%</td><td>-10%</td><td>-50%</td><td>0%</td><td>40%</td><td>-40%</td><td>-40%</td><td>-50%</td></tr>
<tr><td>1860</td><td>As % of world GDP</td><td>-1%</td><td>-2%</td><td>0%</td><td>-5%</td><td>0%</td><td>20%</td><td>-2%</td><td>-2%</td><td>-2%</td></tr>
<tr><td>1890</td><td>As % of regional GDP</td><td>-50%</td><td>-40%</td><td>-30%</td><td>-90%</td><td>0%</td><td>60%</td><td>-80%</td><td>-80%</td><td>-90%</td></tr>
<tr><td>1890</td><td>As % of world GDP</td><td>-2%</td><td>-2%</td><td>2%</td><td>-9%</td><td>0%</td><td>30%</td><td>-2%</td><td>-2%</td><td>-2%</td></tr>
<tr><td>1920</td><td>As % of regional GDP</td><td>-40%</td><td>-20%</td><td>10%</td><td>-80%</td><td>0%</td><td>20%</td><td>-20%</td><td>-100%</td><td>-100%</td></tr>
<tr><td>1920</td><td>As % of world GDP</td><td>-2%</td><td>-1%</td><td>5%</td><td>-7%</td><td>0%</td><td>5%</td><td>-2%</td><td>-2%</td><td>-2%</td></tr>
<tr><td>1950</td><td>As % of regional GDP</td><td>-20%</td><td>-20%</td><td>10%</td><td>-10%</td><td>0%</td><td>5%</td><td>-20%</td><td>0%</td><td>-10%</td></tr>
<tr><td>1950</td><td>As % of world GDP</td><td>-2%</td><td>-1%</td><td>8%</td><td>-1%</td><td>0%</td><td>1%</td><td>-2%</td><td>-1%</td><td>-1%</td></tr>
<tr><td>1980</td><td>As % of regional GDP</td><td>-10%</td><td>-30%</td><td>10%</td><td>-10%</td><td>0%</td><td>5%</td><td>-20%</td><td>-10%</td><td>-10%</td></tr>
<tr><td>1980</td><td>As % of world GDP</td><td>-1%</td><td>-1%</td><td>1%</td><td>0%</td><td>0%</td><td>1%</td><td>-1%</td><td>-1%</td><td>-1%</td></tr>
<tr><td>2010</td><td>As % of regional GDP</td><td>30%</td><td>-20%</td><td>-10%</td><td>-10%</td><td>0%</td><td>10%</td><td>40%</td><td>0%</td><td>-10%</td></tr>
<tr><td>2010</td><td>As % of world GDP</td><td>2%</td><td>-1%</td><td>0%</td><td>0%</td><td>0%</td><td>1%</td><td>0%</td><td>0%</td><td>-1%</td></tr>
<tr><td>2025</td><td>As % of regional GDP</td><td>50%</td><td>-30%</td><td>-60%</td><td>-10%</td><td>0%</td><td>30%</td><td>70%</td><td>0%</td><td>-10%</td></tr>
<tr><td>2025</td><td>As % of world GDP</td><td>12%</td><td>-2%</td><td>-18%</td><td>1%</td><td>0%</td><td>5%</td><td>4%</td><td>0%</td><td>-1%</td></tr>
</tbody>
</table>

### Net foreign assets, MER

**Left panel:** As % of regional GDP
**Right panel:** As % of world GDP

*Interpretation.* Between 1800 and 1914, Europe accumulated a rising share of global foreign assets. By 1914, its net foreign wealth reached 71% of its own GDP. These assets largely vanished after World War I. Measured as a share of world GDP, Europe’s foreign wealth in 1914 was about 6 times larger than East Asia’s foreign wealth in 2025 (12%) and about 18 times larger than that of MENA (4%). During the 20th century, North America &amp; Oceania emerged as a major foreign asset holder, peaking in 1950 at 8% of world GDP. Over the s
```
