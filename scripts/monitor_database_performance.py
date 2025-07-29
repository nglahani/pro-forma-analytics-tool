"""
Database Performance Monitor

Provides ongoing monitoring of database performance, cache effectiveness,
and query optimization recommendations.
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sys
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.logging_config import get_logger
from src.infrastructure.cache.query_cache import get_cache_statistics, cleanup_expired_cache


class DatabasePerformanceMonitor:
    """Monitors database performance and provides optimization insights."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.db_dir = project_root / "data" / "databases"
        self.monitoring_db = project_root / "data" / "cache" / "performance_monitoring.db"
        
        # Ensure monitoring directory exists
        self.monitoring_db.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize monitoring database
        self._init_monitoring_database()
    
    def _init_monitoring_database(self):
        """Initialize database for storing performance metrics."""
        
        try:
            with sqlite3.connect(str(self.monitoring_db)) as conn:
                # Query performance history
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS query_performance (
                        timestamp TEXT NOT NULL,
                        database_name TEXT NOT NULL,
                        query_name TEXT NOT NULL,
                        avg_time_ms REAL NOT NULL,
                        min_time_ms REAL NOT NULL,
                        max_time_ms REAL NOT NULL,
                        std_dev_ms REAL NOT NULL,
                        row_count INTEGER NOT NULL,
                        PRIMARY KEY (timestamp, database_name, query_name)
                    )
                """)
                
                # Database size metrics
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS database_metrics (
                        timestamp TEXT NOT NULL,
                        database_name TEXT NOT NULL,
                        table_name TEXT NOT NULL,
                        row_count INTEGER NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        PRIMARY KEY (timestamp, database_name, table_name)
                    )
                """)
                
                # Cache performance metrics
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache_metrics (
                        timestamp TEXT NOT NULL PRIMARY KEY,
                        memory_entries INTEGER NOT NULL,
                        persistent_entries INTEGER NOT NULL,
                        total_size_bytes INTEGER NOT NULL,
                        hit_rate REAL NOT NULL,
                        cleanup_removed INTEGER DEFAULT 0
                    )
                """)
                
                # Index usage statistics
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS index_usage (
                        timestamp TEXT NOT NULL,
                        database_name TEXT NOT NULL,
                        index_name TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        PRIMARY KEY (timestamp, database_name, index_name)
                    )
                """)
                
                conn.commit()
                self.logger.info("Initialized performance monitoring database")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring database: {e}")
            raise
    
    def collect_query_performance_metrics(self) -> Dict[str, Any]:
        """Collect current query performance metrics."""
        
        from scripts.profile_database_performance import DatabasePerformanceProfiler
        
        profiler = DatabasePerformanceProfiler()
        performance_data = profiler.profile_common_queries()
        
        timestamp = datetime.now().isoformat()
        
        # Store metrics in monitoring database
        try:
            with sqlite3.connect(str(self.monitoring_db)) as conn:
                for db_name, queries in performance_data.items():
                    for query_name, result in queries.items():
                        if isinstance(result, dict) and 'avg_time_ms' in result:
                            conn.execute("""
                                INSERT OR REPLACE INTO query_performance
                                (timestamp, database_name, query_name, avg_time_ms,
                                 min_time_ms, max_time_ms, std_dev_ms, row_count)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                timestamp, db_name, query_name,
                                result['avg_time_ms'], result['min_time_ms'],
                                result['max_time_ms'], result['std_dev_ms'],
                                int(result['avg_rows'])
                            ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store query performance metrics: {e}")
        
        return performance_data
    
    def collect_database_size_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Collect database and table size metrics."""
        
        timestamp = datetime.now().isoformat()
        size_metrics = {}
        
        databases = {
            'market_data': self.db_dir / 'market_data.db',
            'property_data': self.db_dir / 'property_data.db',
            'economic_data': self.db_dir / 'economic_data.db',
            'forecast_cache': self.db_dir / 'forecast_cache.db'
        }
        
        try:
            with sqlite3.connect(str(self.monitoring_db)) as monitoring_conn:
                for db_name, db_path in databases.items():
                    if not db_path.exists():
                        continue
                    
                    size_metrics[db_name] = {}
                    
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
                            
                            # Estimate table size
                            try:
                                cursor = conn.execute(f"SELECT SUM(length(quote(*))) FROM {table}")
                                size_bytes = cursor.fetchone()[0] or (row_count * 100)
                            except:
                                size_bytes = row_count * 100  # Rough estimate
                            
                            size_metrics[db_name][table] = {
                                'row_count': row_count,
                                'size_bytes': size_bytes
                            }
                            
                            # Store in monitoring database
                            monitoring_conn.execute("""
                                INSERT OR REPLACE INTO database_metrics
                                (timestamp, database_name, table_name, row_count, size_bytes)
                                VALUES (?, ?, ?, ?, ?)
                            """, (timestamp, db_name, table, row_count, size_bytes))
                
                monitoring_conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to collect database size metrics: {e}")
        
        return size_metrics
    
    def collect_cache_metrics(self) -> Dict[str, Any]:
        """Collect cache performance metrics."""
        
        timestamp = datetime.now().isoformat()
        
        # Get cache statistics
        cache_stats = get_cache_statistics()
        
        # Cleanup expired cache entries
        cleanup_removed = cleanup_expired_cache()
        
        # Store metrics
        try:
            with sqlite3.connect(str(self.monitoring_db)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_metrics
                    (timestamp, memory_entries, persistent_entries, 
                     total_size_bytes, hit_rate, cleanup_removed)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    cache_stats.get('memory_entries', 0),
                    cache_stats.get('persistent_entries', 0),
                    cache_stats.get('total_size_bytes', 0),
                    cache_stats.get('hit_rate', 0.0),
                    cleanup_removed
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store cache metrics: {e}")
        
        return {**cache_stats, 'cleanup_removed': cleanup_removed}
    
    def analyze_performance_trends(self, days_back: int = 7) -> Dict[str, Any]:
        """Analyze performance trends over the specified period."""
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        trends = {}
        
        try:
            with sqlite3.connect(str(self.monitoring_db)) as conn:
                # Query performance trends
                cursor = conn.execute("""
                    SELECT database_name, query_name, 
                           AVG(avg_time_ms) as avg_time,
                           COUNT(*) as measurements,
                           MIN(avg_time_ms) as best_time,
                           MAX(avg_time_ms) as worst_time
                    FROM query_performance 
                    WHERE timestamp >= ?
                    GROUP BY database_name, query_name
                    ORDER BY avg_time DESC
                """, (cutoff_date,))
                
                query_trends = []
                for row in cursor.fetchall():
                    db_name, query_name, avg_time, measurements, best_time, worst_time = row
                    query_trends.append({
                        'database': db_name,
                        'query': query_name,
                        'avg_time_ms': avg_time,
                        'measurements': measurements,
                        'best_time_ms': best_time,
                        'worst_time_ms': worst_time,
                        'variability': worst_time - best_time
                    })
                
                trends['query_performance'] = query_trends
                
                # Database growth trends
                cursor = conn.execute("""
                    SELECT database_name, table_name,
                           AVG(row_count) as avg_rows,
                           MAX(row_count) - MIN(row_count) as row_growth,
                           AVG(size_bytes) as avg_size_bytes
                    FROM database_metrics
                    WHERE timestamp >= ?
                    GROUP BY database_name, table_name
                    ORDER BY row_growth DESC
                """, (cutoff_date,))
                
                growth_trends = []
                for row in cursor.fetchall():
                    db_name, table_name, avg_rows, row_growth, avg_size = row
                    growth_trends.append({
                        'database': db_name,
                        'table': table_name,
                        'avg_rows': int(avg_rows),
                        'row_growth': int(row_growth),
                        'avg_size_mb': avg_size / (1024 * 1024) if avg_size else 0
                    })
                
                trends['database_growth'] = growth_trends
                
                # Cache performance trends
                cursor = conn.execute("""
                    SELECT AVG(hit_rate) as avg_hit_rate,
                           AVG(memory_entries) as avg_memory_entries,
                           AVG(persistent_entries) as avg_persistent_entries,
                           SUM(cleanup_removed) as total_cleanup_removed
                    FROM cache_metrics
                    WHERE timestamp >= ?
                """, (cutoff_date,))
                
                cache_row = cursor.fetchone()
                if cache_row:
                    trends['cache_performance'] = {
                        'avg_hit_rate': cache_row[0] or 0.0,
                        'avg_memory_entries': int(cache_row[1] or 0),
                        'avg_persistent_entries': int(cache_row[2] or 0),
                        'total_cleanup_removed': int(cache_row[3] or 0)
                    }
                
        except Exception as e:
            self.logger.error(f"Failed to analyze performance trends: {e}")
        
        return trends
    
    def generate_optimization_recommendations(self, 
                                           performance_data: Dict[str, Any],
                                           trends: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations."""
        
        recommendations = []
        
        # Analyze slow queries
        slow_queries = []
        if 'query_performance' in trends:
            for query in trends['query_performance']:
                if query['avg_time_ms'] > 10.0:  # Queries taking more than 10ms
                    slow_queries.append(query)
        
        if slow_queries:
            recommendations.append("SLOW QUERY OPTIMIZATIONS:")
            for query in slow_queries[:5]:  # Top 5 slowest
                recommendations.append(
                    f"  - {query['database']}.{query['query']}: {query['avg_time_ms']:.2f}ms avg"
                )
                recommendations.append("    Consider adding covering indexes or query optimization")
        
        # Analyze database growth
        if 'database_growth' in trends:
            fast_growing = [t for t in trends['database_growth'] if t['row_growth'] > 1000]
            if fast_growing:
                recommendations.append("\nDATABASE GROWTH CONCERNS:")
                for table in fast_growing[:3]:
                    recommendations.append(
                        f"  - {table['database']}.{table['table']}: +{table['row_growth']} rows"
                    )
                    recommendations.append("    Consider data archiving or partitioning")
        
        # Cache recommendations
        if 'cache_performance' in trends:
            cache_perf = trends['cache_performance']
            if cache_perf['avg_hit_rate'] < 0.5:
                recommendations.append("\nCACHE OPTIMIZATION:")
                recommendations.append(f"  - Hit rate is low ({cache_perf['avg_hit_rate']:.1%})")
                recommendations.append("    Consider increasing cache TTL or improving cache keys")
        
        # General recommendations
        recommendations.extend([
            "\nGENERAL RECOMMENDATIONS:",
            "  - Run VACUUM on databases periodically to reclaim space",
            "  - Monitor index usage with EXPLAIN QUERY PLAN",
            "  - Consider read replicas for high-query-volume scenarios",
            "  - Implement connection pooling for concurrent access"
        ])
        
        return recommendations
    
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle."""
        
        self.logger.info("Starting database performance monitoring cycle...")
        
        # Collect all metrics
        query_metrics = self.collect_query_performance_metrics()
        size_metrics = self.collect_database_size_metrics()
        cache_metrics = self.collect_cache_metrics()
        
        # Analyze trends
        trends = self.analyze_performance_trends()
        
        # Generate recommendations
        recommendations = self.generate_optimization_recommendations(
            query_metrics, trends
        )
        
        # Compile monitoring report
        report = {
            'monitoring_timestamp': datetime.now().isoformat(),
            'query_performance': query_metrics,
            'database_sizes': size_metrics,
            'cache_performance': cache_metrics,
            'performance_trends': trends,
            'recommendations': recommendations
        }
        
        self.logger.info("Database performance monitoring cycle completed")
        
        return report
    
    def print_monitoring_report(self, report: Dict[str, Any]):
        """Print a formatted monitoring report."""
        
        print("\n" + "="*80)
        print("DATABASE PERFORMANCE MONITORING REPORT")
        print("="*80)
        print(f"Generated: {report['monitoring_timestamp']}")
        
        # Cache Performance
        cache_perf = report['cache_performance']
        print(f"\nCACHE PERFORMANCE:")
        print(f"  Memory entries: {cache_perf.get('memory_entries', 0)}")
        print(f"  Persistent entries: {cache_perf.get('persistent_entries', 0)}")
        print(f"  Hit rate: {cache_perf.get('hit_rate', 0):.1%}")
        print(f"  Total size: {cache_perf.get('total_size_bytes', 0) / 1024 / 1024:.1f}MB")
        print(f"  Cleanup removed: {cache_perf.get('cleanup_removed', 0)} entries")
        
        # Query Performance Summary
        print(f"\nQUERY PERFORMANCE SUMMARY:")
        for db_name, queries in report['query_performance'].items():
            times = [q['avg_time_ms'] for q in queries.values() 
                    if isinstance(q, dict) and 'avg_time_ms' in q]
            if times:
                print(f"  [{db_name}] Avg: {statistics.mean(times):.2f}ms, "
                      f"Max: {max(times):.2f}ms")
        
        # Performance Trends
        if 'performance_trends' in report:
            trends = report['performance_trends']
            if 'query_performance' in trends:
                slowest = sorted(trends['query_performance'], 
                               key=lambda x: x['avg_time_ms'], reverse=True)[:3]
                print(f"\nSLOWEST QUERIES:")
                for query in slowest:
                    print(f"  {query['database']}.{query['query']}: {query['avg_time_ms']:.2f}ms")
        
        # Recommendations
        print(f"\nRECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(rec)
        
        print("\n" + "="*80)


def main():
    """Main execution function."""
    
    monitor = DatabasePerformanceMonitor()
    
    # Run monitoring cycle
    report = monitor.run_monitoring_cycle()
    
    # Display results
    monitor.print_monitoring_report(report)
    
    # Save detailed report
    report_file = project_root / 'database_performance_monitoring.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed monitoring report saved to: {report_file}")
    
    return report


if __name__ == "__main__":
    main()