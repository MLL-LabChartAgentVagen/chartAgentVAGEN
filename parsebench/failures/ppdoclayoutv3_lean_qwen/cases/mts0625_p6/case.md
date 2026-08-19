# mts0625_p6

****一页两张图都叫 Receipts**，不写图号就分不清是哪一张** · 有个键压根没写进表 · 该页 0 / 10 通过

![page](page.png)

## 这一页发生了什么

页面上是 Figure 3（月度）和 Figure 4（累计），两张图的系列名一模一样：`Receipts` / `Outlays` / `Deficit(-)/Surplus`。
所以规则用了**四个键**来定位一个值，第四个键就是 **`Figure 3.`**。
解析器把两张图合并成了一张表，没有图号这一列，十个点全判 0。

## 对流水线意味着什么

**「一页多图」和「图号进键」是同一件事的两面。**
只要一页上放两张系列名相同的图，图号就必须既画得出来、也导得进键。
P7 原本的判断是「图号基本不影响分数」（4,864 条规则里只有 14 条拿图号当键）——这一页就是那 14 条里的一整页，结论不变，但它说明这条路是通的。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `770` | `Receipts` · `Apr` · `2024` · `Figure 3.` | 0.05 | 有个键压根没写进表 | Value '770' not found in any table |
| **不通过** | `-560` | `Outlays` · `Apr` · `2024` · `Figure 3.` | 0.05 | 有个键压根没写进表 | Value '-560' not found in any table |
| **不通过** | `210` | `Deficit(-)/Surplus` · `Apr` · `2024` · `Figure 3.` | 0.1 | 有个键压根没写进表 | Value '210' not found in any table |
| **不通过** | `530` | `Receipts` · `Sep` · `2024` · `Figure 3.` | 0.05 | 有个键压根没写进表 | Value '530' not found in any table |
| **不通过** | `850` | `Receipts` · `Apr` · `2025` · `Figure 3.` | 0.05 | 有个键压根没写进表 | Value '850' not found in any table |
| **不通过** | `4890` | `Receipts` · `Sep` · `2024` · `Figure 4.` | 0.05 | 有个键压根没写进表 | Value '4890' not found in any table |
| **不通过** | `-6740` | `Outlays` · `Sep` · `2024` · `Figure 4.` | 0.05 | 有个键压根没写进表 | Value '-6740' not found in any table |
| **不通过** | `-1850` | `Deficit(-)/Surplus` · `Sep` · `2024` · `Figure 4.` | 0.05 | 有个键压根没写进表 | Value '-1850' not found in any table |
| **不通过** | `3980` | `Receipts` · `Jun` · `2025` · `Figure 4.` | 0.05 | 有个键压根没写进表 | Value '3980' not found in any table |
| **不通过** | `-5350` | `Outlays` · `Jun` · `2025` · `Figure 4.` | 0.05 | 有个键压根没写进表 | Value '-5350' not found in any table |

## 解析器写下的整页 markdown

```markdown
Figure 3. Monthly Receipts, Outlays, and Budget Deficit/Surplus of the U.S. Government, Fiscal Years 2024 and 2025

**Monthly Receipts, Outlays, and Budget Deficit/Surplus of the U.S. Government, Cumulative, Fiscal Years 2024 and 2025**

<table>
<thead><tr><th>Month (Fiscal Year)</th><th>Receipts</th><th>Outlays</th><th>Deficit(-)/Surplus</th></tr></thead>
<tbody>
<tr><td>Oct 2024</td><td>$250B</td><td>$600B</td><td>($50B)</td></tr>
<tr><td>Nov 2024</td><td>$50B</td><td>$800B</td><td>($320B)</td></tr>
<tr><td>Dec 2024</td><td>$100B</td><td>$900B</td><td>($90B)</td></tr>
<tr><td>Jan 2024</td><td>$200B</td><td>$800B</td><td>($10B)</td></tr>
<tr><td>Feb 2024</td><td>$50B</td><td>$700B</td><td>($280B)</td></tr>
<tr><td>Mar 2024</td><td>$50B</td><td>$800B</td><td>($220B)</td></tr>
<tr><td>Apr 2024</td><td>$450B</td><td>$800B</td><td>$200B</td></tr>
<tr><td>May 2024</td><td>$100B</td><td>$1,000B</td><td>($350B)</td></tr>
<tr><td>Jun 2024</td><td>$150B</td><td>$850B</td><td>($60B)</td></tr>
<tr><td>Jul 2024</td><td>$0B</td><td>$900B</td><td>($220B)</td></tr>
<tr><td>Aug 2024</td><td>$0B</td><td>$1,000B</td><td>($380B)</td></tr>
<tr><td>Sep 2024</td><td>$250B</td><td>$750B</td><td>$50B</td></tr>
<tr><td>Oct 2025</td><td>$150B</td><td>$700B</td><td>($240B)</td></tr>
<tr><td>Nov 2025</td><td>$100B</td><td>$900B</td><td>($380B)</td></tr>
<tr><td>Dec 2025</td><td>$150B</td><td>$700B</td><td>($70B)</td></tr>
<tr><td>Jan 2025</td><td>$250B</td><td>$950B</td><td>($110B)</td></tr>
<tr><td>Feb 2025</td><td>$100B</td><td>$750B</td><td>($320B)</td></tr>
<tr><td>Mar 2025</td><td>$150B</td><td>$750B</td><td>($140B)</td></tr>
<tr><td>Apr 2025</td><td>$500B</td><td>$850B</td><td>$250B</td></tr>
<tr><td>May 2025</td><td>$150B</td><td>$950B</td><td>($330B)</td></tr>
<tr><td>Jun 2025</td><td>$250B</td><td>$700B</td><td>$30B</td></tr>
</tbody>
</table>

**Figure 4. Monthly Receipts, Outlays, and Budget Deficit/Surplus of the U.S. Government, Cumulative, Fiscal Years 2024 and 2025**

Figure 4. Monthly Receipts, Outlays, and Budget Deficit/Surplus of the U.S. Government, Cumulative, Fiscal Years 2024 and 2025

<table>
<thead><tr><th>Month</th><th>Year</th><th>Receipts</th><th>Outlays</th><th>Deficit(-)/Surplus</th></tr></thead>
<tbody>
<tr><td>Oct</td><td>2024</td><td>$300B</td><td>($400B)</td><td>($100B)</td></tr>
<tr><td>Nov</td><td>2024</td><td>$600B</td><td>($800B)</td><td>($350B)</td></tr>
<tr><td>Dec</td><td>2024</td><td>$1,000B</td><td>($1,400B)</td><td>($600B)</td></tr>
<tr><td>Jan</td><td>2024</td><td>$1,500B</td><td>($1,800B)</td><td>($750B)</td></tr>
<tr><td>Feb</td><td>2024</td><td>$1,800B</td><td>($2,700B)</td><td>($900B)</td></tr>
<tr><td>Mar</td><td>2024</td><td>$2,100B</td><td>($3,200B)</td><td>($1,050B)</td></tr>
<tr><td>Apr</td><td>2024</td><td>$2,900B</td><td>($4,000B)</td><td>($900B)</td></tr>
<tr><td>May</td><td>2024</td><td>$3,200B</td><td>($4,500B)</td><td>($1,250B)</td></tr>
<tr><td>Jun</td><td>2024</td><td>$3,700B</td><td>($5,000B)</td><td>($1,350B)</td></tr>
<tr><td>Jul</td><td>2024</td><td>$4,100B</td><td>($5,700B)</td><td>($1,500B)</td></tr>
<tr><td>Aug</td><td>2024</td><td>$4,400B</td><td>($6,800B)</td><td>($1,700B)</td></tr>
<tr><td>Sep</td><td>2024</td><td>$4,900B</td><td>($7,300B)</td><td>($1,800B)</td></tr>
<tr><td>Oct</td><td>2025</td><td>$300B</td><td>($400B)</td><td>($200B)</td></tr>
<tr><td>Nov</td><td>2025</td><td>$500B</td><td>($1,000B)</td><td>($500B)</td></tr>
<tr><td>Dec</td><td>2025</td><td>$1,000B</td><td>($1,800B)</td><td>($700B)</td></tr>
<tr><td>Jan</td><td>2025</td><td>$1,500B</td><td>($2,400B)</td><td>($900B)</td></tr>
<tr><td>Feb</td><td>2025</td><td>$1,800B</td><td>($3,000B)</td><td>($1,200B)</td></tr>
<tr><td>Mar</td><td>2025</td><td>$2,200B</td><td>($3,900B)</td><td>($1,350B)</td></tr>
<tr><td>Apr</td><td>2025</td><td>$3,000B</td><td>($4,400B)</td><td>($1,100B)</td></tr>
<tr><td>May</td><td>2025</td><td>$3,400B</td><td>($4,900B)</td><td>($1,400B)</td></tr>
<tr><td>Jun</td><td>2025</td><td>$4,000B</td><t
```
