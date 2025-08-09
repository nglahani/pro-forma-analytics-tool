/**
 * Global E2E Test Setup
 * Prepares the testing environment before running E2E tests
 */

import { chromium, FullConfig } from '@playwright/test';
import path from 'path';
import fs from 'fs';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E Test Environment Setup');
  
  const baseURL = config.use?.baseURL || 'http://localhost:3000';
  const apiURL = process.env.E2E_API_URL || 'http://localhost:8000';
  
  // Create test results directory
  const testResultsDir = 'test-results';
  if (!fs.existsSync(testResultsDir)) {
    fs.mkdirSync(testResultsDir, { recursive: true });
  }
  
  // Create E2E artifacts directory
  const e2eArtifactsDir = path.join(testResultsDir, 'e2e-artifacts');
  if (!fs.existsSync(e2eArtifactsDir)) {
    fs.mkdirSync(e2eArtifactsDir, { recursive: true });
  }

  try {
    // Launch browser for setup tasks
    console.log('🔧 Setting up test browser...');
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    // Health check - verify frontend is running
    console.log(`🏥 Checking frontend health at ${baseURL}...`);
    try {
      await page.goto(baseURL, { timeout: 30000 });
      await page.waitForLoadState('networkidle', { timeout: 15000 });
      console.log('✅ Frontend is responding');
    } catch (error) {
      console.error(`❌ Frontend health check failed: ${error.message}`);
      throw new Error(`Frontend at ${baseURL} is not accessible`);
    }

    // Health check - verify backend API is running
    console.log(`🏥 Checking backend API at ${apiURL}...`);
    try {
      const response = await page.request.get(`${apiURL}/health`);
      if (response.ok()) {
        console.log('✅ Backend API is responding');
      } else {
        console.log(`⚠️ Backend API returned status: ${response.status()}`);
      }
    } catch (error) {
      console.log(`⚠️ Backend API check failed: ${error.message}`);
      console.log('Note: Tests will use mocked API responses');
    }

    // Clear any existing test data
    console.log('🧹 Clearing existing test data...');
    try {
      // Clear browser storage
      await context.clearCookies();
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      
      // Clear any cached data that might interfere with tests
      await context.clearPermissions();
      
      console.log('✅ Test data cleared');
    } catch (error) {
      console.log(`⚠️ Data clearing warning: ${error.message}`);
    }

    // Warm up the application
    console.log('🔥 Warming up application components...');
    try {
      // Navigate to main pages to warm up components
      await page.goto(`${baseURL}/`, { waitUntil: 'networkidle' });
      
      // Pre-load critical resources
      await page.evaluate(() => {
        // Preload fonts and critical CSS
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'font';
        document.head.appendChild(link);
      });
      
      console.log('✅ Application warmed up');
    } catch (error) {
      console.log(`⚠️ Warmup warning: ${error.message}`);
    }

    // Set up test authentication (if needed)
    console.log('🔐 Setting up test authentication...');
    try {
      // For now, we'll use mock authentication
      // In a real scenario, you might:
      // 1. Create test user accounts
      // 2. Generate authentication tokens
      // 3. Set up test session cookies
      
      await page.evaluate(() => {
        // Store test authentication state
        localStorage.setItem('e2e-test-mode', 'true');
        localStorage.setItem('test-session-id', `e2e-${Date.now()}`);
      });
      
      console.log('✅ Test authentication configured');
    } catch (error) {
      console.log(`⚠️ Authentication setup warning: ${error.message}`);
    }

    // Verify critical app functionality
    console.log('🔍 Verifying critical application functionality...');
    try {
      // Check if main navigation elements are present
      const hasNavigation = await page.locator('nav').count() > 0;
      const hasMainContent = await page.locator('main').count() > 0;
      
      if (hasNavigation && hasMainContent) {
        console.log('✅ Core application structure verified');
      } else {
        console.log('⚠️ Some core elements missing - tests may be affected');
      }
      
      // Check if critical components can be reached
      try {
        await page.click('[data-testid="start-analysis-button"]', { timeout: 5000 });
        await page.goBack();
        console.log('✅ Analysis workflow accessible');
      } catch {
        console.log('⚠️ Analysis workflow not immediately accessible');
      }
      
    } catch (error) {
      console.log(`⚠️ Functionality verification warning: ${error.message}`);
    }

    // Save browser state for reuse in tests
    console.log('💾 Saving browser state...');
    try {
      const storageStatePath = path.join(testResultsDir, 'browser-state.json');
      await context.storageState({ path: storageStatePath });
      console.log('✅ Browser state saved');
    } catch (error) {
      console.log(`⚠️ Browser state save warning: ${error.message}`);
    }

    // Clean up setup browser
    await browser.close();
    
    // Log test environment information
    console.log('\n📊 E2E Test Environment Info:');
    console.log(`   Frontend URL: ${baseURL}`);
    console.log(`   Backend API: ${apiURL}`);
    console.log(`   Test Results: ${testResultsDir}`);
    console.log(`   Headless Mode: ${config.use?.headless !== false ? 'Enabled' : 'Disabled'}`);
    console.log(`   Workers: ${config.workers || 'Auto'}`);
    console.log(`   Retries: ${config.retries || 0}`);
    console.log(`   Timeout: ${config.timeout || 60000}ms`);
    
    console.log('✅ E2E Test Environment Setup Complete\n');
    
  } catch (error) {
    console.error('❌ E2E Test Setup Failed:', error.message);
    throw error;
  }
}

export default globalSetup;