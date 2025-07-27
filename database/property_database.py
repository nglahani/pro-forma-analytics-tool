"""
Property Database Storage System

Provides persistent storage for property listings and pro forma analysis results.
Supports SQLite database backend with full CRUD operations.
"""

import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from src.domain.entities.property_data import SimplifiedPropertyInput, property_manager as simplified_property_manager


class PropertyDatabase:
    """Database manager for property listings and analysis results."""
    
    def __init__(self, db_path: str = "data/databases/property_listings.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Property listings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS property_listings (
                    property_id TEXT PRIMARY KEY,
                    property_name TEXT NOT NULL,
                    analysis_date TEXT NOT NULL,
                    
                    -- Core data points (your requirements)
                    residential_units_count INTEGER NOT NULL DEFAULT 0,
                    residential_rent_per_unit REAL NOT NULL DEFAULT 0,
                    residential_sqft_per_unit INTEGER,
                    residential_unit_types TEXT,
                    
                    commercial_units_count INTEGER NOT NULL DEFAULT 0,
                    commercial_rent_per_unit REAL NOT NULL DEFAULT 0,
                    commercial_sqft_per_unit INTEGER,
                    commercial_unit_types TEXT,
                    
                    renovation_status TEXT NOT NULL DEFAULT 'not_needed',
                    renovation_duration_months INTEGER,
                    renovation_start_date TEXT,
                    renovation_estimated_cost REAL,
                    renovation_description TEXT,
                    
                    investor_equity_share_pct REAL NOT NULL DEFAULT 100.0,
                    self_cash_percentage REAL NOT NULL DEFAULT 25.0,
                    number_of_investors INTEGER DEFAULT 1,
                    investment_structure TEXT,
                    
                    -- Location
                    city TEXT,
                    state TEXT,
                    msa_code TEXT,
                    property_address TEXT,
                    
                    -- Additional fields
                    purchase_price REAL,
                    notes TEXT,
                    
                    -- Metadata
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    
                    -- Calculated metrics (stored as JSON)
                    calculated_metrics TEXT
                )
            """)
            
            # Pro forma analysis results table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pro_forma_analyses (
                    analysis_id TEXT PRIMARY KEY,
                    property_id TEXT NOT NULL,
                    analysis_date TEXT NOT NULL,
                    
                    -- Monte Carlo results
                    num_scenarios INTEGER,
                    horizon_years INTEGER,
                    
                    -- Summary statistics
                    avg_growth_score REAL,
                    avg_risk_score REAL,
                    min_growth_score REAL,
                    max_growth_score REAL,
                    min_risk_score REAL,
                    max_risk_score REAL,
                    
                    -- Market scenario breakdown (JSON)
                    market_scenarios TEXT,
                    
                    -- Extreme scenarios (JSON)
                    extreme_scenarios TEXT,
                    
                    -- Full results (JSON) - for detailed analysis
                    full_results TEXT,
                    
                    -- Metadata
                    created_at TEXT NOT NULL,
                    
                    FOREIGN KEY (property_id) REFERENCES property_listings (property_id)
                )
            """)
            
            # User/listing tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_listings (
                    listing_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    property_id TEXT NOT NULL,
                    listing_status TEXT NOT NULL DEFAULT 'active',
                    listing_date TEXT NOT NULL,
                    listing_notes TEXT,
                    
                    FOREIGN KEY (property_id) REFERENCES property_listings (property_id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_property_msa ON property_listings (msa_code)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_property_type ON property_listings (residential_units_count, commercial_units_count)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_analysis_property ON pro_forma_analyses (property_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_user_listings ON user_listings (user_id, listing_status)")
            
            conn.commit()
            self.logger.info(f"Database initialized at {self.db_path}")
    
    def save_property(self, property_data: SimplifiedPropertyInput) -> bool:
        """Save property to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                now = datetime.now().isoformat()
                metrics_json = json.dumps(property_data.calculate_key_metrics())
                
                conn.execute("""
                    INSERT OR REPLACE INTO property_listings (
                        property_id, property_name, analysis_date,
                        residential_units_count, residential_rent_per_unit, 
                        residential_sqft_per_unit, residential_unit_types,
                        commercial_units_count, commercial_rent_per_unit,
                        commercial_sqft_per_unit, commercial_unit_types,
                        renovation_status, renovation_duration_months,
                        renovation_start_date, renovation_estimated_cost, renovation_description,
                        investor_equity_share_pct, self_cash_percentage,
                        number_of_investors, investment_structure,
                        city, state, msa_code, property_address,
                        purchase_price, notes,
                        created_at, updated_at, calculated_metrics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    property_data.property_id,
                    property_data.property_name,
                    property_data.analysis_date.isoformat(),
                    property_data.residential_units.total_units,
                    property_data.residential_units.average_rent_per_unit,
                    property_data.residential_units.average_square_feet_per_unit,
                    property_data.residential_units.unit_types,
                    property_data.commercial_units.total_units if property_data.commercial_units else 0,
                    property_data.commercial_units.average_rent_per_unit if property_data.commercial_units else 0,
                    property_data.commercial_units.average_square_feet_per_unit if property_data.commercial_units else None,
                    property_data.commercial_units.unit_types if property_data.commercial_units else None,
                    property_data.renovation_info.status.value,
                    property_data.renovation_info.anticipated_duration_months,
                    property_data.renovation_info.start_date.isoformat() if property_data.renovation_info.start_date else None,
                    property_data.renovation_info.estimated_cost,
                    property_data.renovation_info.description,
                    property_data.equity_structure.investor_equity_share_pct,
                    property_data.equity_structure.self_cash_percentage,
                    property_data.equity_structure.number_of_investors,
                    property_data.equity_structure.investment_structure,
                    property_data.city,
                    property_data.state,
                    property_data.msa_code,
                    property_data.property_address,
                    property_data.purchase_price,
                    property_data.notes,
                    now,
                    now,
                    metrics_json
                ))
                
                conn.commit()
                self.logger.info(f"Saved property {property_data.property_id} to database")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save property {property_data.property_id}: {e}")
            return False
    
    def load_property(self, property_id: str) -> Optional[SimplifiedPropertyInput]:
        """Load property from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM property_listings WHERE property_id = ?
                """, (property_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Convert row to dictionary
                data = dict(row)
                
                # Convert back to SimplifiedPropertyInput
                return SimplifiedPropertyInput.from_dict(data)
                
        except Exception as e:
            self.logger.error(f"Failed to load property {property_id}: {e}")
            return None
    
    def list_properties(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all properties with basic info."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT 
                        property_id, property_name, analysis_date,
                        residential_units_count, commercial_units_count,
                        city, state, purchase_price, updated_at,
                        calculated_metrics
                    FROM property_listings 
                    ORDER BY updated_at DESC 
                    LIMIT ?
                """, (limit,))
                
                properties = []
                for row in cursor.fetchall():
                    prop_data = dict(row)
                    # Parse calculated metrics
                    if prop_data['calculated_metrics']:
                        prop_data['metrics'] = json.loads(prop_data['calculated_metrics'])
                    properties.append(prop_data)
                
                return properties
                
        except Exception as e:
            self.logger.error(f"Failed to list properties: {e}")
            return []
    
    def save_analysis_results(self, property_id: str, monte_carlo_results: Any) -> bool:
        """Save Monte Carlo analysis results."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                analysis_id = f"ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{property_id}"
                
                # Extract summary statistics
                growth_scores = [s.scenario_summary.get('growth_score', 0) for s in monte_carlo_results.scenarios]
                risk_scores = [s.scenario_summary.get('risk_score', 0) for s in monte_carlo_results.scenarios]
                
                # Market scenario breakdown
                market_scenarios = {}
                for scenario in monte_carlo_results.scenarios:
                    market_type = scenario.scenario_summary.get('market_scenario', 'unknown')
                    market_scenarios[market_type] = market_scenarios.get(market_type, 0) + 1
                
                conn.execute("""
                    INSERT INTO pro_forma_analyses (
                        analysis_id, property_id, analysis_date,
                        num_scenarios, horizon_years,
                        avg_growth_score, avg_risk_score,
                        min_growth_score, max_growth_score,
                        min_risk_score, max_risk_score,
                        market_scenarios, extreme_scenarios, full_results,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    property_id,
                    datetime.now().isoformat(),
                    len(monte_carlo_results.scenarios),
                    monte_carlo_results.horizon_years,
                    sum(growth_scores) / len(growth_scores) if growth_scores else 0,
                    sum(risk_scores) / len(risk_scores) if risk_scores else 0,
                    min(growth_scores) if growth_scores else 0,
                    max(growth_scores) if growth_scores else 0,
                    min(risk_scores) if risk_scores else 0,
                    max(risk_scores) if risk_scores else 0,
                    json.dumps(market_scenarios),
                    json.dumps(monte_carlo_results.extreme_scenarios) if hasattr(monte_carlo_results, 'extreme_scenarios') else "{}",
                    json.dumps({"summary": "Full results stored separately"}),  # Placeholder for now
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                self.logger.info(f"Saved analysis results for property {property_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save analysis results for {property_id}: {e}")
            return False
    
    def get_property_analyses(self, property_id: str) -> List[Dict[str, Any]]:
        """Get all analysis results for a property."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM pro_forma_analyses 
                    WHERE property_id = ?
                    ORDER BY created_at DESC
                """, (property_id,))
                
                analyses = []
                for row in cursor.fetchall():
                    analysis_data = dict(row)
                    # Parse JSON fields
                    if analysis_data['market_scenarios']:
                        analysis_data['market_scenarios'] = json.loads(analysis_data['market_scenarios'])
                    if analysis_data['extreme_scenarios']:
                        analysis_data['extreme_scenarios'] = json.loads(analysis_data['extreme_scenarios'])
                    analyses.append(analysis_data)
                
                return analyses
                
        except Exception as e:
            self.logger.error(f"Failed to get analyses for property {property_id}: {e}")
            return []
    
    def create_user_listing(self, user_id: str, property_id: str, listing_notes: str = None) -> str:
        """Create a user listing entry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                listing_id = f"LISTING_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"
                
                conn.execute("""
                    INSERT INTO user_listings (
                        listing_id, user_id, property_id, 
                        listing_status, listing_date, listing_notes
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    listing_id,
                    user_id,
                    property_id,
                    'active',
                    datetime.now().isoformat(),
                    listing_notes
                ))
                
                conn.commit()
                self.logger.info(f"Created listing {listing_id} for user {user_id}")
                return listing_id
                
        except Exception as e:
            self.logger.error(f"Failed to create listing for user {user_id}: {e}")
            return ""
    
    def get_user_listings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all listings for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT 
                        ul.listing_id, ul.listing_status, ul.listing_date, ul.listing_notes,
                        pl.property_id, pl.property_name, pl.city, pl.state,
                        pl.residential_units_count, pl.commercial_units_count,
                        pl.purchase_price, pl.calculated_metrics
                    FROM user_listings ul
                    JOIN property_listings pl ON ul.property_id = pl.property_id
                    WHERE ul.user_id = ?
                    ORDER BY ul.listing_date DESC
                """, (user_id,))
                
                listings = []
                for row in cursor.fetchall():
                    listing_data = dict(row)
                    if listing_data['calculated_metrics']:
                        listing_data['metrics'] = json.loads(listing_data['calculated_metrics'])
                    listings.append(listing_data)
                
                return listings
                
        except Exception as e:
            self.logger.error(f"Failed to get listings for user {user_id}: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Property counts
                cursor = conn.execute("SELECT COUNT(*) FROM property_listings")
                stats['total_properties'] = cursor.fetchone()[0]
                
                # Analysis counts
                cursor = conn.execute("SELECT COUNT(*) FROM pro_forma_analyses")
                stats['total_analyses'] = cursor.fetchone()[0]
                
                # User listing counts
                cursor = conn.execute("SELECT COUNT(*) FROM user_listings")
                stats['total_listings'] = cursor.fetchone()[0]
                
                # Property type breakdown
                cursor = conn.execute("""
                    SELECT 
                        CASE 
                            WHEN residential_units_count > 0 AND commercial_units_count > 0 THEN 'mixed_use'
                            WHEN residential_units_count > 0 THEN 'residential'
                            WHEN commercial_units_count > 0 THEN 'commercial'
                            ELSE 'other'
                        END as property_type,
                        COUNT(*) as count
                    FROM property_listings
                    GROUP BY property_type
                """)
                
                stats['property_types'] = {row[0]: row[1] for row in cursor.fetchall()}
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}


# Global database instance
property_db = PropertyDatabase()