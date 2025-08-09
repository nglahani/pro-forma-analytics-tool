# End-to-End Testing Suite

Comprehensive end-to-end testing for the Pro-Forma Analytics Tool using Playwright.

## Overview

This E2E testing suite validates complete user workflows from browser interaction through final results. It tests the entire application stack including frontend UI, API integration, and data processing workflows.

## Test Coverage

### Core DCF Analysis Workflow
- **Property Template Selection**: Verify template loading and selection
- **Multi-Step Property Input**: Complete form validation and navigation  
- **Address Validation**: Real-time MSA detection and address completion
- **Market Data Integration**: Automatic market defaults application
- **DCF Analysis Execution**: Complete calculation workflow
- **Results Display**: Financial metrics, cash flow projections, recommendations
- **Export Functionality**: PDF and Excel export validation
- **Monte Carlo Integration**: Risk analysis workflow

### Error Handling & Edge Cases
- **API Error Recovery**: Graceful handling of backend failures
- **Form Validation**: Input validation and error messaging
- **Network Conditions**: Slow network and timeout scenarios
- **Browser State**: Page refresh and state persistence
- **Concurrent Users**: Multi-user scenario testing

### Accessibility & Usability
- **Keyboard Navigation**: Complete keyboard workflow support
- **Screen Readers**: ARIA compliance and screen reader compatibility
- **Mobile Responsiveness**: Mobile device testing
- **Performance**: End-to-end workflow timing validation

## Test Structure

```
src/tests/e2e/
├── dcf-workflow.test.ts     # Main DCF analysis workflow tests
├── global-setup.ts          # Environment setup and warmup
├── global-teardown.ts       # Cleanup and reporting
├── fixtures/                # Test data and helper utilities
├── page-objects/           # Page Object Model classes
└── README.md               # This file
```

## Running E2E Tests

### Prerequisites

1. **Install Playwright**:
   ```bash
   npm install
   npx playwright install
   ```

2. **Start Development Server**:
   ```bash
   npm run dev
   ```

3. **Start Backend API** (optional - tests use mocks by default):
   ```bash
   # In backend directory
   python -m uvicorn src.presentation.api.main:app --reload
   ```

### Basic Test Execution

```bash
# Run all E2E tests
npm run test:e2e

# Run with UI mode (visual test runner)
npm run test:e2e:ui

# Run in debug mode (step-through debugging)
npm run test:e2e:debug

# Run in headed mode (visible browser)
npm run test:e2e:headed
```

### Browser-Specific Testing

```bash
# Chrome only
npm run test:e2e:chrome

# Firefox only  
npm run test:e2e:firefox

# Safari only (macOS)
npm run test:e2e:safari

# Mobile Chrome
npm run test:e2e:mobile
```

### Test Reports

```bash
# View test results report
npm run test:e2e:report

# Generate and open HTML report
npx playwright show-report
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `E2E_BASE_URL` | http://localhost:3000 | Frontend application URL |
| `E2E_API_URL` | http://localhost:8000 | Backend API URL |
| `E2E_HEADLESS` | true | Run browsers in headless mode |
| `E2E_SLOW_MO` | 0 | Slow motion delay (ms) for debugging |
| `E2E_TIMEOUT` | 60000 | Global test timeout (ms) |

### Custom Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'https://staging.proforma-app.com',
    headless: false,
    slowMo: 500, // 500ms delay between actions
  },
  retries: 2, // Retry failed tests twice
  workers: 1, // Run tests serially
});
```

## Test Development

### Writing New Tests

1. **Follow the Page Object Pattern**:
   ```typescript
   // page-objects/PropertyInputPage.ts
   export class PropertyInputPage {
     constructor(private page: Page) {}
     
     async fillPropertyName(name: string) {
       await this.page.fill('[data-testid="property-name"]', name);
     }
     
     async proceedToNextStep() {
       await this.page.click('[data-testid="next-step"]');
     }
   }
   ```

2. **Use Test Steps for Clarity**:
   ```typescript
   test('should complete DCF analysis', async ({ page }) => {
     await test.step('Fill property information', async () => {
       // Test implementation
     });
     
     await test.step('Wait for analysis completion', async () => {
       // Test implementation  
     });
   });
   ```

3. **Use Data-Testid Selectors**:
   ```typescript
   // Preferred
   await page.click('[data-testid="submit-button"]');
   
   // Avoid
   await page.click('button.submit-btn');
   ```

### Test Data Management

```typescript
// fixtures/test-data.ts
export const TEST_PROPERTIES = {
  BASIC_MULTIFAMILY: {
    name: 'Test Multifamily Property',
    address: {
      street: '123 Test Street',
      city: 'New York',
      state: 'NY',
      zipCode: '10001',
    },
    // ... more data
  },
};
```

### Assertions Best Practices

```typescript
// Wait for elements to be ready
await expect(page.locator('[data-testid="results"]')).toBeVisible();

// Verify text content
await expect(page.locator('[data-testid="npv-value"]')).toContainText('$');

// Check form states
await expect(page.locator('[data-testid="submit-btn"]')).toBeEnabled();

// Validate data ranges
const npvText = await page.locator('[data-testid="npv"]').textContent();
expect(npvText).toMatch(/\$[\d,]+/);
```

## Debugging Tests

### Visual Debugging

1. **Run with UI Mode**:
   ```bash
   npm run test:e2e:ui
   ```
   - Interactive test runner with timeline
   - Step-through debugging
   - Real-time DOM inspection

2. **Run in Headed Mode**:
   ```bash
   npm run test:e2e:headed
   ```
   - Visible browser windows
   - Watch tests execute in real-time

### Debug Mode

```bash
# Step-through debugging
npm run test:e2e:debug

# Debug specific test
npx playwright test dcf-workflow.test.ts --debug
```

### Screenshots and Videos

```typescript
// Take screenshot on failure (automatic)
test('my test', async ({ page }) => {
  // Test will automatically capture screenshot on failure
});

// Manual screenshot
await page.screenshot({ path: 'debug-screenshot.png' });

// Record video (configured in playwright.config.ts)
video: process.env.CI ? 'retain-on-failure' : 'off'
```

### Trace Viewer

```bash
# View detailed execution trace
npx playwright show-trace test-results/trace.zip
```

## Performance Testing

### Workflow Performance

```typescript
test('should complete analysis within performance benchmark', async ({ page }) => {
  const startTime = Date.now();
  
  // Complete workflow
  await completeFullWorkflow(page);
  
  const endTime = Date.now();
  const duration = endTime - startTime;
  
  // Should complete within 30 seconds
  expect(duration).toBeLessThan(30000);
});
```

### Network Performance

```typescript
test('should handle slow network conditions', async ({ page }) => {
  // Simulate slow network
  await page.route('**/api/**', route => {
    setTimeout(() => route.continue(), 5000); // 5s delay
  });
  
  // Test should still complete successfully
  await completeWorkflow(page);
});
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
        
      - name: Run E2E tests
        run: npm run test:e2e
        env:
          E2E_BASE_URL: http://localhost:3000
          
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

### Docker Integration

```dockerfile
# Dockerfile.e2e
FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

CMD ["npm", "run", "test:e2e"]
```

## Monitoring & Reporting

### Test Results

E2E tests generate comprehensive reports:

- **HTML Report**: Visual test results with screenshots/videos
- **JUnit XML**: CI/CD integration format
- **JSON Report**: Machine-readable results for custom processing
- **Trace Files**: Detailed execution traces for debugging

### Performance Metrics

Tests track key performance indicators:

- **Workflow Completion Time**: End-to-end timing
- **API Response Times**: Backend performance validation
- **Page Load Performance**: Frontend loading metrics
- **Resource Usage**: Memory and CPU utilization

### Alert Integration

```typescript
// Custom reporter for alerts
class AlertReporter {
  onTestEnd(test, result) {
    if (result.status === 'failed') {
      // Send alert to monitoring system
      this.sendAlert({
        test: test.title,
        error: result.error,
        duration: result.duration,
      });
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Test Timeouts**:
   ```typescript
   // Increase timeout for slow operations
   test.setTimeout(120000); // 2 minutes
   
   // Wait for specific conditions
   await page.waitForLoadState('networkidle');
   ```

2. **Element Not Found**:
   ```typescript
   // Wait for element to be ready
   await page.waitForSelector('[data-testid="element"]');
   
   // Use more specific selectors
   await page.locator('[data-testid="submit"] >> visible').click();
   ```

3. **Flaky Tests**:
   ```typescript
   // Add proper waits
   await expect(page.locator('[data-testid="result"]')).toBeVisible();
   
   // Use retry logic for unstable operations
   await expect(async () => {
     await page.click('[data-testid="button"]');
     await expect(page.locator('[data-testid="success"]')).toBeVisible();
   }).toPass({ timeout: 10000 });
   ```

### Log Analysis

```bash
# View detailed test logs
DEBUG=pw:api npm run test:e2e

# Browser console logs
await page.on('console', msg => console.log(msg.text()));
```

## Best Practices

### Test Organization

1. **Group Related Tests**: Use `describe` blocks for logical grouping
2. **Independent Tests**: Each test should be able to run in isolation
3. **Clear Test Names**: Describe what the test validates
4. **Test Data**: Use consistent, realistic test data

### Maintainability

1. **Page Objects**: Encapsulate page interactions
2. **Reusable Fixtures**: Create common test utilities
3. **Environment Variables**: Make tests configurable
4. **Regular Updates**: Keep tests synchronized with UI changes

### Performance

1. **Parallel Execution**: Use multiple workers when possible
2. **Test Isolation**: Minimize setup/teardown overhead
3. **Selective Running**: Run relevant tests for changes
4. **Resource Management**: Clean up after tests

## Contributing

When adding new E2E tests:

1. Follow existing patterns and naming conventions
2. Add appropriate test data to fixtures
3. Update this README with new test categories
4. Ensure tests work across all supported browsers
5. Add proper error handling and assertions

## References

- [Playwright Documentation](https://playwright.dev/)
- [Page Object Model Pattern](https://playwright.dev/docs/pom)
- [Best Practices Guide](https://playwright.dev/docs/best-practices)
- [CI/CD Integration](https://playwright.dev/docs/ci)