"""Asset-standard measurement methods (VDD A-004).

Closed-form implementations of several IVS 2025 asset-standard methods and the
IAS 36 recoverable-amount aggregation. Deterministic (closed-form); no network,
no optional backends. Each function returns a plain number; handlers wrap it in
the shared envelope.
"""

from __future__ import annotations

from typing import Sequence


def _annuity_factor(discount_rate: float, periods: int) -> float:
    if periods < 1:
        raise ValueError("periods must be >= 1")
    if discount_rate <= -1:
        raise ValueError("discount_rate must be > -1")
    return sum(1.0 / (1.0 + discount_rate) ** t for t in range(1, periods + 1))


def relief_from_royalty(
    revenue: float, royalty_rate: float, discount_rate: float, periods: int
) -> float:
    """Relief-from-royalty value (IVS 210): PV of hypothetical royalty savings.

    ``value = revenue x royalty_rate x annuity(discount_rate, periods)``.
    """
    return revenue * royalty_rate * _annuity_factor(discount_rate, periods)


def mpeem(
    cash_flows: Sequence[float],
    contributory_charges: Sequence[float],
    discount_rate: float,
) -> float:
    """Multi-period excess earnings (IVS 210): PV of earnings after CAC.

    ``value = sum_t (cash_flow_t - contributory_charge_t) / (1 + r)^t``.
    ``cash_flows`` and ``contributory_charges`` must be the same length.
    """
    flows = list(cash_flows)
    charges = list(contributory_charges)
    if len(flows) != len(charges):
        raise ValueError("cash_flows and contributory_charges must be the same length")
    if not flows:
        raise ValueError("cash_flows must be non-empty")
    return sum(
        (float(cf) - float(cc)) / (1.0 + discount_rate) ** (t + 1)
        for t, (cf, cc) in enumerate(zip(flows, charges))
    )


def with_without(
    with_cash_flows: Sequence[float],
    without_cash_flows: Sequence[float],
    discount_rate: float,
) -> float:
    """With-and-without (premium profit) value (IVS 210): PV of the increment.

    ``value = sum_t (with_t - without_t) / (1 + r)^t``; both arrays aligned.
    """
    with_flows = list(with_cash_flows)
    without_flows = list(without_cash_flows)
    if len(with_flows) != len(without_flows):
        raise ValueError("with_cash_flows and without_cash_flows must be the same length")
    if not with_flows:
        raise ValueError("cash flows must be non-empty")
    return sum(
        (float(w) - float(wo)) / (1.0 + discount_rate) ** (t + 1)
        for t, (w, wo) in enumerate(zip(with_flows, without_flows))
    )


def recoverable_amount(fair_value_less_costs_to_dispose: float, value_in_use: float) -> float:
    """Recoverable amount (IAS 36.18): higher of FVLCD and value in use."""
    return max(float(fair_value_less_costs_to_dispose), float(value_in_use))
