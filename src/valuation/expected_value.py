"""Expected-value routines: truncated-normal moments, simulation, decision trees."""

from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np
from scipy.stats import norm

_SEED = 12345
_ITER_DEFAULT_CAP = 200000


def continuous(
    distribution: str, mean: float, std: float, lower: float, upper: float
) -> Dict[str, Any]:
    if distribution == "uniform":
        prob = max(min(upper, 1.0) - max(lower, 0.0), 0.0)
        if prob <= 0:
            return {"value": 0.0, "probability": 0.0}
        value = (max(lower, 0.0) + min(upper, 1.0)) / 2
        return {"value": value, "probability": prob}

    if distribution not in ("normal", "lognormal"):
        raise ValueError("distribution must be normal, lognormal or uniform")
    sigma = std
    if sigma <= 0:
        inside = lower <= mean <= upper
        return {"value": mean if inside else 0.0, "probability": 1.0 if inside else 0.0}

    a = (lower - mean) / sigma
    b = (upper - mean) / sigma
    fa = float(norm.cdf(a)) if math.isfinite(a) else 0.0
    fb = float(norm.cdf(b)) if math.isfinite(b) else 1.0
    prob = fb - fa
    if prob <= 1e-15:
        return {"value": 0.0, "probability": 0.0}
    pdf_a = float(norm.pdf(a)) if math.isfinite(a) else 0.0
    pdf_b = float(norm.pdf(b)) if math.isfinite(b) else 0.0
    value = mean + sigma * (pdf_a - pdf_b) / prob
    return {"value": value, "probability": prob}


def monte_carlo(
    iterations: int,
    distributions: List[Dict[str, Any]],
    base_params: Dict[str, float],
    seed: int,
) -> Dict[str, Any]:
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    iterations = min(int(iterations), _ITER_DEFAULT_CAP)
    rng = np.random.default_rng(int(seed))
    outcome = np.zeros(iterations)
    for factor in distributions:
        kind = factor.get("distribution", "normal")
        weight = float(factor.get("weight", 1.0))
        if kind == "normal":
            draw = rng.normal(float(factor["mean"]), float(factor["std"]), iterations)
        elif kind == "uniform":
            draw = rng.uniform(float(factor["low"]), float(factor["high"]), iterations)
        elif kind == "lognormal":
            draw = rng.lognormal(float(factor["mean"]), float(factor["std"]), iterations)
        else:
            raise ValueError(f"unsupported distribution {kind!r}")
        outcome += weight * draw
    outcome += sum(float(v) for v in base_params.values())

    p = np.percentile(outcome, [5, 25, 50, 75, 95])
    mean = float(outcome.mean())
    std = float(outcome.std(ddof=1)) if iterations > 1 else 0.0
    return {
        "value": mean,
        "mean": mean,
        "median": float(np.median(outcome)),
        "std": std,
        "percentiles": {
            "p5": float(p[0]),
            "p25": float(p[1]),
            "p50": float(p[2]),
            "p75": float(p[3]),
            "p95": float(p[4]),
        },
        # Statistical characteristics consumed by the shared result envelope.
        "statistics": {
            "solution_type": "simulation",
            "distribution": "empirical",
            "centre": mean,
            "sigma": std,
            "percentiles": {
                "p05": float(p[0]),
                "p50": float(p[2]),
                "p95": float(p[4]),
            },
            "samples": int(iterations),
            "seed": int(seed),
        },
    }


def decision_tree(tree: Dict[str, Any]) -> Dict[str, Any]:
    def roll(node: Dict[str, Any]) -> float:
        kind = node.get("type", "terminal")
        if kind == "terminal":
            return float(node.get("value", 0.0))
        branches = node.get("branches", [])
        if kind == "chance":
            total = sum(float(b.get("probability", 0.0)) for b in branches)
            if abs(total - 1.0) > 1e-6:
                raise ValueError(f"chance node probabilities must sum to 1 (got {total})")
            return sum(float(b.get("probability", 0.0)) * roll(b["node"]) for b in branches)
        if kind == "decision":
            if not branches:
                raise ValueError("decision node requires at least one branch")
            return max(roll(b["node"]) for b in branches)
        raise ValueError(f"unknown node type {kind!r}")

    value = roll(tree)
    return {"value": value}
