/**
 * Visual Regression Testing Suite
 * Tests visual consistency of charts, dashboards, and UI components
 * 
 * This suite captures and compares screenshots to detect visual regressions
 * in financial charts, data visualizations, and dashboard layouts.
 */

import { test, expect, Page } from '@playwright/test';

// Visual test configuration
const VISUAL_CONFIG = {
  // Screenshot comparison threshold (0-1, where 0 = pixel perfect)
  threshold: 0.2, // 20% difference allowed
  
  // Animation settings
  animations: 'disabled' as const,
  
  // Font rendering consistency
  fontFamily: 'Arial, sans-serif',
  
  // Color scheme testing
  colorSchemes: ['light', 'dark'] as const,
  
  // Viewport sizes for responsive testing
  viewports: [
    { width: 1920, height: 1080, name: 'desktop-xl' },
    { width: 1280, height: 720, name: 'desktop' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 375, height: 812, name: 'mobile' },
  ],
};

// Mock data for consistent visual testing
const MOCK_DCF_DATA = {
  property_id: 'visual-test-property',
  analysis_date: '2025-01-01',
  financial_metrics: {
    npv: 15847901,
    irr: 64.8,
    equity_multiple: 9.79,
    payback_period: 4.2,
    terminal_value: 45000000,
    total_return: 156.5,
    investment_recommendation: 'STRONG_BUY' as const,
    confidence_score: 0.89,
  },
  cash_flow_projections: [
    { year: 2025, gross_rental_income: 600000, operating_expenses: 180000, net_operating_income: 420000, debt_service: 150000, net_cash_flow: 270000 },
    { year: 2026, gross_rental_income: 621000, operating_expenses: 186300, net_operating_income: 434700, debt_service: 150000, net_cash_flow: 284700 },
    { year: 2027, gross_rental_income: 642630, operating_expenses: 192909, net_operating_income: 449721, debt_service: 150000, net_cash_flow: 299721 },
    { year: 2028, gross_rental_income: 664921, operating_expenses: 199681, net_operating_income: 465240, debt_service: 150000, net_cash_flow: 315240 },
    { year: 2029, gross_rental_income: 687892, operating_expenses: 206619, net_operating_income: 481273, debt_service: 150000, net_cash_flow: 331273 },
    { year: 2030, gross_rental_income: 711563, operating_expenses: 213728, net_operating_income: 497835, debt_service: 150000, net_cash_flow: 347835 },
  ],
  initial_numbers: {
    acquisition_cost: 12500000,
    total_cash_invested: 3125000,
    loan_amount: 9375000,
    closing_costs: 125000,
    renovation_cost: 500000,
  },
};

const MOCK_MONTE_CARLO_DATA = {
  simulation_id: 'visual-test-mc',
  property_id: 'visual-test-property',
  total_scenarios: 1000,
  execution_time_ms: 2500,
  success: true,
  scenario_analysis: Array.from({ length: 20 }, (_, i) => ({
    scenario_id: i + 1,
    npv: 10000000 + (Math.sin(i * 0.5) * 8000000),
    irr: 45 + (Math.cos(i * 0.3) * 25),
    equity_multiple: 7 + (Math.sin(i * 0.2) * 3),
    market_classification: ['BULL', 'BEAR', 'NEUTRAL', 'GROWTH', 'STRESS'][i % 5] as any,
    risk_score: 0.3 + (Math.sin(i * 0.4) * 0.4),
    growth_score: 0.4 + (Math.cos(i * 0.6) * 0.3),
  })),
  risk_metrics: {
    value_at_risk_95: 8500000,
    expected_shortfall: 7200000,
    probability_of_loss: 0.05,
    worst_case_npv: 2000000,
    best_case_npv: 28000000,
  },
  percentiles: {
    npv: { p5: 5000000, p25: 12000000, median: 15847901, p75: 20000000, p95: 25000000 },
    irr: { p5: 25.0, p25: 45.0, median: 64.8, p75: 75.0, p95: 85.0 },
    total_cash_flow: { p5: 800000, p25: 1200000, median: 1650000, p75: 2100000, p95: 2500000 },
  },
  distribution: Array.from({ length: 50 }, (_, i) => ({
    scenario_id: i + 1,
    npv: 8000000 + (Math.random() * 16000000),
    irr: 30 + (Math.random() * 50),
    total_cash_flow: 1000000 + (Math.random() * 2000000),
    risk_score: Math.random(),
    market_classification: 'NEUTRAL' as any,
  })),
  risk_distribution: { low: 30, moderate: 50, high: 20 },
  overall_risk_assessment: 'Moderate',
};

// Helper function to setup page for visual testing
async function setupVisualTest(page: Page, colorScheme: 'light' | 'dark' = 'light') {
  // Disable animations for consistent screenshots
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-delay: -1ms !important;
        animation-duration: 1ms !important;
        animation-iteration-count: 1 !important;
        background-attachment: initial !important;
        scroll-behavior: auto !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
      
      /* Ensure consistent font rendering */
      * {
        font-family: ${VISUAL_CONFIG.fontFamily} !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
      }
      
      /* Hide dynamic elements that change between runs */
      .timestamp, .current-time, .live-indicator {
        visibility: hidden !important;
      }
    `
  });

  // Set color scheme
  await page.emulateMedia({ colorScheme });

  // Wait for fonts to load
  await page.evaluate(() => document.fonts.ready);
  
  // Wait for any lazy-loaded images
  await page.waitForLoadState('networkidle');
}

// Helper function to mask dynamic content
async function maskDynamicContent(page: Page) {
  await page.addStyleTag({
    content: `
      /* Mask timestamps and dynamic IDs */
      [data-testid*="timestamp"], 
      [data-testid*="id"],
      .timestamp,
      .execution-time {
        background: #f0f0f0 !important;
        color: transparent !important;
      }
      
      /* Ensure consistent chart animations */
      .recharts-wrapper svg {
        opacity: 1 !important;
      }
    `
  });
}

test.describe('Visual Regression Tests - DCF Results Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses with consistent data
    await page.route('**/api/v1/analysis/dcf', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_DCF_DATA),
      });
    });
    
    await page.route('**/api/v1/simulation/monte-carlo/**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_MONTE_CARLO_DATA),
      });
    });
  });

  for (const viewport of VISUAL_CONFIG.viewports) {
    test(`DCF Results Dashboard - ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await setupVisualTest(page);
      
      // Navigate to results page with mock data
      await page.goto('/analysis/results/visual-test-property');
      await page.waitForSelector('[data-testid="dcf-results"]');
      
      // Wait for all charts to load
      await page.waitForSelector('[data-testid="chart-container"]');
      await page.waitForTimeout(1000); // Allow charts to render
      
      await maskDynamicContent(page);
      
      // Capture full dashboard
      await expect(page).toHaveScreenshot(`dcf-dashboard-${viewport.name}.png`, {
        threshold: VISUAL_CONFIG.threshold,
        fullPage: true,
      });
    });
  }

  test('DCF Results Dashboard - Dark Mode', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page, 'dark');
    
    await page.goto('/analysis/results/visual-test-property');
    await page.waitForSelector('[data-testid="dcf-results"]');
    await page.waitForSelector('[data-testid="chart-container"]');
    await page.waitForTimeout(1000);
    
    await maskDynamicContent(page);
    
    await expect(page).toHaveScreenshot('dcf-dashboard-dark-mode.png', {
      threshold: VISUAL_CONFIG.threshold,
      fullPage: true,
    });
  });

  test('Financial Metrics Cards', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/results/visual-test-property');
    await page.waitForSelector('[data-testid="financial-metrics"]');
    
    // Capture just the metrics section
    const metricsSection = page.locator('[data-testid="financial-metrics"]');
    await expect(metricsSection).toHaveScreenshot('financial-metrics-cards.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });

  test('Cash Flow Projections Table', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/results/visual-test-property');
    await page.waitForSelector('[data-testid="cash-flow-table"]');
    
    const cashFlowTable = page.locator('[data-testid="cash-flow-table"]');
    await expect(cashFlowTable).toHaveScreenshot('cash-flow-table.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });

  test('Investment Recommendation Display', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/results/visual-test-property');
    await page.waitForSelector('[data-testid="investment-recommendation"]');
    
    const recommendationSection = page.locator('[data-testid="recommendation-section"]');
    await expect(recommendationSection).toHaveScreenshot('investment-recommendation.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });
});

test.describe('Visual Regression Tests - Monte Carlo Results', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/simulation/monte-carlo/**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_MONTE_CARLO_DATA),
      });
    });
  });

  test('Monte Carlo Results Overview', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/monte-carlo/visual-test-mc');
    await page.waitForSelector('[data-testid="monte-carlo-results"]');
    await page.waitForSelector('[data-testid="chart-container"]');
    await page.waitForTimeout(2000); // Allow all charts to render
    
    await maskDynamicContent(page);
    
    await expect(page).toHaveScreenshot('monte-carlo-overview.png', {
      threshold: VISUAL_CONFIG.threshold,
      fullPage: true,
    });
  });

  test('Distribution Charts', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/monte-carlo/visual-test-mc');
    await page.waitForSelector('[data-testid="monte-carlo-results"]');
    await page.click('[data-testid="tab-distribution"]');
    await page.waitForTimeout(1000);
    
    // Test NPV distribution
    await page.click('[data-testid="metric-npv"]');
    await page.waitForTimeout(500);
    const npvChart = page.locator('[data-testid="distribution-chart"]');
    await expect(npvChart).toHaveScreenshot('distribution-chart-npv.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
    
    // Test IRR distribution
    await page.click('[data-testid="metric-irr"]');
    await page.waitForTimeout(500);
    await expect(npvChart).toHaveScreenshot('distribution-chart-irr.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
    
    // Test Cash Flow distribution
    await page.click('[data-testid="metric-cashflow"]');
    await page.waitForTimeout(500);
    await expect(npvChart).toHaveScreenshot('distribution-chart-cashflow.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });

  test('Percentiles Display', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/monte-carlo/visual-test-mc');
    await page.waitForSelector('[data-testid="monte-carlo-results"]');
    await page.click('[data-testid="tab-percentiles"]');
    await page.waitForTimeout(500);
    
    const percentilesSection = page.locator('[data-testid="percentiles-content"]');
    await expect(percentilesSection).toHaveScreenshot('percentiles-display.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });

  test('Risk Analysis Charts', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/monte-carlo/visual-test-mc');
    await page.waitForSelector('[data-testid="monte-carlo-results"]');
    await page.click('[data-testid="tab-risk"]');
    await page.waitForTimeout(1000);
    
    const riskSection = page.locator('[data-testid="risk-analysis-content"]');
    await expect(riskSection).toHaveScreenshot('risk-analysis-charts.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });

  test('Scenario Scatter Plot', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/monte-carlo/visual-test-mc');
    await page.waitForSelector('[data-testid="monte-carlo-results"]');
    await page.click('[data-testid="tab-scenarios"]');
    await page.waitForTimeout(1000);
    
    const scenariosChart = page.locator('[data-testid="scenarios-scatter-plot"]');
    await expect(scenariosChart).toHaveScreenshot('scenarios-scatter-plot.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });
});

test.describe('Visual Regression Tests - Market Data Explorer', () => {
  test.beforeEach(async ({ page }) => {
    const mockMarketData = {
      msa: 'NYC',
      parameters: {
        interestRate: 5.5,
        capRate: 4.2,
        vacancy: 5.0,
        rentGrowth: 3.5,
        expenseGrowth: 2.8,
        propertyGrowth: 4.1,
      },
      historicalData: Array.from({ length: 60 }, (_, i) => ({
        date: `2020-${String(Math.floor(i/12) + 1).padStart(2, '0')}-01`,
        interestRate: 3.5 + (Math.sin(i * 0.1) * 2),
        capRate: 4.0 + (Math.cos(i * 0.15) * 1),
        vacancy: 5.0 + (Math.sin(i * 0.2) * 2),
        rentGrowth: 3.0 + (Math.cos(i * 0.1) * 2),
      })),
      forecast: Array.from({ length: 24 }, (_, i) => ({
        date: `2025-${String(i + 1).padStart(2, '0')}-01`,
        interestRate: 5.5 + (Math.sin(i * 0.2) * 1),
        capRate: 4.2 + (Math.cos(i * 0.15) * 0.5),
        rentGrowth: 3.5 + (Math.sin(i * 0.1) * 1.5),
        confidenceInterval: { lower: -0.5, upper: 0.5 },
      })),
    };

    await page.route('**/api/v1/market-data/**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMarketData),
      });
    });
  });

  test('Market Data Explorer Overview', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/market-data/explorer');
    await page.waitForSelector('[data-testid="market-data-explorer"]');
    await page.waitForSelector('[data-testid="time-series-chart"]');
    await page.waitForTimeout(1500);
    
    await expect(page).toHaveScreenshot('market-data-explorer.png', {
      threshold: VISUAL_CONFIG.threshold,
      fullPage: true,
    });
  });

  test('Time Series Charts', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/market-data/explorer');
    await page.waitForSelector('[data-testid="time-series-chart"]');
    await page.waitForTimeout(1000);
    
    // Test different parameter charts
    const parameters = ['interestRate', 'capRate', 'vacancy', 'rentGrowth'];
    
    for (const param of parameters) {
      await page.click(`[data-testid="param-${param}"]`);
      await page.waitForTimeout(500);
      
      const chart = page.locator('[data-testid="time-series-chart"]');
      await expect(chart).toHaveScreenshot(`time-series-${param}.png`, {
        threshold: VISUAL_CONFIG.threshold,
      });
    }
  });

  test('Forecast Charts with Confidence Intervals', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/market-data/explorer');
    await page.waitForSelector('[data-testid="forecast-chart"]');
    await page.waitForTimeout(1000);
    
    const forecastChart = page.locator('[data-testid="forecast-chart"]');
    await expect(forecastChart).toHaveScreenshot('forecast-with-confidence-intervals.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });
});

test.describe('Visual Regression Tests - Property Input Form', () => {
  test('Multi-step Form Layout', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/property/input');
    await page.waitForSelector('[data-testid="property-input-form"]');
    
    // Test each step of the form
    const steps = [
      'property-info',
      'unit-details', 
      'renovation-info',
      'equity-structure',
      'review-submit'
    ];
    
    for (let i = 0; i < steps.length; i++) {
      await expect(page).toHaveScreenshot(`form-step-${i + 1}-${steps[i]}.png`, {
        threshold: VISUAL_CONFIG.threshold,
      });
      
      // Fill minimal data to proceed to next step
      if (i < steps.length - 1) {
        await fillFormStepData(page, i);
        await page.click('[data-testid="next-step"]');
        await page.waitForTimeout(500);
      }
    }
  });

  test('Form Validation States', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/property/input');
    await page.waitForSelector('[data-testid="property-input-form"]');
    
    // Test error states
    await page.fill('[data-testid="property-name"]', ''); // Invalid
    await page.fill('[data-testid="residential-units"]', '-1'); // Invalid
    await page.click('[data-testid="next-step"]');
    
    await expect(page).toHaveScreenshot('form-validation-errors.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });
});

test.describe('Visual Regression Tests - Responsive Design', () => {
  const components = [
    { path: '/analysis/results/visual-test-property', name: 'dcf-results' },
    { path: '/analysis/monte-carlo/visual-test-mc', name: 'monte-carlo' },
    { path: '/market-data/explorer', name: 'market-explorer' },
  ];

  for (const viewport of VISUAL_CONFIG.viewports) {
    for (const component of components) {
      test(`${component.name} - ${viewport.name}`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await setupVisualTest(page);
        
        await page.goto(component.path);
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1500); // Allow charts to render
        
        await maskDynamicContent(page);
        
        await expect(page).toHaveScreenshot(`${component.name}-${viewport.name}.png`, {
          threshold: VISUAL_CONFIG.threshold,
          fullPage: true,
        });
      });
    }
  }
});

test.describe('Visual Regression Tests - Chart Interactions', () => {
  test('Chart Hover States', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/results/visual-test-property');
    await page.waitForSelector('[data-testid="cash-flow-chart"]');
    await page.waitForTimeout(1000);
    
    // Hover over chart element
    const chartBar = page.locator('[data-testid="cash-flow-chart"] .recharts-bar').first();
    await chartBar.hover();
    await page.waitForTimeout(300);
    
    await expect(page.locator('[data-testid="cash-flow-chart"]')).toHaveScreenshot('chart-hover-state.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });

  test('Chart Tooltip Display', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await setupVisualTest(page);
    
    await page.goto('/analysis/monte-carlo/visual-test-mc');
    await page.waitForSelector('[data-testid="distribution-chart"]');
    await page.waitForTimeout(1000);
    
    // Trigger tooltip
    const chartElement = page.locator('[data-testid="distribution-chart"] .recharts-bar').first();
    await chartElement.hover();
    await page.waitForTimeout(300);
    
    await expect(page.locator('[data-testid="distribution-chart"]')).toHaveScreenshot('chart-tooltip.png', {
      threshold: VISUAL_CONFIG.threshold,
    });
  });
});

// Helper function to fill form step data
async function fillFormStepData(page: Page, stepIndex: number) {
  switch (stepIndex) {
    case 0: // Property info
      await page.fill('[data-testid="property-name"]', 'Visual Test Property');
      await page.fill('[data-testid="street-address"]', '123 Visual St');
      await page.fill('[data-testid="city"]', 'New York');
      await page.selectOption('[data-testid="state"]', 'NY');
      await page.fill('[data-testid="zip-code"]', '10001');
      break;
    case 1: // Unit details
      await page.fill('[data-testid="residential-units"]', '20');
      await page.fill('[data-testid="avg-rent"]', '2500');
      await page.fill('[data-testid="avg-sqft"]', '900');
      break;
    case 2: // Renovation info
      await page.fill('[data-testid="renovation-duration"]', '6');
      await page.fill('[data-testid="renovation-budget"]', '500000');
      break;
    case 3: // Equity structure
      await page.fill('[data-testid="investor-equity"]', '25');
      await page.fill('[data-testid="self-cash"]', '75');
      break;
  }
}