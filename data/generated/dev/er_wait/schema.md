# Emergency department visits and wait times at three metro hospitals, Jan-Jun 2024

The county health department compiled per-visit records from three hospitals for January through June 2024 to assess a new triage diversion policy.

`er_wait` -- 900 rows, 11 columns

## Dimensions

```mermaid
flowchart LR
  subgraph entity
    hospital[hospital<br/>3]
    department[department<br/>4]
  end
  subgraph triage
    severity[severity<br/>3]
  end
  subgraph calendar
    visit_date[/visit_date<br/>182/]
    day_of_week[day_of_week<br/>7]
    month[month<br/>6]
    quarter[quarter<br/>2]
    is_weekend[is_weekend<br/>2]
  end
  hospital --> department
  visit_date -.-> day_of_week
  visit_date -.-> month
  visit_date -.-> quarter
  visit_date -.-> is_weekend
```

## Numeric columns

```mermaid
flowchart LR
  wait_minutes([wait_minutes<br/>minutes])
  cost([cost<br/>USD])
  satisfaction([satisfaction<br/>points])
  wait_minutes --> cost
  wait_minutes --> satisfaction
```

## Intents

```mermaid
flowchart LR
  i0(["comparison<br/>AVG"])
  i0 --> hospital
  i0 --> wait_minutes
  i1(["trend<br/>AVG"])
  i1 --> visit_date
  i1 --> wait_minutes
  i2(["relation<br/>NONE"])
  i2 --> wait_minutes
  i2 --> satisfaction
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

Densest two-column cross: hospital x quarter at 150.0 rows per cell.

Gaps:

- No dimension is declared ordered="stage", so no process chart can be drawn. If this scenario has genuine sequential stages, declare that dimension as a stage; if it does not, leave it out rather than inventing one.
