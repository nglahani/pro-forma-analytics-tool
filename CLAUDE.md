# CLAUDE.md

> **Operational Guide for Claude Code** — Spec‑first, architecture‑faithful, test‑driven development for the pro‑forma analytics platform.

---

## 0) Golden Rules (Read First)

1. **Spec before code.** Produce `requirements.md` → `design.md` → `tasks.md` for every feature. Do not write code until the spec is approved.
2. **Honor Clean Architecture.** Domain/application/infrastructure/presentation layering is inviolable. No cross‑layer leaks.
3. **TDD/BDD only.** Write failing tests first. Keep tests green as you implement. Maintain ≥82% coverage.
4. **Ask clarifying questions early.** If anything is ambiguous, stop and ask. Document answers immediately.
5. **No broken CI.** Never bypass failing checks. Fix locally, then push. Treat warnings as errors.
6. **Keep docs current.** Update this file and `/docs/*` whenever behavior or interfaces change.

---

## 1) Repository Overview (for Orientation)

**pro‑forma‑analytics‑tool** — A production‑ready real‑estate DCF analysis platform using Prophet forecasting and Monte Carlo simulation.

### Core Capabilities

- **4‑Phase DCF Engine:** Assumptions → Initial Numbers → Cash Flow → Financial Metrics
- **Forecasting:** Prophet‑based projections on key pro‑forma parameters
- **Monte Carlo:** 500+ scenarios with economic correlations
- **Investment Analytics:** NPV, IRR, equity multiple, risk/terminal value
- **Data Infra:** 4 SQLite DBs with validated historical data

### Technical Architecture (Clean Architecture)

```
src/
├─ domain/              # Business logic (no external deps)
│  ├─ entities/         # Immutable business entities
│  └─ repositories/     # Abstract repository interfaces
├─ application/         # Use case orchestration
│  └─ services/         # DCF/forecast/MC services
├─ infrastructure/      # External concerns (SQLite, DI)
│  ├─ repositories/
│  └─ container.py
└─ presentation/        # Visualization components
```

**Key Services:** `DCFAssumptionsService`, `InitialNumbersService`, `CashFlowProjectionService`, `FinancialMetricsService`, `ForecastingService`, `MonteCarloService`

### Data Stores

- `market_data.db` – national indicators
- `property_data.db` – MSA rent & opex
- `economic_data.db` – regional growth & lending
- `forecast_cache.db` – Prophet & Monte Carlo cache

### Environment & Config

- `PRO_FORMA_ENV` controls environment (dev/test/prod)
- Secrets via environment variables (e.g., `FRED_API_KEY`)
- FastAPI‑ready settings (CORS/rate limiting/auth)

---

## 2) Operating Modes for Claude Code

**Default: Spec Mode**

- Deliver `requirements.md`, `design.md`, `tasks.md` under `.kiro/specs/{feature}/`.
- Block coding until user approves the spec.

**Implement Mode** (after spec approval)

- Generate code as **unified diffs** or precise **patch plans** per task.
- For each commit:
  - Add/extend tests → run tests → implement → refactor → re‑run tests.
  - Provide commands to run the same checks locally.

**Refactor Mode**

- Identify code smells and architecture drifts. Propose minimal, safe refactors with tests proving behavioral equivalence.

**Debug Mode**

- Form 3–5 hypotheses. Add targeted logs/tests to isolate root cause. Propose surgical fix. Prove with tests.

**Doc Mode**

- Update `/docs` and this file when APIs, calculations, parameters, or workflows change.

---

## 3) Kiro‑Style Spec‑Driven Development

Each feature follows three artifacts and hard gates:

### Phase 1 — `requirements.md` (Definition of Ready)

- **User story(ies)**: “As a [role], I want [feature], so that [benefit].”
- **Acceptance criteria (EARS):** `WHEN … THEN system SHALL …`
- **Out‑of‑scope** and **assumptions**.
- **Open questions** (to be resolved before design).
- **Approval Gate:** All acceptance criteria are testable; ambiguities resolved.

### Phase 2 — `design.md`

- **Architecture placement** (domain/app/infra), dependency flow, interfaces.
- **Data model changes** (schema/migrations), validation rules.
- **Algorithms & formulas** (e.g., DCF, IRR, MC distributions, correlations).
- **Error handling & edge cases**.
- **Testing strategy**: unit/integration/perf/architecture tests.
- **Non‑functionals:** performance, security, compatibility.
- **Approval Gate:** Design maps 1‑to‑1 to requirements; no layer violations.

### Phase 3 — `tasks.md`

- Numbered checklist (1, 1.1, 1.2…).
- Each task references the requirement(s) it fulfills.
- Include test additions & doc updates.
- **Exit Gate (Definition of Done):**
  - All tasks complete; tests pass locally & in CI; coverage ≥82%.
  - Docs updated; architecture validators clean; no perf regression.

---

## 4) Change Playbooks

### A) Add a New **Pro‑Forma Parameter** or **Metric**

**Impact map**: `config/parameters.py` → DB schema in `data/databases/` → `forecasting/prophet_engine.py` → `monte_carlo/simulation_engine.py` (correlations) → mapping in `src/application/services/dcf_assumptions_service.py` → consumers (e.g., `FinancialMetricsService`). **Tests**: unit for mapping & metrics, integration (complete workflow), update performance/edge tests as needed. **Risks**: inconsistent defaults, missing cache invalidation, derived metrics drift.

### B) Change **DCF Calculations**

**Impact**: new/updated entities in `src/domain/entities/` → application services → metrics/reporting. **Tests**: golden cases vs. benchmarks; edge cases; integration. **Risks**: breaking financial invariants; rounding/precision; time‑horizon assumptions.

### C) Update **Monte Carlo** or **Forecasting**

**Impact**: distributions, correlations, scenario classification, Prophet configs, cache. **Tests**: distribution shape tests, correlation assertions, determinism for seeds, perf. **Risks**: non‑determinism flaking tests; perf regressions; invalid cached forecasts.

### D) Introduce a **New Application Service**

**Impact**: service module under `src/application/services/`, DI registration in `infrastructure/container.py`, potential new domain entities. **Tests**: unit per public method; integration to prove orchestration; architecture compliance. **Risks**: leaking infra concerns into app/domain; wide interfaces; untyped boundaries.

### E) **Database/Schema** Change

**Impact**: migrations, repo interfaces, data managers, seed/caches. **Tests**: migration up/down; backward compatibility; repo contract tests. **Risks**: data loss; mismatched schema vs. entities; long‑running migrations.

---

## 5) TDD/BDD Implementation Checklist

-

**Quality Gates (must pass locally before push):**

```bash
# Tests & coverage
pytest --cov=src --cov=core --cov=monte_carlo --cov-fail-under=82 -q
# End‑to‑end demo
python demo_end_to_end_workflow.py
# Format, lint, type
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
mypy src/
# Architecture & docs validity
python scripts/validate_architecture.py
python scripts/validate_docs.py
# Performance (no regression)
python tests/performance/test_irr_performance.py
```

---

## 6) CI/CD & Release Expectations

- **Linux‑focused CI** on Python 3.10–3.11.
- Enforces: coverage ≥82%, zero architecture violations, doc accuracy, no dependency vulns, perf regression detection.
- Release: semantic versioning; auto release notes; GitHub release artifacts.

**Never ignore a red pipeline.** Fix locally, re‑run, and push only when green.

---

## 7) Clarifying Questions Protocol (for Claude Code)

Trigger this protocol whenever:

- Business logic is complex, requirements have gaps, multiple interpretations exist, domain expertise is needed, or integrations are unclear.

**How to ask:**

- Be specific. Reference exact files/lines or formulas. Share your current understanding and the implications of options A vs. B. Batch related questions. After answers, immediately update the spec/docs.

**Example:**

```
I see parameter X used in Y. Should the calc be A×B/C or (A×B)/(C+D)?
My understanding: … This conflicts with … If A, we need … If B, we need …
Preferred? Any edge cases?
```

---

## 8) Documentation Standards (MECE & Centralized)

- Write for technical audiences; declarative tone; no emojis.
- Keep topics non‑overlapping; place docs in `/docs` with an index in `/docs/README.md`.
- Update docs **with** code changes; record architectural decisions; provide examples.
- Perform repo‑wide markdown review when updating docs (glob, cross‑reference, gap & redundancy analysis).

---

## 9) Commands & Developer Ergonomics

**Quick local cycle**

```bash
python -m pytest tests/ -q
python demo_end_to_end_workflow.py
```

**Linux compatibility (pre‑push)**

```bash
scripts\validate-linux.bat   # Windows
./scripts/validate-linux.sh  # Unix/Mac
# Optional Docker validation
docker build -f Dockerfile.test -t proforma-test .
```

**CI status**

```bash
gh run list --limit 3
```

---

## 10) Self‑Review Checklist (before opening a PR)

-

---

## 11) Output Formats (what Claude should produce)

- **Specs** — `.kiro/specs/{feature}/requirements.md|design.md|tasks.md` with:
  - Requirements: user stories, EARS acceptance criteria, assumptions, OOS.
  - Design: placement, interfaces, data models, algorithms, errors, tests, non‑functionals.
  - Tasks: numbered, atomic, each linked to requirements; includes tests & docs.
- **Patches** — Unified diffs for code/doc changes; highlight file paths; note any migrations.
- **Test Artifacts** — New/updated test files with clear Given/When/Then comments.
- **Docs** — Updates to `/docs`, this file, and any READMEs impacted.

---

## 12) Appendix — Known Expectations & Budgets

- End‑to‑end demo should complete cleanly. Expected financial outputs in demo scenario must remain within tested ranges. Update golden values only with justification and spec changes.
- Performance: Monte Carlo/IRR paths must not regress materially; justify any variance with data.

---

> **Use this file when prompting:** Start requests with: *“Implement {feature} using the Kiro spec workflow. Follow CLAUDE.md for Clean Architecture and TDD. Ask clarifying questions if anything is ambiguous.”*



---

## 13) Appendix A — Repository Facts (Preserved from Prior CLAUDE.md)

**Implementation Status:** Enhanced Technical Foundation (v1.6); Quality: A+ (98/100); Architecture: Clean Architecture with DDD + environment configuration; Testing: 82% coverage with **320+ test methods** across BDD/TDD; Data Coverage: 100% parameter completion; CI/CD: multi‑Python (3.10–3.11) with CLI integration; Configuration: multi‑environment with security best practices.

**Core Capabilities:** 4‑phase DCF engine; Prophet forecasting (11 parameters, 6‑year projections); Monte Carlo (500+ scenarios with economic correlations); Investment analysis (NPV, IRR, equity multiples, terminal value, risk); Data infra (4 SQLite DBs with 2,174+ historical points).

**Data Coverage Detail:** 5 MSAs (NYC, LA, Chicago, DC, Miami); 11 pro‑forma metrics (interest rates, cap rates, vacancy, rent growth, expense growth, property growth, LTV ratios, closing costs, lender reserves, etc.); Historical depth: 2010–2025 (15+ years); Geographic coverage: ≥5 MSAs for location‑dependent parameters; Validation status: statistical validation passed.

**Property Input System:** Current: `SimplifiedPropertyInput` in `src/domain/entities/property_data.py`; Legacy removed; Required fields: 7 core inputs (residential units, renovation time, commercial units, equity share, rent rates, cash percentage, etc.).

**Environment Configuration:** `config/settings.py` with dev/test/prod; `PRO_FORMA_ENV` env var; secrets via env (e.g., `FRED_API_KEY`); FastAPI‑ready (CORS, rate limiting, auth); automatic config validation.

## 14) Appendix B — Recent Enhancements (v1.6)

**Code Quality:** Fixed 100+ flake8 issues; improved TYPE\_CHECKING and forward refs; replaced bare `except`; removed redundant imports/vars.

**CI/CD Pipeline:** Debuggable GitHub Actions; Python 3.8+/3.10+ compatibility work; automated quality gates; simplified workflows; resolved pandas compat; flake8 config parsing fix.

**Testing Infrastructure:** +40 edge‑case tests; infra error‑handling tests; application extreme‑scenario tests; IRR perf tests with batch processing.

**Dev Experience:** Documentation accuracy; Windows file‑handling fixes; enhanced error tracking; automated formatting consistency.

## 15) Appendix C — Monte Carlo & Forecasting Details

**Correlation Modeling:** \~23 economic relationships (e.g., rates → cap rates). **Scenario classes:** Bull, Bear, Neutral, Growth, Stress. **Risk/Growth Scores:** representative ranges previously used: Growth ≈ 0.376–0.557; Risk ≈ 0.385–0.593. **QA:** 5/5 statistical validation checks passed.

**Forecast Cache:** `forecast_cache.db` stores Prophet forecasts and Monte Carlo results with cache invalidation rules implied by parameter/schema changes.

## 16) Appendix D — Comprehensive Testing Procedures (Golden Paths)

**Quick Validation (\~5 min):**

```
python -m pytest tests/unit/application/ tests/integration/ -q
python demo_end_to_end_workflow.py
```

**Expected demo outputs (reference values):** NPV ≈ **\$7,847,901**, IRR ≈ **64.8%**, Equity Multiple ≈ **9.79×**.

**Full System Validation (\~10 min):**

1. Env & DB: `python --version && python data_manager.py status`
2. Test suites: unit app (~122 tests), infra edge (~12), integration (~20), performance (~8), presentation (~68) — **~348 tests total**.
3. End‑to‑end demo: `python demo_end_to_end_workflow.py`
4. Code quality: Black/isort/flake8
5. Linux compat (Docker): `docker build -f Dockerfile.test -t proforma-linux-test .`

**Test Categories:** local env compat; database system; core business logic; infra resilience; DCF integration; performance; e2e demo; code quality; type safety; CI multi‑Python; docs; system performance; Docker Linux.

## 17) Appendix E — CI/CD Files & Validation Scripts

**Workflows (**``**):** `ci.yml` (multi‑Python tests), `quality.yml` (code quality & security), `release.yml` (release/deploy).

**Validation Scripts (**``**):** `validate_architecture.py`, `validate_docs.py`, `profile_memory.py`, `generate_release_notes.py`.

**Automated Gates Enforce:** Python 3.10–3.11 compat; ≥82% coverage; zero architecture violations; dependency vuln checks; perf regression detection; documentation accuracy.

## 18) Appendix F — Release & Failure Protocols

**Release Process:** Tag with SemVer (`vX.Y.Z`), push tag, CI runs full validation, generates release notes, creates GitHub release, optional PyPI publish.

**Failure Response:** Never ignore failures. Review Actions logs; reproduce locally; update tests if business rules changed; preserve architecture; address performance regressions; update docs if examples drift. **Common resolutions:** fix failing tests/expectations; add coverage for new paths; refactor for architecture compliance; optimize hot paths; correct docs/examples.

## 19) Appendix G — Documentation Analysis Protocol (Repo‑Wide)

- Glob search **all** `**/*.md` across repo.
- Cross‑reference for consistency (testing commands, CI references, setup, architecture, workflows).
- Identify gaps/outdated info; collapse duplicates into authoritative sources under `/docs`.
- Output: status assessment, gap analysis, consistency review, prioritized update plan.

## 20) Appendix H — Debugging Standards (Expanded)

- **Systematic diagnosis:** list 5–7 plausible causes → narrow to 1–2 → add targeted logs/tests.
- **Root‑cause first:** trust logs & repro, not hunches; document before fixing.
- **Surgical fixes:** minimal surface area; preserve behavior; keep patterns; prove with tests.
- **Database verification:** confirm schemas, migrations, query plans before changes.
- **Component reuse:** prefer extension/parameterization over duplication.
- **Data‑flow tracing:** instrument critical transitions; handle cache invalidation; add error boundaries.
- **API integration:** retries/backoff, types, CORS, auth; comprehensive error handling.
- **Error handling:** specific exceptions; user‑friendly messages; deep logs.
- **Housekeeping:** remove dead code; clean imports; eliminate unreachable branches.

## 21) Appendix I — Next Development Priorities (Preserved)

1. RESTful API layer (external integrations)
2. Web dashboard (inputs & analysis UI)
3. Investment reporting (PDF/Excel exports)
4. Portfolio optimization (enhanced IRR across property sets)
5. Advanced analytics (ML‑driven recommendations)

