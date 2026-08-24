# Monthly merchandise export values and commodity group shares by destination economy, 2021-2023

The National Directorate of Statistics compiled customs trade declaration summaries from January 2021 through December 2023 to monitor structural shifts in merchandise export composition and evaluate national trade exposure across major trading partner economies.

`s001` -- 360 rows, 8 columns

Drawn from `dom_0299` Export share by product group -- merchandise trade balance and export shares by partner country and product group (macroeconomy and trade / official_statistics), simple

## Dimensions

```mermaid
flowchart LR
  subgraph geography
    destination_market[destination_market<br/>4]
  end
  subgraph merchandise
    broad_sector[broad_sector<br/>3]
    product_group[product_group<br/>7]
  end
  subgraph calendar
    report_month[/report_month<br/>36/]
    quarter[quarter<br/>12]
  end
  broad_sector --> product_group
  report_month -.-> quarter
```

## Numeric columns

```mermaid
flowchart LR
  export_value_usd_m([export_value_usd_m<br/>million USD])
  export_share_pct([export_share_pct<br/>percent])
  yoy_share_change_ppt([yoy_share_change_ppt<br/>percentage points])
  export_value_usd_m --> export_share_pct
```

## Intents

```mermaid
flowchart LR
  i0(["comparison<br/>AVG"])
  i0 --> destination_market
  i0 --> broad_sector
  i0 --> export_share_pct
  i1(["trend<br/>SUM"])
  i1 --> report_month
  i1 --> export_value_usd_m
  i2(["relation<br/>NONE"])
  i2 --> export_share_pct
  i2 --> yoy_share_change_ppt
```

## What can be drawn

| family | drawable |
|---|---|
| comparison | yes |
| trend | yes |
| composition | yes |
| relation | yes |
| distribution | yes |
| process | no |

Densest two-column cross: destination_market x broad_sector at 30.0 rows per cell.

Gaps:

- No dimension is declared ordered="stage", so no process chart can be drawn. If this scenario has genuine sequential stages, declare that dimension as a stage; if it does not, leave it out rather than inventing one.
