# Actuarial present value

Actuarial present value engine. Discount expected cash flows with mortality, survival, and risk adjustment for insurance and benefit obligations, generalising IFRS 17 (fulfilment cash flows), IAS 19 (employee benefits), IFRS 2 (share-based payments), and IAS 37 (provisions). Use this for regulated IFRS/HKFRS obligations only; it does NOT do generic project or scenario probability weighting (use calculate_expected_value).

```mermaid
flowchart TD
  T[Calculate Actuarial Pv]
  T --> calculate_actuarial_pv_ifrs17_gmm["ifrs17_gmm (income)"]
  calculate_actuarial_pv_ifrs17_gmm -. cites .-> IVS_105_A10[IVS.105.A10]
  calculate_actuarial_pv_ifrs17_gmm -. cites .-> IFRS_17_32[IFRS.17.32]
  T --> calculate_actuarial_pv_ifrs17_paa["ifrs17_paa (income)"]
  calculate_actuarial_pv_ifrs17_paa -. cites .-> IVS_105_A10[IVS.105.A10]
  calculate_actuarial_pv_ifrs17_paa -. cites .-> IFRS_17_32[IFRS.17.32]
  T --> calculate_actuarial_pv_ifrs17_vfa["ifrs17_vfa (income)"]
  calculate_actuarial_pv_ifrs17_vfa -. cites .-> IVS_105_A10[IVS.105.A10]
  calculate_actuarial_pv_ifrs17_vfa -. cites .-> IFRS_17_32[IFRS.17.32]
  T --> calculate_actuarial_pv_ias19_puc["ias19_puc (income)"]
  calculate_actuarial_pv_ias19_puc -. cites .-> IVS_105_A10[IVS.105.A10]
  calculate_actuarial_pv_ias19_puc -. cites .-> IAS_19_67[IAS.19.67]
  T --> calculate_actuarial_pv_ias37_provision["ias37_provision (income)"]
  calculate_actuarial_pv_ias37_provision -. cites .-> IVS_220_A10[IVS.220.A10]
  calculate_actuarial_pv_ias37_provision -. cites .-> IAS_37_36[IAS.37.36]
```

## `ifrs17_gmm`

IFRS 17 general measurement model

**Formula:** fulfilment cash flows + risk adjustment + CSM

**Approach:** income  
**Solution:** closed_form

**Inputs**

| Name | Type | Description |
|------|------|-------------|
| `cash_flows` | array | Projected cash flows in reporting currency, indexed t=1..n. |
| `discount_rate` | number | Discount rate as a decimal (0.10 = 10%); pre-tax when method=viu_pre_tax. |
| `risk_adjustment` | number | Explicit risk adjustment for non-financial risk. |

**Standards (verbatim)**

- **IVS.105.A10** — Valuation models
  > 30.01 The valuer must determine that the valuation model is appropriate, which for the purposes of IVS 105 Valuation Models means "fit for purpose" in terms of assets or liabilities being valued, the scope of work and the valuation method. The valuer must apply professional judgement to balance the characteristics of a valuation model in order to choose the most appropriate valuation model.
  > — International Valuation Standards Council (IVSC) (source/ivs-2025.md#ivs-105-valuation-models)
- **IFRS.17.32** — Fulfilment cash flows
  > The fulfilment cash flows comprise: (a) estimates of future cash flows; (b) an adjustment to reflect the time value of money and the financial risks related to the future cash flows, to the extent that the financial risks are not included in the estimates of future cash flows; and (c) a risk adjustment for non-financial risk.
  > — IFRS Foundation (source/ifrs-17.md#paragraph-32)

**IVS ↔ IFRS/IAS divergences**

- `risk_adjustment`: IVS — IVS 105 model risk and uncertainty; IFRS/IAS — IFRS 17.32 explicit risk adjustment for non-financial risk

**Risks & limits**

- Deterministic model: the result is a point value with no modelled distribution; input error and model error are not quantified here.
- IVS/IFRS divergence on 'risk_adjustment': the two regimes treat this differently (IVS 105 model risk and uncertainty vs IFRS 17.32 explicit risk adjustment for non-financial risk); the choice is the caller's, not a default.
- Standards alignment is declared per method; see the cited clauses.

## `ifrs17_paa`

IFRS 17 premium allocation approach

**Formula:** PAA liability for remaining coverage

**Approach:** income  
**Solution:** closed_form

**Inputs**

| Name | Type | Description |
|------|------|-------------|
| `premiums` | number | Premiums in reporting currency. |
| `claims_cash` | number | Expected claims in reporting currency. |
| `acquisition_cash_flows` | number | Acquisition cash flows in reporting currency. |
| `coverage_periods` | integer | Coverage periods for the PAA (>=1). |

**Standards (verbatim)**

- **IVS.105.A10** — Valuation models
  > 30.01 The valuer must determine that the valuation model is appropriate, which for the purposes of IVS 105 Valuation Models means "fit for purpose" in terms of assets or liabilities being valued, the scope of work and the valuation method. The valuer must apply professional judgement to balance the characteristics of a valuation model in order to choose the most appropriate valuation model.
  > — International Valuation Standards Council (IVSC) (source/ivs-2025.md#ivs-105-valuation-models)
- **IFRS.17.32** — Fulfilment cash flows
  > The fulfilment cash flows comprise: (a) estimates of future cash flows; (b) an adjustment to reflect the time value of money and the financial risks related to the future cash flows, to the extent that the financial risks are not included in the estimates of future cash flows; and (c) a risk adjustment for non-financial risk.
  > — IFRS Foundation (source/ifrs-17.md#paragraph-32)

**Risks & limits**

- Deterministic model: the result is a point value with no modelled distribution; input error and model error are not quantified here.
- Standards alignment is declared per method; see the cited clauses.

## `ifrs17_vfa`

IFRS 17 variable fee approach

**Formula:** VFA fulfilment cash flows

**Approach:** income  
**Solution:** closed_form

**Inputs**

| Name | Type | Description |
|------|------|-------------|
| `cash_flows` | array | Projected cash flows in reporting currency, indexed t=1..n. |
| `discount_rate` | number | Discount rate as a decimal (0.10 = 10%); pre-tax when method=viu_pre_tax. |
| `underlying_items_return` | number | Return on underlying items (decimal). |
| `risk_adjustment` | number | Explicit risk adjustment for non-financial risk. |

**Standards (verbatim)**

- **IVS.105.A10** — Valuation models
  > 30.01 The valuer must determine that the valuation model is appropriate, which for the purposes of IVS 105 Valuation Models means "fit for purpose" in terms of assets or liabilities being valued, the scope of work and the valuation method. The valuer must apply professional judgement to balance the characteristics of a valuation model in order to choose the most appropriate valuation model.
  > — International Valuation Standards Council (IVSC) (source/ivs-2025.md#ivs-105-valuation-models)
- **IFRS.17.32** — Fulfilment cash flows
  > The fulfilment cash flows comprise: (a) estimates of future cash flows; (b) an adjustment to reflect the time value of money and the financial risks related to the future cash flows, to the extent that the financial risks are not included in the estimates of future cash flows; and (c) a risk adjustment for non-financial risk.
  > — IFRS Foundation (source/ifrs-17.md#paragraph-32)

**Risks & limits**

- Deterministic model: the result is a point value with no modelled distribution; input error and model error are not quantified here.
- Standards alignment is declared per method; see the cited clauses.

## `ias19_puc`

IAS 19 projected unit credit defined-benefit obligation

**Formula:** PV of benefit obligation

**Approach:** income  
**Solution:** closed_form

**Inputs**

| Name | Type | Description |
|------|------|-------------|
| `projected_benefits` | array | Projected benefits per service year. |
| `discount_rate` | number | Discount rate as a decimal (0.10 = 10%); pre-tax when method=viu_pre_tax. |
| `attribution_years` | integer | Years of service for attribution (>=1). |

**Standards (verbatim)**

- **IVS.105.A10** — Valuation models
  > 30.01 The valuer must determine that the valuation model is appropriate, which for the purposes of IVS 105 Valuation Models means "fit for purpose" in terms of assets or liabilities being valued, the scope of work and the valuation method. The valuer must apply professional judgement to balance the characteristics of a valuation model in order to choose the most appropriate valuation model.
  > — International Valuation Standards Council (IVSC) (source/ivs-2025.md#ivs-105-valuation-models)
- **IAS.19.67** — Projected unit credit method
  > The projected unit credit method (sometimes known as the accrued benefit method pro-rated on service or as the benefit/years of service method) sees each period of service as giving rise to an additional unit of benefit entitlement (see paragraphs 70-74) and measures each unit separately to build up the final obligation (see paragraphs 68-70).
  > — IFRS Foundation (source/ias-19.md#paragraph-67)

**IVS ↔ IFRS/IAS divergences**

- `attribution`: IVS — IVS 105 valuation model (no prescribed benefit attribution); IFRS/IAS — IAS 19.67 projected unit credit attribution per period of service

**Risks & limits**

- Deterministic model: the result is a point value with no modelled distribution; input error and model error are not quantified here.
- IVS/IFRS divergence on 'attribution': the two regimes treat this differently (IVS 105 valuation model (no prescribed benefit attribution) vs IAS 19.67 projected unit credit attribution per period of service); the choice is the caller's, not a default.
- Standards alignment is declared per method; see the cited clauses.

## `ias37_provision`

IAS 37 provision: expected value, discounted

**Formula:** IAS 37 best estimate, discounted

**Approach:** income  
**Solution:** closed_form

**Inputs**

| Name | Type | Description |
|------|------|-------------|
| `outcomes` | array | Outcome values aligned with probabilities. |
| `probabilities` | array | Cumulative success probability per period in [0,1], aligned with cash_flows. |
| `discount_rate` | number | Discount rate as a decimal (0.10 = 10%); pre-tax when method=viu_pre_tax. |
| `periods` | integer | Number of periods n (>=1). |

**Standards (verbatim)**

- **IVS.220.A10** — Non-financial liability (Bottom-Up)
  > 60.04 Under the Bottom-Up Method, the non-financial liability is measured as the costs required to fulfil the performance obligation, plus a reasonable mark-up on those costs, discounted to present value. These costs may or may not include certain overhead items.
  > — International Valuation Standards Council (IVSC) (source/ivs-2025.md#ivs-220-non-financial-liabilities)
- **IAS.37.36** — Best estimate of a provision
  > The amount recognised as a provision shall be the best estimate of the expenditure required to settle the present obligation at the end of the reporting period.
  > — IFRS Foundation (source/ias-37.md#paragraph-36)

**IVS ↔ IFRS/IAS divergences**

- `measurement_objective`: IVS — IVS 220 Bottom-Up: costs to fulfil plus a reasonable mark-up; IFRS/IAS — IAS 37.36 best estimate of the expenditure required to settle (no profit margin)

**Risks & limits**

- Deterministic model: the result is a point value with no modelled distribution; input error and model error are not quantified here.
- IVS/IFRS divergence on 'measurement_objective': the two regimes treat this differently (IVS 220 Bottom-Up: costs to fulfil plus a reasonable mark-up vs IAS 37.36 best estimate of the expenditure required to settle (no profit margin)); the choice is the caller's, not a default.
- Standards alignment is declared per method; see the cited clauses.
