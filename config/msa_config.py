"""
MSA (Metropolitan Statistical Area) Configuration

IMPORTANT: This configuration defines North Carolina MSAs for future expansion.
Current DCF system uses national-level data. MSA-specific functionality is planned
but not yet implemented. Use national data sources for current operations.

Defines geographic areas for data collection with scalable structure
to support nationwide expansion from initial North Carolina focus.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MSAInfo:
    """Metropolitan Statistical Area information."""

    msa_code: str
    name: str
    state: str
    major_cities: List[str]
    population: Optional[int] = None
    market_tier: str = "secondary"  # primary, secondary, tertiary
    notes: Optional[str] = None


# North Carolina MSAs (MVP Focus)
NORTH_CAROLINA_MSAS = {
    "16740": MSAInfo(
        msa_code="16740",
        name="Charlotte-Concord-Gastonia",
        state="NC-SC",
        major_cities=["Charlotte", "Concord", "Gastonia"],
        population=2695000,
        market_tier="primary",
        notes="Major banking center, highest commercial RE activity in NC",
    ),
    "39580": MSAInfo(
        msa_code="39580",
        name="Raleigh-Cary",
        state="NC",
        major_cities=["Raleigh", "Cary", "Apex"],
        population=1390000,
        market_tier="primary",
        notes="Research Triangle, tech hub, strong rental demand",
    ),
    "24660": MSAInfo(
        msa_code="24660",
        name="Greensboro-High Point",
        state="NC",
        major_cities=["Greensboro", "High Point", "Winston-Salem"],
        population=770000,
        market_tier="secondary",
        notes="Manufacturing and logistics center",
    ),
    "20500": MSAInfo(
        msa_code="20500",
        name="Durham-Chapel Hill",
        state="NC",
        major_cities=["Durham", "Chapel Hill"],
        population=650000,
        market_tier="secondary",
        notes="University towns, research institutions, stable rental market",
    ),
}

# Future expansion templates (for reference)
EXPANSION_MSAS = {
    # Southeast expansion candidates
    "12060": MSAInfo("12060", "Atlanta-Sandy Springs-Alpharetta", "GA", ["Atlanta"]),
    "37980": MSAInfo(
        "37980", "Philadelphia-Camden-Wilmington", "PA-NJ-DE-MD", ["Philadelphia"]
    ),
    "40060": MSAInfo("40060", "Richmond", "VA", ["Richmond"]),
    # National primary markets
    "35620": MSAInfo(
        "35620", "New York-Newark-Jersey City", "NY-NJ-PA", ["New York City"]
    ),
    "31080": MSAInfo("31080", "Los Angeles-Long Beach-Anaheim", "CA", ["Los Angeles"]),
    "16980": MSAInfo("16980", "Chicago-Naperville-Elgin", "IL-IN-WI", ["Chicago"]),
}

# Current active MSAs (start with NC, expand as needed)
ACTIVE_MSAS = NORTH_CAROLINA_MSAS.copy()


def get_active_msa_codes() -> List[str]:
    """Get list of currently active MSA codes."""
    return list(ACTIVE_MSAS.keys())


def get_msa_info(msa_code: str) -> Optional[MSAInfo]:
    """Get information for a specific MSA."""
    return ACTIVE_MSAS.get(msa_code)


def get_msas_by_state(state: str) -> Dict[str, MSAInfo]:
    """Get all MSAs for a specific state."""
    return {code: info for code, info in ACTIVE_MSAS.items() if state in info.state}


def add_msa(msa_code: str, msa_info: MSAInfo) -> None:
    """Add a new MSA to active collection (for expansion)."""
    ACTIVE_MSAS[msa_code] = msa_info


def get_msa_display_names() -> Dict[str, str]:
    """Get mapping of MSA codes to display names."""
    return {code: f"{info.name} ({info.state})" for code, info in ACTIVE_MSAS.items()}


# Data source compatibility by MSA tier
DATA_SOURCE_COVERAGE = {
    "primary": {
        "fred": True,
        "bls": True,
        "census": True,
        "fhfa": True,
        "commercial_surveys": True,
    },
    "secondary": {
        "fred": True,  # National only
        "bls": True,
        "census": True,
        "fhfa": True,
        "commercial_surveys": False,  # May need proxies
    },
    "tertiary": {
        "fred": True,  # National only
        "bls": False,  # May need state-level
        "census": True,
        "fhfa": True,
        "commercial_surveys": False,
    },
}


def get_data_coverage(msa_code: str) -> Dict[str, bool]:
    """Get data source coverage for a specific MSA."""
    msa = get_msa_info(msa_code)
    if not msa:
        return {}
    return DATA_SOURCE_COVERAGE.get(msa.market_tier, {})


# Geographic groupings for efficient data collection
REGIONAL_GROUPS = {
    "southeast": ["16740", "39580", "24660", "20500"],  # NC MSAs
    "northeast": ["35620", "37980"],  # Future expansion
    "midwest": ["16980"],
    "west": ["31080"],
    "national": ["NATIONAL"],  # For national-level data
}


def get_regional_group(msa_code: str) -> Optional[str]:
    """Get regional group for an MSA."""
    for region, msa_codes in REGIONAL_GROUPS.items():
        if msa_code in msa_codes:
            return region
    return None
