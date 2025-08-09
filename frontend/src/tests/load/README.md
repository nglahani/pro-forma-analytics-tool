# Concurrent User and Memory Load Testing

Comprehensive load testing suite that validates system behavior under multiple simultaneous users and monitors resource consumption patterns.

## Overview

This load testing suite simulates realistic user behavior patterns to validate system performance, scalability, and resource management under concurrent load. It focuses on the financial analysis workflows that are most critical to application success.

## What We Test

### 👥 **Concurrent User Scenarios**
- **Multiple DCF Analyses**: Simultaneous property analysis requests
- **Monte Carlo Simulations**: Parallel risk analysis computations
- **Market Data Access**: Concurrent market data fetching
- **Database Connections**: Connection pooling and resource limits
- **Session Management**: User state isolation and cleanup

### 🧠 **Memory Usage Patterns**
- **Memory Growth**: Heap usage during sustained operations
- **Memory Leaks**: Detection of unreleased resources
- **Garbage Collection**: Memory cleanup effectiveness
- **Resource Cleanup**: Component unmounting and event listener cleanup
- **Peak Usage**: Memory pressure under high load

### ⚡ **Performance Metrics**
- **Response Times**: API and UI response latency
- **Throughput**: Operations per second capacity
- **Success Rates**: Error rates under load
- **Resource Utilization**: CPU and memory consumption
- **Scalability Limits**: Breaking point identification

## Test Structure

```
src/tests/load/
├── concurrent-users.test.ts    # Main concurrent user test suite
├── load-utils.ts              # Load testing utilities and classes
├── load-reporter.js           # Custom load test reporter
├── fixtures/                  # Test data and scenarios
└── README.md                  # This file
```

## Running Load Tests

### Prerequisites

1. **Install Dependencies**:
   ```bash
   npm install
   npx playwright install
   ```

2. **Start Application**:
   ```bash
   npm run dev
   ```

### Basic Load Testing

```bash
# Run all load tests (default configuration)
npm run test:load

# Light load testing (5 concurrent users)
npm run test:load:light

# Medium load testing (10 concurrent users)  
npm run test:load:medium

# Heavy load testing (20 concurrent users)
npm run test:load:heavy
```

### Specialized Testing

```bash
# Memory-focused testing
npm run test:load:memory

# Stress testing (extended duration)
npm run test:load:stress

# View load test results
npm run test:load:report
```

### Custom Configuration

```bash
# Custom user count and duration
MAX_CONCURRENT_USERS=15 LOAD_TEST_DURATION=180000 npm run test:load

# Memory threshold testing
MEMORY_THRESHOLD=100000000 npm run test:load:memory

# Debug mode with verbose output
DEBUG=pw:api npm run test:load
```

## Test Scenarios

### 1. Concurrent DCF Analyses

**Objective**: Validate system handling of multiple simultaneous property analyses

```typescript
test('should handle multiple concurrent DCF analyses', async ({ browser }) => {
  const userCount = 5;
  // Simulates 5 users performing DCF analysis simultaneously
  // Measures: success rate, response time, resource usage
});
```

**Metrics**:
- Success Rate: >90% expected
- Response Time: <30 seconds per analysis
- Memory Growth: <200MB during test

### 2. Memory Usage Monitoring

**Objective**: Track memory consumption patterns and detect leaks

```typescript  
test('should monitor memory usage during concurrent operations', async ({ browser }) => {
  // Monitors heap usage during intensive operations
  // Detects: memory leaks, excessive growth, cleanup issues
});
```

**Metrics**:
- Memory Growth: <500MB threshold
- Leak Detection: 0 potential leaks
- Cleanup Efficiency: >95% memory recovered

### 3. Database Connection Limits

**Objective**: Test connection pooling and resource management

```typescript
test('should handle database connection limits', async ({ browser }) => {
  // Tests with 8+ concurrent database-heavy operations
  // Validates: connection pooling, timeout handling, recovery
});
```

**Metrics**:
- Connection Success: >80% under load
- Average Duration: <20 seconds
- Recovery Time: <15 seconds

### 4. Sustained Load Testing

**Objective**: Validate performance over extended periods

```typescript
test('should handle sustained load over time', async ({ browser }) => {
  // Runs continuous operations for 60+ seconds
  // Tests: performance degradation, resource cleanup, stability
});
```

**Metrics**:
- Throughput Stability: ±10% variance
- Error Rate: <10% over time
- Resource Stability: No continuous growth

## User Behavior Simulation

### Realistic User Journeys

The load testing framework simulates 4 types of realistic user behavior:

#### 1. Quick Analysis User
- Navigate to app → Select template → Minimal form → Submit analysis
- **Duration**: 30-60 seconds
- **Focus**: Speed and efficiency testing

#### 2. Detailed Analysis User  
- Complete form → DCF analysis → Monte Carlo simulation → Results review
- **Duration**: 2-5 minutes
- **Focus**: Comprehensive workflow testing

#### 3. Comparison Analysis User
- Multiple property comparisons → Side-by-side analysis
- **Duration**: 3-8 minutes  
- **Focus**: Resource management under repeated operations

#### 4. Market Research User
- Market data exploration → Multiple MSAs → Trend analysis
- **Duration**: 1-3 minutes
- **Focus**: Database and caching performance

### User Behavior Patterns

```typescript
class RealisticUserSimulator {
  async simulateRealisticSession(): Promise<UserMetrics> {
    const journeyType = this.selectUserJourney();
    // Executes realistic user behavior with timing variations
    // Records: operations completed, errors, response times
  }
}
```

## Memory Monitoring

### Advanced Memory Analysis

```typescript
class AdvancedMemoryMonitor {
  async startMonitoring(): Promise<void> {
    // Tracks: heap usage, garbage collection, leak patterns
    // Detects: sustained growth, cleanup failures, thresholds
  }
  
  detectMemoryLeaks(threshold: number): number {
    // Analyzes memory growth patterns
    // Identifies potential leak scenarios
  }
}
```

### Memory Metrics Collected

- **Heap Usage**: Used/total/limit tracking
- **Growth Patterns**: Sustained increase detection  
- **Peak Usage**: Maximum memory consumption
- **Cleanup Efficiency**: Post-operation memory recovery
- **Leak Indicators**: Patterns suggesting memory leaks

## Performance Benchmarks

### Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Success Rate** | ≥95% | Successful operations / Total operations |
| **Response Time** | ≤5 seconds | Average API response time |
| **Throughput** | ≥1 ops/sec | Operations completed per second |
| **Memory Growth** | ≤500MB | Peak usage - Initial usage |
| **Error Rate** | ≤5% | Failed operations / Total operations |

### Load Testing Thresholds

```typescript
const LOAD_CONFIG = {
  maxConcurrentUsers: 10,     // Default concurrent users
  testDuration: 120000,       // 2 minutes default duration
  memoryThreshold: 500 * 1024 * 1024, // 500MB memory limit
  maxResponseTime: 10000,     // 10 seconds timeout
  targetThroughput: 5,        // 5 operations per second
};
```

## Reporting and Analysis

### Automated Reports

Load tests generate comprehensive reports:

1. **Load Test Report** (`load-test-report.md`):
   - Executive summary with key metrics
   - Performance benchmark comparison
   - Test results breakdown
   - Error analysis and recommendations

2. **Performance Data** (`performance-data.json`):
   - Machine-readable metrics
   - Detailed test results
   - Benchmark comparisons
   - Metadata and environment info

3. **Metrics Dashboard** (`load-metrics.html`):
   - Interactive HTML dashboard
   - Visual metrics display
   - Success/failure indicators
   - Error breakdown charts

### Sample Report Output

```markdown
# Load Testing Report

**Concurrent Users Tested**: 10
**Total Operations**: 45
**Success Rate**: 93.3%
**Average Response Time**: 3,247ms  
**Throughput**: 2.14 ops/sec

## Performance Analysis
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Success Rate | ≥95% | 93.3% | ❌ FAIL |
| Response Time | ≤5000ms | 3,247ms | ✅ PASS |
| Throughput | ≥1 ops/s | 2.14 ops/s | ✅ PASS |
```

### Error Analysis

Errors are automatically categorized by type:
- **Timeout**: Request timeout errors
- **Memory**: Memory-related failures
- **Connection**: Database connection issues
- **Network**: Network connectivity problems
- **Database**: Database query failures
- **Assertion**: Test assertion failures

## CI/CD Integration

### GitHub Actions Setup

```yaml
name: Load Testing
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:load:medium
      - uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: load-reports/
```

### Performance Monitoring

```typescript
// Integration with monitoring systems
class LoadTestMonitor {
  async sendMetricsToMonitoring(metrics) {
    // Send performance metrics to monitoring system
    // Trigger alerts for performance degradation
  }
}
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**:
   ```bash
   # Enable garbage collection
   node --expose-gc $(npm bin)/playwright test --config=playwright-load.config.ts
   ```

2. **Connection Timeouts**:
   ```typescript
   // Increase timeouts in configuration
   timeout: 300000, // 5 minutes
   navigationTimeout: 180000, // 3 minutes
   ```

3. **Resource Exhaustion**:
   ```bash
   # Reduce concurrent users
   MAX_CONCURRENT_USERS=5 npm run test:load
   ```

### Debug Commands

```bash
# Verbose output
DEBUG=pw:api npm run test:load

# Memory debugging
node --inspect $(npm bin)/playwright test --config=playwright-load.config.ts

# Single test debugging
npx playwright test concurrent-users.test.ts -g "concurrent DCF" --debug
```

### Memory Analysis

```bash
# Generate heap snapshots
node --inspect-brk $(npm bin)/playwright test --config=playwright-load.config.ts

# Analyze memory leaks
node --trace-gc $(npm bin)/playwright test --config=playwright-load.config.ts
```

## Best Practices

### Test Design

1. **Realistic Scenarios**: Model actual user behavior patterns
2. **Gradual Load**: Start small and increase concurrent users
3. **Resource Monitoring**: Track memory, CPU, and connections
4. **Failure Recovery**: Test system recovery after failures

### Performance Optimization

1. **Connection Pooling**: Optimize database connection management
2. **Caching Strategies**: Implement effective caching for repeated data
3. **Resource Cleanup**: Ensure proper cleanup of resources
4. **Monitoring Integration**: Set up alerts for performance degradation

### Maintenance

1. **Regular Execution**: Run load tests regularly (daily/weekly)
2. **Baseline Updates**: Update benchmarks as system improves
3. **Trend Analysis**: Track performance trends over time
4. **Capacity Planning**: Use results for infrastructure planning

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_CONCURRENT_USERS` | 10 | Maximum concurrent users to simulate |
| `LOAD_TEST_DURATION` | 120000 | Test duration in milliseconds |
| `MEMORY_THRESHOLD` | 524288000 | Memory threshold in bytes (500MB) |
| `LOAD_TIMEOUT` | 300000 | Global test timeout in milliseconds |

### Custom Configuration

```typescript
// playwright-load.config.ts
const LOAD_CONFIG = {
  maxConcurrentUsers: 15,
  testDuration: 180000, // 3 minutes
  memoryThreshold: 1024 * 1024 * 1024, // 1GB
};
```

## Contributing

When adding new load tests:

1. **Follow Naming Conventions**: Use descriptive test names with user counts
2. **Include Metrics Collection**: Always measure relevant performance metrics  
3. **Validate Benchmarks**: Ensure tests validate against performance targets
4. **Document Scenarios**: Clearly document what user behavior is simulated
5. **Update Thresholds**: Adjust performance thresholds as needed

## References

- [Playwright Load Testing](https://playwright.dev/docs/test-parallel)
- [Memory Profiling in Node.js](https://nodejs.org/api/inspector.html)
- [Performance Testing Best Practices](../performance/README.md)
- [Database Connection Pooling](https://en.wikipedia.org/wiki/Connection_pool)