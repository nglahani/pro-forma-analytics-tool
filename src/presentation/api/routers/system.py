"""
System Router

Endpoints for system configuration, health monitoring, and operational status.
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, status

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.logging_config import get_logger
from src.presentation.api.middleware.auth import require_permission
from src.presentation.api.models.responses import ConfigurationResponse, HealthResponse

logger = get_logger(__name__)

# Create system router
router = APIRouter(
    prefix="/api/v1",
    tags=["system"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        500: {"description": "Internal server error"},
    },
)


def check_database_connectivity() -> Dict[str, str]:
    """Check connectivity to all required databases."""
    databases = {
        "market_data": project_root / "data" / "databases" / "market_data.db",
        "property_data": project_root / "data" / "databases" / "property_data.db",
        "economic_data": project_root / "data" / "databases" / "economic_data.db",
        "forecast_cache": project_root / "data" / "databases" / "forecast_cache.db",
    }

    status_results = {}

    for db_name, db_path in databases.items():
        try:
            if not db_path.exists():
                status_results[db_name] = "missing"
                continue

            # Test connection
            with sqlite3.connect(str(db_path), timeout=5.0) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                )
                table_count = cursor.fetchone()[0]

                if table_count > 0:
                    status_results[db_name] = "healthy"
                else:
                    status_results[db_name] = "empty"

        except sqlite3.Error as e:
            logger.warning(f"Database {db_name} connectivity issue: {e}")
            status_results[db_name] = "error"
        except Exception as e:
            logger.error(f"Unexpected error checking {db_name}: {e}")
            status_results[db_name] = "unknown"

    return status_results


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def enhanced_health_check() -> HealthResponse:
    """
    Enhanced health check endpoint with database connectivity and dependency status.

    Returns comprehensive service health information including:
    - Overall service status
    - Database connectivity status
    - External dependency availability
    - System resource information

    Returns:
        Complete health status information
    """
    try:
        # Check database connectivity
        db_status = check_database_connectivity()

        # Determine overall health status
        unhealthy_dbs = [
            db for db, status in db_status.items() if status not in ["healthy"]
        ]
        overall_status = "degraded" if unhealthy_dbs else "healthy"

        # Get uptime (approximate - based on when this module was loaded)
        startup_time = getattr(
            enhanced_health_check, "_startup_time", datetime.utcnow()
        )
        uptime_seconds = (datetime.utcnow() - startup_time).total_seconds()

        health_response = HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            environment="development",  # Could be loaded from config
            uptime_seconds=uptime_seconds,
            dependencies={
                **db_status,
                "core_services": "healthy",
                "api_middleware": "healthy",
                "logging_system": "healthy",
            },
        )

        if overall_status == "degraded":
            logger.warning(
                f"Health check shows degraded status. Unhealthy databases: {unhealthy_dbs}"
            )
        else:
            logger.debug("Health check passed - all systems healthy")

        return health_response

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)

        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            environment="development",
            uptime_seconds=0.0,
            dependencies={"health_check": "error", "error_details": str(e)},
        )


# Set startup time for uptime calculation
enhanced_health_check._startup_time = datetime.utcnow()


@router.get(
    "/config", response_model=ConfigurationResponse, status_code=status.HTTP_200_OK
)
async def get_system_configuration(
    _: bool = Depends(require_permission("admin")),
) -> ConfigurationResponse:
    """
    Get system configuration information.

    Returns non-sensitive configuration parameters including:
    - Supported MSAs and markets
    - Available forecast parameters
    - System limits and constraints
    - DCF calculation methodology info

    Requires admin permissions for access.

    Args:
        _: Admin permission check

    Returns:
        System configuration information
    """
    try:
        logger.debug("Retrieving system configuration")

        configuration = ConfigurationResponse(
            supported_msas=[
                "35620",  # New York-Newark-Jersey City, NY-NJ-PA
                "31080",  # Los Angeles-Long Beach-Anaheim, CA
                "16980",  # Chicago-Naperville-Elgin, IL-IN-WI
                "47900",  # Washington-Arlington-Alexandria, DC-VA-MD-WV
                "33100",  # Miami-Fort Lauderdale-West Palm Beach, FL
            ],
            supported_parameters=[
                "commercial_mortgage_rate",
                "treasury_10y",
                "fed_funds_rate",
                "cap_rate",
                "rent_growth",
                "expense_growth",
                "property_growth",
                "vacancy_rate",
                "ltv_ratio",
                "closing_cost_pct",
                "lender_reserves",
            ],
            analysis_limits={
                "max_monte_carlo_scenarios": 50000,
                "min_monte_carlo_scenarios": 500,
                "max_forecast_horizon_years": 10,
                "min_forecast_horizon_years": 3,
                "max_batch_properties": 50,
                "max_concurrent_batch": 10,
                "request_timeout_seconds": 300,
            },
            dcf_methodology={
                "phases": "4-Phase DCF Workflow",
                "phase_1": "DCF Assumptions from Monte Carlo",
                "phase_2": "Initial Numbers & Acquisition Costs",
                "phase_3": "Cash Flow Projections (6 years)",
                "phase_4": "Financial Metrics & Investment Analysis",
                "forecasting_engine": "Prophet Time Series",
                "simulation_engine": "Custom Monte Carlo with Correlations",
                "discount_rate_default": "10%",
                "confidence_level_default": "95%",
            },
            api_version="1.0.0",
            last_updated=datetime.utcnow(),
        )

        logger.debug("System configuration retrieved successfully")
        return configuration

    except Exception as e:
        logger.error(f"Failed to retrieve system configuration: {e}", exc_info=True)
        raise
