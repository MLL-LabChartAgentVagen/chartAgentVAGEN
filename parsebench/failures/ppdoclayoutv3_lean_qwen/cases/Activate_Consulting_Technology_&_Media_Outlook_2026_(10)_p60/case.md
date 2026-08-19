# Activate_Consulting_Technology_&_Media_Outlook_2026_(10)_p60

****图上写 $101B，规则要 101**，多写一个 B 就全错** · 数字写在了错的量级上 · 该页 2 / 10 通过

![page](page.png)

## 这一页发生了什么

图题写着 `BILLIONS USD`，柱子上的标注写的是 `$101B`，而规则的值是 `101`。
解析器照抄了柱子上的标注 `$101B`——**看起来完全忠实**，但判分程序把后缀 `B` 读成 ×10⁹，于是 101 和 101,000,000,000 对不上，八个点判 0。
同一页两个 CAGR 百分点（16% / 10%）判对了，因为百分号不带量级。

## 对流水线意味着什么

**最通用的那个组件（单位只写在轴 / 图题里，149 / 192 页），造出来的失败恰恰是「解析器太老实」。**
对我们的导出：格子里只写和轴刻度同尺度的裸数字，量纲写进表头或表前的标题。
对训练数据：值和量纲必须是两个字段，不能拼成一个字符串。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `101` | `Rest of World` · `2019` | 0.01 | 数字写在了错的量级上（表里是 1.01e+11） | Value '101' not found in any table |
| **不通过** | `35` | `U.S.` · `2019` | 0.01 | 数字写在了错的量级上（表里是 3.5e+10） | Value '35' not found in any table |
| **不通过** | `121` | `Rest of World` · `2021` | 0.01 | 数字写在了错的量级上（表里是 1.21e+11） | Value '121' not found in any table |
| **不通过** | `48` | `U.S.` · `2021` | 0.01 | 数字写在了错的量级上（表里是 4.8e+10） | Value '48' not found in any table |
| **不通过** | `130` | `Rest of World` · `2025E` | 0.01 | 数字写在了错的量级上（表里是 1.3e+11） | Value '130' not found in any table |
| **不通过** | `50` | `U.S.` · `2025E` | 0.01 | 数字写在了错的量级上（表里是 5e+10） | Value '50' not found in any table |
| **不通过** | `155` | `Rest of World` · `2029E` | 0.01 | 数字写在了错的量级上（表里是 1.55e+11） | Value '155' not found in any table |
| **不通过** | `59` | `U.S.` · `2029E` | 0.01 | 数字写在了错的量级上（表里是 5.9e+10） | Value '59' not found in any table |
| 通过 | `16` | `2019-2021 CAGR` · `U.S.` | 0.01 | — | Value '16' found with all labels at (5, 1) |
| 通过 | `10` | `2019-2021 CAGR` · `Rest of World` | 0.01 | — | Value '10' found with all labels at (5, 2) |

## 解析器写下的整页 markdown

```markdown
**VIDEO GAMING**

# **We forecast that global consumer video game revenue will reach $214B by 2029**

## **CONSUMER VIDEO GAME REVENUE BY REGION<sup>1</sup>, GLOBAL, 2019 VS. 2021 VS. 2025E VS. 2029E, BILLIONS USD**

**ACTIVATE FORECAST**

<table><thead><tr><th>Year</th><th>U.S.</th><th>REST OF WORLD</th><th>Total</th></tr></thead><tbody><tr><td>2019</td><td>$35B</td><td>$101B</td><td>$136B</td></tr><tr><td>2021</td><td>$48B</td><td>$121B</td><td>$169B</td></tr><tr><td>2025E</td><td>$50B</td><td>$130B</td><td>$180B</td></tr><tr><td>2029E</td><td>$59B</td><td>$155B</td><td>$214B</td></tr><tr><td>2019-2021 CAGR:</td><td>16%</td><td>10%</td><td>11%</td></tr><tr><td>2021-2025E CAGR:</td><td>1%</td><td>2%</td><td>2%</td></tr><tr><td>2025E-2029E CAGR:</td><td>4%</td><td>4%</td><td>4%</td></tr></tbody></table>

1. Excludes hardware and device sales, augmented/virtual reality content, and advertising.
Sources: Activate analysis, Newzoo, Omdia, PricewaterhouseCoopers, Statista

activate consulting

1. Excludes hardware and device sales, augmented/virtual reality content, and advertising. Sources: Activate analysis, Newzoo, Omdia, PricewaterhouseCoopers, Statista

**59**
```
