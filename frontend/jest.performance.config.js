/**
 * Jest Configuration for Performance Testing
 * Specialized configuration for performance benchmarking tests
 */

const baseConfig = require('./jest.config');

module.exports = {
  ...baseConfig,
  
  // Performance tests need longer timeouts
  testTimeout: 120000, // 2 minutes
  
  // Run performance tests in serial to avoid resource contention
  maxWorkers: 1,
  
  // Only run performance tests
  testMatch: [
    '<rootDir>/src/tests/performance/**/*.test.ts',
    '<rootDir>/src/tests/performance/**/*.test.tsx'
  ],
  
  // Performance-specific setup
  setupFilesAfterEnv: [
    '<rootDir>/src/tests/performance/setup-performance.ts'
  ],
  
  // Disable coverage for performance tests (adds overhead)
  collectCoverage: false,
  
  // Performance tests should run in node environment
  testEnvironment: 'node',
  
  // Custom reporters for performance results
  reporters: [
    'default',
    ['<rootDir>/src/tests/performance/performance-reporter.js', {
      outputPath: './performance-results',
      generateReport: true,
    }]
  ],
  
  // Global configuration for performance tests
  globals: {
    PERFORMANCE_TEST_MODE: true,
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
    PERFORMANCE_ITERATIONS: parseInt(process.env.PERFORMANCE_ITERATIONS || '5'),
    LOAD_TEST_DURATION: parseInt(process.env.LOAD_TEST_DURATION || '30000'),
    CONCURRENT_USERS: parseInt(process.env.CONCURRENT_USERS || '5'),
  },
  
  // Module path mapping for performance utilities
  moduleNameMapping: {
    ...baseConfig.moduleNameMapping,
    '^@/tests/performance/(.*)$': '<rootDir>/src/tests/performance/$1',
  },
  
  // Transform configuration
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        compilerOptions: {
          // Performance tests can use newer features
          target: 'ES2020',
          module: 'CommonJS',
          // Enable source maps for better stack traces
          sourceMap: true,
          inlineSourceMap: false,
        }
      }
    }]
  },
};