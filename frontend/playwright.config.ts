/**
 * Playwright Configuration for End-to-End Testing
 * Comprehensive E2E testing setup for the Pro-Forma Analytics Tool
 */

import { defineConfig, devices } from '@playwright/test';

const E2E_CONFIG = {
  // Base URLs
  baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
  apiURL: process.env.E2E_API_URL || 'http://localhost:8000',
  
  // Test configuration
  timeout: parseInt(process.env.E2E_TIMEOUT || '60000'), // 60 seconds
  slowMo: parseInt(process.env.E2E_SLOW_MO || '0'), // Slow motion for debugging
  
  // Parallel execution
  workers: process.env.CI ? 1 : undefined, // Serial in CI, parallel locally
  
  // Retry configuration
  retries: process.env.CI ? 2 : 0, // Retry failed tests in CI
  
  // Screenshot and video settings
  screenshots: process.env.CI ? 'only-on-failure' : 'off',
  video: process.env.CI ? 'retain-on-failure' : 'off',
  trace: process.env.CI ? 'retain-on-failure' : 'on-first-retry',
};

export default defineConfig({
  // Test directory
  testDir: './src/tests/e2e',
  
  // Test file patterns
  testMatch: '**/*.test.ts',
  
  // Global test timeout
  timeout: E2E_CONFIG.timeout,
  
  // Expect timeout for assertions
  expect: {
    timeout: 15000, // 15 seconds for assertions
  },
  
  // Test execution settings
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: E2E_CONFIG.retries,
  workers: E2E_CONFIG.workers,
  
  // Reporter configuration
  reporter: [
    // Console reporter
    ['list'],
    
    // HTML report for local development
    ['html', { 
      outputFolder: 'playwright-report',
      open: process.env.CI ? 'never' : 'on-failure',
    }],
    
    // JUnit XML for CI integration
    ['junit', { outputFile: 'test-results/e2e-results.xml' }],
    
    // JSON reporter for custom processing
    ['json', { outputFile: 'test-results/e2e-results.json' }],
  ],
  
  // Global test setup
  globalSetup: './src/tests/e2e/global-setup.ts',
  globalTeardown: './src/tests/e2e/global-teardown.ts',
  
  // Test output directory
  outputDir: 'test-results/e2e-artifacts',
  
  // Use default settings
  use: {
    // Base URL for all tests
    baseURL: E2E_CONFIG.baseURL,
    
    // Browser settings
    headless: process.env.E2E_HEADLESS !== 'false',
    slowMo: E2E_CONFIG.slowMo,
    
    // Viewport settings
    viewport: { width: 1280, height: 720 },
    
    // Screenshot settings
    screenshot: E2E_CONFIG.screenshots as any,
    
    // Video recording
    video: E2E_CONFIG.video as any,
    
    // Trace collection
    trace: E2E_CONFIG.trace as any,
    
    // Network settings
    ignoreHTTPSErrors: true,
    
    // Timeout settings
    actionTimeout: 15000, // 15 seconds for actions
    navigationTimeout: 30000, // 30 seconds for navigation
    
    // Context options
    contextOptions: {
      // Permissions
      permissions: ['clipboard-read', 'clipboard-write'],
      
      // Geolocation (for address testing)
      geolocation: { latitude: 40.7128, longitude: -74.0060 }, // NYC coordinates
      
      // Locale
      locale: 'en-US',
      
      // Timezone
      timezoneId: 'America/New_York',
    },
    
    // Additional test data
    extraHTTPHeaders: {
      'X-E2E-Test': 'true',
      'Accept-Language': 'en-US,en;q=0.9',
    },
  },

  // Browser projects
  projects: [
    // Desktop browsers
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Chrome-specific settings
        launchOptions: {
          args: [
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-dev-shm-usage',
          ],
        },
      },
    },
    
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
      },
    },
    
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
      },
    },

    // Mobile browsers (optional)
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
      },
    },
    
    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 12'],
      },
    },

    // High-resolution testing
    {
      name: 'high-dpi',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
        deviceScaleFactor: 2,
      },
    },
  ],

  // Web server configuration for local development
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: E2E_CONFIG.baseURL,
    reuseExistingServer: true,
    timeout: 120 * 1000, // 2 minutes to start
    env: {
      NODE_ENV: 'test',
      E2E_TEST_MODE: 'true',
    },
  },

  // Global test configuration
  globalTimeout: 600000, // 10 minutes for entire test suite
  
  // Test metadata
  metadata: {
    testType: 'end-to-end',
    application: 'pro-forma-analytics-tool',
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'test',
    baseURL: E2E_CONFIG.baseURL,
    timestamp: new Date().toISOString(),
  },
});