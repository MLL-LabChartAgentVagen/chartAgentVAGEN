# Weekly claim turnaround performance across four regional processing centers of a national health insurer, January-December 2024

The claims operations analytics team of a national health insurer assembled this weekly batch-level extract covering all four regional processing centers for calendar year 2024. Each row is one weekly closing batch: a single center, claim type and submission channel combination that finished adjudication in that week. The data was pulled from the adjudication workflow log in January 2025 to support a service-level review, since the insurer had committed to a 14-day average turnaround and had rolled out an auto-adjudication rules engine at the start of the third quarter. Analysts wanted to know which centers were slow, whether electronic submissions really closed faster than paper, and whether turnaround was improving after the rollout.

`s000` -- 420 rows, 11 columns

## Dimensions

```mermaid
flowchart LR
  subgraph org
    region[region<br/>4]
    processing_center[processing_center<br/>7]
  end
  subgraph claim
    claim_type[claim_type<br/>4]
    submission_channel[submission_channel<br/>3]
  end
  subgraph calendar
    week_closed[/week_closed<br/>53/]
    month[month<br/>12]
    quarter[quarter<br/>4]
  end
  region --> processing_center
  week_closed -.-> month
  week_closed -.-> quarter
```

## Numeric columns

```mermaid
flowchart LR
  claims_closed([claims_closed<br/>claims/week])
  mean_cycle_time_days([mean_cycle_time_days<br/>days])
  pended_claims([pended_claims<br/>claims/week])
  auto_adjudication_rate([auto_adjudication_rate<br/>fraction])
  claims_closed --> pended_claims
  mean_cycle_time_days --> pended_claims
  mean_cycle_time_days --> auto_adjudication_rate
```

## Intents

```mermaid
flowchart LR
  i0(["comparison<br/>AVG"])
  i0 --> processing_center
  i0 --> mean_cycle_time_days
  i1(["trend<br/>AVG"])
  i1 --> week_closed
  i1 --> mean_cycle_time_days
  i2(["relation<br/>NONE"])
  i2 --> auto_adjudication_rate
  i2 --> mean_cycle_time_days
  i3(["distribution<br/>MEDIAN"])
  i3 --> submission_channel
  i3 --> mean_cycle_time_days
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

Densest two-column cross: region x submission_channel at 35.0 rows per cell.

Gaps:

- No dimension is declared ordered="stage", so no process chart can be drawn. If this scenario has genuine sequential stages, declare that dimension as a stage; if it does not, leave it out rather than inventing one.
