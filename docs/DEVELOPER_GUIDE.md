# Developer Guide

This guide helps developers set up, run, test, and monitor the Pro-Forma Analytics backend and frontend.

## Prerequisites
- Python 3.10–3.13 (validated in CI)
- Node.js 18+ (for frontend)
- Git

## Quick Start (Backend)
```bash
# 1) Create and activate a virtual environment
python -m venv .venv
# Windows
. .venv\Scripts\activate
# macOS/Linux
# . .venv/bin/activate

# 2) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3) Create a local env file
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# 4) Initialize local databases
python data_manager.py setup

# 5) Run tests and quality checks
pytest -q
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
mypy src/

# 6) Run the API locally
python src/presentation/api/main.py
# Open http://127.0.0.1:8000/api/v1/docs
```

## Quick Start (Frontend)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## Environment Variables
Configure via `.env` (see `.env.example`). Key settings:
- PRO_FORMA_ENV: development | testing | production
- API_HOST, API_PORT, API_WORKERS, ALLOWED_ORIGINS
- SECRET_KEY
- FRED_API_KEY
- Optional Observability: SENTRY_DSN, SENTRY_TRACES_SAMPLE_RATE

## Authentication
- API key via `X-API-Key` header (dev keys defined in `APIKeyManager`) for all endpoints except:
  - `/api/v1/health`
  - `/api/v1/metrics`
  - API docs (`/api/v1/docs`, `/api/v1/redoc`, `/api/v1/openapi.json`)

## Endpoints (Backend)
- System
  - `GET /api/v1/health` — health status
  - `GET /api/v1/metrics` — JSON metrics
  - `GET /api/v1/metrics?format=prometheus` — Prometheus text format
  - `GET /api/v1/config` — configuration (admin only)
- Analysis
  - `POST /api/v1/analysis/dcf` — full DCF workflow
  - `POST /api/v1/analysis/batch` — batch DCF
- Simulation
  - `POST /api/v1/simulation/monte-carlo` — Monte Carlo generation

## Testing
- Python tests
  - Unit/integration/performance under `tests/`
  - Run: `pytest -q`
  - Coverage thresholds via `pytest.ini`
- Frontend tests
  - Run: `cd frontend && npm test`

Performance tests include latency and p95 concurrency checks for DCF and Monte Carlo endpoints. See `tests/performance/test_api_performance_endpoints.py`.

## Code Quality
- Formatting: Black (88), isort
- Linting: flake8
- Types: mypy (strict)
- Pre-commit hooks: `.pre-commit-config.yaml`

## Observability
- Metrics: `GET /api/v1/metrics` (JSON) or `?format=prometheus` for Prometheus scraping
- Optional Sentry: set `SENTRY_DSN` to enable automatic error capture

Prometheus scrape example:
```yaml
scrape_configs:
  - job_name: proforma-api
    metrics_path: /api/v1/metrics
    params:
      format: [prometheus]
    static_configs:
      - targets: ['127.0.0.1:8000']
```

## Useful Scripts
- `scripts/health_check.py` — end-to-end health verification
- `scripts/profile_memory.py` — memory profiling
- `scripts/profile_database_performance.py` — DB performance profiling
- `scripts/backup_recovery.py` — backups and restore

## CI/CD Expectations
- All tests green, coverage thresholds respected
- Linting, typing, and architecture validations pass

## Troubleshooting
- Verify `.env` values and database paths (`config/settings.py`)
- Run `scripts/validate_docs.py` and `scripts/validate_architecture.py`
- Check logs in `logs/`
