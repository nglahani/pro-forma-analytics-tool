/**
 * Performance Testing Utilities
 * Helper functions and types for performance benchmarking
 */

export interface PerformanceMetrics {
  duration: number;
  memoryUsage?: {
    used: number;
    total: number;
  };
  cpuTime?: number;
  networkRequests?: number;
}

export interface PerformanceBenchmark {
  name: string;
  maxDuration: number;
  maxMemoryIncrease?: number;
  description: string;
}

export interface PerformanceResult<T> {
  result: T;
  metrics: PerformanceMetrics;
  benchmark: PerformanceBenchmark;
  passed: boolean;
}

/**
 * Performance benchmarks based on backend integration specs
 */
export const API_PERFORMANCE_BENCHMARKS: Record<string, PerformanceBenchmark> = {
  DCF_ANALYSIS: {
    name: 'DCF Analysis',
    maxDuration: 3000, // 3 seconds
    maxMemoryIncrease: 50 * 1024 * 1024, // 50MB
    description: 'Complete DCF analysis including cash flow projections and financial metrics',
  },
  MONTE_CARLO_START: {
    name: 'Monte Carlo Simulation Start',
    maxDuration: 1000, // 1 second
    maxMemoryIncrease: 10 * 1024 * 1024, // 10MB
    description: 'Initialize and start Monte Carlo simulation',
  },
  MONTE_CARLO_COMPLETE: {
    name: 'Monte Carlo Simulation Complete',
    maxDuration: 10000, // 10 seconds
    maxMemoryIncrease: 100 * 1024 * 1024, // 100MB
    description: 'Complete Monte Carlo simulation with 1000+ scenarios',
  },
  MARKET_DATA_FETCH: {
    name: 'Market Data Fetch',
    maxDuration: 2000, // 2 seconds
    maxMemoryIncrease: 5 * 1024 * 1024, // 5MB
    description: 'Fetch market data for specific MSA including historical trends',
  },
  PROPERTY_TEMPLATES: {
    name: 'Property Templates Load',
    maxDuration: 1000, // 1 second
    maxMemoryIncrease: 2 * 1024 * 1024, // 2MB
    description: 'Load all available property templates with configurations',
  },
  AUTHENTICATION: {
    name: 'Authentication',
    maxDuration: 500, // 500ms
    maxMemoryIncrease: 1 * 1024 * 1024, // 1MB
    description: 'User authentication and token validation',
  },
};

/**
 * Measures performance of an async operation
 */
export async function measurePerformance<T>(
  operation: () => Promise<T>,
  benchmark: PerformanceBenchmark,
  options: {
    measureMemory?: boolean;
    measureCpu?: boolean;
    measureNetwork?: boolean;
  } = {}
): Promise<PerformanceResult<T>> {
  const { measureMemory = true, measureCpu = false, measureNetwork = false } = options;

  // Initial measurements
  const startTime = performance.now();
  const initialMemory = measureMemory && (performance as any).memory?.usedJSHeapSize || 0;
  
  let networkRequestCount = 0;
  if (measureNetwork) {
    // Mock network request counting (would need actual implementation)
    networkRequestCount = 0;
  }

  // Execute operation
  const result = await operation();

  // Final measurements
  const endTime = performance.now();
  const duration = endTime - startTime;
  const finalMemory = measureMemory && (performance as any).memory?.usedJSHeapSize || 0;
  const memoryIncrease = finalMemory - initialMemory;

  const metrics: PerformanceMetrics = {
    duration,
    ...(measureMemory && {
      memoryUsage: {
        used: finalMemory,
        total: (performance as any).memory?.totalJSHeapSize || 0,
      },
    }),
    ...(measureNetwork && {
      networkRequests: networkRequestCount,
    }),
  };

  // Check if performance meets benchmark
  const passed = 
    duration <= benchmark.maxDuration &&
    (!benchmark.maxMemoryIncrease || memoryIncrease <= benchmark.maxMemoryIncrease);

  return {
    result,
    metrics,
    benchmark,
    passed,
  };
}

/**
 * Runs a performance test multiple times and calculates statistics
 */
export async function runPerformanceTest<T>(
  operation: () => Promise<T>,
  benchmark: PerformanceBenchmark,
  iterations: number = 5
): Promise<{
  results: PerformanceResult<T>[];
  statistics: {
    avgDuration: number;
    minDuration: number;
    maxDuration: number;
    stdDeviation: number;
    successRate: number;
  };
}> {
  const results: PerformanceResult<T>[] = [];

  for (let i = 0; i < iterations; i++) {
    const result = await measurePerformance(operation, benchmark);
    results.push(result);
    
    // Small delay between iterations to avoid overwhelming the API
    if (i < iterations - 1) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  // Calculate statistics
  const durations = results.map(r => r.metrics.duration);
  const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
  const minDuration = Math.min(...durations);
  const maxDuration = Math.max(...durations);
  
  const variance = durations.reduce((sum, d) => sum + Math.pow(d - avgDuration, 2), 0) / durations.length;
  const stdDeviation = Math.sqrt(variance);
  
  const successRate = results.filter(r => r.passed).length / results.length;

  return {
    results,
    statistics: {
      avgDuration,
      minDuration,
      maxDuration,
      stdDeviation,
      successRate,
    },
  };
}

/**
 * Generates a performance report
 */
export function generatePerformanceReport(
  testResults: Array<{
    testName: string;
    benchmark: PerformanceBenchmark;
    statistics: {
      avgDuration: number;
      minDuration: number;
      maxDuration: number;
      stdDeviation: number;
      successRate: number;
    };
  }>
): string {
  const lines: string[] = [];
  
  lines.push('# API Performance Benchmarking Report');
  lines.push('');
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push('');
  
  // Summary table
  lines.push('## Summary');
  lines.push('');
  lines.push('| Test | Benchmark | Avg Duration | Max Duration | Success Rate | Status |');
  lines.push('|------|-----------|--------------|--------------|--------------|--------|');
  
  testResults.forEach(({ testName, benchmark, statistics }) => {
    const status = statistics.successRate >= 0.8 ? '✅ PASS' : '❌ FAIL';
    const avgDurationFormatted = `${statistics.avgDuration.toFixed(1)}ms`;
    const maxDurationFormatted = `${statistics.maxDuration.toFixed(1)}ms`;
    const benchmarkFormatted = `${benchmark.maxDuration}ms`;
    const successRateFormatted = `${(statistics.successRate * 100).toFixed(1)}%`;
    
    lines.push(
      `| ${testName} | ${benchmarkFormatted} | ${avgDurationFormatted} | ${maxDurationFormatted} | ${successRateFormatted} | ${status} |`
    );
  });
  
  lines.push('');
  
  // Detailed results
  lines.push('## Detailed Results');
  lines.push('');
  
  testResults.forEach(({ testName, benchmark, statistics }) => {
    lines.push(`### ${testName}`);
    lines.push('');
    lines.push(`**Description**: ${benchmark.description}`);
    lines.push(`**Benchmark**: ${benchmark.maxDuration}ms`);
    lines.push('');
    lines.push('**Results**:');
    lines.push(`- Average Duration: ${statistics.avgDuration.toFixed(1)}ms`);
    lines.push(`- Min Duration: ${statistics.minDuration.toFixed(1)}ms`);
    lines.push(`- Max Duration: ${statistics.maxDuration.toFixed(1)}ms`);
    lines.push(`- Standard Deviation: ${statistics.stdDeviation.toFixed(1)}ms`);
    lines.push(`- Success Rate: ${(statistics.successRate * 100).toFixed(1)}%`);
    lines.push('');
    
    // Performance analysis
    const performanceRatio = statistics.avgDuration / benchmark.maxDuration;
    if (performanceRatio <= 0.5) {
      lines.push('**Analysis**: Excellent performance - significantly under benchmark 🚀');
    } else if (performanceRatio <= 0.8) {
      lines.push('**Analysis**: Good performance - comfortably within benchmark ✅');
    } else if (performanceRatio <= 1.0) {
      lines.push('**Analysis**: Acceptable performance - meeting benchmark requirements ⚠️');
    } else {
      lines.push('**Analysis**: Performance concern - exceeding benchmark requirements ❌');
    }
    
    lines.push('');
  });
  
  // Recommendations
  lines.push('## Recommendations');
  lines.push('');
  
  const failedTests = testResults.filter(r => r.statistics.successRate < 0.8);
  if (failedTests.length === 0) {
    lines.push('All performance benchmarks are being met. Continue monitoring performance in production.');
  } else {
    lines.push('The following tests are not meeting performance requirements:');
    lines.push('');
    failedTests.forEach(({ testName, benchmark, statistics }) => {
      lines.push(`- **${testName}**: Average ${statistics.avgDuration.toFixed(1)}ms exceeds ${benchmark.maxDuration}ms benchmark`);
      
      // Specific recommendations
      if (testName.includes('DCF')) {
        lines.push('  - Consider optimizing financial calculation algorithms');
        lines.push('  - Implement result caching for similar property inputs');
        lines.push('  - Review database query performance');
      } else if (testName.includes('Monte Carlo')) {
        lines.push('  - Consider parallel processing for scenario generation');
        lines.push('  - Optimize correlation matrix calculations');
        lines.push('  - Implement progressive result streaming');
      } else if (testName.includes('Market Data')) {
        lines.push('  - Implement aggressive caching for market data');
        lines.push('  - Consider pre-loading frequently accessed MSA data');
        lines.push('  - Optimize database indexing for time series queries');
      }
      
      lines.push('');
    });
  }
  
  return lines.join('\n');
}

/**
 * Load testing utility for concurrent operations
 */
export async function runLoadTest<T>(
  operation: () => Promise<T>,
  benchmark: PerformanceBenchmark,
  concurrentUsers: number = 5,
  duration: number = 30000 // 30 seconds
): Promise<{
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  requestsPerSecond: number;
  errors: Error[];
}> {
  const startTime = Date.now();
  const endTime = startTime + duration;
  const results: Array<{ success: boolean; duration: number; error?: Error }> = [];
  const errors: Error[] = [];

  // Start concurrent users
  const userPromises = Array.from({ length: concurrentUsers }, async () => {
    while (Date.now() < endTime) {
      const requestStart = performance.now();
      try {
        await operation();
        const requestEnd = performance.now();
        results.push({
          success: true,
          duration: requestEnd - requestStart,
        });
      } catch (error) {
        const requestEnd = performance.now();
        errors.push(error as Error);
        results.push({
          success: false,
          duration: requestEnd - requestStart,
          error: error as Error,
        });
      }
      
      // Small delay between requests from same user
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  });

  await Promise.all(userPromises);

  const totalRequests = results.length;
  const successfulRequests = results.filter(r => r.success).length;
  const failedRequests = totalRequests - successfulRequests;
  const averageResponseTime = results.reduce((sum, r) => sum + r.duration, 0) / totalRequests;
  const actualDuration = Date.now() - startTime;
  const requestsPerSecond = (totalRequests / actualDuration) * 1000;

  return {
    totalRequests,
    successfulRequests,
    failedRequests,
    averageResponseTime,
    requestsPerSecond,
    errors,
  };
}

/**
 * Memory leak detection utility
 */
export async function detectMemoryLeaks<T>(
  operation: () => Promise<T>,
  iterations: number = 10
): Promise<{
  hasMemoryLeak: boolean;
  memoryGrowth: number;
  iterations: number;
  memorySnapshots: number[];
}> {
  const memorySnapshots: number[] = [];
  
  // Force garbage collection before starting
  if (global.gc) {
    global.gc();
  }
  
  // Take initial memory snapshot
  const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
  memorySnapshots.push(initialMemory);

  // Run operations
  for (let i = 0; i < iterations; i++) {
    await operation();
    
    // Force garbage collection every few iterations
    if (global.gc && i % 3 === 0) {
      global.gc();
    }
    
    const currentMemory = (performance as any).memory?.usedJSHeapSize || 0;
    memorySnapshots.push(currentMemory);
  }

  // Final garbage collection
  if (global.gc) {
    global.gc();
  }
  
  const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
  memorySnapshots.push(finalMemory);
  
  const memoryGrowth = finalMemory - initialMemory;
  const acceptableGrowth = 10 * 1024 * 1024; // 10MB
  const hasMemoryLeak = memoryGrowth > acceptableGrowth;

  return {
    hasMemoryLeak,
    memoryGrowth,
    iterations,
    memorySnapshots,
  };
}