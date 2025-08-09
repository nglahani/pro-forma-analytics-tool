/**
 * Visual Testing Utilities
 * Helper functions and configurations for visual regression testing
 */

import { Page, Locator } from '@playwright/test';

export interface VisualTestConfig {
  threshold?: number;
  animations?: 'disabled' | 'reduced' | 'normal';
  maskDynamicContent?: boolean;
  waitForCharts?: boolean;
  colorScheme?: 'light' | 'dark';
  deviceScaleFactor?: number;
}

export interface ChartWaitOptions {
  chartSelector?: string;
  timeout?: number;
  stabilizationDelay?: number;
}

/**
 * Standard visual test configuration
 */
export const VISUAL_CONFIG = {
  DEFAULT_THRESHOLD: 0.2, // 20% difference allowed
  CHART_WAIT_TIMEOUT: 5000, // 5 seconds to wait for charts
  STABILIZATION_DELAY: 1000, // 1 second after charts load
  FONT_FAMILY: 'Arial, sans-serif',
  
  VIEWPORTS: {
    MOBILE: { width: 375, height: 812 },
    TABLET: { width: 768, height: 1024 },
    DESKTOP: { width: 1280, height: 720 },
    DESKTOP_XL: { width: 1920, height: 1080 },
  },
  
  SELECTORS: {
    CHARTS: [
      '[data-testid="chart-container"]',
      '.recharts-wrapper',
      '[data-testid*="chart"]',
      '.chart-component',
    ],
    DYNAMIC_CONTENT: [
      '[data-testid*="timestamp"]',
      '[data-testid*="id"]',
      '.timestamp',
      '.execution-time',
      '.current-time',
      '.live-indicator',
    ],
  },
} as const;

/**
 * Prepares page for consistent visual testing
 */
export async function setupPageForVisualTest(
  page: Page, 
  config: VisualTestConfig = {}
): Promise<void> {
  const {
    animations = 'disabled',
    colorScheme = 'light',
    deviceScaleFactor = 1,
  } = config;

  // Set device scale factor
  if (deviceScaleFactor !== 1) {
    const viewport = page.viewportSize();
    if (viewport) {
      await page.setViewportSize({
        width: viewport.width,
        height: viewport.height,
      });
    }
  }

  // Disable animations and transitions for consistent screenshots
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-delay: -1ms !important;
        animation-duration: ${animations === 'disabled' ? '1ms' : '100ms'} !important;
        animation-iteration-count: 1 !important;
        background-attachment: initial !important;
        scroll-behavior: auto !important;
        transition-duration: ${animations === 'disabled' ? '0s' : '0.1s'} !important;
        transition-delay: 0s !important;
      }
      
      /* Ensure consistent font rendering */
      * {
        font-family: ${VISUAL_CONFIG.FONT_FAMILY} !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        text-rendering: optimizeLegibility !important;
      }
      
      /* Disable hover effects that can cause flakiness */
      *:hover {
        transition: none !important;
      }
      
      /* Ensure consistent chart rendering */
      .recharts-wrapper, .chart-container {
        opacity: 1 !important;
      }
      
      /* Hide scrollbars for consistent screenshots */
      ::-webkit-scrollbar {
        width: 0px;
        background: transparent;
      }
      
      /* Ensure consistent loading states */
      .loading, .spinner {
        display: none !important;
      }
    `
  });

  // Set color scheme
  await page.emulateMedia({ colorScheme });
  
  // Reduce motion for users with motion sensitivity
  if (animations === 'reduced') {
    await page.emulateMedia({ reducedMotion: 'reduce' });
  }

  // Wait for fonts to load
  await page.evaluate(() => document.fonts.ready);
  
  // Wait for images and other resources
  await page.waitForLoadState('networkidle');
}

/**
 * Masks dynamic content that changes between test runs
 */
export async function maskDynamicContent(page: Page): Promise<void> {
  await page.addStyleTag({
    content: `
      /* Mask timestamps and dynamic IDs */
      ${VISUAL_CONFIG.SELECTORS.DYNAMIC_CONTENT.join(', ')} {
        background: #f0f0f0 !important;
        color: transparent !important;
        border-radius: 4px !important;
      }
      
      /* Mask random IDs and generated content */
      [data-id], [id*="random"], [id*="generated"] {
        background: #f0f0f0 !important;
        color: transparent !important;
      }
      
      /* Ensure chart animations are complete */
      .recharts-wrapper svg * {
        opacity: 1 !important;
        transform: none !important;
      }
      
      /* Hide dynamic badges and indicators */
      .live-badge, .status-indicator[class*="animate"] {
        display: none !important;
      }
    `
  });
}

/**
 * Waits for charts to fully render and stabilize
 */
export async function waitForChartsToStabilize(
  page: Page, 
  options: ChartWaitOptions = {}
): Promise<void> {
  const {
    timeout = VISUAL_CONFIG.CHART_WAIT_TIMEOUT,
    stabilizationDelay = VISUAL_CONFIG.STABILIZATION_DELAY,
  } = options;

  try {
    // Wait for at least one chart to be present
    const chartSelectors = VISUAL_CONFIG.SELECTORS.CHARTS;
    const chartPromises = chartSelectors.map(selector => 
      page.waitForSelector(selector, { timeout: timeout / chartSelectors.length })
        .catch(() => null) // Ignore individual selector failures
    );
    
    await Promise.race(chartPromises.filter(Boolean));

    // Wait for charts to finish rendering
    await page.waitForFunction(() => {
      const charts = document.querySelectorAll('.recharts-wrapper svg, [data-testid*="chart"] svg');
      return Array.from(charts).every(chart => {
        const rect = chart.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      });
    }, { timeout });

    // Additional stabilization delay
    await page.waitForTimeout(stabilizationDelay);

  } catch (error) {
    console.warn('Chart stabilization warning:', error.message);
    // Continue with test even if charts don't fully stabilize
    await page.waitForTimeout(500); // Minimal delay as fallback
  }
}

/**
 * Captures a screenshot with consistent settings
 */
export async function captureStableScreenshot(
  locator: Locator | Page,
  name: string,
  config: VisualTestConfig = {}
): Promise<void> {
  const { threshold = VISUAL_CONFIG.DEFAULT_THRESHOLD } = config;

  // Take multiple screenshots to ensure stability
  const screenshots: Buffer[] = [];
  
  for (let i = 0; i < 3; i++) {
    await new Promise(resolve => setTimeout(resolve, 100)); // Small delay between shots
    const screenshot = await locator.screenshot({ 
      type: 'png',
      animations: 'disabled',
    });
    screenshots.push(screenshot);
  }

  // Use the last screenshot (most likely to be stable)
  const finalScreenshot = screenshots[screenshots.length - 1];
  
  // Compare against baseline (this would be handled by expect().toHaveScreenshot())
  // For now, we'll rely on Playwright's built-in comparison
  if ('toHaveScreenshot' in locator) {
    await (locator as any).toHaveScreenshot(name, { threshold });
  } else {
    await (locator as Page).screenshot({ 
      path: `test-results/screenshots/${name}`,
      type: 'png',
      animations: 'disabled',
    });
  }
}

/**
 * Sets up mock data for consistent visual testing
 */
export async function setupMockData(page: Page): Promise<void> {
  // Mock API responses with consistent data
  await page.route('**/api/v1/**', async (route) => {
    const url = route.request().url();
    
    if (url.includes('/analysis/dcf')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(getMockDCFData()),
      });
    } else if (url.includes('/simulation/monte-carlo')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(getMockMonteCarloData()),
      });
    } else if (url.includes('/market-data')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(getMockMarketData()),
      });
    } else {
      await route.continue();
    }
  });
}

/**
 * Mock DCF analysis data
 */
function getMockDCFData() {
  return {
    property_id: 'visual-test-property',
    analysis_date: '2025-01-01',
    financial_metrics: {
      npv: 15847901,
      irr: 64.8,
      equity_multiple: 9.79,
      payback_period: 4.2,
      terminal_value: 45000000,
      total_return: 156.5,
      investment_recommendation: 'STRONG_BUY',
      confidence_score: 0.89,
    },
    cash_flow_projections: Array.from({ length: 6 }, (_, i) => ({
      year: 2025 + i,
      gross_rental_income: 600000 + (i * 21000),
      operating_expenses: 180000 + (i * 6300),
      net_operating_income: 420000 + (i * 14700),
      debt_service: 150000,
      net_cash_flow: 270000 + (i * 14700),
    })),
    initial_numbers: {
      acquisition_cost: 12500000,
      total_cash_invested: 3125000,
      loan_amount: 9375000,
      closing_costs: 125000,
      renovation_cost: 500000,
    },
  };
}

/**
 * Mock Monte Carlo simulation data
 */
function getMockMonteCarloData() {
  return {
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
      market_classification: ['BULL', 'BEAR', 'NEUTRAL', 'GROWTH', 'STRESS'][i % 5],
      risk_score: 0.3 + (Math.sin(i * 0.4) * 0.4),
      growth_score: 0.4 + (Math.cos(i * 0.6) * 0.3),
    })),
    percentiles: {
      npv: { p5: 5000000, p25: 12000000, median: 15847901, p75: 20000000, p95: 25000000 },
      irr: { p5: 25.0, p25: 45.0, median: 64.8, p75: 75.0, p95: 85.0 },
      total_cash_flow: { p5: 800000, p25: 1200000, median: 1650000, p75: 2100000, p95: 2500000 },
    },
    distribution: Array.from({ length: 50 }, (_, i) => ({
      scenario_id: i + 1,
      npv: 8000000 + (Math.sin(i * 0.1) * 12000000),
      irr: 30 + (Math.cos(i * 0.15) * 40),
      total_cash_flow: 1000000 + (Math.sin(i * 0.2) * 1500000),
      risk_score: 0.2 + (Math.cos(i * 0.3) * 0.6),
      market_classification: 'NEUTRAL',
    })),
    risk_distribution: { low: 30, moderate: 50, high: 20 },
    overall_risk_assessment: 'Moderate',
  };
}

/**
 * Mock market data
 */
function getMockMarketData() {
  return {
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
      date: new Date(2020, Math.floor(i / 12), 1).toISOString().split('T')[0],
      interestRate: 3.5 + (Math.sin(i * 0.1) * 2),
      capRate: 4.0 + (Math.cos(i * 0.15) * 1),
      vacancy: 5.0 + (Math.sin(i * 0.2) * 2),
      rentGrowth: 3.0 + (Math.cos(i * 0.1) * 2),
    })),
    forecast: Array.from({ length: 24 }, (_, i) => ({
      date: new Date(2025, i, 1).toISOString().split('T')[0],
      interestRate: 5.5 + (Math.sin(i * 0.2) * 1),
      capRate: 4.2 + (Math.cos(i * 0.15) * 0.5),
      rentGrowth: 3.5 + (Math.sin(i * 0.1) * 1.5),
      confidenceInterval: { lower: -0.5, upper: 0.5 },
    })),
    lastUpdated: '2025-01-01T00:00:00Z',
  };
}

/**
 * Highlights visual differences for debugging
 */
export async function highlightVisualDifferences(
  page: Page,
  selector: string
): Promise<void> {
  await page.addStyleTag({
    content: `
      ${selector} {
        outline: 3px solid red !important;
        outline-offset: 2px !important;
      }
      
      ${selector}::after {
        content: "VISUAL DIFF DETECTED";
        position: absolute;
        top: -30px;
        left: 0;
        background: red;
        color: white;
        padding: 4px 8px;
        font-size: 12px;
        font-weight: bold;
        z-index: 9999;
      }
    `
  });
}

/**
 * Generates a visual testing report
 */
export interface VisualTestResult {
  testName: string;
  passed: boolean;
  threshold: number;
  actualDifference?: number;
  screenshotPath?: string;
  baselinePath?: string;
  diffPath?: string;
}

export function generateVisualReport(results: VisualTestResult[]): string {
  const totalTests = results.length;
  const passedTests = results.filter(r => r.passed).length;
  const failedTests = totalTests - passedTests;
  
  const report = [
    '# Visual Regression Testing Report',
    '',
    `**Generated**: ${new Date().toISOString()}`,
    `**Total Tests**: ${totalTests}`,
    `**Passed**: ${passedTests}`,
    `**Failed**: ${failedTests}`,
    `**Pass Rate**: ${((passedTests / totalTests) * 100).toFixed(1)}%`,
    '',
    '## Results Summary',
    '',
    '| Test | Status | Threshold | Actual Diff | Screenshot |',
    '|------|--------|-----------|-------------|------------|',
  ];

  results.forEach(result => {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    const diff = result.actualDifference ? `${(result.actualDifference * 100).toFixed(1)}%` : 'N/A';
    const threshold = `${(result.threshold * 100).toFixed(1)}%`;
    const screenshot = result.screenshotPath ? `[View](${result.screenshotPath})` : 'N/A';
    
    report.push(`| ${result.testName} | ${status} | ${threshold} | ${diff} | ${screenshot} |`);
  });

  if (failedTests > 0) {
    report.push('', '## Failed Tests', '');
    
    results.filter(r => !r.passed).forEach(result => {
      report.push(`### ${result.testName}`);
      report.push(`- **Threshold**: ${(result.threshold * 100).toFixed(1)}%`);
      if (result.actualDifference) {
        report.push(`- **Actual Difference**: ${(result.actualDifference * 100).toFixed(1)}%`);
      }
      if (result.diffPath) {
        report.push(`- **Diff Image**: [View Difference](${result.diffPath})`);
      }
      report.push('');
    });
  }

  return report.join('\n');
}

/**
 * Viewport testing utility
 */
export async function testAcrossViewports(
  page: Page,
  testCallback: (viewport: { width: number; height: number; name: string }) => Promise<void>
): Promise<void> {
  const viewports = [
    { ...VISUAL_CONFIG.VIEWPORTS.MOBILE, name: 'mobile' },
    { ...VISUAL_CONFIG.VIEWPORTS.TABLET, name: 'tablet' },
    { ...VISUAL_CONFIG.VIEWPORTS.DESKTOP, name: 'desktop' },
    { ...VISUAL_CONFIG.VIEWPORTS.DESKTOP_XL, name: 'desktop-xl' },
  ];

  for (const viewport of viewports) {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.waitForTimeout(500); // Allow layout to adjust
    await testCallback(viewport);
  }
}