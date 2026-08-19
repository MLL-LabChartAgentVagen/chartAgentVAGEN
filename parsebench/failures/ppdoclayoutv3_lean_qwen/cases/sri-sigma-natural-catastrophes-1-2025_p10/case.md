# sri-sigma-natural-catastrophes-1-2025_p10

****每根柱子都读低了正好半格**：1→0、4→3.5、8→7.5** · 数字读错了 · 该页 2 / 10 通过

![page](page.png)

## 这一页发生了什么

直方图的纵轴是「有多少年落在这个区间」，**只能是整数**。
八个失败点，**每一个都正好比真值低 0.5**：1→0 · 4→3.5 · 8→7.5 · 2→1.5 · 4→3.5 · 3→2.5 · 2→1.5 · 1→0.5。唯一通过的那个 5→4.5 也是同样的偏移，只是 10% 的容差刚好收住了它。
**这不是噪声，是把柱顶读到了两条格线中间。**

## 对流水线意味着什么

**P1 还差一条：测度自己的取值域。**
「这个图元能读到 ±3%」（可达精度 ε）描述不了「这个量只能取整数」。计数型测度四舍五入到整数，这八个点里有几个就能救回来。
我们的 schema 里 measure 已经声明了类型，把它传进值目标与自检是零成本的，而现有工作没有这一项标注。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| 通过 | `5` | `-100%` · `Primary perils` | 0.1 | — | Value '5' found with all labels at (3, 1) |
| **不通过** | `1` | `-75%` · `Secondary perils` | 0.1 | 数字读错了（表里是 0） | Value '1' not found in any table |
| **不通过** | `4` | `-50%` · `Primary perils` | 0.05 | 数字读错了（表里是 3.5） | Value '4' not found in any table |
| **不通过** | `8` | `-25%` · `Secondary perils` | 0.05 | 数字读错了（表里是 7.5） | Value '8' not found in any table |
| **不通过** | `2` | `0%` · `Primary perils` | 0.05 | 数字读错了（表里是 1.5） | Value '2' not found in any table |
| **不通过** | `4` | `25%` · `Secondary perils` | 0.05 | 数字读错了（表里是 3.5） | Value '4' not found in any table |
| **不通过** | `3` | `50%` · `Primary perils` | 0.1 | 数字读错了（表里是 2.5） | Value '3' not found in any table |
| 通过 | `0` | `125%` · `Primary perils` | 0.01 | — | Value '0' found with all labels at (2, 1) |
| **不通过** | `2` | `225%` · `Primary perils` | 0.05 | 数字读错了（表里是 1.5） | Value '2' not found in any table |
| **不通过** | `1` | `675%` · `Primary perils` | 0.1 | 数字读错了（表里是 0.5） | Value '1' not found in any table |

## 解析器写下的整页 markdown

```markdown
10 **Swiss Re Institute** *sigma No 1/2025* Insured losses on trend

**Figure 6**
Distribution of annual losses from primary and secondary perils in % deviation from trend (1995 – 2024)

12 Number of years

<table>
<thead>
<tr><th>Deviations from trend</th><th>Primary perils</th><th>Secondary perils</th><th>Year</th></tr>
</thead>
<tbody>
<tr><td>-150%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>-125%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>-100%</td><td>4.5</td><td>0</td><td></td></tr>
<tr><td>-75%</td><td>5.5</td><td>0</td><td></td></tr>
<tr><td>-50%</td><td>3.5</td><td>3.5</td><td></td></tr>
<tr><td>-25%</td><td>2.5</td><td>7.5</td><td></td></tr>
<tr><td>0%</td><td>1.5</td><td>10.5</td><td></td></tr>
<tr><td>25%</td><td>1.5</td><td>3.5</td><td></td></tr>
<tr><td>50%</td><td>2.5</td><td>0.5</td><td></td></tr>
<tr><td>75%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>100%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>125%</td><td>0</td><td>0.5</td><td>2011</td></tr>
<tr><td>150%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>175%</td><td>0.5</td><td>0</td><td>1999</td></tr>
<tr><td>200%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>225%</td><td>1.5</td><td>0</td><td>2011, 2017</td></tr>
<tr><td>250%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>275%</td><td>0.5</td><td>0</td><td>2004</td></tr>
<tr><td>300%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>325%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>350%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>375%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>400%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>425%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>450%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>475%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>500%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>525%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>550%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>575%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>600%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>625%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>650%</td><td>0</td><td>0</td><td></td></tr>
<tr><td>675%</td><td>0.5</td><td>0</td><td>2005</td></tr>
<tr><td>700%</td><td>0</td><td>0</td><td></td></tr>
</tbody>
</table>

**Number of years** (y-axis) vs **Deviations from trend** (x-axis)

Legend: Primary perils | Secondary perils

Source: Swiss Re Institute

...and it is a matter of *when*, not if, the next peak loss year will occur.

The absence of peak-loss years since 2017 should not be read as a signal that primary peril loss events, especially large “tail” events, are becoming less likely. History shows

Primary perils  Secondary perils

Source: Swiss Re Institute

…and it is a matter of *when*, not if, the next peak loss year will occur.

The absence of peak-loss years since 2017 should not be read as a signal that primary peril loss events, especially large “tail” events, are becoming less likely. History shows that annual losses from primary perils vary considerably, punctuated by peak loss years. The experience of Hurricanes Katrina, Wilma and Rita in 2005, or Harvey, Irma and Maria in 2017 illustrates the scale of huge losses that can result from primary perils. And also that in years when low-frequency high-severity events do strike, particularly in regions of high economic exposure, insured losses from all natural catastrophes can reach well above trend levels, sometimes 100% or more above trend. In the next chapter, we estimate and demonstrate the potential magnitude of insured losses in a next peak-loss year and highlight scenarios that can cause such losses.
```
