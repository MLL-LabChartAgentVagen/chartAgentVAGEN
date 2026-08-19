# Technopak_Industry_Report_p18

****三张饼拆成三张小表**，年份和类目名分别丢在不同的表里** · 数字对，但表里说不清这个数字是谁的 · 该页 0 / 6 通过

![page](page.png)

## 这一页发生了什么

**六个数字全部写对，六个点全判 0。**
页面上是同一个图号下的三张饼（2019 / 2024 / 2029P），年份写在每张饼的上方，`Branded Play` / `Unbranded Play` 的图例只画在中间那张饼下面。
解析器照着版面输出了三张两列小表：**2019 和 2029P 那两张只有数字，没有类目名；中间那张有类目名，没有年份。**每张表都少一个键，所以每个点都对不上。

## 对流水线意味着什么

**这就是 P2（面板名进键）要解决的情形。**面板名如果只是个 id、不作为键写出去，每张面板表都会少一个键。
更值得注意的是：这一页的数值**全部印在图上**，读数根本没出错。读得准和写得对，在这个度量下是两件独立的事。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `78` | `2019` · `Branded Play` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (1, 0) missing labels: ['2019', 'branded play'] (data labels [] in table, title labels [] in context); Value at  |
| **不通过** | `22` | `2019` · `Unbranded Play` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (2, 0) missing labels: ['2019', 'unbranded play'] (data labels [] in table, title labels [] in context); Value a |
| **不通过** | `83` | `2024` · `Branded Play` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (1, 1) missing labels: ['2024'] (data labels ['branded play'] in table, title labels [] in context) |
| **不通过** | `17` | `2024` · `Unbranded Play` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (2, 1) missing labels: ['2024'] (data labels ['unbranded play'] in table, title labels [] in context) |
| **不通过** | `88` | `2029P` · `Branded Play` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (1, 0) missing labels: ['branded play'] (data labels [] in table, title labels ['2029p'] in context); Value at ( |
| **不通过** | `12` | `2029P` · `Unbranded Play` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (2, 0) missing labels: ['unbranded play'] (data labels [] in table, title labels ['2029p'] in context); Value at |

## 解析器写下的整页 markdown

```markdown
The water purifier product market in India has steadily transitioned towards branded play, with branded players commanding a substantial 83% market share as of FY2024. Within this branded market, the top 5-7 leading players hold close to 90% market share. The shift towards branded play over unbranded play is influenced by factors on both the demand and supply sides. On the demand side, increasing health awareness among consumers and increase in availability and access to piped water are key drivers of this shift. On the supply side, technological interventions, brand-building initiatives by major players, the implementation of GST, and robust distribution network servicing extensive retail footprints contribute to the transformation towards branded play. As of FY2024, branded play accounted for nearly 83% (~INR 4,035 crore) of the water purifier product market in India. This marks a significant increase from the market share of around 78% (~ INR 2,960 crore) recorded in FY2019, showcasing a notable growth trajectory for the branded market. The branded play is estimated to capture ~88% (~INR 6,890 crore) market share by FY2029.

*Exhibit 3.5: Share of Branded Play in Indian Water Purifier (Product) Market- By Value (in %) (FY)*

**2019**

<table>
<tr><th></th><th>2019</th></tr>
<tr><td>78%</td><td>78%</td></tr>
<tr><td>22%</td><td>22%</td></tr>
</table>

Key Sub-categories of Water Purifiers

2019

Source: Technopak Analysis
<table>
<tr><th></th><th></th></tr>
<tr><td>Branded Play</td><td>83%</td></tr>
<tr><td>Unbranded Play</td><td>17%</td></tr>
</table>
**2029P**

<table>
<tr><th></th><th></th></tr>
<tr><td>88%</td><td>88%</td></tr>
<tr><td>12%</td><td>12%</td></tr>
</table>

2029P

*Source: Technopak Analysis*

## **Key Sub-categories of Water Purifiers**

### **By Need for Electricity**

The Indian water purifier market can be segmented based on the need for electricity into Electric and Non-Electric categories. Electric water purifiers require electricity to operate and utilize RO, UV, or a combination of both RO+UV technology to provide pure and clean drinking water. RO water purifiers reduce Total Dissolved Solids (TDS) and enhance taste, making them suitable for areas with medium to high TDS levels in the fresh water supply. On the other hand, UV water purifiers remove sediments, microbials, and improve the water odor, making them applicable in areas with a low level of TDS in the fresh water supply. Filters of electric water purifiers typically need replacement once a year.

Non-electric water purifiers operate without electricity and employ gravity-based mechanisms to purify water. They use a variety of filters like sediment filters, carbon filters etc., UF (Ultra Filtration) and/or chemical technology to remove impurities and bacteria, ensuring water purification. Non-electric water purifiers are particularly preferred in situations where inline water supply and electricity are not available. While these water purifiers do not enhance the taste and color of the water, they are suitable for use when the TDS level is low, i.e., within consumable limits. Filters of non-electric water purifiers typically require replacement every 3-6 months.

Electric water purifiers exhibit superior water purification efficiency compared to non-electric water purifiers. As of FY2024, electric and non-electric water purifiers accounted for ~97% (INR 4,715 crore) and ~3% (INR 145 crore) respectively, of the overall Indian water purifier product market by value. It is projected that by FY2029, electric and non-electric water purifiers will constitute ~99% (INR 7,750 crore) and ~1% (INR 80 crore) respectively, of the overall Indian water purifier product market by value. In terms of volume, the market size of electric and non-electric water purifiers was ~3.6 and ~0.6 million units as of FY2024. By FY2029, the market size of electric and non-electric water purifiers is projected to be ~5.1 and ~0.2 million units, respectively.

18
```
