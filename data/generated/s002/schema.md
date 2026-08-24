# Daily energy delivered on six residential distribution feeders across three substations, January-December 2023, examined by customer class and weather

The distribution planning group of a mid-sized municipal electric utility assembled this table from SCADA feeder meters and the customer information system for calendar year 2023. Each record is one settled daily reading for one feeder and one customer class, joined to the substation weather station and to the estimated technical loss factor. The dataset was built in early 2024 to support the annual load forecast, to see which feeders approach their thermal rating on hot afternoons, and to quantify how strongly residential energy responds to heating and cooling degree days before the utility commits to a feeder reconductoring budget.

`s002` -- 450 rows, 13 columns

## Dimensions

```mermaid
flowchart LR
  subgraph network
    substation[substation<br/>3]
    feeder[feeder<br/>6]
  end
  subgraph customer
    customer_class[customer_class<br/>3]
  end
  subgraph calendar
    reading_date[/reading_date<br/>365/]
    day_of_week[day_of_week<br/>7]
    month[month<br/>12]
    quarter[quarter<br/>4]
    is_weekend[is_weekend<br/>2]
  end
  substation --> feeder
  reading_date -.-> day_of_week
  reading_date -.-> month
  reading_date -.-> quarter
  reading_date -.-> is_weekend
```

## Numeric columns

```mermaid
flowchart LR
  air_temperature([air_temperature<br/>degrees Celsius])
  energy_delivered([energy_delivered<br/>MWh])
  peak_demand([peak_demand<br/>MW])
  technical_loss_rate([technical_loss_rate<br/>percent])
  metered_customers([metered_customers<br/>customers])
  air_temperature --> energy_delivered
  energy_delivered --> peak_demand
  peak_demand --> technical_loss_rate
```

## Intents

```mermaid
flowchart LR
  i0(["comparison<br/>AVG"])
  i0 --> feeder
  i0 --> energy_delivered
  i1(["trend<br/>SUM"])
  i1 --> reading_date
  i1 --> energy_delivered
  i2(["relation<br/>NONE"])
  i2 --> air_temperature
  i2 --> energy_delivered
  i3(["composition<br/>SUM"])
  i3 --> substation
  i3 --> customer_class
  i3 --> energy_delivered
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

Densest two-column cross: substation x is_weekend at 75.0 rows per cell.

Gaps:

- No dimension is declared ordered="stage", so no process chart can be drawn. If this scenario has genuine sequential stages, declare that dimension as a stage; if it does not, leave it out rather than inventing one.
