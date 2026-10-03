# AGENTS.md

Financial valuation library + MCP server (DCF/NAV/CCA, cost of capital, derivatives, credit risk, report review) aligned to IVS 2025 / IFRS. Capability spec lives in `SKILL.md`; local immutable constraints (gitignored) live in `constitution.md`.

## Commands (CI parity — run via the compute box)

CI is the executable source of truth (`.github/workflows/ci.yml`):

```bash
pip install -r requirements.txt -r requirements-dev.txt   # setup (pip; repo is not uv-managed, no uv.lock)
ruff check .                                               # lint (config in pyproject.toml)
mypy                                                       # type-check (no args; reads `files` from pyproject)
python -m pytest                                           # all tests (pytest.ini: testpaths=tests)
python -m pytest tests/test_dcf.py::test_dcf_valuation     # one test
python -m pytest --cov=src --cov=mcp_server --cov=valuation_engine --cov-report=term-missing
python scripts/check_conformance.py                        # registry + surface gate
python -m tdqs lint --command "python -m mcp_server.server" --fail-on error
pip install . && python -c "import mcp_server.server as s; s.build_server()"   # packaging/smoke
mkdocs build --strict                                      # docs
```

Per global policy, never run these locally: `cs run "ruff check . && mypy && python -m pytest"`. `cs provision`/`uv sync` does not fit this repo (pip + `requirements*.txt`, no `uv.lock`) — install deps with pip on the box.

`mypy` only checks `mcp_server`, `valuation_engine.py`, and `src/output` (pyproject `files`); type errors in the rest of `src/` are not gated. Ruff `E501` is ignored despite `line-length = 100`.

## Layout

- `valuation_engine.py` — public facade + CLI. Validates, lazily imports `src/`, returns the shared envelope.
- `src/` — computation only: `valuation/`, `cost_of_capital/`, `derivatives/`, `credit_risk/`, `report_review/`, `output/`, `fetch_data.py`, `constants.py`.
- `mcp_server/` — FastMCP server. `method_spec.py` + `method_spec_seed.py` are the single source of truth for the 16 `calculate_*` tools and their 123 methods; `tool_surface.py` derives the surface from the registry; `engine.py` validates and dispatches; `server.py` renders it; `asgi.py` is the hosted ASGI app; `catalog.py`/`prompts.py` serve the `valuation://methods` and `valuation://standards` resources and guided prompts.
- `api/index.py` — Vercel Python entrypoint (imports `mcp_server.asgi:app`). `Dockerfile`/`docker-compose.yml` run `fair-value-mcp --http`.
- `tests/` — pytest; `tests/conftest.py` holds the offline fixtures/seam.
- `scripts/check_conformance.py` — CI needs no network and must exit 0.

## Envelope contract

Every public result uses `src/output/result.py` `ok()`/`error()`. Success envelopes must carry `status, method, value, assumptions, formula_ref, data_timestamp, steps, disclaimer` (`OK_REQUIRED_FIELDS`); `missing_ok_fields()` checks this. Do not invent a new return shape.

## MCP tool surface

Edit `mcp_server/method_spec_seed.py` (method tables) and `mcp_server/method_spec.py` (parameter vocabulary), not `server.py`, to add/change tools; `tool_surface.py` derives the surface from the registry. `build_server()` requires the `[mcp]` extra (fastmcp); importing `server.py` is side-effect free and raises only on `build_server()`. Tests enforce surface invariants: every parameter has a `description`, every tool has all four annotations, a non-empty output schema, and a title longer than its name (`tests/test_tdqs_surface.py`). Every registered method must be implemented or explicitly listed as deferred in `scripts/check_conformance.py` (currently 2 convertible-bond discretizations needing QuantLib). Handlers auto-wrap the shared envelope; expected failures become error envelopes, never raises.

## Packaging & release invariants

- PEP 621 `pyproject.toml` is authoritative; `fair-value-mcp = mcp_server.server:main` is the console script.
- **Version lockstep:** `server.json` `version` must equal `pyproject.toml` `version` (`tests/test_manifest.py::test_version_locked_to_pyproject`). Bump both `version` fields in `server.json` (top-level and `packages[0]`).
- `README.md` must contain `mcp-name: io.github.simonmak-ascent/fair-value`; `assets/icon.svg` must exist (manifest tests).
- `.vercelignore` excludes `pyproject.toml`; Vercel uses `requirements.txt` (`includeFiles` in `vercel.json`).
- Release is tag-triggered (`release.yml`): `python -m build` → PyPI → MCP Registry. Don't publish by hand.

## Import & runtime quirks

- Run from the repo root. Tests, `valuation_engine.py`, and `check_conformance.py` insert the root on `sys.path`; import `src.<pkg>.<mod>` and top-level `mcp_server`/`valuation_engine`. Internal relative imports (e.g. `from ..fetch_data import ...`) require that form.
- `import src` runs `src/__init__.py`, which imports `fetch_data` → `yfinance`. So **yfinance must be installed even for pure-math tests**, which make no network calls.
- Network/data fetching happens only at call time in `src/fetch_data.py`; never at import time. Tests monkeypatch `valuation_engine._get_market_metrics`/`_get_company_info`/`_get_stock_price`/`_get_volatility`.

## Data & report rules

- Missing source data stays absent/NULL — never synthesize a plausible value (`fetch_data` omits missing keys; `tests/test_fetch_provenance.py` guards this). Never hardcode PD/LGD/ratings outside `src/constants.py`.
- Report review runs guards before parsing: macro-enabled Office files are refused and spreadsheet formulas invoking remote access (WEBSERVICE/IMPORTDATA/DDE…) are flagged (`src/report_review/guards.py`). Never execute embedded macros/scripts.
- No `print()` in `src/` (use `logging`); no bare `except:` (optional-import guards set an `*_AVAILABLE` flag).

## Optional dependencies (all guarded with try/except; tests need none)

`requirements-optional.txt`: QuantLib (native NumPy/SciPy Black-Scholes fallback in `derivatives/options.py`), `pandas_datareader` (FF5 fallback), `pytesseract`/`easyocr` (OCR fallbacks), plus openpyxl/pdfplumber/python-docx for report review. Observability: `sentry-sdk` is a no-op unless `SENTRY_DSN` is set.

## Deliberate quirk to preserve

`src/credit_risk/ecl.py` spells its functions with a capital L: `calculate_ecL`, `calculate_12m_ecL`, `calculate_lifetime_ecL`, `calculate_ecL_portfolio`. Tests import these exact names — do not "correct" the casing without updating tests.

## Other

- Generated reports/models go to `~/docgen_output/` (see `SKILL.md`).
- `vdd/` and `constitution.md` are gitignored local artifacts, not published.
- Public MIT repo (`LICENSE`); keep new files consistent with the existing code.
