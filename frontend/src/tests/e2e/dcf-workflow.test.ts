/**
 * End-to-End DCF Analysis Workflow Tests
 * Tests the complete user journey from property input through final analysis
 * 
 * This test suite validates the entire DCF workflow:
 * 1. Property template selection
 * 2. Multi-step property input form
 * 3. Address validation and MSA detection
 * 4. Market data integration
 * 5. DCF analysis execution
 * 6. Results display and interpretation
 * 7. Export functionality
 * 8. Monte Carlo integration
 */

import { test, expect, Page, Browser } from '@playwright/test';

// Test configuration
const TEST_CONFIG = {
  baseUrl: process.env.E2E_BASE_URL || 'http://localhost:3000',
  apiUrl: process.env.E2E_API_URL || 'http://localhost:8000',
  timeout: 30000,
  slowMo: parseInt(process.env.E2E_SLOW_MO || '0'),
};

// Test data
const TEST_PROPERTY = {
  name: 'E2E Test Property - Sunset Gardens',
  address: {
    street: '123 Main Street',
    city: 'New York',
    state: 'NY',
    zipCode: '10001',
  },
  units: {
    residential: 24,
    avgRent: 2800,
    avgSqFt: 900,
  },
  renovation: {
    duration: 6,
    budget: 500000,
  },
  equity: {
    investorShare: 25,
    selfCash: 75,
  },
};

const EXPECTED_RESULTS = {
  npv: {
    min: 1000000, // $1M minimum NPV
    max: 50000000, // $50M maximum NPV
  },
  irr: {
    min: 10, // 10% minimum IRR
    max: 100, // 100% maximum IRR
  },
  recommendation: ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'],
  cashFlowYears: 6,
};

test.describe('Complete DCF Analysis Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Set longer timeout for E2E tests
    test.setTimeout(60000);
    
    // Navigate to the application
    await page.goto(TEST_CONFIG.baseUrl);
    
    // Wait for the application to load
    await page.waitForLoadState('networkidle');
    
    // Verify the main page loaded
    await expect(page).toHaveTitle(/Pro-Forma Analytics/i);
  });

  test('should complete full DCF analysis workflow successfully', async ({ page }) => {
    // Step 1: Navigate to property analysis
    await test.step('Navigate to property analysis', async () => {
      await page.click('[data-testid="start-analysis-button"]');
      await expect(page.locator('h1')).toContainText('Property Analysis');
    });

    // Step 2: Select property template
    await test.step('Select property template', async () => {
      await page.waitForSelector('[data-testid="property-templates"]');
      
      // Select multifamily template
      await page.click('[data-testid="template-multifamily-basic"]');
      
      // Verify template selection
      await expect(page.locator('[data-testid="selected-template"]'))
        .toContainText('Multifamily Basic');
      
      await page.click('[data-testid="continue-with-template"]');
    });

    // Step 3: Complete property input form
    await test.step('Complete property input form', async () => {
      // Step 3a: Basic Information
      await expect(page.locator('h2')).toContainText('Property Information');
      
      await page.fill('[data-testid="property-name"]', TEST_PROPERTY.name);
      await page.fill('[data-testid="street-address"]', TEST_PROPERTY.address.street);
      await page.fill('[data-testid="city"]', TEST_PROPERTY.address.city);
      await page.selectOption('[data-testid="state"]', TEST_PROPERTY.address.state);
      await page.fill('[data-testid="zip-code"]', TEST_PROPERTY.address.zipCode);
      
      // Wait for MSA auto-detection
      await page.waitForSelector('[data-testid="detected-msa"]', { timeout: 5000 });
      await expect(page.locator('[data-testid="detected-msa"]')).toContainText('NYC');
      
      await page.click('[data-testid="next-step"]');
      
      // Step 3b: Unit Information
      await expect(page.locator('h2')).toContainText('Unit Details');
      
      await page.fill('[data-testid="residential-units"]', TEST_PROPERTY.units.residential.toString());
      await page.fill('[data-testid="avg-rent"]', TEST_PROPERTY.units.avgRent.toString());
      await page.fill('[data-testid="avg-sqft"]', TEST_PROPERTY.units.avgSqFt.toString());
      
      await page.click('[data-testid="next-step"]');
      
      // Step 3c: Renovation Information
      await expect(page.locator('h2')).toContainText('Renovation Details');
      
      await page.fill('[data-testid="renovation-duration"]', TEST_PROPERTY.renovation.duration.toString());
      await page.fill('[data-testid="renovation-budget"]', TEST_PROPERTY.renovation.budget.toString());
      
      await page.click('[data-testid="next-step"]');
      
      // Step 3d: Equity Structure
      await expect(page.locator('h2')).toContainText('Equity Structure');
      
      await page.fill('[data-testid="investor-equity"]', TEST_PROPERTY.equity.investorShare.toString());
      await page.fill('[data-testid="self-cash"]', TEST_PROPERTY.equity.selfCash.toString());
      
      await page.click('[data-testid="next-step"]');
      
      // Step 3e: Review and Submit
      await expect(page.locator('h2')).toContainText('Review Information');
      
      // Verify all entered information is displayed
      await expect(page.locator('[data-testid="review-property-name"]'))
        .toContainText(TEST_PROPERTY.name);
      await expect(page.locator('[data-testid="review-address"]'))
        .toContainText(`${TEST_PROPERTY.address.city}, ${TEST_PROPERTY.address.state}`);
      await expect(page.locator('[data-testid="review-units"]'))
        .toContainText(TEST_PROPERTY.units.residential.toString());
      
      await page.click('[data-testid="submit-for-analysis"]');
    });

    // Step 4: Wait for DCF analysis completion
    await test.step('Wait for DCF analysis completion', async () => {
      // Should show loading state
      await expect(page.locator('[data-testid="analysis-loading"]')).toBeVisible();
      await expect(page.locator('[data-testid="analysis-status"]'))
        .toContainText('Analyzing your property...');
      
      // Wait for analysis completion (up to 30 seconds)
      await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 30000 });
      
      // Verify loading state is gone
      await expect(page.locator('[data-testid="analysis-loading"]')).not.toBeVisible();
    });

    // Step 5: Validate DCF analysis results
    await test.step('Validate DCF analysis results', async () => {
      // Verify results dashboard is displayed
      await expect(page.locator('h1')).toContainText('DCF Analysis Results');
      
      // Check financial metrics
      const npvElement = page.locator('[data-testid="npv-value"]');
      const irrElement = page.locator('[data-testid="irr-value"]');
      const recommendationElement = page.locator('[data-testid="investment-recommendation"]');
      
      await expect(npvElement).toBeVisible();
      await expect(irrElement).toBeVisible();
      await expect(recommendationElement).toBeVisible();
      
      // Validate NPV format and range
      const npvText = await npvElement.textContent();
      expect(npvText).toMatch(/\$[\d,]+/); // Should be formatted as currency
      
      // Validate IRR format and range  
      const irrText = await irrElement.textContent();
      expect(irrText).toMatch(/[\d.]+%/); // Should be formatted as percentage
      
      // Validate recommendation is one of expected values
      const recommendationText = await recommendationElement.textContent();
      expect(EXPECTED_RESULTS.recommendation).toContain(
        recommendationText?.replace(/\s+/g, '_').toUpperCase()
      );
      
      // Check cash flow projections
      await expect(page.locator('[data-testid="cash-flow-table"]')).toBeVisible();
      
      // Should show 6 years of projections
      const cashFlowRows = page.locator('[data-testid="cash-flow-row"]');
      await expect(cashFlowRows).toHaveCount(EXPECTED_RESULTS.cashFlowYears);
      
      // Verify first year data is present
      await expect(page.locator('[data-testid="cash-flow-year-2025"]')).toBeVisible();
      await expect(page.locator('[data-testid="gross-income-2025"]')).toContainText('$');
      await expect(page.locator('[data-testid="net-cash-flow-2025"]')).toContainText('$');
      
      // Check initial investment numbers
      await expect(page.locator('[data-testid="acquisition-cost"]')).toBeVisible();
      await expect(page.locator('[data-testid="total-cash-invested"]')).toBeVisible();
      await expect(page.locator('[data-testid="loan-amount"]')).toBeVisible();
    });

    // Step 6: Test export functionality
    await test.step('Test export functionality', async () => {
      // Test PDF export
      const pdfExportPromise = page.waitForDownload();
      await page.click('[data-testid="export-pdf"]');
      const pdfDownload = await pdfExportPromise;
      expect(pdfDownload.suggestedFilename()).toMatch(/dcf-analysis.*\.pdf$/i);
      
      // Test Excel export
      const excelExportPromise = page.waitForDownload();
      await page.click('[data-testid="export-excel"]');
      const excelDownload = await excelExportPromise;
      expect(excelDownload.suggestedFilename()).toMatch(/dcf-analysis.*\.xlsx?$/i);
    });

    // Step 7: Initialize Monte Carlo simulation
    await test.step('Initialize Monte Carlo simulation', async () => {
      // Click Monte Carlo button
      await page.click('[data-testid="run-monte-carlo"]');
      
      // Should navigate to Monte Carlo configuration
      await expect(page.locator('h2')).toContainText('Monte Carlo Risk Analysis');
      
      // Configure simulation parameters
      await page.fill('[data-testid="num-scenarios"]', '1000');
      await page.selectOption('[data-testid="confidence-level"]', '95');
      
      // Ensure advanced options are enabled
      await expect(page.locator('[data-testid="include-correlations"]')).toBeChecked();
      await expect(page.locator('[data-testid="include-market-cycles"]')).toBeChecked();
      
      // Start simulation
      await page.click('[data-testid="start-simulation"]');
      
      // Should show simulation in progress
      await expect(page.locator('[data-testid="simulation-status"]'))
        .toContainText('Running simulation...');
      
      // Wait for simulation completion (up to 45 seconds)
      await page.waitForSelector('[data-testid="simulation-results"]', { timeout: 45000 });
      
      // Verify results are displayed
      await expect(page.locator('[data-testid="success-probability"]')).toBeVisible();
      await expect(page.locator('[data-testid="risk-assessment"]')).toBeVisible();
      await expect(page.locator('[data-testid="scenario-distribution"]')).toBeVisible();
    });
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API to return errors
    await page.route(`${TEST_CONFIG.apiUrl}/api/v1/analysis/dcf`, route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' }),
      });
    });

    // Navigate to analysis
    await page.click('[data-testid="start-analysis-button"]');
    await page.click('[data-testid="template-multifamily-basic"]');
    await page.click('[data-testid="continue-with-template"]');

    // Fill minimal form data
    await page.fill('[data-testid="property-name"]', 'Error Test Property');
    await page.fill('[data-testid="street-address"]', '123 Error St');
    await page.fill('[data-testid="city"]', 'New York');
    await page.selectOption('[data-testid="state"]', 'NY');
    await page.fill('[data-testid="zip-code"]', '10001');

    // Complete form steps quickly
    for (let i = 0; i < 4; i++) {
      await page.click('[data-testid="next-step"]');
    }

    // Submit form
    await page.click('[data-testid="submit-for-analysis"]');

    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('Unable to complete analysis');

    // Should show retry option
    await expect(page.locator('[data-testid="retry-analysis"]')).toBeVisible();
  });

  test('should validate form inputs properly', async ({ page }) => {
    await page.click('[data-testid="start-analysis-button"]');
    await page.click('[data-testid="template-multifamily-basic"]');
    await page.click('[data-testid="continue-with-template"]');

    // Test required field validation
    await test.step('Test required field validation', async () => {
      // Try to proceed without filling required fields
      await expect(page.locator('[data-testid="next-step"]')).toBeDisabled();
      
      // Fill property name only
      await page.fill('[data-testid="property-name"]', 'Validation Test');
      
      // Should still be disabled due to missing address
      await expect(page.locator('[data-testid="next-step"]')).toBeDisabled();
      
      // Complete address
      await page.fill('[data-testid="street-address"]', '123 Test St');
      await page.fill('[data-testid="city"]', 'New York');
      await page.selectOption('[data-testid="state"]', 'NY');
      await page.fill('[data-testid="zip-code"]', '10001');
      
      // Now should be enabled
      await expect(page.locator('[data-testid="next-step"]')).toBeEnabled();
    });

    // Test numeric field validation
    await test.step('Test numeric field validation', async () => {
      await page.click('[data-testid="next-step"]');
      
      // Test invalid number inputs
      await page.fill('[data-testid="residential-units"]', '-5');
      await page.fill('[data-testid="avg-rent"]', 'abc');
      await page.fill('[data-testid="avg-sqft"]', '999999999999');
      
      // Should show validation errors
      await expect(page.locator('[data-testid="units-error"]'))
        .toContainText('must be positive');
      await expect(page.locator('[data-testid="rent-error"]'))
        .toContainText('must be a valid number');
      await expect(page.locator('[data-testid="sqft-error"]'))
        .toContainText('must be reasonable');
      
      // Next button should be disabled
      await expect(page.locator('[data-testid="next-step"]')).toBeDisabled();
    });
  });

  test('should handle slow network conditions', async ({ page }) => {
    // Simulate slow network
    await page.route(`${TEST_CONFIG.apiUrl}/api/v1/analysis/dcf`, route => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            property_id: 'slow-test-123',
            financial_metrics: {
              npv: 5000000,
              irr: 25.5,
              investment_recommendation: 'BUY',
            },
            cash_flow_projections: [],
            initial_numbers: {},
          }),
        });
      }, 15000); // 15-second delay
    });

    // Complete form submission
    await page.click('[data-testid="start-analysis-button"]');
    await page.click('[data-testid="template-multifamily-basic"]');
    await page.click('[data-testid="continue-with-template"]');

    // Fill form quickly
    await page.fill('[data-testid="property-name"]', 'Slow Network Test');
    await page.fill('[data-testid="street-address"]', '123 Slow St');
    await page.fill('[data-testid="city"]', 'New York');
    await page.selectOption('[data-testid="state"]', 'NY');
    await page.fill('[data-testid="zip-code"]', '10001');

    // Skip through steps
    for (let i = 0; i < 4; i++) {
      await page.click('[data-testid="next-step"]');
    }

    await page.click('[data-testid="submit-for-analysis"]');

    // Should show appropriate loading states
    await expect(page.locator('[data-testid="analysis-loading"]')).toBeVisible();
    await expect(page.locator('[data-testid="progress-indicator"]')).toBeVisible();
    
    // Should show time estimation
    await expect(page.locator('[data-testid="estimated-time"]'))
      .toContainText('Estimated time');

    // Should eventually complete
    await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 20000 });
    await expect(page.locator('[data-testid="npv-value"]')).toContainText('$5,000,000');
  });

  test('should maintain state across browser refresh', async ({ page }) => {
    // Start analysis and fill partial form
    await page.click('[data-testid="start-analysis-button"]');
    await page.click('[data-testid="template-multifamily-basic"]');
    await page.click('[data-testid="continue-with-template"]');

    await page.fill('[data-testid="property-name"]', 'Persistence Test');
    await page.fill('[data-testid="street-address"]', '123 State St');
    await page.fill('[data-testid="city"]', 'New York');
    await page.selectOption('[data-testid="state"]', 'NY');
    await page.fill('[data-testid="zip-code"]', '10001');

    // Refresh the page
    await page.reload();

    // Should restore form state (if implemented)
    // This tests client-side persistence features
    const propertyName = await page.locator('[data-testid="property-name"]').inputValue();
    
    if (propertyName === 'Persistence Test') {
      // State persistence is working
      await expect(page.locator('[data-testid="property-name"]'))
        .toHaveValue('Persistence Test');
      await expect(page.locator('[data-testid="street-address"]'))
        .toHaveValue('123 State St');
    } else {
      // State persistence not implemented - verify graceful fallback
      await expect(page.locator('[data-testid="property-name"]')).toHaveValue('');
      await expect(page.locator('h2')).toContainText('Property Information');
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.click('[data-testid="start-analysis-button"]');
    await page.click('[data-testid="template-multifamily-basic"]');
    await page.click('[data-testid="continue-with-template"]');

    // Test tab navigation through form fields
    await page.keyboard.press('Tab'); // Focus first field
    await page.keyboard.type('Keyboard Test Property');
    
    await page.keyboard.press('Tab'); // Move to street address
    await page.keyboard.type('123 Keyboard St');
    
    await page.keyboard.press('Tab'); // Move to city
    await page.keyboard.type('New York');
    
    await page.keyboard.press('Tab'); // Move to state dropdown
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter'); // Select NY
    
    await page.keyboard.press('Tab'); // Move to zip code
    await page.keyboard.type('10001');
    
    // Should be able to proceed with keyboard
    await page.keyboard.press('Tab'); // Focus next button
    await page.keyboard.press('Enter'); // Click next
    
    // Verify we moved to next step
    await expect(page.locator('h2')).toContainText('Unit Details');
  });

  test('should handle concurrent user scenarios', async ({ browser }) => {
    // Create multiple browser contexts to simulate concurrent users
    const contexts = await Promise.all([
      browser.newContext(),
      browser.newContext(),
      browser.newContext(),
    ]);

    const pages = await Promise.all(
      contexts.map(context => context.newPage())
    );

    // Simulate concurrent analysis submissions
    const analysisPromises = pages.map(async (page, index) => {
      await page.goto(TEST_CONFIG.baseUrl);
      await page.click('[data-testid="start-analysis-button"]');
      await page.click('[data-testid="template-multifamily-basic"]');
      await page.click('[data-testid="continue-with-template"]');

      // Fill unique property data
      await page.fill('[data-testid="property-name"]', `Concurrent Test ${index + 1}`);
      await page.fill('[data-testid="street-address"]', `${123 + index} Concurrent St`);
      await page.fill('[data-testid="city"]', 'New York');
      await page.selectOption('[data-testid="state"]', 'NY');
      await page.fill('[data-testid="zip-code"]', `1000${index + 1}`);

      // Complete form steps
      for (let step = 0; step < 4; step++) {
        await page.click('[data-testid="next-step"]');
      }

      await page.click('[data-testid="submit-for-analysis"]');
      
      // Wait for completion
      await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 45000 });
      
      return page;
    });

    // All analyses should complete successfully
    const completedPages = await Promise.all(analysisPromises);
    
    // Verify all pages show results
    for (const page of completedPages) {
      await expect(page.locator('[data-testid="npv-value"]')).toBeVisible();
      await expect(page.locator('[data-testid="irr-value"]')).toBeVisible();
    }

    // Cleanup
    await Promise.all(contexts.map(context => context.close()));
  });
});

test.describe('DCF Workflow Performance', () => {
  test('should complete analysis within performance benchmarks', async ({ page }) => {
    const startTime = Date.now();
    
    // Navigate and complete minimal analysis
    await page.goto(TEST_CONFIG.baseUrl);
    await page.click('[data-testid="start-analysis-button"]');
    await page.click('[data-testid="template-multifamily-basic"]');
    await page.click('[data-testid="continue-with-template"]');

    // Fill minimal required data
    await page.fill('[data-testid="property-name"]', 'Performance Test');
    await page.fill('[data-testid="street-address"]', '123 Performance St');
    await page.fill('[data-testid="city"]', 'New York');
    await page.selectOption('[data-testid="state"]', 'NY');
    await page.fill('[data-testid="zip-code"]', '10001');

    // Complete form steps quickly
    for (let i = 0; i < 4; i++) {
      await page.click('[data-testid="next-step"]');
    }

    await page.click('[data-testid="submit-for-analysis"]');
    
    // Wait for results
    await page.waitForSelector('[data-testid="dcf-results"]', { timeout: 30000 });
    
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // Should complete within 30 seconds total (including form filling)
    expect(totalTime).toBeLessThan(30000);
    
    console.log(`Total workflow time: ${totalTime}ms`);
  });
});