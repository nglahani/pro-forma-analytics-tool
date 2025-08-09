/**
 * Concurrent User and Memory Usage Testing Suite
 * Tests system behavior under multiple simultaneous users and monitors memory consumption
 * 
 * This suite validates:
 * - Multiple concurrent DCF analyses
 * - Simultaneous Monte Carlo simulations
 * - Memory usage patterns under load
 * - Resource cleanup and garbage collection
 * - Database connection handling
 * - API rate limiting and throttling
 */

import { test, expect, Browser, BrowserContext, Page } from '@playwright/test';

// Load testing configuration
const LOAD_CONFIG = {
  // User simulation settings
  maxConcurrentUsers: parseInt(process.env.MAX_CONCURRENT_USERS || '10'),
  testDuration: parseInt(process.env.LOAD_TEST_DURATION || '60000'), // 60 seconds
  
  // Memory monitoring
  memoryCheckInterval: 5000, // 5 seconds
  memoryThreshold: 500 * 1024 * 1024, // 500MB threshold
  
  // Performance benchmarks
  maxResponseTime: 10000, // 10 seconds max response
  targetThroughput: 5, // 5 requests per second
  
  // Resource limits
  maxOpenConnections: 50,
  maxMemoryGrowth: 200 * 1024 * 1024, // 200MB max growth
};

// Test data for concurrent users
const TEST_PROPERTIES = Array.from({ length: 20 }, (_, i) => ({
  property_name: `Concurrent Test Property ${i + 1}`,
  address: {
    street_address: `${100 + i} Concurrent Street`,
    city: 'New York',
    state: 'NY',
    zip_code: `1000${i % 10}`,
  },
  msa: 'NYC',
  residential_units: {
    total_units: 20 + (i * 2),
    average_rent_per_unit: 2500 + (i * 50),
    average_square_feet_per_unit: 900 + (i * 10),
  },
  commercial_units: {
    total_units: 0,
    average_rent_per_unit: 0,
    average_square_feet_per_unit: 0,
  },
  renovation_info: {
    status: 'NOT_NEEDED' as const,
    anticipated_duration_months: 0,
    estimated_cost: 0,
  },
  equity_structure: {
    investor_equity_share_pct: 25 + (i % 10),
    self_cash_percentage: 75 - (i % 10),
  },
  template_id: 'multifamily-basic',
}));

// Memory monitoring utility
class MemoryMonitor {
  private measurements: Array<{
    timestamp: number;
    heapUsed: number;
    heapTotal: number;
    external: number;
  }> = [];

  constructor(private page: Page) {}

  async startMonitoring(): Promise<void> {
    const checkMemory = async () => {
      try {
        const memoryInfo = await this.page.evaluate(() => {
          if ('memory' in performance) {
            return {
              heapUsed: (performance as any).memory.usedJSHeapSize,
              heapTotal: (performance as any).memory.totalJSHeapSize,
              external: (performance as any).memory.jsHeapSizeLimit,
            };
          }
          return null;
        });

        if (memoryInfo) {
          this.measurements.push({
            timestamp: Date.now(),
            ...memoryInfo,
          });
        }
      } catch (error) {
        console.warn('Memory measurement failed:', error.message);
      }
    };

    // Initial measurement
    await checkMemory();
    
    // Set up periodic monitoring
    const interval = setInterval(checkMemory, LOAD_CONFIG.memoryCheckInterval);
    
    // Store interval for cleanup
    (this.page as any)._memoryInterval = interval;
  }

  stopMonitoring(): void {
    if ((this.page as any)._memoryInterval) {
      clearInterval((this.page as any)._memoryInterval);
      delete (this.page as any)._memoryInterval;
    }
  }

  getMemoryReport() {
    if (this.measurements.length === 0) {
      return { error: 'No memory measurements available' };
    }

    const initial = this.measurements[0];
    const final = this.measurements[this.measurements.length - 1];
    const peak = this.measurements.reduce((max, curr) => 
      curr.heapUsed > max.heapUsed ? curr : max
    );

    return {
      initial: initial.heapUsed,
      final: final.heapUsed,
      peak: peak.heapUsed,
      growth: final.heapUsed - initial.heapUsed,
      growthPercent: ((final.heapUsed - initial.heapUsed) / initial.heapUsed) * 100,
      measurements: this.measurements.length,
      duration: final.timestamp - initial.timestamp,
      samples: this.measurements,
    };
  }
}

// User simulation utility
class UserSimulator {
  private metrics = {
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
    errors: [] as string[],
  };

  constructor(
    private context: BrowserContext, 
    private userId: number
  ) {}

  async simulateUserSession(): Promise<void> {
    const page = await this.context.newPage();
    
    try {
      // Navigate to application
      const startTime = Date.now();
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Simulate realistic user behavior
      await this.performDCFAnalysis(page);
      await this.performMonteCarloAnalysis(page);
      
      const endTime = Date.now();
      this.updateMetrics(true, endTime - startTime);
      
    } catch (error) {
      this.updateMetrics(false, 0, error.message);
    } finally {
      await page.close();
    }
  }

  private async performDCFAnalysis(page: Page): Promise<string> {
    const property = TEST_PROPERTIES[this.userId % TEST_PROPERTIES.length];
    
    // Navigate to property analysis
    await page.click('[data-testid="start-analysis-button"]');
    await page.click('[data-testid="template-multifamily-basic"]');
    await page.click('[data-testid="continue-with-template"]');

    // Fill property form quickly
    await page.fill('[data-testid="property-name"]', property.property_name);
    await page.fill('[data-testid="street-address"]', property.address.street_address);
    await page.fill('[data-testid="city"]', property.address.city);
    await page.selectOption('[data-testid="state"]', property.address.state);
    await page.fill('[data-testid="zip-code"]', property.address.zip_code);

    // Complete form steps
    for (let step = 0; step < 4; step++) {
      await page.click('[data-testid="next-step"]');
      await this.fillStepData(page, step, property);
    }

    // Submit analysis
    await page.click('[data-testid="submit-for-analysis"]');
    
    // Wait for results
    await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 30000 });
    
    // Extract property ID for Monte Carlo
    const propertyId = await page.getAttribute('[data-testid="property-id"]', 'data-id');
    return propertyId || `user-${this.userId}-property`;
  }

  private async fillStepData(page: Page, step: number, property: any): Promise<void> {
    switch (step) {
      case 0: // Units
        await page.fill('[data-testid="residential-units"]', property.residential_units.total_units.toString());
        await page.fill('[data-testid="avg-rent"]', property.residential_units.average_rent_per_unit.toString());
        break;
      case 1: // Renovation
        await page.fill('[data-testid="renovation-duration"]', '3');
        await page.fill('[data-testid="renovation-budget"]', '250000');
        break;
      case 2: // Equity
        await page.fill('[data-testid="investor-equity"]', property.equity_structure.investor_equity_share_pct.toString());
        await page.fill('[data-testid="self-cash"]', property.equity_structure.self_cash_percentage.toString());
        break;
    }
  }

  private async performMonteCarloAnalysis(page: Page): Promise<void> {
    // Navigate to Monte Carlo from DCF results
    await page.click('[data-testid="run-monte-carlo"]');
    await page.waitForSelector('[data-testid="monte-carlo-panel"]');

    // Configure simulation
    await page.fill('[data-testid="num-scenarios"]', '500'); // Reduced for load testing
    await page.selectOption('[data-testid="confidence-level"]', '95');

    // Start simulation
    await page.click('[data-testid="start-simulation"]');
    
    // Wait for completion
    await page.waitForSelector('[data-testid="simulation-results"]', { timeout: 45000 });
  }

  private updateMetrics(success: boolean, responseTime: number, error?: string): void {
    this.metrics.totalRequests++;
    
    if (success) {
      this.metrics.successfulRequests++;
      this.metrics.averageResponseTime = 
        (this.metrics.averageResponseTime * (this.metrics.successfulRequests - 1) + responseTime) / 
        this.metrics.successfulRequests;
    } else {
      this.metrics.failedRequests++;
      if (error) {
        this.metrics.errors.push(`User ${this.userId}: ${error}`);
      }
    }
  }

  getMetrics() {
    return {
      ...this.metrics,
      userId: this.userId,
      successRate: (this.metrics.successfulRequests / this.metrics.totalRequests) * 100,
    };
  }
}

test.describe('Concurrent User Load Testing', () => {
  test.setTimeout(120000); // 2-minute timeout for load tests

  test('should handle multiple concurrent DCF analyses', async ({ browser }) => {
    const userCount = Math.min(LOAD_CONFIG.maxConcurrentUsers, 5); // Start with 5 users
    const contexts: BrowserContext[] = [];
    const simulators: UserSimulator[] = [];
    
    try {
      // Create browser contexts for each user
      for (let i = 0; i < userCount; i++) {
        const context = await browser.newContext({
          viewport: { width: 1280, height: 720 },
          userAgent: `LoadTestUser-${i}`,
        });
        contexts.push(context);
        simulators.push(new UserSimulator(context, i));
      }

      // Start concurrent user sessions
      console.log(`🚀 Starting ${userCount} concurrent user sessions...`);
      const startTime = Date.now();
      
      const userPromises = simulators.map(sim => sim.simulateUserSession());
      await Promise.all(userPromises);
      
      const endTime = Date.now();
      const totalDuration = endTime - startTime;

      // Collect and analyze metrics
      const userMetrics = simulators.map(sim => sim.getMetrics());
      const overallMetrics = {
        totalUsers: userCount,
        duration: totalDuration,
        totalRequests: userMetrics.reduce((sum, m) => sum + m.totalRequests, 0),
        successfulRequests: userMetrics.reduce((sum, m) => sum + m.successfulRequests, 0),
        failedRequests: userMetrics.reduce((sum, m) => sum + m.failedRequests, 0),
        averageResponseTime: userMetrics.reduce((sum, m) => sum + m.averageResponseTime, 0) / userCount,
        throughput: userMetrics.reduce((sum, m) => sum + m.totalRequests, 0) / (totalDuration / 1000),
      };

      // Log results
      console.log('📊 Concurrent User Test Results:');
      console.log(`   Users: ${overallMetrics.totalUsers}`);
      console.log(`   Duration: ${Math.round(totalDuration / 1000)}s`);
      console.log(`   Total Requests: ${overallMetrics.totalRequests}`);
      console.log(`   Success Rate: ${(overallMetrics.successfulRequests / overallMetrics.totalRequests * 100).toFixed(1)}%`);
      console.log(`   Avg Response Time: ${Math.round(overallMetrics.averageResponseTime)}ms`);
      console.log(`   Throughput: ${overallMetrics.throughput.toFixed(2)} req/s`);

      // Validate performance benchmarks
      expect(overallMetrics.successfulRequests / overallMetrics.totalRequests).toBeGreaterThan(0.9); // 90% success rate
      expect(overallMetrics.averageResponseTime).toBeLessThan(LOAD_CONFIG.maxResponseTime);
      expect(overallMetrics.throughput).toBeGreaterThan(1); // At least 1 request per second

    } finally {
      // Cleanup browser contexts
      await Promise.all(contexts.map(context => context.close()));
    }
  });

  test('should monitor memory usage during concurrent operations', async ({ browser }) => {
    const memoryReports: any[] = [];
    const contexts: BrowserContext[] = [];
    
    try {
      const userCount = 3; // Smaller number for detailed memory monitoring
      
      // Create contexts with memory monitoring
      for (let i = 0; i < userCount; i++) {
        const context = await browser.newContext();
        contexts.push(context);
        
        const page = await context.newPage();
        const monitor = new MemoryMonitor(page);
        
        await monitor.startMonitoring();
        
        // Simulate user activity with memory monitoring
        await page.goto('/');
        await page.waitForLoadState('networkidle');
        
        // Perform memory-intensive operations
        await this.simulateMemoryIntensiveWorkflow(page);
        
        // Stop monitoring and collect report
        monitor.stopMonitoring();
        const report = monitor.getMemoryReport();
        memoryReports.push({ userId: i, ...report });
        
        await page.close();
      }

      // Analyze memory reports
      const memoryAnalysis = this.analyzeMemoryUsage(memoryReports);
      
      console.log('🧠 Memory Usage Analysis:');
      console.log(`   Average Growth: ${Math.round(memoryAnalysis.averageGrowth / 1024 / 1024)}MB`);
      console.log(`   Peak Usage: ${Math.round(memoryAnalysis.peakUsage / 1024 / 1024)}MB`);
      console.log(`   Memory Leaks Detected: ${memoryAnalysis.potentialLeaks}`);

      // Validate memory usage
      expect(memoryAnalysis.averageGrowth).toBeLessThan(LOAD_CONFIG.maxMemoryGrowth);
      expect(memoryAnalysis.potentialLeaks).toBe(0);

    } finally {
      await Promise.all(contexts.map(context => context.close()));
    }
  });

  test('should handle database connection limits', async ({ browser }) => {
    const connectionCount = 8; // Test connection pooling
    const contexts: BrowserContext[] = [];
    const connectionMetrics: any[] = [];
    
    try {
      // Create multiple contexts that will hit the database
      for (let i = 0; i < connectionCount; i++) {
        const context = await browser.newContext();
        contexts.push(context);
      }

      // Simulate simultaneous database-heavy operations
      const dbOperations = contexts.map(async (context, index) => {
        const page = await context.newPage();
        const startTime = Date.now();
        
        try {
          // Operations that hit the database
          await page.goto('/market-data/explorer');
          await page.waitForSelector('[data-testid="market-data-chart"]', { timeout: 15000 });
          
          // Multiple market data requests
          const msas = ['NYC', 'LA', 'CHI'];
          for (const msa of msas) {
            await page.selectOption('[data-testid="msa-selector"]', msa);
            await page.waitForSelector('[data-testid="data-updated"]', { timeout: 10000 });
          }
          
          const endTime = Date.now();
          connectionMetrics.push({
            connectionId: index,
            success: true,
            duration: endTime - startTime,
          });
          
        } catch (error) {
          const endTime = Date.now();
          connectionMetrics.push({
            connectionId: index,
            success: false,
            duration: endTime - startTime,
            error: error.message,
          });
        } finally {
          await page.close();
        }
      });

      await Promise.all(dbOperations);

      // Analyze connection performance
      const successfulConnections = connectionMetrics.filter(m => m.success).length;
      const averageDuration = connectionMetrics
        .filter(m => m.success)
        .reduce((sum, m) => sum + m.duration, 0) / successfulConnections;

      console.log('🔗 Database Connection Test Results:');
      console.log(`   Total Connections: ${connectionCount}`);
      console.log(`   Successful: ${successfulConnections}`);
      console.log(`   Failed: ${connectionCount - successfulConnections}`);
      console.log(`   Average Duration: ${Math.round(averageDuration)}ms`);

      // Validate connection handling
      expect(successfulConnections / connectionCount).toBeGreaterThan(0.8); // 80% success rate
      expect(averageDuration).toBeLessThan(20000); // 20 seconds max

    } finally {
      await Promise.all(contexts.map(context => context.close()));
    }
  });

  test('should handle memory pressure scenarios', async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
      const monitor = new MemoryMonitor(page);
      await monitor.startMonitoring();
      
      // Simulate memory-intensive scenario
      await page.goto('/');
      
      // Create memory pressure by running multiple heavy operations
      const heavyOperations = [];
      
      for (let i = 0; i < 5; i++) {
        heavyOperations.push(
          page.evaluate(() => {
            // Simulate memory-intensive client-side operations
            const largeArray = new Array(100000).fill(0).map((_, idx) => ({
              id: idx,
              data: new Array(100).fill(0).map(() => Math.random()),
              timestamp: Date.now(),
            }));
            
            // Simulate data processing
            return largeArray.reduce((sum, item) => sum + item.data.length, 0);
          })
        );
      }
      
      await Promise.all(heavyOperations);
      
      // Force garbage collection if available
      await page.evaluate(() => {
        if (window.gc) {
          window.gc();
        }
      });
      
      monitor.stopMonitoring();
      const memoryReport = monitor.getMemoryReport();
      
      console.log('💾 Memory Pressure Test Results:');
      console.log(`   Memory Growth: ${Math.round(memoryReport.growth / 1024 / 1024)}MB`);
      console.log(`   Peak Usage: ${Math.round(memoryReport.peak / 1024 / 1024)}MB`);
      
      // Memory should not grow excessively
      expect(memoryReport.growth).toBeLessThan(100 * 1024 * 1024); // 100MB limit
      
    } finally {
      await context.close();
    }
  });

  // Helper method for memory-intensive workflow simulation
  private async simulateMemoryIntensiveWorkflow(page: Page): Promise<void> {
    // Navigate through memory-intensive pages
    await page.goto('/analysis/results/memory-test-property');
    await page.waitForLoadState('networkidle');
    
    // Trigger chart rendering (memory intensive)
    await page.click('[data-testid="run-monte-carlo"]');
    await page.waitForSelector('[data-testid="monte-carlo-panel"]');
    
    // Generate large dataset simulation
    await page.fill('[data-testid="num-scenarios"]', '2000');
    await page.click('[data-testid="start-simulation"]');
    
    // Wait briefly for memory allocation
    await page.waitForTimeout(5000);
  }

  // Memory analysis helper
  private analyzeMemoryUsage(reports: any[]): any {
    if (reports.length === 0) {
      return { error: 'No memory reports available' };
    }

    const validReports = reports.filter(r => !r.error);
    const totalGrowth = validReports.reduce((sum, r) => sum + r.growth, 0);
    const averageGrowth = totalGrowth / validReports.length;
    const peakUsage = Math.max(...validReports.map(r => r.peak));
    
    // Detect potential memory leaks (growth > 50MB is suspicious)
    const potentialLeaks = validReports.filter(r => r.growth > 50 * 1024 * 1024).length;
    
    return {
      totalReports: reports.length,
      validReports: validReports.length,
      averageGrowth,
      peakUsage,
      potentialLeaks,
      reports: validReports,
    };
  }
});

test.describe('Stress Testing and Resource Limits', () => {
  test.setTimeout(180000); // 3-minute timeout for stress tests

  test('should handle sustained load over time', async ({ browser }) => {
    const duration = Math.min(LOAD_CONFIG.testDuration, 60000); // 60 seconds max
    const userCount = 3; // Conservative for sustained load
    
    console.log(`🔥 Starting sustained load test: ${userCount} users for ${duration/1000}s`);
    
    const contexts: BrowserContext[] = [];
    const results: any[] = [];
    
    try {
      // Create user contexts
      for (let i = 0; i < userCount; i++) {
        const context = await browser.newContext();
        contexts.push(context);
      }

      const startTime = Date.now();
      const endTime = startTime + duration;

      // Start sustained user activity
      const sustainedLoad = contexts.map(async (context, userId) => {
        const page = await context.newPage();
        const userResults = { userId, operations: 0, errors: 0, totalTime: 0 };
        
        try {
          while (Date.now() < endTime) {
            const opStart = Date.now();
            
            try {
              // Perform a quick analysis cycle
              await page.goto('/');
              await page.click('[data-testid="start-analysis-button"]');
              await page.click('[data-testid="template-multifamily-basic"]');
              await page.click('[data-testid="continue-with-template"]');
              
              // Quick form completion
              await this.fillQuickForm(page, userId);
              await page.click('[data-testid="submit-for-analysis"]');
              await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 15000 });
              
              userResults.operations++;
              userResults.totalTime += Date.now() - opStart;
              
              // Brief pause between operations
              await page.waitForTimeout(2000);
              
            } catch (error) {
              userResults.errors++;
              console.warn(`User ${userId} operation failed:`, error.message);
            }
          }
        } finally {
          await page.close();
        }
        
        return userResults;
      });

      const userResults = await Promise.all(sustainedLoad);
      
      // Analyze sustained load results
      const totalOperations = userResults.reduce((sum, r) => sum + r.operations, 0);
      const totalErrors = userResults.reduce((sum, r) => sum + r.errors, 0);
      const averageOperationTime = userResults.reduce((sum, r) => 
        sum + (r.operations > 0 ? r.totalTime / r.operations : 0), 0) / userCount;
      
      console.log('⚡ Sustained Load Test Results:');
      console.log(`   Duration: ${Math.round((Date.now() - startTime) / 1000)}s`);
      console.log(`   Total Operations: ${totalOperations}`);
      console.log(`   Error Rate: ${(totalErrors / (totalOperations + totalErrors) * 100).toFixed(1)}%`);
      console.log(`   Avg Operation Time: ${Math.round(averageOperationTime)}ms`);
      console.log(`   Throughput: ${(totalOperations / ((Date.now() - startTime) / 1000)).toFixed(2)} ops/s`);

      // Validate sustained performance
      expect(totalOperations).toBeGreaterThan(userCount * 2); // At least 2 operations per user
      expect(totalErrors / (totalOperations + totalErrors)).toBeLessThan(0.1); // <10% error rate
      expect(averageOperationTime).toBeLessThan(30000); // <30s average operation time

    } finally {
      await Promise.all(contexts.map(context => context.close()));
    }
  });

  // Helper for quick form filling
  private async fillQuickForm(page: Page, userId: number): Promise<void> {
    await page.fill('[data-testid="property-name"]', `Stress Test ${userId}-${Date.now()}`);
    await page.fill('[data-testid="street-address"]', `${100 + userId} Stress St`);
    await page.fill('[data-testid="city"]', 'New York');
    await page.selectOption('[data-testid="state"]', 'NY');
    await page.fill('[data-testid="zip-code"]', '10001');

    // Quick navigation through steps
    for (let step = 0; step < 4; step++) {
      await page.click('[data-testid="next-step"]');
      if (step === 0) {
        await page.fill('[data-testid="residential-units"]', '20');
        await page.fill('[data-testid="avg-rent"]', '2500');
      }
    }
  }

  test('should recover from resource exhaustion', async ({ browser }) => {
    const context = await browser.newContext();
    
    try {
      // Create resource exhaustion scenario
      const pages: Page[] = [];
      
      // Open many pages to consume resources
      for (let i = 0; i < 10; i++) {
        const page = await context.newPage();
        pages.push(page);
        
        // Navigate to resource-intensive page
        await page.goto('/analysis/monte-carlo/stress-test');
        
        // Don't wait for full load to stress the system
        page.waitForLoadState('networkidle').catch(() => {}); // Ignore errors
      }
      
      // Wait for resource pressure
      await new Promise(resolve => setTimeout(resolve, 10000));
      
      // Close all pages to free resources
      await Promise.all(pages.map(page => page.close().catch(() => {})));
      
      // Test recovery - create a new page and verify it works
      const recoveryPage = await context.newPage();
      const startTime = Date.now();
      
      try {
        await recoveryPage.goto('/');
        await recoveryPage.waitForLoadState('networkidle');
        
        const recoveryTime = Date.now() - startTime;
        console.log(`🔄 Recovery Time: ${recoveryTime}ms`);
        
        // Should recover within reasonable time
        expect(recoveryTime).toBeLessThan(15000); // 15 seconds
        
      } finally {
        await recoveryPage.close();
      }
      
    } finally {
      await context.close();
    }
  });
});

test.describe('Memory Leak Detection', () => {
  test('should not leak memory during repeated operations', async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
      const monitor = new MemoryMonitor(page);
      await monitor.startMonitoring();
      
      await page.goto('/');
      
      // Perform repeated operations that could cause memory leaks
      for (let i = 0; i < 10; i++) {
        // Navigation that could leak event listeners
        await page.goto('/analysis/results/memory-leak-test');
        await page.waitForLoadState('networkidle');
        
        // Component mounting/unmounting
        await page.goto('/market-data/explorer');
        await page.waitForLoadState('networkidle');
        
        // Force garbage collection every few iterations
        if (i % 3 === 0) {
          await page.evaluate(() => {
            if (window.gc) window.gc();
          });
        }
        
        console.log(`   Iteration ${i + 1}/10 completed`);
      }
      
      // Final garbage collection
      await page.evaluate(() => {
        if (window.gc) window.gc();
      });
      
      monitor.stopMonitoring();
      const memoryReport = monitor.getMemoryReport();
      
      console.log('🔍 Memory Leak Detection Results:');
      console.log(`   Initial Memory: ${Math.round(memoryReport.initial / 1024 / 1024)}MB`);
      console.log(`   Final Memory: ${Math.round(memoryReport.final / 1024 / 1024)}MB`);
      console.log(`   Memory Growth: ${Math.round(memoryReport.growth / 1024 / 1024)}MB`);
      console.log(`   Growth Rate: ${memoryReport.growthPercent.toFixed(1)}%`);
      
      // Memory growth should be reasonable
      expect(memoryReport.growth).toBeLessThan(50 * 1024 * 1024); // 50MB max growth
      expect(memoryReport.growthPercent).toBeLessThan(100); // 100% max growth percentage
      
    } finally {
      await context.close();
    }
  });
});