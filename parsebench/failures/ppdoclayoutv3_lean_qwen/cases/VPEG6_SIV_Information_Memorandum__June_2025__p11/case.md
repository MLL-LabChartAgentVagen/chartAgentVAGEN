# VPEG6_SIV_Information_Memorandum__June_2025__p11

****系列名只画在图里当文字**，一个字都没进表** · 有个键压根没写进表 · 该页 0 / 5 通过

![page](page.png)

## 这一页发生了什么

两个系列 `VANTAGE` 和 `GLOBAL PRIVATE EQUITY`，在图上是绘图区里的两行文字标签，不是图例。
解析器把它们原样抄成了表**外面**的两行普通正文，表头则自己起了名：`Quartile TVPI (x)` / `Vantage TVPI (x)`。
**`GLOBAL PRIVATE EQUITY` 在整张表里一个字都没有**，四个点因此判 0；第五个点的值 2.1 只出现在一句加粗的句子里，表里根本没有。

## 对流水线意味着什么

**系列名画在哪里，决定了它会不会进表。**
图例、线端文字、绘图区内标签——这三种画法现在不是风格向量的一维，而它们的后果完全不同。P6 的「标注形态」应该把系列名标签一起收进去。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `2.1` | `VANTAGE` · `Quartile 1` | 0.01 | 键都在，就是没写这个数 | Value '2.1' not found in any table |
| **不通过** | `2.5` | `GLOBAL PRIVATE EQUITY` · `Quartile 1` | 0.01 | 有个键压根没写进表 | Value '2.5' not found in any table |
| **不通过** | `1.7` | `GLOBAL PRIVATE EQUITY` · `Quartile 2` | 0.05 | 有个键压根没写进表 | Value '1.7' not found in any table |
| **不通过** | `1.4` | `GLOBAL PRIVATE EQUITY` · `Quartile 3` | 0.05 | 有个键压根没写进表 | Value '1.4' not found in any table |
| **不通过** | `1.0` | `GLOBAL PRIVATE EQUITY` · `Quartile 4` | 0.01 | 有个键压根没写进表 | Value '1.0' not found in any table |

## 解析器写下的整页 markdown

```markdown
# **VANTAGE HAS GENERATED GLOBAL TOP QUARTILE PRIVATE EQUITY RETURNS**

Vantage has generated Top Quartile returns against direct buyout funds, with investors receiving the added benefits of diversification and lower risk through a Fund of Funds approach.

## **Vantage has Generated Top Quartile Returns when Compared to Global Direct Private Equity Funds**

### **Vantage vs Global Private Equity (Direct Buyout Funds) TVPI - 2009-2018**

VANTAGE

GLOBAL PRIVATE EQUITY

<table>
<thead><tr><th>Category</th><th>Quartile TVPI (x)</th><th>Vantage TVPI (x)</th></tr></thead>
<tbody>
<tr><td>Quartile 1</td><td>2.5x</td><td>2.0x</td></tr>
<tr><td>Quartile 2</td><td>1.7x</td><td>2.0x</td></tr>
<tr><td>Quartile 3</td><td>1.35x</td><td>2.0x</td></tr>
<tr><td>Quartile 4</td><td>0.95x</td><td>2.0x</td></tr>
</tbody>
</table>

**Vantage has generated a 2.1x platform wide Net Multiple on all funds post GFC, this is Top Quartile for Direct Buyout**

Source: Based on global private equity returns on a Total Value Paid In basis from 2009-2018, Persistence in Alternative Strategies: Private Equity Buyout, Preqin. Vantage TVPI based on VPEG2 and VPEG3 TVPI as at 31 March 2025.

Source: Based on global private equity returns on a Total Value Paid In basis from 2009-2018, Persistence in Alternative Strategies: Private Equity Buyout, Preqin. Vantage TVPI based on VPEG2 and VPEG3 TVPI as at 31 March 2025.

VANTAGE

**VANTAGE PRIVATE EQUITY GROWTH 6, LP INFORMATION MEMORANDUM**

**11**
```
