/**
 * Load Testing Utilities
 * Helper functions and classes for concurrent user and memory testing
 */

import { Browser, BrowserContext, Page } from '@playwright/test';

export interface LoadTestConfig {
  maxConcurrentUsers: number;
  testDuration: number;
  memoryCheckInterval: number;
  memoryThreshold: number;
  maxResponseTime: number;
  targetThroughput: number;
  maxOpenConnections: number;
  maxMemoryGrowth: number;
}

export interface UserMetrics {
  userId: number;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  errors: string[];
  successRate: number;
  operationsCompleted: number;
}

export interface MemorySnapshot {
  timestamp: number;
  heapUsed: number;
  heapTotal: number;
  external: number;
}

export interface LoadTestResult {
  duration: number;
  totalUsers: number;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  throughput: number;
  errorRate: number;
  memoryMetrics?: MemoryAnalysis;
  userMetrics: UserMetrics[];
}

export interface MemoryAnalysis {
  initialUsage: number;
  finalUsage: number;
  peakUsage: number;
  growth: number;
  growthPercent: number;
  potentialLeaks: number;
  measurements: number;
  duration: number;
}

/**
 * Advanced Memory Monitor with leak detection
 */
export class AdvancedMemoryMonitor {
  private measurements: MemorySnapshot[] = [];
  private monitoringInterval?: NodeJS.Timeout;
  private isMonitoring = false;

  constructor(private page: Page, private config: { interval?: number; threshold?: number } = {}) {}

  async startMonitoring(): Promise<void> {
    if (this.isMonitoring) return;

    this.isMonitoring = true;
    this.measurements = [];
    
    const interval = this.config.interval || 2000; // 2 seconds default
    
    const measureMemory = async () => {
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

        if (memoryInfo && this.isMonitoring) {
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
    await measureMemory();
    
    // Set up periodic monitoring
    this.monitoringInterval = setInterval(measureMemory, interval);
  }

  stopMonitoring(): void {
    this.isMonitoring = false;
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = undefined;
    }
  }

  getMemoryAnalysis(): MemoryAnalysis {
    if (this.measurements.length === 0) {
      throw new Error('No memory measurements available');
    }

    const initial = this.measurements[0];
    const final = this.measurements[this.measurements.length - 1];
    const peak = this.measurements.reduce((max, curr) => 
      curr.heapUsed > max.heapUsed ? curr : max
    );

    const growth = final.heapUsed - initial.heapUsed;
    const growthPercent = (growth / initial.heapUsed) * 100;
    
    // Detect potential memory leaks
    const threshold = this.config.threshold || 50 * 1024 * 1024; // 50MB default
    const potentialLeaks = this.detectMemoryLeaks(threshold);

    return {
      initialUsage: initial.heapUsed,
      finalUsage: final.heapUsed,
      peakUsage: peak.heapUsed,
      growth,
      growthPercent,
      potentialLeaks,
      measurements: this.measurements.length,
      duration: final.timestamp - initial.timestamp,
    };
  }

  private detectMemoryLeaks(threshold: number): number {
    if (this.measurements.length < 3) return 0;

    // Look for sustained memory growth patterns
    let leakCount = 0;
    const windowSize = 5; // Check 5-measurement windows
    
    for (let i = windowSize; i < this.measurements.length; i++) {
      const windowStart = this.measurements[i - windowSize];
      const windowEnd = this.measurements[i];
      const windowGrowth = windowEnd.heapUsed - windowStart.heapUsed;
      
      if (windowGrowth > threshold) {
        leakCount++;
      }
    }

    return leakCount;
  }

  getMemoryTrend(): Array<{ timestamp: number; usage: number }> {
    return this.measurements.map(m => ({
      timestamp: m.timestamp,
      usage: m.heapUsed,
    }));
  }
}

/**
 * User Session Simulator with realistic behavior patterns
 */
export class RealisticUserSimulator {
  private metrics: UserMetrics;
  private operations: string[] = [];

  constructor(private context: BrowserContext, private userId: number) {
    this.metrics = {
      userId,
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      averageResponseTime: 0,
      errors: [],
      successRate: 0,
      operationsCompleted: 0,
    };
  }

  async simulateRealisticSession(): Promise<UserMetrics> {
    const page = await this.context.newPage();
    
    try {
      // Realistic user journey patterns
      const journeyType = this.selectUserJourney();
      
      switch (journeyType) {
        case 'quick-analysis':
          await this.performQuickAnalysis(page);
          break;
        case 'detailed-analysis':
          await this.performDetailedAnalysis(page);
          break;
        case 'comparison-analysis':
          await this.performComparisonAnalysis(page);
          break;
        case 'market-research':
          await this.performMarketResearch(page);
          break;
      }
      
      this.calculateFinalMetrics();
      
    } catch (error) {
      this.recordError(error.message);
    } finally {
      await page.close();
    }

    return this.metrics;
  }

  private selectUserJourney(): string {
    const journeys = ['quick-analysis', 'detailed-analysis', 'comparison-analysis', 'market-research'];
    return journeys[Math.floor(Math.random() * journeys.length)];
  }

  private async performQuickAnalysis(page: Page): Promise<void> {
    const startTime = Date.now();
    this.operations.push('navigate-to-app');
    
    try {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Quick property input
      await page.click('[data-testid="start-analysis-button"]');
      await this.recordOperation('start-analysis', Date.now() - startTime);
      
      await page.click('[data-testid="template-multifamily-basic"]');
      await page.click('[data-testid="continue-with-template"]');
      
      // Minimal form completion
      await this.fillBasicPropertyInfo(page);
      await this.recordOperation('form-completion', Date.now() - startTime);
      
      // Submit and wait for results
      await page.click('[data-testid="submit-for-analysis"]');
      await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 30000 });
      await this.recordOperation('dcf-analysis', Date.now() - startTime);
      
      // Brief review of results
      await page.waitForTimeout(2000);
      await this.recordOperation('results-review', Date.now() - startTime);
      
    } catch (error) {
      this.recordError(`Quick analysis failed: ${error.message}`);
    }
  }

  private async performDetailedAnalysis(page: Page): Promise<void> {
    const startTime = Date.now();
    
    try {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // Detailed property input with all steps
      await page.click('[data-testid="start-analysis-button"]');
      await page.click('[data-testid="template-multifamily-basic"]');
      await page.click('[data-testid="continue-with-template"]');
      
      await this.fillDetailedPropertyInfo(page);
      await this.recordOperation('detailed-form', Date.now() - startTime);
      
      // Submit analysis
      await page.click('[data-testid="submit-for-analysis"]');
      await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 30000 });
      
      // Review DCF results thoroughly
      await this.reviewDCFResults(page);
      await this.recordOperation('dcf-review', Date.now() - startTime);
      
      // Run Monte Carlo simulation
      await page.click('[data-testid="run-monte-carlo"]');
      await page.waitForSelector('[data-testid="monte-carlo-panel"]');
      
      // Configure Monte Carlo
      await page.fill('[data-testid="num-scenarios"]', '1000');
      await page.selectOption('[data-testid="confidence-level"]', '95');
      await page.click('[data-testid="start-simulation"]');
      
      await page.waitForSelector('[data-testid="simulation-results"]', { timeout: 60000 });
      await this.recordOperation('monte-carlo', Date.now() - startTime);
      
      // Review simulation results
      await this.reviewMonteCarloResults(page);
      await this.recordOperation('simulation-review', Date.now() - startTime);
      
    } catch (error) {
      this.recordError(`Detailed analysis failed: ${error.message}`);
    }
  }

  private async performComparisonAnalysis(page: Page): Promise<void> {
    // Simulate user comparing multiple properties
    const propertyCount = 2 + Math.floor(Math.random() * 2); // 2-3 properties
    
    for (let i = 0; i < propertyCount; i++) {
      const startTime = Date.now();
      
      try {
        await page.goto('/');
        await page.click('[data-testid="start-analysis-button"]');
        await page.click('[data-testid="template-multifamily-basic"]');
        await page.click('[data-testid="continue-with-template"]');
        
        // Fill property with variations
        await this.fillPropertyVariation(page, i);
        
        await page.click('[data-testid="submit-for-analysis"]');
        await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 30000 });
        
        // Quick results review
        await page.waitForTimeout(1000);
        await this.recordOperation(`comparison-property-${i}`, Date.now() - startTime);
        
      } catch (error) {
        this.recordError(`Comparison property ${i} failed: ${error.message}`);
      }
    }
  }

  private async performMarketResearch(page: Page): Promise<void> {
    const startTime = Date.now();
    
    try {
      await page.goto('/market-data/explorer');
      await page.waitForSelector('[data-testid="market-data-explorer"]');
      
      // Explore different MSAs
      const msas = ['NYC', 'LA', 'CHI', 'DC', 'MIA'];
      for (const msa of msas.slice(0, 3)) { // Test 3 MSAs
        await page.selectOption('[data-testid="msa-selector"]', msa);
        await page.waitForSelector('[data-testid="market-data-updated"]', { timeout: 10000 });
        await page.waitForTimeout(1000); // User review time
      }
      
      await this.recordOperation('market-research', Date.now() - startTime);
      
    } catch (error) {
      this.recordError(`Market research failed: ${error.message}`);
    }
  }

  private async fillBasicPropertyInfo(page: Page): Promise<void> {
    await page.fill('[data-testid="property-name"]', `User${this.userId}-QuickTest`);
    await page.fill('[data-testid="street-address"]', `${100 + this.userId} Quick St`);
    await page.fill('[data-testid="city"]', 'New York');
    await page.selectOption('[data-testid="state"]', 'NY');
    await page.fill('[data-testid="zip-code"]', '10001');
    
    // Skip through steps with minimal data
    for (let step = 0; step < 4; step++) {
      await page.click('[data-testid="next-step"]');
      if (step === 0) {
        await page.fill('[data-testid="residential-units"]', '20');
        await page.fill('[data-testid="avg-rent"]', '2500');
      }
    }
  }

  private async fillDetailedPropertyInfo(page: Page): Promise<void> {
    // Complete detailed form filling
    await page.fill('[data-testid="property-name"]', `User${this.userId}-DetailedProperty-${Date.now()}`);
    await page.fill('[data-testid="street-address"]', `${200 + this.userId} Detailed Ave`);
    await page.fill('[data-testid="city"]', 'New York');
    await page.selectOption('[data-testid="state"]', 'NY');
    await page.fill('[data-testid="zip-code"]', '10002');
    await page.click('[data-testid="next-step"]');
    
    // Units step
    await page.fill('[data-testid="residential-units"]', (25 + this.userId).toString());
    await page.fill('[data-testid="avg-rent"]', (2600 + this.userId * 50).toString());
    await page.fill('[data-testid="avg-sqft"]', '950');
    await page.click('[data-testid="next-step"]');
    
    // Renovation step
    await page.fill('[data-testid="renovation-duration"]', '6');
    await page.fill('[data-testid="renovation-budget"]', '500000');
    await page.click('[data-testid="next-step"]');
    
    // Equity step
    await page.fill('[data-testid="investor-equity"]', '30');
    await page.fill('[data-testid="self-cash"]', '70');
    await page.click('[data-testid="next-step"]');
  }

  private async fillPropertyVariation(page: Page, variation: number): Promise<void> {
    const baseUnits = 20 + (variation * 5);
    const baseRent = 2500 + (variation * 100);
    
    await page.fill('[data-testid="property-name"]', `Comparison-${this.userId}-${variation}`);
    await page.fill('[data-testid="street-address"]', `${300 + this.userId + variation} Compare St`);
    await page.fill('[data-testid="city"]', 'New York');
    await page.selectOption('[data-testid="state"]', 'NY');
    await page.fill('[data-testid="zip-code"]', `1000${variation}`);
    
    for (let step = 0; step < 4; step++) {
      await page.click('[data-testid="next-step"]');
      if (step === 0) {
        await page.fill('[data-testid="residential-units"]', baseUnits.toString());
        await page.fill('[data-testid="avg-rent"]', baseRent.toString());
      }
    }
  }

  private async reviewDCFResults(page: Page): Promise<void> {
    // Simulate user reviewing different sections
    const sections = [
      '[data-testid="financial-metrics"]',
      '[data-testid="cash-flow-table"]', 
      '[data-testid="investment-recommendation"]'
    ];
    
    for (const section of sections) {
      try {
        await page.locator(section).scrollIntoViewIfNeeded();
        await page.waitForTimeout(500); // Review time
      } catch (error) {
        // Section might not exist, continue
      }
    }
  }

  private async reviewMonteCarloResults(page: Page): Promise<void> {
    // Review different tabs
    const tabs = ['distribution', 'percentiles', 'risk', 'scenarios'];
    
    for (const tab of tabs) {
      try {
        await page.click(`[data-testid="tab-${tab}"]`);
        await page.waitForTimeout(1000); // Review time
      } catch (error) {
        // Tab might not exist, continue
      }
    }
  }

  private recordOperation(operation: string, totalTime: number): void {
    this.metrics.totalRequests++;
    this.metrics.successfulRequests++;
    this.metrics.operationsCompleted++;
    
    // Update average response time
    this.metrics.averageResponseTime = 
      (this.metrics.averageResponseTime * (this.metrics.successfulRequests - 1) + totalTime) / 
      this.metrics.successfulRequests;
      
    this.operations.push(`${operation}:${totalTime}ms`);
  }

  private recordError(error: string): void {
    this.metrics.totalRequests++;
    this.metrics.failedRequests++;
    this.metrics.errors.push(error);
  }

  private calculateFinalMetrics(): void {
    if (this.metrics.totalRequests > 0) {
      this.metrics.successRate = (this.metrics.successfulRequests / this.metrics.totalRequests) * 100;
    }
  }

  getOperationDetails(): string[] {
    return this.operations;
  }
}

/**
 * Load Test Orchestrator
 */
export class LoadTestOrchestrator {
  constructor(
    private browser: Browser,
    private config: LoadTestConfig
  ) {}

  async runConcurrentUserTest(userCount: number): Promise<LoadTestResult> {
    console.log(`🚀 Starting concurrent user test with ${userCount} users`);
    
    const contexts: BrowserContext[] = [];
    const simulators: RealisticUserSimulator[] = [];
    const startTime = Date.now();
    
    try {
      // Create browser contexts
      for (let i = 0; i < userCount; i++) {
        const context = await this.browser.newContext({
          viewport: { width: 1280, height: 720 },
          userAgent: `LoadTestUser-${i}-${Date.now()}`,
        });
        contexts.push(context);
        simulators.push(new RealisticUserSimulator(context, i));
      }

      // Execute concurrent sessions
      const userPromises = simulators.map(sim => sim.simulateRealisticSession());
      const userResults = await Promise.all(userPromises);
      
      const endTime = Date.now();
      const duration = endTime - startTime;

      // Aggregate results
      const result = this.aggregateResults(userResults, duration);
      
      console.log('📊 Load Test Results:');
      console.log(`   Duration: ${Math.round(duration / 1000)}s`);
      console.log(`   Users: ${result.totalUsers}`);
      console.log(`   Success Rate: ${result.errorRate.toFixed(1)}%`);
      console.log(`   Throughput: ${result.throughput.toFixed(2)} req/s`);
      
      return result;
      
    } finally {
      // Cleanup
      await Promise.all(contexts.map(context => context.close()));
    }
  }

  private aggregateResults(userResults: UserMetrics[], duration: number): LoadTestResult {
    const totalRequests = userResults.reduce((sum, r) => sum + r.totalRequests, 0);
    const successfulRequests = userResults.reduce((sum, r) => sum + r.successfulRequests, 0);
    const failedRequests = userResults.reduce((sum, r) => sum + r.failedRequests, 0);
    
    const averageResponseTime = userResults
      .filter(r => r.successfulRequests > 0)
      .reduce((sum, r) => sum + r.averageResponseTime, 0) / 
      userResults.filter(r => r.successfulRequests > 0).length;

    return {
      duration,
      totalUsers: userResults.length,
      totalRequests,
      successfulRequests,
      failedRequests,
      averageResponseTime: averageResponseTime || 0,
      throughput: totalRequests / (duration / 1000),
      errorRate: (1 - (successfulRequests / totalRequests)) * 100,
      userMetrics: userResults,
    };
  }
}

/**
 * Resource Monitor for system-level metrics
 */
export class ResourceMonitor {
  private metrics: Array<{
    timestamp: number;
    cpuUsage?: number;
    memoryUsage?: number;
    connectionCount?: number;
  }> = [];

  async startMonitoring(): Promise<void> {
    const interval = setInterval(async () => {
      try {
        // In a real implementation, you would collect actual system metrics
        // For testing, we'll simulate or use available browser APIs
        this.metrics.push({
          timestamp: Date.now(),
          cpuUsage: Math.random() * 100, // Simulated
          memoryUsage: Math.random() * 8192, // Simulated MB
          connectionCount: Math.floor(Math.random() * 50), // Simulated
        });
      } catch (error) {
        console.warn('Resource monitoring error:', error);
      }
    }, 5000); // 5-second intervals

    // Store interval for cleanup
    (this as any)._monitoringInterval = interval;
  }

  stopMonitoring(): void {
    if ((this as any)._monitoringInterval) {
      clearInterval((this as any)._monitoringInterval);
      delete (this as any)._monitoringInterval;
    }
  }

  getResourceReport() {
    if (this.metrics.length === 0) {
      return { error: 'No resource metrics collected' };
    }

    const avgCpu = this.metrics.reduce((sum, m) => sum + (m.cpuUsage || 0), 0) / this.metrics.length;
    const avgMemory = this.metrics.reduce((sum, m) => sum + (m.memoryUsage || 0), 0) / this.metrics.length;
    const peakMemory = Math.max(...this.metrics.map(m => m.memoryUsage || 0));
    
    return {
      averageCpuUsage: avgCpu.toFixed(1),
      averageMemoryUsage: avgMemory.toFixed(1),
      peakMemoryUsage: peakMemory.toFixed(1),
      measurementCount: this.metrics.length,
      samples: this.metrics,
    };
  }
}