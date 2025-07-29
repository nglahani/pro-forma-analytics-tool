"""
Database Index Optimization Script

Creates optimized composite indexes for improved query performance
based on common access patterns identified in the pro-forma analytics system.
"""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logging_config import get_logger


class DatabaseIndexOptimizer:
    """Optimizes database indexes for improved query performance."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.db_dir = project_root / "data" / "databases"
        self.databases = {
            'market_data': self.db_dir / 'market_data.db',
            'property_data': self.db_dir / 'property_data.db',
            'economic_data': self.db_dir / 'economic_data.db',
            'forecast_cache': self.db_dir / 'forecast_cache.db'
        }
    
    def get_optimized_indexes(self) -> Dict[str, List[Dict[str, str]]]:
        """Define optimized composite indexes based on query patterns."""
        
        return {
            'market_data': [
                {
                    'name': 'idx_interest_rates_param_geo_date',
                    'table': 'interest_rates',
                    'columns': 'parameter_name, geographic_code, date DESC',
                    'purpose': 'Optimize parameter lookups by geography with date sorting'
                },
                {
                    'name': 'idx_interest_rates_date_range',
                    'table': 'interest_rates', 
                    'columns': 'date, parameter_name, geographic_code',
                    'purpose': 'Optimize date range queries'
                },
                {
                    'name': 'idx_cap_rates_geo_type_date',
                    'table': 'cap_rates',
                    'columns': 'geographic_code, property_type, date DESC',
                    'purpose': 'Optimize cap rate lookups by location and property type'
                },
                {
                    'name': 'idx_economic_indicators_name_geo_date',
                    'table': 'economic_indicators',
                    'columns': 'indicator_name, geographic_code, date DESC',
                    'purpose': 'Optimize economic indicator queries'
                }
            ],
            
            'property_data': [
                {
                    'name': 'idx_rental_market_metric_geo_date',
                    'table': 'rental_market_data',
                    'columns': 'metric_name, geographic_code, date DESC',
                    'purpose': 'Optimize rental market data queries by metric and geography'
                },
                {
                    'name': 'idx_rental_market_geo_date',
                    'table': 'rental_market_data',
                    'columns': 'geographic_code, date DESC, metric_name',
                    'purpose': 'Optimize queries for all metrics in a geography'
                },
                {
                    'name': 'idx_operating_expenses_geo_date',
                    'table': 'operating_expenses',
                    'columns': 'geographic_code, date DESC',
                    'purpose': 'Optimize operating expense queries by geography'
                },
                {
                    'name': 'idx_property_tax_geo_date',
                    'table': 'property_tax_data',
                    'columns': 'geographic_code, date DESC',
                    'purpose': 'Optimize property tax queries'
                }
            ],
            
            'economic_data': [
                {
                    'name': 'idx_property_growth_geo_date',
                    'table': 'property_growth',
                    'columns': 'geographic_code, date DESC',
                    'purpose': 'Optimize property growth rate queries'
                },
                {
                    'name': 'idx_lending_requirements_geo_date',
                    'table': 'lending_requirements',
                    'columns': 'geographic_code, date DESC',
                    'purpose': 'Optimize lending requirement queries'
                },
                {
                    'name': 'idx_regional_economic_geo_indicator_date',
                    'table': 'regional_economic_indicators',
                    'columns': 'geographic_code, indicator_name, date DESC',
                    'purpose': 'Optimize regional economic indicator queries'
                }
            ],
            
            'forecast_cache': [
                {
                    'name': 'idx_prophet_forecasts_param_geo_date',
                    'table': 'prophet_forecasts',
                    'columns': 'parameter_name, geographic_code, forecast_date DESC',
                    'purpose': 'Optimize forecast retrieval by parameter and geography'
                },
                {
                    'name': 'idx_prophet_forecasts_date_horizon',
                    'table': 'prophet_forecasts',
                    'columns': 'forecast_date DESC, forecast_horizon_years',
                    'purpose': 'Optimize forecast cleanup and age filtering'
                },
                {
                    'name': 'idx_parameter_correlations_geo_date',
                    'table': 'parameter_correlations',
                    'columns': 'geographic_code, calculation_date DESC',
                    'purpose': 'Optimize correlation matrix retrieval'
                },
                {
                    'name': 'idx_monte_carlo_results_geo_date',
                    'table': 'monte_carlo_results',
                    'columns': 'geographic_code, simulation_date DESC',
                    'purpose': 'Optimize Monte Carlo result queries'
                }
            ]
        }
    
    def analyze_existing_indexes(self, db_path: Path) -> List[Dict[str, str]]:
        """Analyze existing indexes in a database."""
        
        existing_indexes = []
        
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.execute("""
                    SELECT name, tbl_name, sql 
                    FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                
                for row in cursor.fetchall():
                    index_name, table_name, sql = row
                    existing_indexes.append({
                        'name': index_name,
                        'table': table_name,
                        'definition': sql or 'PRIMARY KEY'
                    })
                    
        except Exception as e:
            self.logger.error(f"Failed to analyze existing indexes: {e}")
        
        return existing_indexes
    
    def create_index(self, db_path: Path, index_info: Dict[str, str]) -> bool:
        """Create a single optimized index."""
        
        index_name = index_info['name']
        table_name = index_info['table']
        columns = index_info['columns']
        
        # Check if table exists first
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,)
                )
                if not cursor.fetchone():
                    self.logger.warning(f"Table {table_name} does not exist, skipping index {index_name}")
                    return False
                
                # Drop existing index if it exists
                conn.execute(f"DROP INDEX IF EXISTS {index_name}")
                
                # Create new optimized index
                create_sql = f"CREATE INDEX {index_name} ON {table_name} ({columns})"
                conn.execute(create_sql)
                conn.commit()
                
                self.logger.info(f"Created index {index_name} on {table_name}({columns})")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create index {index_name}: {e}")
            return False
    
    def optimize_database_indexes(self, db_name: str) -> Dict[str, any]:
        """Optimize indexes for a specific database."""
        
        if db_name not in self.databases:
            raise ValueError(f"Unknown database: {db_name}")
        
        db_path = self.databases[db_name]
        if not db_path.exists():
            self.logger.warning(f"Database {db_name} not found at {db_path}")
            return {'success': False, 'error': 'Database not found'}
        
        self.logger.info(f"Optimizing indexes for {db_name}...")
        
        # Analyze existing indexes
        existing_indexes = self.analyze_existing_indexes(db_path)
        
        # Get optimized index definitions
        optimized_indexes = self.get_optimized_indexes()
        db_indexes = optimized_indexes.get(db_name, [])
        
        # Create optimized indexes
        results = {
            'database': db_name,
            'existing_indexes': len(existing_indexes),
            'indexes_created': 0,
            'indexes_failed': 0,
            'created_indexes': [],
            'failed_indexes': []
        }
        
        for index_info in db_indexes:
            if self.create_index(db_path, index_info):
                results['indexes_created'] += 1
                results['created_indexes'].append(index_info['name'])
            else:
                results['indexes_failed'] += 1
                results['failed_indexes'].append(index_info['name'])
        
        self.logger.info(f"Index optimization completed for {db_name}: "
                        f"{results['indexes_created']} created, {results['indexes_failed']} failed")
        
        return results
    
    def optimize_all_databases(self) -> Dict[str, any]:
        """Optimize indexes for all databases."""
        
        self.logger.info("Starting database index optimization for all databases...")
        
        overall_results = {
            'optimization_date': datetime.now().isoformat(),
            'databases_processed': 0,
            'total_indexes_created': 0,
            'total_indexes_failed': 0,
            'database_results': {}
        }
        
        for db_name in self.databases.keys():
            try:
                result = self.optimize_database_indexes(db_name)
                overall_results['database_results'][db_name] = result
                overall_results['databases_processed'] += 1
                overall_results['total_indexes_created'] += result.get('indexes_created', 0)
                overall_results['total_indexes_failed'] += result.get('indexes_failed', 0)
                
            except Exception as e:
                self.logger.error(f"Failed to optimize {db_name}: {e}")
                overall_results['database_results'][db_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        self.logger.info("Database index optimization completed")
        return overall_results
    
    def analyze_query_performance_improvement(self) -> Dict[str, any]:
        """Analyze performance improvement after index optimization."""
        
        self.logger.info("Analyzing query performance after index optimization...")
        
        # Import the profiler to test performance
        from scripts.profile_database_performance import DatabasePerformanceProfiler
        
        profiler = DatabasePerformanceProfiler()
        performance_report = profiler.profile_common_queries()
        
        # Analyze improvements
        improvements = {
            'analysis_date': datetime.now().isoformat(),
            'query_performance': performance_report,
            'performance_summary': {}
        }
        
        # Calculate performance statistics
        all_times = []
        for db_name, queries in performance_report.items():
            db_times = []
            for query_name, result in queries.items():
                if isinstance(result, dict) and 'avg_time_ms' in result:
                    all_times.append(result['avg_time_ms'])
                    db_times.append(result['avg_time_ms'])
            
            if db_times:
                improvements['performance_summary'][db_name] = {
                    'avg_query_time_ms': sum(db_times) / len(db_times),
                    'max_query_time_ms': max(db_times),
                    'min_query_time_ms': min(db_times),
                    'total_queries': len(db_times)
                }
        
        if all_times:
            improvements['performance_summary']['overall'] = {
                'avg_query_time_ms': sum(all_times) / len(all_times),
                'max_query_time_ms': max(all_times),
                'min_query_time_ms': min(all_times),
                'total_queries': len(all_times),
                'queries_under_1ms': len([t for t in all_times if t < 1.0]),
                'queries_under_10ms': len([t for t in all_times if t < 10.0])
            }
        
        return improvements
    
    def generate_optimization_report(self, optimization_results: Dict[str, any], 
                                   performance_results: Dict[str, any]) -> str:
        """Generate a comprehensive optimization report."""
        
        report_lines = [
            "=" * 80,
            "DATABASE INDEX OPTIMIZATION REPORT",
            "=" * 80,
            f"Generated: {optimization_results['optimization_date']}",
            "",
            "OPTIMIZATION SUMMARY:",
            f"  Databases processed: {optimization_results['databases_processed']}",
            f"  Total indexes created: {optimization_results['total_indexes_created']}",
            f"  Total indexes failed: {optimization_results['total_indexes_failed']}",
            "",
            "DATABASE DETAILS:",
        ]
        
        for db_name, result in optimization_results['database_results'].items():
            if 'indexes_created' in result:
                report_lines.extend([
                    f"  [{db_name.upper()}]",
                    f"    Indexes created: {result['indexes_created']}",
                    f"    Indexes failed: {result['indexes_failed']}",
                    f"    Created: {', '.join(result['created_indexes']) or 'None'}",
                ])
                if result['failed_indexes']:
                    report_lines.append(f"    Failed: {', '.join(result['failed_indexes'])}")
                report_lines.append("")
        
        # Add performance analysis
        if 'performance_summary' in performance_results:
            report_lines.extend([
                "PERFORMANCE ANALYSIS:",
                f"  Analysis date: {performance_results['analysis_date']}",
                ""
            ])
            
            overall = performance_results['performance_summary'].get('overall', {})
            if overall:
                report_lines.extend([
                    "  OVERALL PERFORMANCE:",
                    f"    Average query time: {overall['avg_query_time_ms']:.2f}ms",
                    f"    Maximum query time: {overall['max_query_time_ms']:.2f}ms",
                    f"    Minimum query time: {overall['min_query_time_ms']:.2f}ms",
                    f"    Queries under 1ms: {overall['queries_under_1ms']}/{overall['total_queries']}",
                    f"    Queries under 10ms: {overall['queries_under_10ms']}/{overall['total_queries']}",
                    ""
                ])
            
            for db_name, perf in performance_results['performance_summary'].items():
                if db_name != 'overall':
                    report_lines.extend([
                        f"  [{db_name.upper()}]",
                        f"    Average query time: {perf['avg_query_time_ms']:.2f}ms",
                        f"    Query count: {perf['total_queries']}",
                        ""
                    ])
        
        report_lines.extend([
            "RECOMMENDATIONS:",
            "  - Monitor query performance regularly",
            "  - Consider additional indexes if new query patterns emerge",
            "  - Implement query result caching for expensive operations",
            "  - Use EXPLAIN QUERY PLAN to verify index usage",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)


def main():
    """Main execution function."""
    
    optimizer = DatabaseIndexOptimizer()
    
    # Run index optimization
    optimization_results = optimizer.optimize_all_databases()
    
    # Analyze performance after optimization
    performance_results = optimizer.analyze_query_performance_improvement()
    
    # Generate and display report
    report = optimizer.generate_optimization_report(optimization_results, performance_results)
    print(report)
    
    # Save detailed results
    import json
    results_file = project_root / 'database_optimization_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'optimization_results': optimization_results,
            'performance_results': performance_results
        }, f, indent=2, default=str)
    
    print(f"Detailed results saved to: {results_file}")
    
    return optimization_results, performance_results


if __name__ == "__main__":
    main()