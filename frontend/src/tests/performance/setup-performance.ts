/**
 * Performance Test Setup
 * Configuration and utilities for performance benchmarking
 */

import { TextEncoder, TextDecoder } from 'util';
import 'whatwg-fetch';

// Polyfills for Node.js environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

// Mock performance.memory if not available
if (!('memory' in performance)) {
  (performance as any).memory = {
    usedJSHeapSize: 50 * 1024 * 1024, // 50MB baseline
    totalJSHeapSize: 100 * 1024 * 1024, // 100MB total
    jsHeapSizeLimit: 2 * 1024 * 1024 * 1024, // 2GB limit
  };
}

// Global performance tracking
let performanceResults: Array<{
  testName: string;
  duration: number;
  memory?: number;
  timestamp: number;
}> = [];

// Enhanced performance measurement
const originalMeasure = performance.now;
performance.now = function() {
  return originalMeasure.call(this);
};

// Global test utilities
(global as any).performanceUtils = {
  recordResult: (testName: string, duration: number, memory?: number) => {
    performanceResults.push({
      testName,
      duration,
      memory,
      timestamp: Date.now(),
    });
  },
  
  getResults: () => performanceResults,
  
  clearResults: () => {
    performanceResults = [];
  },
  
  // Memory measurement helper
  measureMemory: () => {
    if ((performance as any).memory) {
      return (performance as any).memory.usedJSHeapSize;
    }
    return null;
  },
  
  // Force garbage collection if available
  gc: () => {
    if (global.gc) {
      global.gc();
    }
  },
};

// Console logging configuration for performance tests
const originalLog = console.log;
const originalWarn = console.warn;
const originalError = console.error;

// Suppress non-critical logs during performance tests unless explicitly enabled
if (!process.env.PERFORMANCE_VERBOSE) {
  console.log = (...args: any[]) => {
    if (args.some(arg => typeof arg === 'string' && (
      arg.includes('Performance') || 
      arg.includes('ms') ||
      arg.includes('Benchmark')
    ))) {
      originalLog.apply(console, args);
    }
  };
  
  console.warn = (...args: any[]) => {
    if (args.some(arg => typeof arg === 'string' && arg.includes('Performance'))) {
      originalWarn.apply(console, args);
    }
  };
} else {
  console.log = originalLog;
  console.warn = originalWarn;
}

console.error = originalError; // Always show errors

// API Client mock configuration for performance testing
jest.mock('@/lib/api/client', () => {
  // Import the actual implementation
  const actualApiClient = jest.requireActual('@/lib/api/client');
  
  return {
    ...actualApiClient,
    apiClient: {
      ...actualApiClient.apiClient,
      
      // Override with performance tracking
      analyzeDCF: jest.fn().mockImplementation(async (data) => {
        const start = performance.now();
        
        // Simulate realistic API delay
        const delay = Math.random() * 1000 + 500; // 500-1500ms
        await new Promise(resolve => setTimeout(resolve, delay));
        
        const duration = performance.now() - start;
        (global as any).performanceUtils.recordResult('DCF Analysis', duration);
        
        // Return realistic mock data
        return {
          property_id: `perf-test-${Date.now()}`,
          analysis_date: new Date().toISOString().split('T')[0],
          financial_metrics: {
            npv: 5000000 + Math.random() * 10000000,
            irr: 15 + Math.random() * 50,
            equity_multiple: 2 + Math.random() * 8,
            payback_period: 3 + Math.random() * 7,
            terminal_value: 20000000 + Math.random() * 30000000,
            total_return: 100 + Math.random() * 300,
            investment_recommendation: Math.random() > 0.7 ? 'STRONG_BUY' : 'BUY',
            confidence_score: 0.7 + Math.random() * 0.3,
          },
          cash_flow_projections: Array.from({ length: 6 }, (_, year) => ({
            year: 2025 + year,
            gross_rental_income: 600000 + (year * 20000),
            operating_expenses: 180000 + (year * 6000),
            net_operating_income: 420000 + (year * 14000),
            debt_service: 150000,
            net_cash_flow: 270000 + (year * 14000),
          })),
          initial_numbers: {
            acquisition_cost: 10000000 + Math.random() * 5000000,
            total_cash_invested: 2500000 + Math.random() * 1000000,
            loan_amount: 7500000 + Math.random() * 2500000,
            closing_costs: 100000 + Math.random() * 50000,
            renovation_cost: Math.random() * 1000000,
          },
        };
      }),
      
      startMonteCarloSimulation: jest.fn().mockImplementation(async (propertyId, config) => {
        const start = performance.now();
        
        // Simulate initialization delay
        const delay = Math.random() * 500 + 200; // 200-700ms
        await new Promise(resolve => setTimeout(resolve, delay));
        
        const duration = performance.now() - start;
        (global as any).performanceUtils.recordResult('Monte Carlo Start', duration);
        
        return {
          simulation_id: `mc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          property_id: propertyId,
          status: 'RUNNING',
          progress: 0,
        };
      }),
      
      getMonteCarloStatus: jest.fn().mockImplementation(async (simulationId) => {
        const start = performance.now();
        
        // Simulate processing delay
        const delay = Math.random() * 200 + 100; // 100-300ms
        await new Promise(resolve => setTimeout(resolve, delay));
        
        const duration = performance.now() - start;
        (global as any).performanceUtils.recordResult('Monte Carlo Status Check', duration);
        
        // Return completed simulation result
        return {
          simulation_id: simulationId,
          property_id: 'test-property',
          total_scenarios: 1000,
          execution_time_ms: 5000 + Math.random() * 3000,
          success: true,
          scenario_analysis: Array.from({ length: 20 }, (_, i) => ({
            scenario_id: i + 1,
            npv: 2000000 + Math.random() * 8000000,
            irr: 15 + Math.random() * 70,
            equity_multiple: 2 + Math.random() * 8,
            market_classification: ['BULL', 'BEAR', 'NEUTRAL', 'GROWTH', 'STRESS'][
              Math.floor(Math.random() * 5)
            ],
            risk_score: Math.random(),
            growth_score: Math.random(),
          })),
          risk_metrics: {
            value_at_risk_95: 1500000,
            expected_shortfall: 800000,
            probability_of_loss: Math.random() * 0.2,
            worst_case_npv: 500000,
            best_case_npv: 15000000,
          },
        };
      }),
      
      getMarketData: jest.fn().mockImplementation(async (msa) => {
        const start = performance.now();
        
        // Simulate market data fetch delay
        const delay = Math.random() * 1000 + 300; // 300-1300ms
        await new Promise(resolve => setTimeout(resolve, delay));
        
        const duration = performance.now() - start;
        (global as any).performanceUtils.recordResult('Market Data Fetch', duration);
        
        return {
          msa,
          parameters: {
            interestRate: 5 + Math.random() * 3,
            capRate: 4 + Math.random() * 2,
            vacancy: 3 + Math.random() * 5,
            rentGrowth: 2 + Math.random() * 4,
            expenseGrowth: 2 + Math.random() * 3,
            propertyGrowth: 3 + Math.random() * 4,
          },
          lastUpdated: new Date().toISOString(),
          confidence: 0.8 + Math.random() * 0.2,
        };
      }),
      
      getPropertyTemplates: jest.fn().mockImplementation(async () => {
        const start = performance.now();
        
        // Simulate template loading delay
        const delay = Math.random() * 500 + 200; // 200-700ms
        await new Promise(resolve => setTimeout(resolve, delay));
        
        const duration = performance.now() - start;
        (global as any).performanceUtils.recordResult('Property Templates Load', duration);
        
        return [
          {
            id: 'multifamily-basic',
            name: 'Multifamily Basic',
            description: 'Standard multifamily rental property',
            icon: '🏢',
            category: 'multifamily',
            defaultConfig: {
              residential_units: { total_units: 20, average_rent_per_unit: 2500, average_square_feet_per_unit: 900 },
              renovation_info: { status: 'NOT_NEEDED', anticipated_duration_months: 0, estimated_cost: 0 },
              equity_structure: { investor_equity_share_pct: 25, self_cash_percentage: 75 },
            },
            formConfig: {
              showResidentialUnits: true,
              showCommercialUnits: false,
              showRenovation: true,
              requiredFields: ['property_name', 'residential_units'],
            },
          },
        ];
      }),
      
      healthCheck: jest.fn().mockImplementation(async () => {
        const start = performance.now();
        
        // Simulate auth check delay
        const delay = Math.random() * 200 + 50; // 50-250ms
        await new Promise(resolve => setTimeout(resolve, delay));
        
        const duration = performance.now() - start;
        (global as any).performanceUtils.recordResult('Authentication', duration);
        
        return { status: 'ok', timestamp: Date.now() };
      }),
    },
  };
});

// Test timeout configuration
jest.setTimeout(120000); // 2 minutes for performance tests

// Performance test hooks
beforeAll(() => {
  console.log('🚀 Starting Performance Test Suite');
  console.log(`Iterations per test: ${process.env.PERFORMANCE_ITERATIONS || 5}`);
  console.log(`Concurrent users: ${process.env.CONCURRENT_USERS || 5}`);
  console.log(`Load test duration: ${process.env.LOAD_TEST_DURATION || 30000}ms`);
  
  (global as any).performanceUtils.clearResults();
});

beforeEach(() => {
  // Force garbage collection before each test
  (global as any).performanceUtils.gc();
});

afterEach(() => {
  // Small delay to allow cleanup
  return new Promise(resolve => setTimeout(resolve, 100));
});

afterAll(() => {
  const results = (global as any).performanceUtils.getResults();
  console.log('\n📊 Performance Test Summary:');
  
  // Group results by test type
  const grouped = results.reduce((acc: any, result: any) => {
    if (!acc[result.testName]) {
      acc[result.testName] = [];
    }
    acc[result.testName].push(result.duration);
    return acc;
  }, {});
  
  Object.entries(grouped).forEach(([testName, durations]: [string, any]) => {
    const avg = durations.reduce((sum: number, d: number) => sum + d, 0) / durations.length;
    const min = Math.min(...durations);
    const max = Math.max(...durations);
    
    console.log(`  ${testName}: avg=${avg.toFixed(1)}ms, min=${min.toFixed(1)}ms, max=${max.toFixed(1)}ms`);
  });
  
  console.log('✅ Performance Test Suite Completed\n');
});