"""
FastAPI Application Entry Point

Main application configuration and startup for the Pro-Forma Analytics API.
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.presentation.api.exceptions import register_exception_handlers
from src.presentation.api.middleware.auth import APIKeyAuthMiddleware
from src.presentation.api.middleware.logging import RequestLoggingMiddleware
from src.presentation.api.middleware.rate_limit import RateLimitMiddleware
from src.presentation.api.routers import analysis, data, simulation, system

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings
from core.logging_config import get_logger

# Optional Sentry integration
_sentry_initialized = False
try:
    import sentry_sdk  # type: ignore
    from sentry_sdk.integrations.fastapi import FastAPIIntegration  # type: ignore
except Exception:  # pragma: no cover
    FastAPIIntegration = None  # type: ignore
    sentry_sdk = None  # type: ignore

# Initialize settings and logging
settings = get_settings()
logger = get_logger(__name__)

# Configure Sentry if DSN provided
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN and sentry_sdk and FastAPIIntegration:
    try:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FastAPIIntegration()],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        )
        _sentry_initialized = True
        logger.info("Sentry initialized for FastAPI")
    except Exception as _e:  # pragma: no cover
        logger.warning(f"Sentry initialization failed: {_e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Pro-Forma Analytics API v1.5.0")
    logger.info(f"Environment: {settings.environment.value}")
    logger.info(f"API Host: {settings.api.host}:{settings.api.port}")
    logger.info(f"Debug mode: {settings.api.debug}")

    yield

    # Shutdown
    logger.info("Shutting down Pro-Forma Analytics API")


# Create FastAPI application
app = FastAPI(
    lifespan=lifespan,
    title="Pro-Forma Analytics API",
    description="""
    **Production-ready REST API for real estate DCF analysis and investment modeling.**

    Transform static Excel-based pro formas into sophisticated financial models using Prophet time series
    forecasting and Monte Carlo simulations.

    ## Features

    * **Complete 4-Phase DCF Engine**: Assumptions → Initial Numbers → Cash Flow → Financial Metrics
    * **Prophet Forecasting**: 11 pro forma parameters with 6-year projections
    * **Monte Carlo Simulation**: 500+ scenarios with economic correlations
    * **Investment Analysis**: NPV, IRR, equity multiples, risk assessment, terminal value
    * **Market Data Access**: 5 major MSAs with 15+ years of historical data (2,174+ data points)
    * **Real-time Analysis**: Sub-second response times for comprehensive property analysis

    ## Supported Markets

    * **New York** (MSA: 35620) - NYC metro area
    * **Los Angeles** (MSA: 31080) - LA metro area
    * **Chicago** (MSA: 16980) - Chicago metro area
    * **Washington DC** (MSA: 47900) - DC metro area
    * **Miami** (MSA: 33100) - Miami metro area

    ## Authentication

    All endpoints (except health check) require API key authentication via **X-API-Key** header.

    ## DCF Methodology

    Our 4-phase DCF workflow provides institutional-grade analysis:

    1. **DCF Assumptions** - Monte Carlo scenario mapping to financial parameters
    2. **Initial Numbers** - Acquisition costs, financing terms, and investment requirements
    3. **Cash Flow Projections** - 6-year cash flow modeling with waterfall distributions
    4. **Financial Metrics** - NPV, IRR, terminal value, and investment recommendations

    ## Rate Limiting

    * **Standard Rate**: 100 requests per minute per API key
    * **Burst Handling**: Short-term spikes accommodated with token bucket algorithm
    * **Batch Endpoints**: Use `/analysis/batch` for multiple properties to optimize rate limits
    """,
    version="1.5.0",
    contact={
        "name": "Pro-Forma Analytics API",
        "url": "https://github.com/nglahani/pro-forma-analytics-tool",
        "email": "api-support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://github.com/nglahani/pro-forma-analytics-tool/blob/main/TERMS.md",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    openapi_tags=[
        {
            "name": "analysis",
            "description": "DCF analysis and financial modeling endpoints",
        },
        {
            "name": "simulation",
            "description": "Monte Carlo simulation and forecasting endpoints",
        },
        {
            "name": "data",
            "description": "Market data and historical information endpoints",
        },
        {
            "name": "system",
            "description": "System health, configuration, and operational endpoints",
        },
    ],
)

# Add middleware stack (order matters - last added = first executed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add request logging middleware (outermost layer)
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    default_capacity=settings.api.rate_limit_requests,
    default_refill_rate=settings.api.rate_limit_requests / 60.0,
)

# Add authentication middleware (innermost layer - closest to endpoints)
app.add_middleware(APIKeyAuthMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(analysis.router)
app.include_router(simulation.router)
app.include_router(system.router)
app.include_router(data.router)

# Application startup time for health checks
_startup_time = datetime.now(timezone.utc)


@app.get("/api/v1/test")
async def test_endpoint() -> Dict[str, Any]:
    """Test endpoint for middleware validation."""
    return {"message": "Test endpoint works", "authenticated": True}


# Enhanced health check is now in system.py router


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error_code": "internal_server_error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        log_level="info" if settings.api.debug else "warning",
    )
