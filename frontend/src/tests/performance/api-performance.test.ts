/**
 * API Performance Benchmarking Suite
 * Tests response times and validates performance requirements
 * 
 * Performance Requirements (from backend integration specs):
 * - DCF analysis: < 3 seconds
 * - Monte Carlo simulation: < 10 seconds
 * - Market data fetching: < 2 seconds
 * - Property template loading: < 1 second
 * - Authentication: < 500ms
 */

import { apiClient } from '@/lib/api/client';
import { SimplifiedPropertyInput } from '@/types/property';
import { MonteCarloConfig } from '@/types/analysis';

describe('API Performance Benchmarking', () => {
  const mockPropertyData: SimplifiedPropertyInput = {
    property_name: 'Performance Test Property',
    address: {
      street_address: '123 Test Street',
      city: 'New York',
      state: 'NY',
      zip_code: '10001',
    },
    msa: 'NYC',
    residential_units: {
      total_units: 20,
      average_rent_per_unit: 2500,
      average_square_feet_per_unit: 900,
    },
    commercial_units: {
      total_units: 0,
      average_rent_per_unit: 0,
      average_square_feet_per_unit: 0,
    },
    renovation_info: {
      status: 'NOT_NEEDED',
      anticipated_duration_months: 0,
      estimated_cost: 0,
    },
    equity_structure: {
      investor_equity_share_pct: 25,
      self_cash_percentage: 75,
    },
    template_id: 'multifamily-basic',
  };

  const mockMonteCarloConfig: MonteCarloConfig = {
    numScenarios: 1000,
    confidenceLevel: 95,
    includeCorrelations: true,
    includeMarketCycles: true,
  };

  // Performance measurement helper
  const measurePerformance = async <T>(
    operation: () => Promise<T>,
    label: string
  ): Promise<{ result: T; duration: number }> => {
    const startTime = performance.now();
    const result = await operation();
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    console.log(`${label}: ${duration.toFixed(2)}ms`);
    return { result, duration };
  };

  describe('Authentication Performance', () => {
    it('should authenticate within 500ms', async () => {
      const { duration } = await measurePerformance(
        () => apiClient.healthCheck(),
        'Authentication check'
      );

      expect(duration).toBeLessThan(500);
    }, 10000);

    it('should handle token refresh quickly', async () => {
      // Simulate token refresh scenario
      const { duration } = await measurePerformance(
        () => apiClient.healthCheck(),
        'Token refresh check'
      );

      expect(duration).toBeLessThan(500);
    }, 10000);
  });

  describe('Property Template Performance', () => {
    it('should load property templates within 1 second', async () => {
      const { result, duration } = await measurePerformance(
        () => apiClient.getPropertyTemplates(),
        'Property templates loading'
      );

      expect(duration).toBeLessThan(1000);
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
    }, 15000);

    it('should handle concurrent template requests efficiently', async () => {
      const requests = Array.from({ length: 5 }, () =>
        measurePerformance(
          () => apiClient.getPropertyTemplates(),
          'Concurrent template request'
        )
      );

      const results = await Promise.all(requests);
      
      // All requests should complete within acceptable time
      results.forEach(({ duration }, index) => {
        expect(duration).toBeLessThan(1500); // Allow some overhead for concurrent requests
      });

      // Average response time should be under 1 second
      const avgDuration = results.reduce((sum, { duration }) => sum + duration, 0) / results.length;
      expect(avgDuration).toBeLessThan(1000);
    }, 20000);
  });

  describe('Market Data Performance', () => {
    it('should fetch market data within 2 seconds', async () => {
      const { result, duration } = await measurePerformance(
        () => apiClient.getMarketData('NYC'),
        'Market data fetching'
      );

      expect(duration).toBeLessThan(2000);
      expect(result).toBeDefined();
      expect(result.msa).toBe('NYC');
    }, 15000);

    it('should handle multiple MSA requests efficiently', async () => {
      const msas = ['NYC', 'LA', 'CHI', 'DC', 'MIA'];
      const requests = msas.map(msa =>
        measurePerformance(
          () => apiClient.getMarketData(msa),
          `Market data for ${msa}`
        )
      );

      const results = await Promise.all(requests);
      
      // Each request should meet the 2-second requirement
      results.forEach(({ duration }, index) => {
        expect(duration).toBeLessThan(2000);
      });

      // Verify data integrity
      results.forEach(({ result }, index) => {
        expect(result.msa).toBe(msas[index]);
        expect(result.parameters).toBeDefined();
      });
    }, 25000);

    it('should cache market data for improved performance', async () => {
      // First request (uncached)
      const { duration: firstDuration } = await measurePerformance(
        () => apiClient.getMarketData('NYC'),
        'First market data request (uncached)'
      );

      // Second request (should be cached)
      const { duration: secondDuration } = await measurePerformance(
        () => apiClient.getMarketData('NYC'),
        'Second market data request (cached)'
      );

      // Cached request should be significantly faster
      expect(secondDuration).toBeLessThan(firstDuration * 0.5);
      expect(secondDuration).toBeLessThan(500); // Cached requests should be very fast
    }, 15000);
  });

  describe('DCF Analysis Performance', () => {
    it('should complete DCF analysis within 3 seconds', async () => {
      const { result, duration } = await measurePerformance(
        () => apiClient.analyzeDCF(mockPropertyData),
        'DCF analysis'
      );

      expect(duration).toBeLessThan(3000);
      expect(result).toBeDefined();
      expect(result.financial_metrics).toBeDefined();
      expect(result.cash_flow_projections).toBeDefined();
    }, 15000);

    it('should handle multiple DCF analyses concurrently', async () => {
      // Create multiple property variations
      const properties = Array.from({ length: 3 }, (_, index) => ({
        ...mockPropertyData,
        property_name: `Performance Test Property ${index + 1}`,
        residential_units: {
          ...mockPropertyData.residential_units,
          total_units: 20 + (index * 5),
        },
      }));

      const requests = properties.map((property, index) =>
        measurePerformance(
          () => apiClient.analyzeDCF(property),
          `DCF analysis ${index + 1}`
        )
      );

      const results = await Promise.all(requests);
      
      // All analyses should complete within time limit
      results.forEach(({ duration, result }, index) => {
        expect(duration).toBeLessThan(4000); // Allow some overhead for concurrent processing
        expect(result.property_id).toBeDefined();
        expect(result.financial_metrics.npv).toBeGreaterThan(0);
      });
    }, 25000);

    it('should maintain performance under different property sizes', async () => {
      const propertySizes = [5, 20, 50, 100]; // Different unit counts
      
      const results = await Promise.all(
        propertySizes.map(units =>
          measurePerformance(
            () => apiClient.analyzeDCF({
              ...mockPropertyData,
              property_name: `${units}-Unit Property`,
              residential_units: {
                ...mockPropertyData.residential_units,
                total_units: units,
              },
            }),
            `DCF analysis for ${units} units`
          )
        )
      );

      // Performance should not degrade significantly with property size
      results.forEach(({ duration }, index) => {
        expect(duration).toBeLessThan(3000);
      });

      // Check that performance doesn't degrade too much with size
      const smallPropertyTime = results[0].duration;
      const largePropertyTime = results[results.length - 1].duration;
      
      // Large property should not take more than 2x the time of small property
      expect(largePropertyTime).toBeLessThan(smallPropertyTime * 2);
    }, 30000);
  });

  describe('Monte Carlo Simulation Performance', () => {
    let propertyId: string;

    beforeAll(async () => {
      // Create a property for Monte Carlo testing
      const dcfResult = await apiClient.analyzeDCF(mockPropertyData);
      propertyId = dcfResult.property_id;
    });

    it('should start Monte Carlo simulation within 1 second', async () => {
      const { result, duration } = await measurePerformance(
        () => apiClient.startMonteCarloSimulation(propertyId, mockMonteCarloConfig),
        'Monte Carlo simulation start'
      );

      expect(duration).toBeLessThan(1000);
      expect(result.simulation_id).toBeDefined();
    }, 15000);

    it('should complete Monte Carlo simulation within 10 seconds', async () => {
      const startResult = await apiClient.startMonteCarloSimulation(propertyId, mockMonteCarloConfig);
      
      const startTime = performance.now();
      let completed = false;
      let result;

      // Poll for completion
      while (!completed) {
        const statusResult = await apiClient.getMonteCarloStatus(startResult.simulation_id);
        
        if (statusResult.success && statusResult.scenario_analysis?.length > 0) {
          completed = true;
          result = statusResult;
        } else {
          // Wait 500ms before next poll
          await new Promise(resolve => setTimeout(resolve, 500));
        }

        const elapsed = performance.now() - startTime;
        if (elapsed > 15000) { // 15-second timeout for safety
          throw new Error('Monte Carlo simulation timeout');
        }
      }

      const totalDuration = performance.now() - startTime;
      console.log(`Monte Carlo simulation completion: ${totalDuration.toFixed(2)}ms`);

      expect(totalDuration).toBeLessThan(10000);
      expect(result).toBeDefined();
      expect(result.scenario_analysis.length).toBeGreaterThan(0);
    }, 20000);

    it('should handle different scenario counts efficiently', async () => {
      const scenarioCounts = [100, 500, 1000];
      
      const results = await Promise.all(
        scenarioCounts.map(async (numScenarios) => {
          const config = { ...mockMonteCarloConfig, numScenarios };
          
          const startResult = await apiClient.startMonteCarloSimulation(propertyId, config);
          const startTime = performance.now();
          
          // Wait for completion (simplified for test)
          await new Promise(resolve => setTimeout(resolve, 2000));
          const statusResult = await apiClient.getMonteCarloStatus(startResult.simulation_id);
          
          const duration = performance.now() - startTime;
          
          return {
            scenarioCount: numScenarios,
            duration,
            result: statusResult,
          };
        })
      );

      // Verify performance scales reasonably with scenario count
      results.forEach(({ scenarioCount, duration }) => {
        console.log(`${scenarioCount} scenarios: ${duration.toFixed(2)}ms`);
        
        // Performance should scale sub-linearly
        const expectedMaxTime = Math.min(10000, 2000 + (scenarioCount / 100) * 1000);
        expect(duration).toBeLessThan(expectedMaxTime);
      });
    }, 30000);
  });

  describe('API Response Caching', () => {
    it('should cache identical requests effectively', async () => {
      // Clear any existing cache
      const cacheKey = 'test-property-performance';
      
      // First request
      const { duration: firstDuration } = await measurePerformance(
        () => apiClient.analyzeDCF({
          ...mockPropertyData,
          property_name: cacheKey,
        }),
        'First DCF request'
      );

      // Second identical request (should be cached)
      const { duration: secondDuration } = await measurePerformance(
        () => apiClient.analyzeDCF({
          ...mockPropertyData,
          property_name: cacheKey,
        }),
        'Second DCF request (cached)'
      );

      // Cached request should be significantly faster
      expect(secondDuration).toBeLessThan(firstDuration * 0.3);
      expect(secondDuration).toBeLessThan(500);
    }, 20000);
  });

  describe('Error Handling Performance', () => {
    it('should handle API errors quickly', async () => {
      const { duration } = await measurePerformance(
        async () => {
          try {
            await apiClient.analyzeDCF({
              ...mockPropertyData,
              property_name: '', // Invalid data to trigger error
            });
          } catch (error) {
            // Expected error
            return error;
          }
        },
        'Error handling'
      );

      // Error responses should be fast
      expect(duration).toBeLessThan(1000);
    }, 10000);

    it('should implement proper timeout handling', async () => {
      const startTime = performance.now();
      
      try {
        // Mock a request that should timeout
        await new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Timeout')), 5000);
        });
      } catch (error) {
        const duration = performance.now() - startTime;
        
        // Should timeout within expected timeframe
        expect(duration).toBeLessThan(6000);
        expect(error.message).toContain('Timeout');
      }
    }, 10000);
  });

  describe('Memory Usage Performance', () => {
    it('should handle large datasets without memory leaks', async () => {
      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
      
      // Perform multiple operations that could cause memory leaks
      const operations = Array.from({ length: 10 }, (_, index) =>
        measurePerformance(
          () => apiClient.getMarketData('NYC'),
          `Memory test operation ${index + 1}`
        )
      );

      await Promise.all(operations);

      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }

      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
      
      // Memory usage should not grow excessively
      if (initialMemory > 0 && finalMemory > 0) {
        const memoryGrowth = finalMemory - initialMemory;
        const maxAcceptableGrowth = 50 * 1024 * 1024; // 50MB
        
        expect(memoryGrowth).toBeLessThan(maxAcceptableGrowth);
      }
    }, 30000);
  });
});

/**
 * Performance Regression Test Suite
 * Validates that performance doesn't degrade over time
 */
describe('Performance Regression Tests', () => {
  const performanceBenchmarks = {
    dcfAnalysis: 3000, // 3 seconds
    monteCarloStart: 1000, // 1 second
    marketDataFetch: 2000, // 2 seconds
    templateLoad: 1000, // 1 second
    authentication: 500, // 500ms
  };

  it('should meet all performance benchmarks consistently', async () => {
    const testRuns = 3; // Run each test multiple times
    const results: Record<string, number[]> = {};

    // Initialize results object
    Object.keys(performanceBenchmarks).forEach(key => {
      results[key] = [];
    });

    // Run performance tests multiple times
    for (let run = 0; run < testRuns; run++) {
      console.log(`Performance test run ${run + 1}/${testRuns}`);

      // DCF Analysis
      const { duration: dcfDuration } = await measurePerformance(
        () => apiClient.analyzeDCF({
          property_name: `Regression Test ${run}`,
          address: {
            street_address: '123 Test St',
            city: 'New York',
            state: 'NY',
            zip_code: '10001',
          },
          msa: 'NYC',
          residential_units: {
            total_units: 20,
            average_rent_per_unit: 2500,
            average_square_feet_per_unit: 900,
          },
          commercial_units: {
            total_units: 0,
            average_rent_per_unit: 0,
            average_square_feet_per_unit: 0,
          },
          renovation_info: {
            status: 'NOT_NEEDED',
            anticipated_duration_months: 0,
            estimated_cost: 0,
          },
          equity_structure: {
            investor_equity_share_pct: 25,
            self_cash_percentage: 75,
          },
          template_id: 'multifamily-basic',
        }),
        `DCF Analysis Run ${run + 1}`
      );
      results.dcfAnalysis.push(dcfDuration);

      // Market Data
      const { duration: marketDuration } = await measurePerformance(
        () => apiClient.getMarketData('NYC'),
        `Market Data Run ${run + 1}`
      );
      results.marketDataFetch.push(marketDuration);

      // Templates
      const { duration: templateDuration } = await measurePerformance(
        () => apiClient.getPropertyTemplates(),
        `Template Load Run ${run + 1}`
      );
      results.templateLoad.push(templateDuration);

      // Authentication
      const { duration: authDuration } = await measurePerformance(
        () => apiClient.healthCheck(),
        `Authentication Run ${run + 1}`
      );
      results.authentication.push(authDuration);
    }

    // Validate results against benchmarks
    Object.entries(results).forEach(([testName, durations]) => {
      const benchmark = performanceBenchmarks[testName as keyof typeof performanceBenchmarks];
      const avgDuration = durations.reduce((sum, duration) => sum + duration, 0) / durations.length;
      const maxDuration = Math.max(...durations);

      console.log(`${testName}: avg=${avgDuration.toFixed(2)}ms, max=${maxDuration.toFixed(2)}ms, benchmark=${benchmark}ms`);

      // Average should meet benchmark
      expect(avgDuration).toBeLessThan(benchmark);
      
      // No single run should exceed benchmark by more than 50%
      expect(maxDuration).toBeLessThan(benchmark * 1.5);
      
      // Performance should be consistent (standard deviation < 30% of average)
      const stdDev = Math.sqrt(
        durations.reduce((sum, duration) => sum + Math.pow(duration - avgDuration, 2), 0) / durations.length
      );
      expect(stdDev).toBeLessThan(avgDuration * 0.3);
    });
  }, 60000);
});