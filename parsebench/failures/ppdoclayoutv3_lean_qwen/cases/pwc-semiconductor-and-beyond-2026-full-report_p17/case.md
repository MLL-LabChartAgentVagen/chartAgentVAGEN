# pwc-semiconductor-and-beyond-2026-full-report_p17

****列名写成了颜色**：Gray / Orange，而图例上写的是 Conventional / AI-driven demand** · 数字对，但表里说不清这个数字是谁的 · 该页 0 / 10 通过

![page](page.png)

## 这一页发生了什么

**十个数字一个不差，十个点全判 0。**
图例在右上角，两个色块分别标着 `Conventional demand`（灰）与 `AI-driven demand`（橙）。解析器没有把色块和柱子对起来，列名直接写成了 `Gray` / `Orange`。规则要「`'19` 这一年的 `Conventional demand` 是多少」，而表里从头到尾没出现过 `Conventional demand` 这几个字。
**还多出来一列。** 两根柱子之间那条浅橙色的连接带是装饰，不是数据，解析器把它当成第三个系列写成了 `Light orange band`。

## 对流水线意味着什么

**「哪个颜色是哪个系列」这件事，现在没有任何训练目标在教。**
我们画图的时候，每个图元的颜色和它的系列名都是已知的，多导出一条「色块 → 系列名」的配对是纯加法，而现有 chart 数据集没有这项标注。
顺带这一页也给「图里的装饰元素」定了价：一条不是数据的色带被当成数据列，代价是整页 0 分。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `22` | `'19` · `Conventional demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (1, 1) missing labels: ['conventional demand'] (data labels ["'19"] in table, title labels [] in context); Value |
| **不通过** | `1` | `'19` · `AI-driven demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (1, 2) missing labels: ['ai-driven demand'] (data labels ["'19"] in table, title labels [] in context) |
| **不通过** | `46` | `'22` · `Conventional demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (4, 1) missing labels: ['conventional demand'] (data labels ["'22"] in table, title labels [] in context); Value |
| **不通过** | `11` | `'22` · `AI-driven demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (4, 2) missing labels: ['ai-driven demand'] (data labels ["'22"] in table, title labels [] in context) |
| **不通过** | `62` | `'25F` · `Conventional demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (4, 3) missing labels: ["'25f", 'conventional demand'] (data labels [] in table, title labels [] in context); Va |
| **不通过** | `33` | `'25F` · `AI-driven demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (2, 3) missing labels: ['ai-driven demand'] (data labels ["'25f"] in table, title labels [] in context); Value a |
| **不通过** | `80` | `'28F` · `Conventional demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (5, 3) missing labels: ["'28f", 'conventional demand'] (data labels [] in table, title labels [] in context); Va |
| **不通过** | `62` | `'28F` · `AI-driven demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (4, 3) missing labels: ["'28f", 'ai-driven demand'] (data labels [] in table, title labels [] in context); Value |
| **不通过** | `96` | `'30F` · `Conventional demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (6, 3) missing labels: ["'30f", 'conventional demand'] (data labels [] in table, title labels [] in context); Va |
| **不通过** | `68` | `'30F` · `AI-driven demand` | 0.1 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (7, 1) missing labels: ["'30f", 'ai-driven demand'] (data labels [] in table, title labels [] in context); Value |

## 解析器写下的整页 markdown

```markdown
# Faster, bigger, smarter data centers

It is cliché, but true, that we are living in the world of data and connectivity now. More and more devices are interconnected than ever before, including cars, home appliances, smartphones, and PCs. In addition to the growth of number of devices connected, consumers are demanding higher-quality entertainment such as AR/VR/XR gaming and seamless video streaming. Moreover, the introduction of 'ChatGPT' in November 2022 became a motivator for both companies and individuals to actively utilize AI services in various applications they can possibly imagine.

These applications generate and require astronomical amount of data, and we've witnessed just the start of it. With high demand for gaming and video streaming, and most importantly, with the rising demand of AI, global data centers are expected to more than double their power consumption by 2030.

Data centers are a crucial resource for storing, processing, and managing data. They used to focus on providing services for enterprises, but with rising demand, they have achieved hyperscale status, providing internet as a service. Now with the demand of AI-specific applications, Data centers are once again evolving into AI-data centers, enhancing managers' ability to provide lossless services to data center users.

**Rising AI data center power consumption signals growing AI compute demand and chipset needs**

<table>
<thead><tr><th>Year</th><th>Gray</th><th>Orange</th><th>Light orange band</th></tr></thead>
<tbody>
<tr><td>'19</td><td>21</td><td>1</td><td>22</td></tr>
<tr><td>'20</td><td>29</td><td>2</td><td>31</td></tr>
<tr><td>'21</td><td>35</td><td>3</td><td>38</td></tr>
<tr><td>'22</td><td>45</td><td>11</td><td>58</td></tr>
<tr><td>'23</td><td>52</td><td>15</td><td>86</td></tr>
<tr><td>'24</td><td>57</td><td>22</td><td>98</td></tr>
<tr><td>'25F</td><td>62</td><td>31</td><td>110</td></tr>
<tr><td>'26F</td><td>68</td><td>42</td><td>128</td></tr>
<tr><td>'27F</td><td>75</td><td>53</td><td>145</td></tr>
<tr><td>'28F</td><td>80</td><td>61</td><td>158</td></tr>
<tr><td>'29F</td><td>87</td><td>68</td><td>165</td></tr>
<tr><td>'30F</td><td>95</td><td>68</td><td>165</td></tr>
</tbody>
</table>

**Rising AI data center power consumption signals growing AI compute demand and chipset needs**

Source: IEA, PwC analysis

Source: IEA, PwC analysis

**PwC** Semiconductor and beyond 2026

17
```
