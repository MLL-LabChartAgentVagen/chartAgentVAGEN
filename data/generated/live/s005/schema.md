# Preferential trade agreement origin claims, duty forgone, and customs compliance verifications across major entry ports, 2022–2023

The national customs administration maintains this registry of monthly preferential tariff filings to monitor revenue forgone under free trade agreements, evaluate origin certification compliance across tariff headings, and track claims through clearance and audit stages.

`s005` -- 800 rows, 11 columns

Drawn from `dom_0308` Preferential origin claims and duty forgone under trade agreements -- macroeconomy and trade: customs import declarations and duty amounts assessed by tariff heading and port of entry (macroeconomy and trade / registry), medium

## Dimensions

```mermaid
flowchart LR
  subgraph agreement
    trade_programme[trade_programme<br/>4]
  end
  subgraph geography
    port_region[port_region<br/>4]
    port_of_entry[port_of_entry<br/>8]
  end
  subgraph commodity
    tariff_heading[tariff_heading<br/>5]
  end
  subgraph workflow
    clearance_stage[clearance_stage<br/>4]
  end
  subgraph calendar
    declaration_month[/declaration_month<br/>24/]
    quarter[quarter<br/>8]
  end
  port_region --> port_of_entry
  declaration_month -.-> quarter
```

## Numeric columns

```mermaid
flowchart LR
  customs_value([customs_value<br/>thousand USD])
  duty_forgone([duty_forgone<br/>thousand USD])
  disallowed_amount([disallowed_amount<br/>thousand USD])
  effective_preference_pct([effective_preference_pct<br/>percent])
  customs_value --> duty_forgone
  duty_forgone --> disallowed_amount
  customs_value --> effective_preference_pct
  duty_forgone --> effective_preference_pct
```

## Intents

```mermaid
flowchart LR
  i0(["comparison<br/>SUM"])
  i0 --> trade_programme
  i0 --> duty_forgone
  i1(["trend<br/>SUM"])
  i1 --> declaration_month
  i1 --> customs_value
  i2(["process<br/>COUNT"])
  i2 --> clearance_stage
  i3(["relation<br/>NONE"])
  i3 --> customs_value
  i3 --> duty_forgone
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

Densest two-column cross: trade_programme x port_region at 50.0 rows per cell.
