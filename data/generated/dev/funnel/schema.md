# Online checkout funnel for a regional grocery retailer, Jan-Mar 2024

The e-commerce team logged every session step for the first quarter of 2024 while a redesigned cart page was rolled out, to see where shoppers stop.

`funnel` -- 1400 rows, 10 columns

## Dimensions

```mermaid
flowchart LR
  subgraph funnel
    stage[stage<br/>5]
  end
  subgraph acquisition
    channel[channel<br/>4]
    device[device<br/>3]
  end
  subgraph calendar
    event_date[/event_date<br/>91/]
    day_of_week[day_of_week<br/>7]
    month[month<br/>3]
    is_weekend[is_weekend<br/>2]
  end
  event_date -.-> day_of_week
  event_date -.-> month
  event_date -.-> is_weekend
```

## Numeric columns

```mermaid
flowchart LR
  basket_value([basket_value<br/>USD])
  dwell_seconds([dwell_seconds<br/>seconds])
  bounce_rate([bounce_rate<br/>rate])
```

## Intents

```mermaid
flowchart LR
  i0(["process<br/>COUNT"])
  i0 --> stage
  i1(["composition<br/>SUM"])
  i1 --> channel
  i1 --> basket_value
  i2(["distribution<br/>FIVE_NUM"])
  i2 --> stage
  i2 --> dwell_seconds
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

Densest two-column cross: device x is_weekend at 233.3 rows per cell.
