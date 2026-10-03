# Examples

Worked Hong Kong market examples live in `examples/hk_examples.py` and run
offline against the engine (Monte-Carlo methods are seeded, so output is
deterministic):

```bash
python examples/hk_examples.py
```

| Scenario | Method | Value (illustrative) |
|----------|--------|----------------------|
| HKD convertible bond, 3y with a 2y issuer call at par | `calculate_convertible_bond` `lattice_tsf` | ~112.4 |
| HKEX inline range warrant (90–110, pays 1) | `calculate_structured_product` `inline_warrant` | ~4231.7 |
| Loss-making listing, margin-ramp DCF | `calculate_loss_making_company` `margin_ramp_dcf` | ~24.0 per share |

Each call returns the shared result envelope. The examples are also exercised
by the test suite, so they stay in step with the registry.
