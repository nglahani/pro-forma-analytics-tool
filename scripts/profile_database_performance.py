"""
Database Performance Profiler

Analyzes and profiles database query performance to identify optimization opportunities.
"""

import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime, date, timedelta
import sys
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.databases.database_manager import db_manager
from core.logging_config import get_logger


class DatabasePerformanceProfiler:
    """Profiles database query performance and identifies bottlenecks."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.db_dir = project_root / "data" / "databases"
        self.databases = {
            'market_data': self.db_dir / 'market_data.db',
            'property_data': self.db_dir / 'property_data.db', 
            'economic_data': self.db_dir / 'economic_data.db',
            'forecast_cache': self.db_dir / 'forecast_cache.db'
        }
        self.results = {}
    
    def profile_query(self, db_path: Path, query: str, params: tuple = (), iterations: int = 10) -> Dict[str, Any]:
        """Profile a single query performance."""
        
        execution_times = []
        row_counts = []
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    cursor = conn.execute(query, params)
                    rows = cursor.fetchall()
                    row_count = len(rows)
                    
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                execution_times.append(execution_time)
                row_counts.append(row_count)
                
            except Exception as e:
                self.logger.error(f"Query failed: {e}")
                return {'error': str(e)}
        
        return {
            'avg_time_ms': statistics.mean(execution_times),
            'min_time_ms': min(execution_times),
            'max_time_ms': max(execution_times),
            'std_dev_ms': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            'avg_rows': statistics.mean(row_counts),
            'query': query,
            'params': params
        }
    
    def profile_common_queries(self) -> Dict[str, Any]:
        """Profile the most common queries used in the application."""
        
        self.logger.info("Profiling common database queries...")
        
        # Define common query patterns used in the application
        common_queries = {
            'market_data': [
                {
                    'name': 'get_parameter_data_by_date_range',
                    'query': '''
                        SELECT date, value, data_source 
                        FROM interest_rates 
                        WHERE parameter_name = ? AND geographic_code = ? 
                        AND date BETWEEN ? AND ?
                        ORDER BY date DESC
                    ''',
                    'params': ('treasury_10y', 'NATIONAL', '2020-01-01', '2024-12-31')
                },
                {
                    'name': 'get_latest_cap_rates',
                    'query': '''
                        SELECT date, value, property_type 
                        FROM cap_rates 
                        WHERE geographic_code = ?
                        ORDER BY date DESC 
                        LIMIT 10
                    ''',
                    'params': ('35620',)
                },
                {
                    'name': 'get_all_parameters_for_msa',
                    'query': '''
                        SELECT DISTINCT parameter_name 
                        FROM interest_rates 
                        WHERE geographic_code = ?
                    ''',
                    'params': ('35620',)
                }
            ],
            
            'property_data': [
                {
                    'name': 'get_rental_market_data',
                    'query': '''
                        SELECT date, value, data_source 
                        FROM rental_market_data 
                        WHERE metric_name = ? AND geographic_code = ?
                        ORDER BY date DESC
                    ''',
                    'params': ('rent_growth', '35620')
                },
                {
                    'name': 'get_operating_expenses_range',
                    'query': '''
                        SELECT date, expense_growth 
                        FROM operating_expenses 
                        WHERE geographic_code = ? AND date BETWEEN ? AND ?
                    ''',
                    'params': ('35620', '2020-01-01', '2024-12-31')
                }
            ],
            
            'forecast_cache': [
                {
                    'name': 'get_recent_forecasts',
                    'query': '''
                        SELECT parameter_name, forecast_values, model_performance 
                        FROM prophet_forecasts 
                        WHERE parameter_name = ? AND geographic_code = ? 
                        AND forecast_date >= ?
                        ORDER BY forecast_date DESC 
                        LIMIT 1
                    ''',
                    'params': ('rent_growth', '35620', '2024-01-01')
                },
                {
                    'name': 'get_correlation_matrix',
                    'query': '''
                        SELECT correlation_matrix, parameter_names, calculation_date
                        FROM parameter_correlations 
                        WHERE geographic_code = ? 
                        AND calculation_date >= ?
                        ORDER BY calculation_date DESC 
                        LIMIT 1
                    ''',
                    'params': ('35620', '2024-01-01')
                }
            ]
        }
        
        results = {}
        
        for db_name, queries in common_queries.items():
            if db_name not in self.databases:
                continue
                
            db_path = self.databases[db_name]
            if not db_path.exists():
                self.logger.warning(f"Database {db_name} not found at {db_path}")
                continue
            
            results[db_name] = {}
            
            for query_info in queries:
                query_name = query_info['name']
                query = query_info['query'].strip()
                params = query_info['params']
                
                self.logger.info(f"Profiling {db_name}.{query_name}...")
                
                result = self.profile_query(db_path, query, params)
                results[db_name][query_name] = result
        
        return results
    
    def analyze_table_sizes(self) -> Dict[str, Dict[str, int]]:
        """Analyze table sizes and row counts."""
        
        self.logger.info("Analyzing table sizes...")
        
        table_info = {}
        
        for db_name, db_path in self.databases.items():
            if not db_path.exists():
                continue
                
            table_info[db_name] = {}
            
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    # Get all table names
                    cursor = conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    for table in tables:
                        # Get row count
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                        row_count = cursor.fetchone()[0]
                        
                        # Get approximate table size (simplified)
                        try:
                            cursor = conn.execute(f"SELECT SUM(length(quote(*))) FROM {table}")
                            size_bytes = cursor.fetchone()[0] or 0
                        except:
                            size_bytes = row_count * 100  # Rough estimate
                        
                        table_info[db_name][table] = {
                            'row_count': row_count,
                            'estimated_size_bytes': size_bytes
                        }
                        
            except Exception as e:
                self.logger.error(f"Failed to analyze {db_name}: {e}")
        
        return table_info
    
    def check_index_usage(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze index usage and effectiveness."""
        
        self.logger.info("Analyzing index usage...")
        
        index_info = {}
        
        for db_name, db_path in self.databases.items():
            if not db_path.exists():
                continue
                
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    # Get all indexes
                    cursor = conn.execute("""
                        SELECT name, tbl_name, sql 
                        FROM sqlite_master 
                        WHERE type='index' AND name NOT LIKE 'sqlite_%'
                    """)
                    
                    indexes = []
                    for row in cursor.fetchall():
                        index_name, table_name, sql = row
                        indexes.append({
                            'index_name': index_name,
                            'table_name': table_name,
                            'definition': sql
                        })
                    
                    index_info[db_name] = indexes
                    
            except Exception as e:
                self.logger.error(f"Failed to analyze indexes for {db_name}: {e}")
        
        return index_info
    
    def suggest_optimizations(self, query_results: Dict[str, Any], 
                            table_info: Dict[str, Dict[str, int]]) -> List[str]:
        """Analyze results and suggest optimizations."""
        
        suggestions = ["=== DATABASE OPTIMIZATION SUGGESTIONS ===\n"]
        
        # Identify slow queries (> 50ms average)
        slow_queries = []
        for db_name, queries in query_results.items():
            for query_name, result in queries.items():
                if isinstance(result, dict) and 'avg_time_ms' in result:
                    if result['avg_time_ms'] > 50:
                        slow_queries.append({
                            'db': db_name,
                            'query': query_name,
                            'avg_time': result['avg_time_ms'],
                            'rows': result['avg_rows']
                        })
        
        if slow_queries:
            suggestions.append("SLOW QUERIES IDENTIFIED:")
            for sq in sorted(slow_queries, key=lambda x: x['avg_time'], reverse=True):
                suggestions.append(
                    f"  - {sq['db']}.{sq['query']}: {sq['avg_time']:.2f}ms "
                    f"({sq['rows']:.0f} rows)"
                )
            suggestions.append("")
        
        # Suggest indexes for large tables
        suggestions.append("INDEXING RECOMMENDATIONS:")
        for db_name, tables in table_info.items():
            for table_name, info in tables.items():
                if info['row_count'] > 1000:
                    suggestions.append(
                        f"  - {db_name}.{table_name}: {info['row_count']} rows "
                        f"- Consider composite indexes on frequently queried columns"
                    )
        
        suggestions.append("")
        suggestions.append("GENERAL OPTIMIZATIONS:")
        suggestions.append("  - Add covering indexes for SELECT queries")
        suggestions.append("  - Consider partitioning large tables by date")
        suggestions.append("  - Implement query result caching for expensive operations")
        suggestions.append("  - Use LIMIT clauses for large result sets")
        
        return suggestions
    
    def run_full_profile(self) -> Dict[str, Any]:
        """Run complete database performance profile."""
        
        self.logger.info("Starting comprehensive database performance profile...")
        
        # Profile common queries
        query_results = self.profile_common_queries()
        
        # Analyze table sizes
        table_info = self.analyze_table_sizes()
        
        # Check index usage
        index_info = self.check_index_usage()
        
        # Generate optimization suggestions
        suggestions = self.suggest_optimizations(query_results, table_info)
        
        # Compile full report
        report = {
            'profile_date': datetime.now().isoformat(),
            'query_performance': query_results,
            'table_analysis': table_info,
            'index_analysis': index_info,
            'optimization_suggestions': suggestions
        }
        
        self.logger.info("Database performance profile completed")
        
        return report
    
    def print_performance_report(self, report: Dict[str, Any]):
        """Print a formatted performance report."""
        
        print("\n" + "="*80)
        print("DATABASE PERFORMANCE ANALYSIS REPORT")
        print("="*80)
        print(f"Generated: {report['profile_date']}")
        
        # Query Performance Summary
        print(f"\n{'QUERY PERFORMANCE SUMMARY':<50}")
        print("-" * 80)
        
        for db_name, queries in report['query_performance'].items():
            print(f"\n[{db_name.upper()}]")
            for query_name, result in queries.items():
                if isinstance(result, dict) and 'avg_time_ms' in result:
                    status = "SLOW" if result['avg_time_ms'] > 50 else "FAST"
                    print(f"  {status:<4} {query_name:<35} {result['avg_time_ms']:>8.2f}ms "
                          f"({result['avg_rows']:>6.0f} rows)")
                elif 'error' in result:
                    print(f"  ERR  {query_name:<35} ERROR: {result['error']}")
        
        # Table Analysis
        print(f"\n{'TABLE SIZE ANALYSIS':<50}")
        print("-" * 80)
        
        for db_name, tables in report['table_analysis'].items():
            print(f"\n[{db_name.upper()}]")
            for table_name, info in tables.items():
                size_mb = info['estimated_size_bytes'] / (1024 * 1024) if info['estimated_size_bytes'] else 0
                print(f"  TBL  {table_name:<25} {info['row_count']:>8,} rows "
                      f"({size_mb:>6.1f}MB)")
        
        # Optimization Suggestions
        print(f"\n{'OPTIMIZATION RECOMMENDATIONS':<50}")
        print("-" * 80)
        
        for suggestion in report['optimization_suggestions']:
            print(suggestion)
        
        print("\n" + "="*80)


def main():
    """Main execution function."""
    
    profiler = DatabasePerformanceProfiler()
    
    # Run comprehensive performance analysis
    report = profiler.run_full_profile()
    
    # Display results
    profiler.print_performance_report(report)
    
    # Save detailed report to file
    report_file = project_root / 'performance_analysis_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return report


if __name__ == "__main__":
    main()