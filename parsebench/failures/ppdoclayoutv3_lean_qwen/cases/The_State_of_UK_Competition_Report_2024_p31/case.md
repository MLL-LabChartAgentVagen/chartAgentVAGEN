# The_State_of_UK_Competition_Report_2024_p31

****刻度写的是 `.4` 不是 `0.4`**，整张图读大了 10 倍** · 数字写在了错的量级上 · 该页 0 / 9 通过

![page](page.png)

## 这一页发生了什么

横向系数点图（Stata 默认样式），系数轴的刻度标签是斜排的 `-.4  -.2  0  .2  .4  .6  .8  1`——**省掉了整数位的 0**。
解析器写下 4.4 / 1.5 / −1.6 / −2.3，真值是 0.45 / 0.15 / −0.2 / −0.25：**九个点整体差一个数量级，方向和相对大小全对。**

## 对流水线意味着什么

**刻度标签怎么写，直接决定读数的量级**，而风格向量里现在没有这一维。
P6 的「刻度格式」要细到：省不省前导零、标签斜不斜、负号是 `-` 还是 `−`。
另外这张图是横向系数点图（带误差棒），条件表里没有这一族。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `0.45` | `Berry ratio` · `Year FE` | 0.1 | 数字写在了错的量级上（表里是 4.4） | Value '0.45' not found in any table |
| **不通过** | `0.15` | `Berry ratio` · `+ Firm FE` | 0.1 | 数字写在了错的量级上（表里是 1.5） | Value '0.15' not found in any table |
| **不通过** | `0.05` | `Berry ratio` · `+ sales-weighted` | 0.1 | 数字读错了（表里是 0.8） | Value '0.05' not found in any table |
| **不通过** | `-0.2` | `Debt ratio` · `Year FE` | 0.1 | 数字读错了（表里是 -1.6） | Value '-0.2' not found in any table |
| **不通过** | `-0.25` | `Liquidity ratio` · `Year FE` | 0.1 | 数字写在了错的量级上（表里是 -2.3） | Value '-0.25' not found in any table |
| **不通过** | `-0.1` | `Liquidity ratio` · `+ Firm FE` | 0.1 | 数字读错了（表里是 -3.3） | Value '-0.1' not found in any table |
| **不通过** | `-0.15` | `Liquidity ratio` · `+ sales-weighted` | 0.1 | 数字读错了（表里是 -2.8） | Value '-0.15' not found in any table |
| **不通过** | `1.05` | `Labour share` · `Year FE` | 0.1 | 数字读错了（表里是 8.3） | Value '1.05' not found in any table |
| **不通过** | `0.32` | `Labour share` · `+ sales-weighted` | 0.1 | 数字读错了（表里是 2.8） | Value '0.32' not found in any table |

## 解析器写下的整页 markdown

```markdown
However, our primary data source does not contain balance sheet information that would allow us to replicate this analysis.

2.49 We have therefore conducted supplementary analysis using Bureau van Dijk's FAME dataset and the methodology that we used in the CMA's previous <u>State of Competition report (2022)</u>.

2.50 While our baseline methodological approach is more robust, Figure E.1 in the appendix shows that overall markup trends using this alternative data source and methodology are similar to our preferred baseline. Figure 13 below also shows that the relationship between markups and the labour share (which we can also calculate using FAME data) is comparable to what we find in our baseline data.

***Figure 13: Markups are consistently positively related to profits, overall debt, and the labour share, and negatively related to short-term liquidity***

*Regression coefficients of markups on Berry ratio, debt ratio, liquidity ratio and labour share under different model specifications. Controls include year fixed effects, firm fixed effects, and observations weighted by turnover. Data from Bureau van Dijk's FAME 2013-2023. UK*

<table>
<tr><th>Variable</th><th>Year FE</th><th>+ Firm FE</th><th>+ sales-weighted</th></tr>
<tr><td>Berry ratio</td><td>4.4</td><td>1.5</td><td>0.8</td></tr>
<tr><td>Debt ratio</td><td>-1.6</td><td>0.6</td><td>0.7</td></tr>
<tr><td>Liquidity ratio</td><td>-2.3</td><td>-3.3</td><td>-2.8</td></tr>
<tr><td>Labour share</td><td>8.3</td><td>3.0</td><td>2.8</td></tr>
</table>

Coefficient from markup regression

Year FE   + Firm FE   + sales-weighted

Coefficients from various regression specifications of markups on financial variables. Markup estimated using cost share method, with fixed assets. Calculations exclude Standard Industrial Classification (SIC) sectors: A, B, D, E, K, L, O, P, Q, T, U. Berry ratio = gross profit/operating expenses. Debt ratio = total liabilities/total assets. Liquidity ratio = current assets/current liabilities. Labour share = total remuneration/turnover. Data from *Bureau van Dijk's FAME* (2013-2023).

Coefficients from various regression specifications of markups on financial variables. Markup estimated using cost share method, with fixed assets. Calculations exclude Standard Industrial Classification (SIC) sectors: A, B, D, E, K, L, O, P, Q, T, U. Berry ratio = gross profit/operating expenses. Debt ratio = total liabilities/total assets. Liquidity ratio = current assets/current liabilities. Labour share = total remuneration/turnover. Data from *Bureau van Dijk's FAME* (2013–2023).

29
```
