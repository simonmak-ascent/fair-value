# AGENTS.md

Financial valuation library (DCF/NAV/CCA, cost of capital, derivatives, credit risk, report review) aligned to IVS 2025 / IFRS. Capability spec lives in `SKILL.md`.

## Top-level API (wired, A-001)

`valuation_engine.py` is the public facade. `run_valuation(ticker, method, params=None)` (methods `dcf`/`nav`/`cca`), `run_nav`, `run_cca`, `review_report(path)`, `scan_directory(dir)`, and `get_valuation_summary(ticker)` validate inputs, lazily import the concrete `src/` implementation, and return a shared result/error envelope (`{"status": "ok", ...}` or `{"status": "error", "error": {"code", "message"}}`). Network access happens only at call time; a monkeypatchable provider seam (`_get_market_metrics`, `_get_company_info`, `_get_stock_price`, `_get_volatility`) keeps tests offline.

The concrete computation functions also live in `src/` and can be imported directly:

```python
from src.valuation.dcf import dcf_valuation
from src.cost_of_capital.wacc import calculate_wacc
from src.credit_risk.ecl import calculate_ecL
```

## Layout

- `src/valuation/` — `dcf.py`, `nav.py`, `multiples.py` (CCA), `sensitivity.py`
- `src/cost_of_capital/` — `wacc.py`, `fama_french.py`, `kmv.py`
- `src/derivatives/` — `options.py`, `swaps.py`, `convertible_bonds.py`, `futures.py`, `greeks.py`
- `src/credit_risk/` — `ecl.py`, `pd_models.py`
- `src/report_review/` — `excel_analyzer.py`, `pdf_analyzer.py`, `word_analyzer.py`, `image_analyzer.py`
- `src/output/` — `report_formatter.py`, `chart_data.py`
- `src/fetch_data.py` — Yahoo Finance via `yfinance` (network at call time only)
- `src/constants.py` — standards refs, rating→PD, LGD tables

Subpackage `__init__.py` files are mostly empty; `src/valuation/__init__.py` re-exports its functions. Import concrete modules, not the package root.

## Commands

```bash
pip install -r requirements.txt   # no pyproject.toml/setup.py — pip, not uv/pnpm
python -m pytest                   # all tests (pytest.ini: testpaths=tests)
python -m pytest tests/test_dcf.py::test_dcf_valuation   # one test
```

Per the global compute policy, run tests via the box, e.g. `cs run "python -m pytest"`. `cs provision` uses `uv sync`, which fails here (no `pyproject.toml`); install deps with pip on the box instead. No lint/typecheck/formatter config exists in-repo.

## Import & runtime quirks

- Run from the repo root; tests do `sys.path.insert(0, repo_root)` and import absolute `src....`. `valuation_engine.py` does the same.
- `import src` runs `src/__init__.py`, which imports `fetch_data` → `yfinance`. So **yfinance must be installed even for the pure-math tests**, which themselves make no network calls.
- Internal relative imports exist (e.g. `from ..fetch_data import ...` in `multiples.py`), so import modules as `src.<pkg>.<mod>`.

## Optional dependencies (all guarded with try/except)

Tests do **not** require any of these:
- QuantLib — `derivatives/options.py` falls back to native NumPy/SciPy Black-Scholes.
- `pandas_datareader` — FF5 factor fetch fallback in `fama_french.py`.
- `pytesseract` / `easyocr` — OCR fallbacks in `image_analyzer.py`.

## Deliberate quirk to preserve

`src/credit_risk/ecl.py` spells its functions with a capital L: `calculate_ecL`, `calculate_12m_ecL`, `calculate_lifetime_ecL`, `calculate_ecL_portfolio`. Tests import these exact names — do not "correct" the casing without updating tests.

## Other

- `README.md` points to `IMPLEMENTATION_PLAN.md`, which is not in the repo (removed from tracking) — ignore that reference.
- Generated reports/models are written to `~/docgen_output/` (see `SKILL.md`).
- Public, MIT-licensed repo (`LICENSE`); keep new files consistent with the existing code.
