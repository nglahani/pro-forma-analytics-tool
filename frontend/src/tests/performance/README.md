# Performance Testing Suite

Comprehensive performance benchmarking and monitoring for the Pro-Forma Analytics Tool API integration.

## Overview

This performance testing suite validates that all API endpoints meet the specified performance requirements from the backend integration specifications:

- **DCF Analysis**: < 3 seconds
- **Monte Carlo Simulation**: < 10 seconds  
- **Market Data Fetching**: < 2 seconds
- **Property Template Loading**: < 1 second
- **Authentication**: < 500ms

## Test Structure

```
src/tests/performance/
├── api-performance.test.ts      # Main performance test suite
├── performance-utils.ts         # Performance measurement utilities
├── setup-performance.ts        # Test environment configuration
├── performance-reporter.js     # Custom Jest reporter
└── README.md                   # This file
```

## Running Performance Tests

### Basic Performance Testing
```bash
# Run all performance tests
npm run test:performance

# Run with detailed logging
npm run test:performance:verbose

# Run specific test pattern
npm run test:performance -- --testNamePattern="DCF Analysis"
```

### Load Testing
```bash
# Extended load test (60 seconds, 10 concurrent users)
npm run test:load

# Custom load test configuration
LOAD_TEST_DURATION=30000 CONCURRENT_USERS=5 npm run test:performance
```

### Benchmark Regression Testing
```bash
# Run only benchmark regression tests
npm run test:benchmark

# Generate performance report
npm run performance:report
```

## Test Categories

### 1. Authentication Performance
- **Benchmark**: 500ms
- **Tests**: Token validation, health checks, refresh operations
- **Key Metrics**: Response time, token expiration handling

### 2. Property Template Performance  
- **Benchmark**: 1 second
- **Tests**: Template loading, concurrent requests, caching validation
- **Key Metrics**: Load time, cache hit rate, concurrent performance

### 3. Market Data Performance
- **Benchmark**: 2 seconds
- **Tests**: MSA data fetching, multi-region requests, cache effectiveness
- **Key Metrics**: Fetch time, data freshness, cache performance

### 4. DCF Analysis Performance
- **Benchmark**: 3 seconds
- **Tests**: Analysis computation, concurrent analyses, property size scaling
- **Key Metrics**: Calculation time, memory usage, scalability

### 5. Monte Carlo Simulation Performance
- **Benchmark**: 10 seconds (completion), 1 second (start)
- **Tests**: Simulation initialization, progress tracking, scenario scaling
- **Key Metrics**: Start time, completion time, memory efficiency

## Performance Utilities

### measurePerformance()
```typescript
const result = await measurePerformance(
  () => apiClient.analyzeDCF(propertyData),
  API_PERFORMANCE_BENCHMARKS.DCF_ANALYSIS
);

console.log(`Duration: ${result.metrics.duration}ms`);
console.log(`Passed: ${result.passed}`);
```

### runPerformanceTest()
```typescript
const testResults = await runPerformanceTest(
  () => apiClient.getMarketData('NYC'),
  API_PERFORMANCE_BENCHMARKS.MARKET_DATA_FETCH,
  5 // iterations
);

console.log(`Average: ${testResults.statistics.avgDuration}ms`);
console.log(`Success Rate: ${testResults.statistics.successRate * 100}%`);
```

### runLoadTest()
```typescript
const loadResults = await runLoadTest(
  () => apiClient.analyzeDCF(propertyData),
  API_PERFORMANCE_BENCHMARKS.DCF_ANALYSIS,
  5, // concurrent users
  30000 // 30 seconds
);

console.log(`Requests/sec: ${loadResults.requestsPerSecond}`);
console.log(`Success rate: ${loadResults.successfulRequests / loadResults.totalRequests * 100}%`);
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PERFORMANCE_ITERATIONS` | 5 | Number of test iterations per benchmark |
| `LOAD_TEST_DURATION` | 30000 | Load test duration in milliseconds |
| `CONCURRENT_USERS` | 5 | Number of concurrent users for load tests |
| `PERFORMANCE_VERBOSE` | false | Enable detailed logging |
| `API_BASE_URL` | http://localhost:8000 | Base URL for API testing |

### Custom Configuration
```javascript
// jest.performance.config.js
module.exports = {
  testTimeout: 120000, // 2 minutes
  maxWorkers: 1, // Serial execution
  globals: {
    PERFORMANCE_ITERATIONS: 10, // More iterations
    CONCURRENT_USERS: 20, // Higher load
  },
};
```

## Report Generation

### Automated Reports
Performance tests automatically generate:

1. **Console Output**: Real-time test results with status indicators
2. **Markdown Report**: Detailed analysis with recommendations (`performance-results/performance-report.md`)
3. **JSON Data**: Machine-readable benchmark data (`performance-results/benchmark-data.json`)
4. **Trends Tracking**: Historical performance data (`performance-results/performance-trends.json`)

### Sample Report Structure
```markdown
# API Performance Benchmarking Report

**Generated**: 2025-08-07T10:30:00.000Z
**Overall Status**: ✅ PASS

| Category | Tests | Avg Duration | Benchmark | Status |
|----------|-------|--------------|-----------|--------|
| DCF Analysis | 5 | 1,250.5ms | 3000ms | ✅ PASS |
| Monte Carlo | 3 | 8,750.2ms | 10000ms | ✅ PASS |
| Market Data | 15 | 850.1ms | 2000ms | ✅ PASS |

## Detailed Results
### DCF Analysis
- **Average Duration**: 1,250.5ms
- **Analysis**: 🚀 Excellent performance - significantly under benchmark

## Recommendations
All performance benchmarks are being met. Continue monitoring performance.
```

## Monitoring Integration

### CI/CD Integration
```yaml
# .github/workflows/performance.yml
- name: Run Performance Tests
  run: npm run test:performance
  env:
    PERFORMANCE_ITERATIONS: 3
    API_BASE_URL: ${{ secrets.STAGING_API_URL }}
```

### Performance Alerting
The test suite can integrate with monitoring systems:

```typescript
// Alert on performance degradation
if (testResults.statistics.avgDuration > benchmark.maxDuration * 1.2) {
  // Send alert to monitoring system
  console.error(`Performance degradation detected: ${testName}`);
}
```

## Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Enable garbage collection
node --expose-gc $(npm bin)/jest --config=jest.performance.config.js
```

#### Network Timeouts
```javascript
// Increase timeout in configuration
globals: {
  API_TIMEOUT: 30000, // 30 seconds
}
```

#### Inconsistent Results
```bash
# Run with more iterations for statistical significance
PERFORMANCE_ITERATIONS=10 npm run test:performance
```

### Debugging Performance Issues

1. **Enable Verbose Logging**:
   ```bash
   npm run test:performance:verbose
   ```

2. **Check Memory Usage**:
   ```bash
   node --inspect $(npm bin)/jest --config=jest.performance.config.js
   ```

3. **Analyze Network Requests**:
   ```bash
   DEBUG=* npm run test:performance
   ```

## Best Practices

### Writing Performance Tests

1. **Use Realistic Data**: Test with production-like data sizes
2. **Measure End-to-End**: Include network, processing, and rendering time
3. **Account for Variance**: Run multiple iterations and calculate statistics
4. **Test Edge Cases**: Large properties, complex scenarios, error conditions

### Maintaining Performance

1. **Regular Monitoring**: Run performance tests in CI/CD pipeline
2. **Trend Analysis**: Track performance over time to catch regressions
3. **Capacity Planning**: Use load test results for infrastructure planning
4. **Optimization Priorities**: Focus on tests that fail benchmarks

## Advanced Features

### Memory Leak Detection
```typescript
const leakResults = await detectMemoryLeaks(
  () => apiClient.analyzeDCF(propertyData),
  10 // iterations
);

if (leakResults.hasMemoryLeak) {
  console.error(`Memory leak detected: ${leakResults.memoryGrowth} bytes`);
}
```

### Custom Benchmarks
```typescript
const CUSTOM_BENCHMARKS = {
  LARGE_PROPERTY_ANALYSIS: {
    name: 'Large Property Analysis',
    maxDuration: 5000, // 5 seconds for 100+ unit properties
    description: 'DCF analysis for properties with 100+ units',
  },
};
```

### Performance Profiling
```bash
# Generate CPU profile
node --prof $(npm bin)/jest --config=jest.performance.config.js

# Analyze profile
node --prof-process isolate-*.log > performance-profile.txt
```

## Integration with Backend

The performance tests complement the backend's performance monitoring:

- **API Response Times**: Validated against backend metrics
- **Database Performance**: Indirectly tested through API response times  
- **Cache Effectiveness**: Measured through repeated request patterns
- **Resource Utilization**: Memory and CPU usage during operations

## Contributing

When adding new performance tests:

1. Follow the existing pattern in `api-performance.test.ts`
2. Add appropriate benchmarks to `API_PERFORMANCE_BENCHMARKS`
3. Include both single-request and load testing scenarios
4. Document expected performance characteristics
5. Update this README with new test categories

## References

- [Backend Integration Specifications](../../specs/backend-integration/)
- [Jest Performance Testing](https://jestjs.io/docs/configuration#testtimeout)
- [Node.js Performance Monitoring](https://nodejs.org/api/perf_hooks.html)
- [API Performance Best Practices](../../../docs/PERFORMANCE_GUIDELINES.md)