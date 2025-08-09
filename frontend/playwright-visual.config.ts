/**
 * Playwright Configuration for Visual Regression Testing
 * Specialized configuration for screenshot comparison and visual testing
 */

import { defineConfig, devices } from '@playwright/test';

const VISUAL_CONFIG = {
  // Base URLs
  baseURL: process.env.VISUAL_BASE_URL || process.env.E2E_BASE_URL || 'http://localhost:3000',
  
  // Visual testing specific settings
  timeout: parseInt(process.env.VISUAL_TIMEOUT || '90000'), // 90 seconds for visual tests
  
  // Screenshot comparison settings
  threshold: parseFloat(process.env.VISUAL_THRESHOLD || '0.2'), // 20% difference threshold
  
  // Animation control
  animations: 'disabled' as const,
  
  // Font consistency
  fontFamily: 'Arial, sans-serif',
};

export default defineConfig({
  // Test directory for visual tests
  testDir: './src/tests/visual',
  
  // Test file patterns
  testMatch: '**/*.test.ts',
  
  // Global test timeout
  timeout: VISUAL_CONFIG.timeout,
  
  // Expect timeout for assertions (longer for visual comparisons)
  expect: {
    timeout: 30000, // 30 seconds for screenshot comparisons
    
    // Global screenshot comparison settings
    toHaveScreenshot: { 
      threshold: VISUAL_CONFIG.threshold,
      mode: 'binary', // Strict pixel comparison
    },
    
    toMatchSnapshot: { 
      threshold: VISUAL_CONFIG.threshold 
    },
  },
  
  // Test execution settings
  fullyParallel: false, // Serial execution for consistent rendering
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0, // Retry visual tests in CI
  workers: 1, // Single worker for consistent screenshots
  
  // Reporter configuration
  reporter: [
    // Console output
    ['list'],
    
    // HTML report with screenshot diffs
    ['html', { 
      outputFolder: 'visual-test-results',
      open: process.env.CI ? 'never' : 'on-failure',
    }],
    
    // JSON for processing visual differences
    ['json', { outputFile: 'test-results/visual-results.json' }],
  ],
  
  // Output directories
  outputDir: 'test-results/visual-artifacts',
  
  // Global settings for all visual tests
  use: {
    // Base URL
    baseURL: VISUAL_CONFIG.baseURL,
    
    // Browser settings optimized for visual consistency
    headless: true, // Always headless for consistent rendering
    
    // Fixed viewport for baseline screenshots
    viewport: { width: 1280, height: 720 },
    
    // Device scale factor for high-DPI testing
    deviceScaleFactor: 1,
    
    // Disable animations globally
    reducedMotion: 'reduce',
    
    // Color scheme
    colorScheme: 'light',
    
    // Font settings
    fontFamily: VISUAL_CONFIG.fontFamily,
    
    // Screenshot settings
    screenshot: 'only-on-failure',
    
    // Video recording (disabled for visual tests)
    video: 'off',
    
    // Trace (disabled for performance)
    trace: 'off',
    
    // Network settings
    ignoreHTTPSErrors: true,
    
    // Disable web security for consistent font loading
    launchOptions: {
      args: [
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--font-render-hinting=none',
        '--disable-font-subpixel-positioning',
        '--disable-gpu',
        '--no-sandbox',
      ],
    },
    
    // Context options for consistent rendering
    contextOptions: {
      // Consistent locale
      locale: 'en-US',
      
      // Timezone
      timezoneId: 'America/New_York',
      
      // Permissions
      permissions: ['clipboard-read', 'clipboard-write'],
      
      // Force consistent font rendering
      forcedColors: 'none',
    },
    
    // Additional HTTP headers
    extraHTTPHeaders: {
      'X-Visual-Test': 'true',
    },
  },

  // Visual testing projects for different scenarios
  projects: [
    // Desktop Chrome - Primary visual testing
    {
      name: 'visual-chrome-desktop',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
        deviceScaleFactor: 1,
      },
    },
    
    // High-DPI desktop testing
    {
      name: 'visual-chrome-hidpi',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
        deviceScaleFactor: 2,
      },
    },
    
    // Large desktop screens
    {
      name: 'visual-chrome-xl',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
        deviceScaleFactor: 1,
      },
    },
    
    // Tablet responsive testing
    {
      name: 'visual-tablet',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 768, height: 1024 },
        deviceScaleFactor: 1,
      },
    },
    
    // Mobile responsive testing
    {
      name: 'visual-mobile',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 375, height: 812 },
        deviceScaleFactor: 2,
      },
    },
    
    // Dark mode testing
    {
      name: 'visual-chrome-dark',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
        deviceScaleFactor: 1,
        colorScheme: 'dark',
      },
    },
    
    // Firefox comparison (optional)
    {
      name: 'visual-firefox',
      use: {
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 720 },
        deviceScaleFactor: 1,
      },
    },
  ],

  // Web server for local development
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: VISUAL_CONFIG.baseURL,
    reuseExistingServer: true,
    timeout: 120 * 1000, // 2 minutes
    env: {
      NODE_ENV: 'test',
      VISUAL_TEST_MODE: 'true',
    },
  },

  // Global configuration
  globalTimeout: 1800000, // 30 minutes for visual test suite
  
  // Test metadata
  metadata: {
    testType: 'visual-regression',
    application: 'pro-forma-analytics-tool',
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'test',
    baseURL: VISUAL_CONFIG.baseURL,
    threshold: VISUAL_CONFIG.threshold,
    timestamp: new Date().toISOString(),
  },
});