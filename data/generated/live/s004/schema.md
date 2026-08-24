# Real agricultural producer price indices and per-capita output value by World Bank income tier and commodity group, 2005–2023

The Food and Agriculture Organization (FAO) Statistics Division compiled country-level agricultural producer prices deflated by consumer price indices alongside gross per-capita agricultural output from 2005 to 2023. The dataset evaluates terms of trade shocks, commodity-specific volatility, and structural agricultural output differences across global income classifications.

`s004` -- 1800 rows, 9 columns

Drawn from `dom_0482` Real producer prices and per-capita agricultural output value by income group -- food and agriculture: annual agricultural producer price indices and year-on-year change by commodity group and region (food and agriculture / official_statistics), complex

## Dimensions

```mermaid
flowchart LR
  subgraph socioeconomic
    income_group[income_group<br/>4]
    region[region<br/>8]
  end
  subgraph production
    commodity_group[commodity_group<br/>4]
  end
  subgraph market
    market_orientation[market_orientation<br/>2]
  end
  subgraph calendar
    record_period[/record_period<br/>228/]
    quarter[quarter<br/>76]
  end
  income_group --> region
  record_period -.-> quarter
```

## Numeric columns

```mermaid
flowchart LR
  real_producer_price_index([real_producer_price_index<br/>index])
  yoy_real_price_change([yoy_real_price_change<br/>%])
  per_capita_output_value([per_capita_output_value<br/>USD])
  real_producer_price_index --> yoy_real_price_change
```

## Intents

```mermaid
flowchart LR
  i0(["comparison<br/>AVG"])
  i0 --> income_group
  i0 --> per_capita_output_value
  i1(["trend<br/>AVG"])
  i1 --> record_period
  i1 --> real_producer_price_index
  i2(["relation<br/>NONE"])
  i2 --> real_producer_price_index
  i2 --> yoy_real_price_change
  i3(["composition<br/>SUM"])
  i3 --> commodity_group
  i3 --> per_capita_output_value
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

Densest two-column cross: income_group x market_orientation at 225.0 rows per cell.

Gaps:

- No dimension is declared ordered="stage", so no process chart can be drawn. If this scenario has genuine sequential stages, declare that dimension as a stage; if it does not, leave it out rather than inventing one.
