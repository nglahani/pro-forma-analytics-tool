/**
 * Playwright Configuration for Load Testing
 * Optimized settings for concurrent user and memory testing
 */

import { defineConfig, devices } from '@playwright/test';

const LOAD_CONFIG = {
  // Base URLs
  baseURL: process.env.LOAD_BASE_URL || process.env.E2E_BASE_URL || 'http://localhost:3000',
  
  // Load testing specific settings
  timeout: parseInt(process.env.LOAD_TIMEOUT || '300000'), // 5 minutes for load tests
  
  // Concurrent user settings
  maxConcurrentUsers: parseInt(process.env.MAX_CONCURRENT_USERS || '10'),
  testDuration: parseInt(process.env.LOAD_TEST_DURATION || '120000'), // 2 minutes
  
  // Resource limits
  memoryThreshold: parseInt(process.env.MEMORY_THRESHOLD || (500 * 1024 * 1024).toString()), // 500MB
};

export default defineConfig({
  // Test directory for load tests
  testDir: './src/tests/load',
  
  // Test file patterns
  testMatch: '**/*.test.ts',
  
  // Global test timeout (very long for load tests)
  timeout: LOAD_CONFIG.timeout,
  
  // Expect timeout for assertions
  expect: {
    timeout: 60000, // 60 seconds for load test assertions
  },
  
  // Test execution settings optimized for load testing
  fullyParallel: false, // Serial execution to control resource usage
  forbidOnly: !!process.env.CI,
  retries: 0, // No retries for load tests to get accurate metrics
  workers: 1, // Single worker to control concurrency at test level
  
  // Reporter configuration
  reporter: [
    // Console output with timing details
    ['list', { printSteps: false }],
    
    // HTML report for load test analysis
    ['html', { 
      outputFolder: 'load-test-results',
      open: process.env.CI ? 'never' : 'on-failure',
    }],
    
    // JSON for detailed analysis
    ['json', { outputFile: 'test-results/load-results.json' }],
    
    // Custom load test reporter
    ['./src/tests/load/load-reporter.js', {
      outputPath: './load-reports',
    }],
  ],
  
  // Output directories
  outputDir: 'test-results/load-artifacts',
  
  // Global settings optimized for load testing
  use: {
    // Base URL
    baseURL: LOAD_CONFIG.baseURL,
    
    // Browser settings for load testing
    headless: true, // Always headless for load tests
    
    // Reduced viewport for performance
    viewport: { width: 1024, height: 768 },
    
    // Disable screenshots and videos for performance
    screenshot: 'off',
    video: 'off',
    trace: 'off',
    
    // Network settings
    ignoreHTTPSErrors: true,
    
    // Timeout settings for load testing
    actionTimeout: 30000, // 30 seconds
    navigationTimeout: 60000, // 60 seconds
    
    // Context options for load testing
    contextOptions: {
      // Reduced permissions for performance
      permissions: [],
      
      // Disable some features for performance
      reducedMotion: 'reduce',
      
      // Consistent locale
      locale: 'en-US',
      timezoneId: 'America/New_York',
    },
    
    // Launch options optimized for load testing
    launchOptions: {
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images', // Faster loading
        '--disable-javascript-harmony-shipping',
        '--memory-pressure-off',
        '--max_old_space_size=4096', // 4GB heap limit
      ],
    },
    
    // Additional HTTP headers for load testing
    extraHTTPHeaders: {
      'X-Load-Test': 'true',
      'X-Test-Type': 'concurrent-users',
    },
  },

  // Load testing projects for different scenarios
  projects: [
    // Light load testing (5 users)
    {
      name: 'load-light',
      use: {
        ...devices['Desktop Chrome'],
      },
      testMatch: '**/concurrent-users.test.ts',
      grep: /@light-load/,
    },
    
    // Medium load testing (10 users)  
    {
      name: 'load-medium',
      use: {
        ...devices['Desktop Chrome'],
      },
      testMatch: '**/concurrent-users.test.ts',
      grep: /@medium-load/,
    },
    
    // Heavy load testing (20+ users)
    {
      name: 'load-heavy',
      use: {
        ...devices['Desktop Chrome'],
      },
      testMatch: '**/concurrent-users.test.ts',
      grep: /@heavy-load/,
    },
    
    // Memory-focused testing
    {
      name: 'memory-test',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--no-sandbox',
            '--disable-setuid-sandbox', 
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--expose-gc', // Enable garbage collection API
            '--max_old_space_size=2048', // 2GB limit for memory testing
          ],
        },
      },
      testMatch: '**/concurrent-users.test.ts',
      grep: /@memory-test/,
    },
    
    // Database load testing
    {
      name: 'database-load',
      use: {
        ...devices['Desktop Chrome'],
      },
      testMatch: '**/concurrent-users.test.ts',
      grep: /@database-load/,
    },
    
    // Stress testing
    {
      name: 'stress-test',
      use: {
        ...devices['Desktop Chrome'],
        actionTimeout: 120000, // 2 minutes for stress tests
        navigationTimeout: 180000, // 3 minutes
      },
      testMatch: '**/concurrent-users.test.ts',
      grep: /@stress-test/,
    },
  ],

  // Web server for local development
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: LOAD_CONFIG.baseURL,
    reuseExistingServer: true,
    timeout: 120 * 1000, // 2 minutes
    env: {
      NODE_ENV: 'test',
      LOAD_TEST_MODE: 'true',
      MAX_CONNECTIONS: '100', // Increased for load testing
    },
  },

  // Global configuration
  globalTimeout: 1800000, // 30 minutes for entire load test suite
  
  // Test metadata
  metadata: {
    testType: 'load-testing',
    application: 'pro-forma-analytics-tool',
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'test',
    baseURL: LOAD_CONFIG.baseURL,
    maxUsers: LOAD_CONFIG.maxConcurrentUsers,
    testDuration: LOAD_CONFIG.testDuration,
    memoryThreshold: LOAD_CONFIG.memoryThreshold,
    timestamp: new Date().toISOString(),
  },
});