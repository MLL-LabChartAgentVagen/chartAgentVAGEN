# Monthly loan loss provision build and allowance coverage across seven commercial banking segments, January 2022 to December 2024

The credit risk analytics team at a regional commercial bank assembled this table from the monthly allowance close package covering January 2022 through December 2024. Each row is a single provision posting made at a month-end close for one business segment, tagged with the driver cited in the allowance memo and with the segment's position in the quarterly reporting calendar. The data was pulled in early 2025 to support a review of why provision expense clusters in the final month of each quarter and how allowance coverage responded to the deterioration in charge-offs that began in late 2023.

`s001` -- 360 rows, 10 columns

## Dimensions

```mermaid
flowchart LR
  subgraph entity
    segment_group[segment_group<br/>3]
    business_segment[business_segment<br/>7]
  end
  subgraph close_calendar
    quarter_month_position[quarter_month_position<br/>3]
  end
  subgraph driver
    provision_driver[provision_driver<br/>4]
  end
  subgraph calendar
    close_month[/close_month<br/>36/]
    quarter[quarter<br/>12]
  end
  segment_group --> business_segment
  close_month -.-> quarter
```

## Numeric columns

```mermaid
flowchart LR
  loans_outstanding([loans_outstanding<br/>USD millions])
  net_charge_offs([net_charge_offs<br/>USD millions])
  provision_expense([provision_expense<br/>USD millions])
  allowance_coverage_ratio([allowance_coverage_ratio<br/>percent])
  loans_outstanding --> net_charge_offs
  loans_outstanding --> provision_expense
  net_charge_offs --> provision_expense
  loans_outstanding --> allowance_coverage_ratio
  net_charge_offs --> allowance_coverage_ratio
```

## Intents

```mermaid
flowchart LR
  i0(["comparison<br/>SUM"])
  i0 --> quarter_month_position
  i0 --> provision_expense
  i1(["trend<br/>SUM"])
  i1 --> close_month
  i1 --> provision_expense
  i2(["composition<br/>SUM"])
  i2 --> provision_driver
  i2 --> segment_group
  i2 --> provision_expense
  i3(["relation<br/>NONE"])
  i3 --> net_charge_offs
  i3 --> allowance_coverage_ratio
```

## What can be drawn

| family | drawable |
|---|---|
| comparison | yes |
| trend | yes |
| composition | yes |
| relation | yes |
| distribution | yes |
| process | yes |

Densest two-column cross: segment_group x quarter_month_position at 40.0 rows per cell.
