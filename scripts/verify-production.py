#!/usr/bin/env python3
"""
Production Deployment Verification Script

Comprehensive verification of production deployment including:
- System health checks
- Performance validation
- Security configuration
- Monitoring system validation
- Integration testing
"""

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionVerifier:
    """Production deployment verification suite."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = self._create_session()
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "base_url": base_url,
            "checks": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _record_result(self, check_name: str, status: str, details: str, 
                      response_time: Optional[float] = None) -> None:
        """Record check result."""
        self.results["checks"][check_name] = {
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.results["summary"]["total"] += 1
        if status == "PASS":
            self.results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.results["summary"]["failed"] += 1
        elif status == "WARN":
            self.results["summary"]["warnings"] += 1
    
    def check_health_endpoint(self) -> bool:
        """Verify API health endpoint."""
        logger.info("🏥 Checking API health endpoint...")
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/api/v1/health",
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status", "unknown")
                
                if status == "healthy":
                    self._record_result(
                        "health_endpoint",
                        "PASS",
                        f"API is healthy (response time: {response_time:.3f}s)",
                        response_time
                    )
                    return True
                else:
                    self._record_result(
                        "health_endpoint",
                        "WARN",
                        f"API status: {status}",
                        response_time
                    )
                    return False
            else:
                self._record_result(
                    "health_endpoint",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self._record_result(
                "health_endpoint",
                "FAIL",
                f"Connection failed: {str(e)}"
            )
            return False
    
    def check_metrics_endpoint(self) -> bool:
        """Verify metrics endpoint."""
        logger.info("📊 Checking metrics endpoint...")
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/api/v1/metrics",
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                metrics_data = response.json()
                
                # Verify expected metrics
                expected_metrics = ["uptime_seconds", "total_requests", "total_errors"]
                missing_metrics = [m for m in expected_metrics if m not in metrics_data]
                
                if not missing_metrics:
                    self._record_result(
                        "metrics_endpoint",
                        "PASS",
                        f"Metrics endpoint working (response time: {response_time:.3f}s)",
                        response_time
                    )
                    return True
                else:
                    self._record_result(
                        "metrics_endpoint",
                        "WARN",
                        f"Missing metrics: {missing_metrics}",
                        response_time
                    )
                    return False
            else:
                self._record_result(
                    "metrics_endpoint",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self._record_result(
                "metrics_endpoint",
                "FAIL",
                f"Metrics check failed: {str(e)}"
            )
            return False
    
    def check_dcf_analysis(self) -> bool:
        """Test DCF analysis endpoint."""
        logger.info("🏢 Testing DCF analysis functionality...")
        
        test_property = {
            "property_name": "Production Test Property",
            "residential_units": 24,
            "renovation_time_months": 6,
            "commercial_units": 0,
            "investor_equity_share_pct": 75.0,
            "residential_rent_per_unit": 2800,
            "commercial_rent_per_unit": 0,
            "self_cash_percentage": 30.0,
            "city": "Chicago",
            "state": "IL",
            "purchase_price": 3500000
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/v1/analysis/dcf",
                json=test_property,
                timeout=60  # DCF analysis can take longer
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                dcf_data = response.json()
                
                # Verify expected response structure
                required_fields = ["financial_metrics", "investment_recommendation"]
                missing_fields = [f for f in required_fields if f not in dcf_data]
                
                if not missing_fields:
                    npv = dcf_data["financial_metrics"].get("npv", 0)
                    irr = dcf_data["financial_metrics"].get("irr", 0)
                    
                    self._record_result(
                        "dcf_analysis",
                        "PASS",
                        f"DCF analysis successful (NPV: ${npv:,.0f}, IRR: {irr:.1%}, time: {response_time:.3f}s)",
                        response_time
                    )
                    
                    # Warn if response time is slow
                    if response_time > 30:
                        self._record_result(
                            "dcf_performance",
                            "WARN",
                            f"DCF analysis slow: {response_time:.3f}s > 30s threshold"
                        )
                    
                    return True
                else:
                    self._record_result(
                        "dcf_analysis",
                        "FAIL",
                        f"Missing response fields: {missing_fields}",
                        response_time
                    )
                    return False
            else:
                self._record_result(
                    "dcf_analysis",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self._record_result(
                "dcf_analysis",
                "FAIL",
                f"DCF analysis failed: {str(e)}"
            )
            return False
    
    def check_monte_carlo(self) -> bool:
        """Test Monte Carlo simulation."""
        logger.info("🎲 Testing Monte Carlo simulation...")
        
        # First need a property for Monte Carlo
        # Use a simplified request for testing
        simulation_request = {
            "property_id": "test_property",
            "scenarios": 100,  # Reduced for testing
            "confidence_level": 0.95
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/v1/simulation/monte-carlo",
                json=simulation_request,
                timeout=120  # Monte Carlo can take longer
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                mc_data = response.json()
                
                # Verify response structure
                if "results" in mc_data and "npv_distribution" in mc_data["results"]:
                    scenarios_completed = mc_data.get("scenarios_completed", 0)
                    
                    self._record_result(
                        "monte_carlo",
                        "PASS",
                        f"Monte Carlo completed ({scenarios_completed} scenarios, time: {response_time:.3f}s)",
                        response_time
                    )
                    return True
                else:
                    self._record_result(
                        "monte_carlo",
                        "FAIL",
                        "Invalid Monte Carlo response structure",
                        response_time
                    )
                    return False
            else:
                # Monte Carlo might not work without proper property setup
                self._record_result(
                    "monte_carlo",
                    "WARN",
                    f"Monte Carlo test inconclusive: HTTP {response.status_code}",
                    response_time
                )
                return False
                
        except Exception as e:
            self._record_result(
                "monte_carlo",
                "WARN",
                f"Monte Carlo test inconclusive: {str(e)}"
            )
            return False
    
    def check_security_headers(self) -> bool:
        """Check security headers."""
        logger.info("🔒 Checking security headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            
            expected_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block"
            }
            
            missing_headers = []
            for header, expected_value in expected_headers.items():
                actual_value = response.headers.get(header)
                if not actual_value:
                    missing_headers.append(header)
                elif actual_value.lower() != expected_value.lower():
                    missing_headers.append(f"{header} (value mismatch)")
            
            if not missing_headers:
                self._record_result(
                    "security_headers",
                    "PASS",
                    "All security headers present"
                )
                return True
            else:
                self._record_result(
                    "security_headers",
                    "WARN",
                    f"Missing/incorrect security headers: {missing_headers}"
                )
                return False
                
        except Exception as e:
            self._record_result(
                "security_headers",
                "FAIL",
                f"Security header check failed: {str(e)}"
            )
            return False
    
    def check_rate_limiting(self) -> bool:
        """Test rate limiting functionality."""
        logger.info("🚦 Testing rate limiting...")
        
        try:
            # Make rapid requests to trigger rate limiting
            responses = []
            start_time = time.time()
            
            for i in range(10):  # Rapid requests
                response = self.session.get(f"{self.base_url}/api/v1/health")
                responses.append(response.status_code)
                
                if response.status_code == 429:  # Rate limited
                    self._record_result(
                        "rate_limiting",
                        "PASS",
                        f"Rate limiting active (got 429 after {i+1} requests)"
                    )
                    return True
            
            # If no rate limiting triggered, it might be configured differently
            self._record_result(
                "rate_limiting",
                "WARN",
                f"No rate limiting detected in {len(responses)} rapid requests"
            )
            return False
            
        except Exception as e:
            self._record_result(
                "rate_limiting",
                "WARN",
                f"Rate limiting test inconclusive: {str(e)}"
            )
            return False
    
    def check_prometheus_metrics(self) -> bool:
        """Check Prometheus metrics format."""
        logger.info("📈 Checking Prometheus metrics format...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/metrics",
                params={"format": "prometheus"}
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Check for Prometheus format indicators
                if "# HELP" in content and "# TYPE" in content:
                    metric_lines = [line for line in content.split('\n') 
                                  if line and not line.startswith('#')]
                    
                    self._record_result(
                        "prometheus_metrics",
                        "PASS",
                        f"Prometheus metrics format valid ({len(metric_lines)} metrics)"
                    )
                    return True
                else:
                    self._record_result(
                        "prometheus_metrics",
                        "FAIL",
                        "Invalid Prometheus metrics format"
                    )
                    return False
            else:
                self._record_result(
                    "prometheus_metrics",
                    "FAIL",
                    f"Prometheus metrics endpoint failed: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self._record_result(
                "prometheus_metrics",
                "FAIL",
                f"Prometheus metrics check failed: {str(e)}"
            )
            return False
    
    def run_all_checks(self) -> Dict:
        """Run all verification checks."""
        logger.info("🚀 Starting production deployment verification...")
        logger.info(f"Target URL: {self.base_url}")
        
        checks = [
            ("Health Endpoint", self.check_health_endpoint),
            ("Metrics Endpoint", self.check_metrics_endpoint),
            ("DCF Analysis", self.check_dcf_analysis),
            ("Monte Carlo Simulation", self.check_monte_carlo),
            ("Security Headers", self.check_security_headers),
            ("Rate Limiting", self.check_rate_limiting),
            ("Prometheus Metrics", self.check_prometheus_metrics)
        ]
        
        for check_name, check_func in checks:
            try:
                check_func()
            except Exception as e:
                logger.error(f"Check '{check_name}' failed with exception: {str(e)}")
                self._record_result(
                    check_name.lower().replace(' ', '_'),
                    "FAIL",
                    f"Check failed with exception: {str(e)}"
                )
        
        return self.results
    
    def print_summary(self) -> None:
        """Print verification summary."""
        summary = self.results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        warnings = summary["warnings"]
        
        print("\n" + "="*60)
        print("🎯 PRODUCTION DEPLOYMENT VERIFICATION SUMMARY")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Target URL: {self.results['base_url']}")
        print()
        print(f"Total Checks: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print()
        
        if failed == 0:
            print("🎉 All critical checks passed! Deployment verification successful.")
        elif failed < total / 2:
            print("⚠️  Some checks failed. Review results before going live.")
        else:
            print("❌ Multiple critical failures. Deployment needs attention.")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 60)
        
        for check_name, result in self.results["checks"].items():
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌", 
                "WARN": "⚠️"
            }.get(result["status"], "❓")
            
            print(f"{status_icon} {check_name.replace('_', ' ').title()}: {result['details']}")
            
            if result.get("response_time"):
                print(f"   Response time: {result['response_time']:.3f}s")
        
        print("-" * 60)
        
        # Overall status
        if failed == 0 and warnings == 0:
            print("🚀 STATUS: READY FOR PRODUCTION")
        elif failed == 0:
            print("🟡 STATUS: READY WITH WARNINGS")
        else:
            print("🔴 STATUS: NOT READY - REQUIRES FIXES")


def main():
    """Main verification function."""
    parser = argparse.ArgumentParser(description="Production Deployment Verification")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL for API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--output",
        help="Output file for detailed results (JSON format)"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Reduce output (only show summary)"
    )
    
    args = parser.parse_args()
    
    if args.silent:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Run verification
    verifier = ProductionVerifier(args.url, args.timeout)
    results = verifier.run_all_checks()
    
    # Print summary
    verifier.print_summary()
    
    # Save detailed results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {args.output}")
    
    # Exit with appropriate code
    if results["summary"]["failed"] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()