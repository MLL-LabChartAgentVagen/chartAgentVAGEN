# Protected species incident filings, investigation durations, and penalty assessments across regional enforcement registries, 2023–2024

The National Wildlife Law Enforcement Division maintains an incident and compliance registry logging protected species violations, strandings, and unauthorized habitat disturbances across regional field offices. Field agents and registry intake officers recorded case progression stages, field response times, staff investigation hours, and assessed civil penalties from January 2023 through December 2024 to evaluate enforcement pipeline efficiency and backlog resolution.

`s000` -- 360 rows, 10 columns

Drawn from `dom_0451` Illegal-take case backlog and closure counts -- climate and environment: protected species incident filings logged by field offices — strandings, illegal-take cases and habitat-disturbance reports — with case volumes, response times and enforcement outcomes by district and month (climate and environment / registry), simple

## Dimensions

```mermaid
flowchart LR
  subgraph jurisdiction
    region[region<br/>3]
    district[district<br/>9]
  end
  subgraph incident
    incident_type[incident_type<br/>4]
  end
  subgraph workflow
    case_stage[case_stage<br/>5]
  end
  subgraph calendar
    filing_month[/filing_month<br/>24/]
    quarter[quarter<br/>8]
  end
  region --> district
  filing_month -.-> quarter
```

## Numeric columns

```mermaid
flowchart LR
  response_time_days([response_time_days<br/>days])
  penalty_assessed_usd([penalty_assessed_usd<br/>USD])
  investigation_hours([investigation_hours<br/>hours])
  evidence_sufficiency_score([evidence_sufficiency_score<br/>points])
```

## Intents

```mermaid
flowchart LR
  i0(["process<br/>COUNT"])
  i0 --> case_stage
  i1(["comparison<br/>AVG"])
  i1 --> incident_type
  i1 --> penalty_assessed_usd
  i2(["trend<br/>SUM"])
  i2 --> filing_month
  i2 --> investigation_hours
  i3(["relation<br/>NONE"])
  i3 --> response_time_days
  i3 --> evidence_sufficiency_score
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

Densest two-column cross: region x incident_type at 30.0 rows per cell.
