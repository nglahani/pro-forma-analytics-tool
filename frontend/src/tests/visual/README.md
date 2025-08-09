# Visual Regression Testing Suite

Comprehensive visual regression testing for charts, dashboards, and UI components using Playwright screenshot comparison.

## Overview

Visual regression testing captures screenshots of key UI components and compares them against baseline images to detect unintended visual changes. This is especially critical for financial applications where chart accuracy and dashboard consistency are essential.

## What We Test

### 🎯 **Core Visual Components**
- **DCF Results Dashboard**: Complete financial analysis layout
- **Monte Carlo Results**: Statistical visualizations and risk charts  
- **Market Data Explorer**: Time series charts and forecast visualizations
- **Property Input Forms**: Multi-step form layouts and validation states

### 📊 **Chart Types**
- **Bar Charts**: Distribution histograms, cash flow projections
- **Line Charts**: Time series data, forecast trends
- **Pie Charts**: Risk distribution, portfolio breakdowns
- **Scatter Plots**: Scenario analysis, correlation visualization
- **Area Charts**: Confidence intervals, forecast ranges

### 📱 **Responsive Testing**
- **Desktop**: 1280x720 (standard), 1920x1080 (XL)
- **Tablet**: 768x1024 (portrait and landscape)
- **Mobile**: 375x812 (iPhone-style)
- **High-DPI**: 2x device pixel ratio testing

### 🎨 **Theme Testing**
- **Light Mode**: Default application theme
- **Dark Mode**: Dark theme consistency
- **High Contrast**: Accessibility compliance
- **Color Schemes**: Brand color consistency

## Test Structure

```
src/tests/visual/
├── visual-regression.test.ts    # Main visual test suite
├── visual-utils.ts             # Helper utilities and configurations
├── fixtures/                   # Mock data for consistent testing
├── baseline-images/            # Reference screenshots (auto-generated)
└── README.md                   # This file
```

## Running Visual Tests

### Prerequisites

1. **Install Dependencies**:
   ```bash
   npm install
   npx playwright install
   ```

2. **Generate Baseline Screenshots** (first-time setup):
   ```bash
   npm run test:visual:update
   ```

### Basic Visual Testing

```bash
# Run all visual regression tests
npm run test:visual

# Update baseline screenshots
npm run test:visual:update

# Run with visual UI (recommended for development)
npm run test:visual:ui

# Debug visual differences
npm run test:visual:debug
```

### Platform-Specific Testing

```bash
# Desktop Chrome (primary platform)
npm run test:visual:chrome

# Mobile responsive testing
npm run test:visual:mobile

# Dark mode testing
npm run test:visual:dark

# All browser/platform combinations
npm run test:visual
```

### View Test Results

```bash
# Open visual test results report
npm run test:visual:report

# View detailed HTML report with image diffs
npx playwright show-report visual-test-results
```

## Configuration

### Visual Test Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `threshold` | 0.2 (20%) | Acceptable visual difference |
| `timeout` | 90000ms | Test timeout for visual comparisons |
| `animations` | disabled | Animation handling for consistency |
| `deviceScaleFactor` | 1 | Pixel density for HiDPI testing |

### Environment Variables

```bash
# Custom configuration
VISUAL_BASE_URL=http://localhost:3000    # Frontend URL
VISUAL_THRESHOLD=0.1                     # 10% difference threshold
VISUAL_TIMEOUT=120000                    # 2-minute timeout
```

### Viewport Configuration

```typescript
const VIEWPORTS = {
  MOBILE: { width: 375, height: 812 },    // iPhone-style
  TABLET: { width: 768, height: 1024 },   // iPad-style  
  DESKTOP: { width: 1280, height: 720 },  // Standard desktop
  DESKTOP_XL: { width: 1920, height: 1080 }, // Large desktop
};
```

## Test Development

### Writing Visual Tests

1. **Basic Screenshot Comparison**:
   ```typescript
   test('DCF dashboard layout', async ({ page }) => {
     await page.goto('/analysis/results/test-property');
     await setupPageForVisualTest(page);
     await waitForChartsToStabilize(page);
     
     await expect(page).toHaveScreenshot('dcf-dashboard.png', {
       threshold: 0.2,
       fullPage: true,
     });
   });
   ```

2. **Component-Level Testing**:
   ```typescript
   test('financial metrics cards', async ({ page }) => {
     await page.goto('/analysis/results/test-property');
     await setupPageForVisualTest(page);
     
     const metricsSection = page.locator('[data-testid="financial-metrics"]');
     await expect(metricsSection).toHaveScreenshot('metrics-cards.png');
   });
   ```

3. **Responsive Testing**:
   ```typescript
   test('mobile responsive layout', async ({ page }) => {
     await page.setViewportSize({ width: 375, height: 812 });
     await setupPageForVisualTest(page);
     
     await page.goto('/analysis/results/test-property');
     await expect(page).toHaveScreenshot('mobile-layout.png');
   });
   ```

### Visual Test Utilities

```typescript
import { 
  setupPageForVisualTest, 
  waitForChartsToStabilize, 
  maskDynamicContent,
  setupMockData 
} from './visual-utils';

// Standard setup for visual consistency
await setupPageForVisualTest(page, {
  threshold: 0.15,
  animations: 'disabled',
  colorScheme: 'light'
});

// Wait for charts to fully render
await waitForChartsToStabilize(page, {
  timeout: 5000,
  stabilizationDelay: 1000
});

// Hide dynamic content that changes between runs
await maskDynamicContent(page);
```

### Mock Data Strategy

Visual tests use consistent mock data to ensure repeatable results:

```typescript
// Consistent DCF results for visual testing
const mockDCFData = {
  npv: 15847901,
  irr: 64.8,
  investment_recommendation: 'STRONG_BUY',
  // ... consistent data
};

// Mock API responses
await page.route('**/api/v1/analysis/dcf', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify(mockDCFData)
  });
});
```

## Visual Debugging

### Identifying Visual Differences

1. **View Diff Images**: Test failures generate side-by-side comparisons
2. **HTML Reports**: Interactive diff viewer with zoom and overlay features
3. **Threshold Tuning**: Adjust sensitivity for different components

### Common Visual Issues

#### Chart Rendering Problems
```typescript
// Wait for charts to fully stabilize
await page.waitForFunction(() => {
  const charts = document.querySelectorAll('.recharts-wrapper svg');
  return Array.from(charts).every(chart => {
    const rect = chart.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  });
}, { timeout: 10000 });
```

#### Font Rendering Inconsistencies
```typescript
// Force consistent font rendering
await page.addStyleTag({
  content: `
    * {
      font-family: Arial, sans-serif !important;
      -webkit-font-smoothing: antialiased !important;
      -moz-osx-font-smoothing: grayscale !important;
    }
  `
});
```

#### Dynamic Content Issues
```typescript
// Mask timestamps and IDs that change
await page.addStyleTag({
  content: `
    [data-testid*="timestamp"], 
    [data-testid*="id"] {
      background: #f0f0f0 !important;
      color: transparent !important;
    }
  `
});
```

## Best Practices

### Screenshot Consistency

1. **Disable Animations**: Prevent timing-related differences
2. **Use Fixed Data**: Consistent mock data for reproducible results
3. **Wait for Stability**: Allow charts and components to fully render
4. **Mask Dynamic Elements**: Hide timestamps, IDs, and changing content

### Test Organization

```typescript
test.describe('Visual Tests - Dashboard Components', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockData(page);
    await setupPageForVisualTest(page);
  });

  test('financial metrics display', async ({ page }) => {
    // Test implementation
  });
});
```

### Baseline Management

1. **Initial Baselines**: Generate comprehensive baseline set
2. **Selective Updates**: Update only changed components
3. **Review Process**: Manual review of baseline changes
4. **Version Control**: Commit baseline images to repository

## CI/CD Integration

### GitHub Actions Setup

```yaml
name: Visual Regression Tests
on: [push, pull_request]

jobs:
  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 # Needed for baseline comparison
          
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium
        
      - name: Run visual tests
        run: npm run test:visual
        
      - name: Upload visual diff report
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: visual-diff-report
          path: visual-test-results/
```

### Baseline Management in CI

```bash
# Update baselines on main branch
if [ "$GITHUB_REF" = "refs/heads/main" ]; then
  npm run test:visual:update
  git add -A
  git commit -m "Update visual baselines [skip ci]"
  git push
fi
```

## Monitoring & Alerts

### Visual Regression Detection

The test suite automatically detects:
- **Layout Shifts**: Changes in component positioning
- **Color Changes**: Brand color or theme inconsistencies  
- **Typography Changes**: Font, size, or spacing modifications
- **Chart Differences**: Data visualization accuracy issues

### Reporting

Visual tests generate:
- **HTML Reports**: Interactive diff viewer with side-by-side comparisons
- **JSON Reports**: Machine-readable results for automation
- **Diff Images**: Highlighted difference overlays
- **Trend Analysis**: Track visual stability over time

### Integration with Monitoring

```typescript
// Custom reporter for visual regression alerts
class VisualRegressionReporter {
  onTestEnd(test, result) {
    if (result.status === 'failed' && test.title.includes('visual')) {
      this.sendVisualRegressionAlert({
        component: this.extractComponent(test.title),
        threshold: test.expectedScreenshot?.threshold,
        actualDiff: result.attachments?.find(a => a.name.includes('diff')),
      });
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Flaky Screenshots**:
   - Increase stabilization delays
   - Disable animations more thoroughly
   - Use consistent mock data

2. **Font Rendering Differences**:
   - Standardize font loading
   - Use system fonts for consistency
   - Test across different OS environments

3. **Chart Timing Issues**:
   - Wait for chart libraries to fully render
   - Use deterministic data sets
   - Add chart-specific waiting logic

4. **Responsive Layout Problems**:
   - Test all target viewport sizes
   - Account for scrollbar differences
   - Verify layout stability

### Debug Commands

```bash
# Run single test with debugging
npx playwright test visual-regression.test.ts -g "DCF dashboard" --debug

# Generate new baselines for specific test
npx playwright test visual-regression.test.ts -g "financial metrics" --update-snapshots

# Run with verbose output
npx playwright test --config=playwright-visual.config.ts --reporter=list --verbose
```

## Performance Considerations

### Optimization Strategies

1. **Selective Testing**: Focus on critical visual components
2. **Parallel Execution**: Balance speed vs. consistency
3. **Incremental Updates**: Only update changed baselines
4. **Smart Scheduling**: Run visual tests on key changes

### Resource Usage

- **Screenshot Storage**: ~2-5MB per full-page screenshot
- **Test Duration**: ~30-60 seconds per visual test
- **CI Resources**: Moderate CPU, high storage for artifacts

## Contributing

When adding new visual tests:

1. **Follow Naming Conventions**: Descriptive test and screenshot names
2. **Use Consistent Setup**: Leverage existing utilities
3. **Document Expectations**: Describe what visual aspects are tested
4. **Test Multiple Viewports**: Ensure responsive compatibility
5. **Review Baselines**: Manually verify initial screenshots

## References

- [Playwright Visual Comparisons](https://playwright.dev/docs/test-screenshots)
- [Visual Testing Best Practices](https://playwright.dev/docs/best-practices)
- [Chart Testing Strategies](../performance/README.md)
- [CI/CD Integration Guide](../e2e/README.md)