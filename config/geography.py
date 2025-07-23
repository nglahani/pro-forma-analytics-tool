"""
Geographic Configuration for Pro Forma Analytics

Manages MSA and County-level geographic identifiers for data collection.
Provides mapping between different geographic coding systems.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class GeographicRegion:
    """Represents a geographic region for data collection."""
    name: str
    msa_code: Optional[str] = None
    fips_code: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    cbsa_code: Optional[str] = None  # Core Based Statistical Area
    
    def __str__(self) -> str:
        return f"{self.name} ({self.state})"

class GeographyManager:
    """Manages geographic regions and their identifiers."""
    
    def __init__(self):
        self.regions: Dict[str, GeographicRegion] = {}
        self._load_default_regions()
    
    def _load_default_regions(self):
        """Load commonly used MSAs for real estate analysis."""
        default_msas = [
            # Major Real Estate Markets
            GeographicRegion(
                name="New York-Newark-Jersey City",
                msa_code="35620",
                cbsa_code="35620",
                state="NY-NJ-PA",
                fips_code="36061"  # Manhattan
            ),
            GeographicRegion(
                name="Los Angeles-Long Beach-Anaheim",
                msa_code="31080",
                cbsa_code="31080", 
                state="CA",
                fips_code="06037"  # Los Angeles County
            ),
            GeographicRegion(
                name="Chicago-Naperville-Elgin",
                msa_code="16980",
                cbsa_code="16980",
                state="IL-IN-WI",
                fips_code="17031"  # Cook County
            ),
            GeographicRegion(
                name="Washington-Arlington-Alexandria",
                msa_code="47900",
                cbsa_code="47900",
                state="DC-VA-MD-WV",
                fips_code="11001"  # District of Columbia
            ),
            GeographicRegion(
                name="Miami-Fort Lauderdale-West Palm Beach",
                msa_code="33100",
                cbsa_code="33100",
                state="FL", 
                fips_code="12086"  # Miami-Dade County
            ),
            GeographicRegion(
                name="Atlanta-Sandy Springs-Roswell",
                msa_code="12060",
                cbsa_code="12060",
                state="GA",
                fips_code="13121"  # Fulton County
            ),
            GeographicRegion(
                name="Dallas-Fort Worth-Arlington",
                msa_code="19100",
                cbsa_code="19100",
                state="TX",
                fips_code="48113"  # Dallas County
            ),
            GeographicRegion(
                name="Houston-The Woodlands-Sugar Land",
                msa_code="26420",
                cbsa_code="26420",
                state="TX",
                fips_code="48201"  # Harris County
            ),
            # Example: Wilmington, NC (from the original Excel)
            GeographicRegion(
                name="Wilmington",
                msa_code="48900",
                cbsa_code="48900",
                state="NC",
                county="New Hanover County",
                fips_code="37129"
            )
        ]
        
        for region in default_msas:
            self.regions[region.name] = region
    
    def add_region(self, region: GeographicRegion) -> None:
        """Add a new geographic region."""
        self.regions[region.name] = region
    
    def get_region(self, name: str) -> Optional[GeographicRegion]:
        """Get a region by name."""
        return self.regions.get(name)
    
    def get_region_by_msa(self, msa_code: str) -> Optional[GeographicRegion]:
        """Get a region by MSA code."""
        for region in self.regions.values():
            if region.msa_code == msa_code:
                return region
        return None
    
    def get_region_by_fips(self, fips_code: str) -> Optional[GeographicRegion]:
        """Get a region by FIPS code."""
        for region in self.regions.values():
            if region.fips_code == fips_code:
                return region
        return None
    
    def list_regions(self) -> List[str]:
        """List all available region names."""
        return list(self.regions.keys())
    
    def get_regions_by_state(self, state: str) -> List[GeographicRegion]:
        """Get all regions in a specific state."""
        return [region for region in self.regions.values() 
                if region.state and state in region.state]

# Global instance for easy access
geography = GeographyManager()

# Common geographic utility functions
def validate_msa_code(msa_code: str) -> bool:
    """Validate MSA code format (5 digits)."""
    return msa_code.isdigit() and len(msa_code) == 5

def validate_fips_code(fips_code: str) -> bool:
    """Validate FIPS code format (5 digits for county)."""
    return fips_code.isdigit() and len(fips_code) == 5

def get_default_region() -> GeographicRegion:
    """Get default region for testing (Wilmington, NC from Excel example)."""
    return geography.get_region("Wilmington") or GeographicRegion(
        name="Default", 
        state="NC", 
        fips_code="37129"
    )