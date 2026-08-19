# ac8b3538-en_p62

****两条线的名字没进表**：图例被写成页顶一行普通文字，9 个失败点里 7 个卡在这里** · 数字对，但表里说不清这个数字是谁的 · 该页 1 / 10 通过

![page](page.png)

## 这一页发生了什么

一页排了 15 个国家的小折线，每个面板一个国名，两条线（`Nominal minimum wage` / `Real minimum wage`），横轴 61 个半年刻度，**全页 1,830 个图元，一个数值都不写**。
**结构其实选对了。** 一个面板一张表，行是时间、列是两条线，国名写成表前面的 `## **Japan**` 标题——判分程序就是靠这个标题认出 `Japan` 的，它的原话是 `title labels ['japan'] in context`。
**挂在系列名上。** 图例那行 `Nominal minimum wage    Real minimum wage` 被写成了页顶一行**普通正文**：既不在任何表头里（第一张表的表头写成了截断的 `Nomini`），也不是粗体或标题，所以表外回退那一步不认它。9 个失败点里 7 个的缺失键含这个系列名，其中 **4 个只缺这一个**。
国名接错是次要的：`Japan` 那张表的表头写着 `Lithuania`、`Korea` 那张的第二列写着 `Luxembourg`，只影响 4 个点。
唯一通过的那个点还是蒙对的——`**Real minimum wage**` 与 `Nominal minimum wage` 的相似度 0.81，而回退只要 0.60，把「实际」当成「名义」放了过去。

## 对流水线意味着什么

**P2：系列名要能作为一个键导出去，不能只画在图例里。**
我们记录层里系列名本来就是键的一维。这一页说明的是导出时它必须落进表头或标题，写成一行普通文字等于没写——这正好是可以拿来训的一条：图例上的名字，要跟着它那条线一起写进表。
**P5：这一页我们一张也生成不出来。**`chart_types.md` 现在 line 的系列上限是 6、grouped_bar 的 |P|·|S| ≤ 24，画不到 1,830 个图元这一档。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `10` | `Japan` · `Nominal minimum wage` · `Nov-22` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (8, 1) missing labels: ['nominal minimum wage'] (data labels ['nov-22'] in table, title labels ['japan'] in cont |
| **不通过** | `17` | `Latvia` · `Real minimum wage` · `May-24` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (11, 1) missing labels: ['latvia', 'real minimum wage'] (data labels ['may-24'] in table, title labels [] in con |
| 通过 | `16` | `Lithuania` · `Nominal minimum wage` · `Nov-21` | 0.1 | — | Value '16' found with data labels ['nov-21'] in table and title labels ['lithuania', 'nominal minimum wage'] in context at (6, 1) |
| **不通过** | `90` | `Mexico` · `Real minimum wage` · `May-24` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (8, 1) missing labels: ['real minimum wage', 'may-24'] (data labels ['mexico'] in table, title labels [] in cont |
| **不通过** | `42` | `Netherlands` · `Nominal minimum wage` · `May-24` | 0.05 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (6, 2) missing labels: ['nominal minimum wage', 'may-24'] (data labels [] in table, title labels ['netherlands'] |
| **不通过** | `35` | `Poland` · `Real minimum wage` · `May-24` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (7, 1) missing labels: ['poland', 'may-24'] (data labels [] in table, title labels ['real minimum wage'] in cont |
| **不通过** | `38` | `Portugal` · `Nominal minimum wage` · `May-24` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (5, 1) missing labels: ['portugal', 'nominal minimum wage', 'may-24'] (data labels [] in table, title labels []  |
| **不通过** | `9` | `Slovak Republic` · `Real minimum wage` · `May-24` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (8, 1) missing labels: ['slovak republic', 'real minimum wage', 'may-24'] (data labels [] in table, title labels |
| **不通过** | `700` | `Türkiye` · `Nominal minimum wage` · `May-24` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (11, 1) missing labels: ['nominal minimum wage'] (data labels ['may-24'] in table, title labels ['turkiye'] in c |
| **不通过** | `12` | `United Kingdom` · `Real minimum wage` · `May-24` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (8, 1) missing labels: ['united kingdom', 'real minimum wage'] (data labels ['may-24'] in table, title labels [] |

## 解析器写下的整页 markdown

```markdown
**60** |

Nominal minimum wage    Real minimum wage

## **Japan**

**Japan**

<table>
<tr><th>Lithuania</th><th>Nomini</th><th></th></tr>
<tr><td>May-19</td><td>0</td><td>0</td></tr>
<tr><td>Nov-19</td><td>0</td><td>1</td></tr>
<tr><td>May-20</td><td>3</td><td>2</td></tr>
<tr><td>Nov-20</td><td>3</td><td>3</td></tr>
<tr><td>May-21</td><td>3</td><td>4</td></tr>
<tr><td>Nov-21</td><td>6</td><td>6</td></tr>
<tr><td>May-22</td><td>6</td><td>5</td></tr>
<tr><td>Nov-22</td><td>10</td><td>6</td></tr>
<tr><td>May-23</td><td>10</td><td>6</td></tr>
<tr><td>Nov-23</td><td>15</td><td>5</td></tr>
<tr><td>May-24</td><td>15</td><td>7</td></tr>
</table>

**Japan**

(Legend, truncated at top of region: "Nomini")

**Lithuania**

## **Korea**

**Korea**

<table>
<thead><tr><th></th><th>Korea</th><th>Luxembourg</th></tr></thead>
<tbody>
<tr><td>May '19</td><td>0</td><td>0</td></tr>
<tr><td>Nov '19</td><td>0</td><td>1</td></tr>
<tr><td>May '20</td><td>1</td><td>1</td></tr>
<tr><td>Nov '20</td><td>4</td><td>2</td></tr>
<tr><td>May '21</td><td>4</td><td>2</td></tr>
<tr><td>Nov '21</td><td>10</td><td>0</td></tr>
<tr><td>May '22</td><td>5</td><td>5</td></tr>
<tr><td>Nov '22</td><td>5</td><td>2</td></tr>
<tr><td>May '23</td><td>14</td><td>1</td></tr>
<tr><td>Nov '23</td><td>14</td><td>0</td></tr>
<tr><td>May '24</td><td>18</td><td>2</td></tr>
</tbody>
</table>

# Korea

**Luxembourg**

## **Latvia**

**Real minimum wage**

<table>
<thead><tr><th></th><th>Latvia</th><th>Mexico</th></tr></thead>
<tbody>
<tr><td>May-19</td><td>0</td><td>-1</td></tr>
<tr><td>Nov-19</td><td>0</td><td>-1</td></tr>
<tr><td>May-20</td><td>0</td><td>0</td></tr>
<tr><td>Nov-20</td><td>0</td><td>0</td></tr>
<tr><td>May-21</td><td>16</td><td>17</td></tr>
<tr><td>Nov-21</td><td>16</td><td>10</td></tr>
<tr><td>May-22</td><td>16</td><td>0</td></tr>
<tr><td>Nov-22</td><td>16</td><td>-13</td></tr>
<tr><td>May-23</td><td>45</td><td>8</td></tr>
<tr><td>Nov-23</td><td>45</td><td>8</td></tr>
<tr><td>May-24</td><td>61</td><td>22</td></tr>
</tbody>
</table>

## Real minimum wage

Series annotations: **Latvia** (upper line), **Mexico** (lower line).

## **Lithuania**

**Lithuania**

<table>
<tr><th></th><th>Light green</th><th>Dark green</th></tr>
<tr><td>May-19</td><td>0</td><td>0</td></tr>
<tr><td>Nov-19</td><td>0</td><td>0</td></tr>
<tr><td>May-20</td><td>10</td><td>10</td></tr>
<tr><td>Nov-20</td><td>10</td><td>10</td></tr>
<tr><td>May-21</td><td>16</td><td>16</td></tr>
<tr><td>Nov-21</td><td>16</td><td>16</td></tr>
<tr><td>May-22</td><td>32</td><td>10</td></tr>
<tr><td>Nov-22</td><td>32</td><td>0</td></tr>
<tr><td>May-23</td><td>52</td><td>0</td></tr>
<tr><td>Nov-23</td><td>52</td><td>10</td></tr>
<tr><td>May-24</td><td>68</td><td>20</td></tr>
</table>

## Lithuania

## Netherlands

## **Luxembourg**

**Luxembourg / New Zealand**

<table>
<tr><th></th><th>Luxembourg (green)</th><th>Luxembourg (teal)</th><th>New Zealand</th></tr>
<tr><td>May-19</td><td>0</td><td>0</td><td></td></tr>
<tr><td>Nov-19</td><td>0</td><td>0</td><td></td></tr>
<tr><td>May-20</td><td>1</td><td>1</td><td></td></tr>
<tr><td>Nov-20</td><td>2</td><td>2</td><td></td></tr>
<tr><td>May-21</td><td>4</td><td>1</td><td></td></tr>
<tr><td>Nov-21</td><td>7</td><td>1</td><td></td></tr>
<tr><td>May-22</td><td>8</td><td>-1</td><td></td></tr>
<tr><td>Nov-22</td><td>11</td><td>0</td><td></td></tr>
<tr><td>May-23</td><td>17</td><td>5</td><td></td></tr>
<tr><td>Nov-23</td><td>21</td><td>7</td><td></td></tr>
<tr><td>May-24</td><td>23</td><td>6</td><td></td></tr>
</table>

**Luxembourg**

**New Zealand**

## **Mexico**

**Mexico**

<table>
<thead>
<tr><th></th><th>Mexico</th><th>Poland</th></tr>
</thead>
<tbody>
<tr><td>May-19</td><td>0</td><td>0</td></tr>
<tr><td>Nov-19</td><td>0</td><td>0</td></tr>
<tr><td>May-20</td><td>20</td><td>10</td></tr>
<tr><td>Nov-20</td><td>22</td><td>20</td></tr>
<tr><td>May-21</td><td>35</td><td>25</td></tr>
<tr><td>Nov-21</td><td>35</td><td>40</td></tr>
<tr><td>May-22</td><td>70</td><td>45</td></tr>
<tr
```
