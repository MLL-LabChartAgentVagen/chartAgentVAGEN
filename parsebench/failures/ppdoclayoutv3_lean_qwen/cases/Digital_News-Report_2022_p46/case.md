# Digital_News-Report_2022_p46

****值那一列的表头**写成了整段问卷题干，规则要的是 `Percentage`** · 数字对，但表里说不清这个数字是谁的 · 该页 0 / 4 通过

![page](page.png)

## 这一页发生了什么

42 个国家的横向条形图，数字全部印在条末，解析器一行不差地抄进了一张 43 行的长表——**表的形状是对的**。
问题在值那一列的表头：解析器写的是问卷原题 `Q10. Thinking about how you got news online…`，而规则的第二个键是 **`Percentage`**——标注者从百分数轴上取的测度名。
国家名对上了，测度名对不上，四个点全判 0。

## 对流水线意味着什么

**值那一列的表头本身就是一个键。**
它的名字应该来自测度声明（我们的 schema 里 measure 有名字有单位），而不是页面上离得最近的一句话。这也是 `unit_in_axis_or_title`（149 / 192 页，基准里最通用的组件）在判分侧的具体形态。

## 逐条抽查点

| 判定 | 值 | 定位键 | 容差 | 归类 | 度量原话 |
|---|---|---|---|---|---|
| **不通过** | `24` | `Austria` · `Percentage` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (1, 1) missing labels: ['percentage'] (data labels ['austria'] in table, title labels [] in context) |
| **不通过** | `22` | `USA` · `Percentage` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (3, 1) missing labels: ['percentage'] (data labels ['usa'] in table, title labels [] in context); Value at (4, 1 |
| **不通过** | `11` | `Norway` · `Percentage` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (38, 1) missing labels: ['norway', 'percentage'] (data labels [] in table, title labels [] in context); Value at |
| **不通过** | `9` | `UK` · `Percentage` | 0.01 | 数字对，但表里说不清这个数字是谁的 | Value found but labels not associated: Value at (42, 1) missing labels: ['percentage'] (data labels ['uk'] in table, title labels [] in context) |

## 解析器写下的整页 markdown

```markdown
**46** Reuters Institute for the Study of Journalism | Digital News Report 2022

# 2.4 Email News: Its Contribution to Engagement and Monetisation

**Nic Newman**

In the last few years, the emergence of paid newsletter platforms, such as Substack, Revue, and Bulletin, have opened up new opportunities for individuals and small publishers to distribute and monetise content. A number of high-profile columnists have left big news organisations to run newsletter-based businesses, with a few of the most successful earning salaries in the high six figures.<sup>19</sup>

At the same time, digital-born brands such as Politico and Axios have found that smart, journalist-curated emails have been a key driver of growth for businesses which cover a range of niches from politics to health, technology, sports, and local.<sup>20</sup> Meanwhile, mainstream news organisations have been shifting resources into email production as they try to attract new subscribers, build loyalty with existing users, and introduce more personalisation into their digital products (Jack 2016; Newman et al. 2020). *The New York Times*, for example, now produces 50 different emails read by 15 million people a week.<sup>21</sup>

Much of this recent free and paid newsletter activity has been focused on the United States, but we were keen to know if this had extended elsewhere. More widely, we wanted to understand more about the appeal of newsletters in general. In what ways can this low-tech and often unfashionable medium help build or support sustainable journalism?

## **WEEKLY EMAIL CONSUMPTION**

Our *Digital News Report* data show that email newsletters remain an important channel across countries, with an average of 17% using them weekly. In the United States, 22% use newsletters or email alerts, with almost half of them (10%) saying it is their *main way of accessing digital news*. Austria (24%), Belgium (23%) and Portugal (22%) also have surprisingly high email usage, but Norway (11%) and the UK (9%) have some of the lowest levels. This may be because their stronger brand connections – with users more likely to go directly to website and apps – mean that publishers feel there is less need to push content to audiences.

**PROPORTION WHO ACCESSED NEWS VIA EMAIL IN THE LAST WEEK – SELECTED MARKETS**

<table>
<thead><tr><th>Market</th><th>Q10. Thinking about how you got news online (via computer, mobile, or any device) in the last week, which were the ways in which you came across news stories?</th></tr></thead>
<tbody>
<tr><td>Austria</td><td>24</td></tr>
<tr><td>Belgium</td><td>23</td></tr>
<tr><td>USA</td><td>22</td></tr>
<tr><td>Portugal</td><td>22</td></tr>
<tr><td>Switzerland</td><td>20</td></tr>
<tr><td>Brazil</td><td>20</td></tr>
<tr><td>Greece</td><td>20</td></tr>
<tr><td>Romania</td><td>20</td></tr>
<tr><td>Colombia</td><td>19</td></tr>
<tr><td>Germany</td><td>19</td></tr>
<tr><td>Mexico</td><td>18</td></tr>
<tr><td>Philippines</td><td>18</td></tr>
<tr><td>Hungary</td><td>18</td></tr>
<tr><td>Australia</td><td>17</td></tr>
<tr><td>Canada</td><td>17</td></tr>
<tr><td>Chile</td><td>16</td></tr>
<tr><td>France</td><td>16</td></tr>
<tr><td>Peru</td><td>16</td></tr>
<tr><td>Netherlands</td><td>16</td></tr>
<tr><td>Singapore</td><td>16</td></tr>
<tr><td>Thailand</td><td>16</td></tr>
<tr><td>Malaysia</td><td>15</td></tr>
<tr><td>Slovakia</td><td>15</td></tr>
<tr><td>Denmark</td><td>15</td></tr>
<tr><td>Italy</td><td>15</td></tr>
<tr><td>Spain</td><td>15</td></tr>
<tr><td>Ireland</td><td>15</td></tr>
<tr><td>Poland</td><td>15</td></tr>
<tr><td>Czech Republic</td><td>15</td></tr>
<tr><td>Turkey</td><td>14</td></tr>
<tr><td>Sweden</td><td>14</td></tr>
<tr><td>Hong Kong</td><td>14</td></tr>
<tr><td>Japan</td><td>13</td></tr>
<tr><td>Indonesia</td><td>13</td></tr>
<tr><td>Bulgaria</td><td>13</td></tr>
<tr><td>Taiwan</td><td>12</td></tr>
<tr><td>Argentina</td><td>12</td></tr>
<tr><td>Croatia</td><td>11</td></tr>
<tr><td>Finland</td><td>11</td></tr>
<tr><td>Norway<
```
