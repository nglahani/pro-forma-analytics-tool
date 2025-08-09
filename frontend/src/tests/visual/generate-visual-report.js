#!/usr/bin/env node

/**
 * Visual Regression Test Report Generator
 * Processes visual test results and generates comprehensive reports
 */

const fs = require('fs');
const path = require('path');

const RESULTS_DIR = 'test-results';
const VISUAL_RESULTS_DIR = 'visual-test-results';
const OUTPUT_DIR = 'visual-reports';

class VisualReportGenerator {
  constructor() {
    this.results = [];
    this.summary = {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      skippedTests: 0,
      regressions: [],
    };
  }

  async generateReport() {
    console.log('📊 Generating Visual Regression Report...');
    
    try {
      // Create output directory
      this.ensureDirectoryExists(OUTPUT_DIR);
      
      // Load test results
      await this.loadTestResults();
      
      // Analyze results
      this.analyzeResults();
      
      // Generate reports
      await this.generateMarkdownReport();
      await this.generateJSONReport();
      await this.generateHTMLReport();
      
      // Copy visual artifacts
      await this.copyVisualArtifacts();
      
      console.log(`✅ Visual regression report generated in ${OUTPUT_DIR}/`);
      
    } catch (error) {
      console.error('❌ Failed to generate visual report:', error.message);
      process.exit(1);
    }
  }

  async loadTestResults() {
    const resultsFile = path.join(RESULTS_DIR, 'visual-results.json');
    
    if (!fs.existsSync(resultsFile)) {
      console.log('⚠️ No visual test results found. Running tests first...');
      return;
    }
    
    try {
      const rawResults = fs.readFileSync(resultsFile, 'utf8');
      const testResults = JSON.parse(rawResults);
      
      // Process test results
      if (testResults.suites) {
        testResults.suites.forEach(suite => {
          this.processSuite(suite);
        });
      }
      
      console.log(`📋 Loaded ${this.results.length} visual test results`);
      
    } catch (error) {
      console.error('Failed to load test results:', error.message);
    }
  }

  processSuite(suite) {
    if (suite.specs) {
      suite.specs.forEach(spec => {
        if (spec.tests) {
          spec.tests.forEach(test => {
            const testResult = {
              suiteName: suite.title,
              testName: test.title,
              fullName: `${suite.title} - ${test.title}`,
              status: test.status,
              duration: test.duration || 0,
              errors: test.errors || [],
              attachments: test.attachments || [],
              isVisualTest: this.isVisualTest(test.title),
            };
            
            this.results.push(testResult);
            this.updateSummary(testResult);
          });
        }
      });
    }
  }

  isVisualTest(testTitle) {
    return testTitle.toLowerCase().includes('visual') || 
           testTitle.toLowerCase().includes('screenshot') ||
           testTitle.toLowerCase().includes('regression');
  }

  updateSummary(testResult) {
    this.summary.totalTests++;
    
    switch (testResult.status) {
      case 'passed':
        this.summary.passedTests++;
        break;
      case 'failed':
        this.summary.failedTests++;
        if (testResult.isVisualTest) {
          this.summary.regressions.push(testResult);
        }
        break;
      case 'skipped':
        this.summary.skippedTests++;
        break;
    }
  }

  analyzeResults() {
    console.log('🔍 Analyzing visual test results...');
    
    // Categorize visual tests
    const visualTests = this.results.filter(r => r.isVisualTest);
    const componentTests = this.categorizeByComponent(visualTests);
    const viewportTests = this.categorizeByViewport(visualTests);
    
    this.summary.visualTests = {
      total: visualTests.length,
      byComponent: componentTests,
      byViewport: viewportTests,
      regressionRate: (this.summary.regressions.length / visualTests.length * 100).toFixed(1),
    };
    
    console.log(`   Visual tests: ${visualTests.length}`);
    console.log(`   Regressions: ${this.summary.regressions.length}`);
    console.log(`   Regression rate: ${this.summary.visualTests.regressionRate}%`);
  }

  categorizeByComponent(tests) {
    const components = {};
    
    tests.forEach(test => {
      const component = this.extractComponent(test.testName);
      if (!components[component]) {
        components[component] = { total: 0, passed: 0, failed: 0 };
      }
      
      components[component].total++;
      if (test.status === 'passed') {
        components[component].passed++;
      } else if (test.status === 'failed') {
        components[component].failed++;
      }
    });
    
    return components;
  }

  categorizeByViewport(tests) {
    const viewports = {};
    
    tests.forEach(test => {
      const viewport = this.extractViewport(test.testName);
      if (!viewports[viewport]) {
        viewports[viewport] = { total: 0, passed: 0, failed: 0 };
      }
      
      viewports[viewport].total++;
      if (test.status === 'passed') {
        viewports[viewport].passed++;
      } else if (test.status === 'failed') {
        viewports[viewport].failed++;
      }
    });
    
    return viewports;
  }

  extractComponent(testName) {
    const lowerName = testName.toLowerCase();
    
    if (lowerName.includes('dcf')) return 'DCF Dashboard';
    if (lowerName.includes('monte carlo')) return 'Monte Carlo';
    if (lowerName.includes('market')) return 'Market Data';
    if (lowerName.includes('form')) return 'Property Form';
    if (lowerName.includes('chart')) return 'Charts';
    if (lowerName.includes('metrics')) return 'Financial Metrics';
    
    return 'Other';
  }

  extractViewport(testName) {
    const lowerName = testName.toLowerCase();
    
    if (lowerName.includes('mobile')) return 'Mobile';
    if (lowerName.includes('tablet')) return 'Tablet';
    if (lowerName.includes('desktop-xl')) return 'Desktop XL';
    if (lowerName.includes('desktop')) return 'Desktop';
    if (lowerName.includes('dark')) return 'Dark Mode';
    
    return 'Default';
  }

  async generateMarkdownReport() {
    console.log('📄 Generating Markdown report...');
    
    const report = this.buildMarkdownReport();
    const reportPath = path.join(OUTPUT_DIR, 'visual-regression-report.md');
    
    fs.writeFileSync(reportPath, report);
    console.log(`   Saved: ${reportPath}`);
  }

  buildMarkdownReport() {
    const passRate = (this.summary.passedTests / this.summary.totalTests * 100).toFixed(1);
    const timestamp = new Date().toISOString();
    
    const lines = [
      '# Visual Regression Testing Report',
      '',
      `**Generated**: ${timestamp}`,
      `**Environment**: ${process.env.NODE_ENV || 'development'}`,
      '',
      '## Executive Summary',
      '',
      `- **Total Tests**: ${this.summary.totalTests}`,
      `- **Passed**: ${this.summary.passedTests} (${passRate}%)`,
      `- **Failed**: ${this.summary.failedTests}`,
      `- **Skipped**: ${this.summary.skippedTests}`,
      '',
      `**Visual Regression Rate**: ${this.summary.visualTests?.regressionRate || 0}%`,
      '',
      '## Test Results by Component',
      '',
      '| Component | Total | Passed | Failed | Success Rate |',
      '|-----------|-------|--------|--------|--------------|',
    ];
    
    if (this.summary.visualTests?.byComponent) {
      Object.entries(this.summary.visualTests.byComponent).forEach(([component, stats]) => {
        const successRate = ((stats.passed / stats.total) * 100).toFixed(1);
        const status = stats.failed > 0 ? '❌' : '✅';
        lines.push(`| ${component} | ${stats.total} | ${stats.passed} | ${stats.failed} | ${status} ${successRate}% |`);
      });
    }
    
    lines.push('', '## Test Results by Viewport', '');
    lines.push('| Viewport | Total | Passed | Failed | Success Rate |');
    lines.push('|----------|-------|--------|--------|--------------|');
    
    if (this.summary.visualTests?.byViewport) {
      Object.entries(this.summary.visualTests.byViewport).forEach(([viewport, stats]) => {
        const successRate = ((stats.passed / stats.total) * 100).toFixed(1);
        const status = stats.failed > 0 ? '❌' : '✅';
        lines.push(`| ${viewport} | ${stats.total} | ${stats.passed} | ${stats.failed} | ${status} ${successRate}% |`);
      });
    }
    
    // Visual regressions section
    if (this.summary.regressions.length > 0) {
      lines.push('', '## Visual Regressions Detected', '');
      
      this.summary.regressions.forEach((regression, index) => {
        lines.push(`### ${index + 1}. ${regression.testName}`);
        lines.push(`**Suite**: ${regression.suiteName}`);
        lines.push(`**Status**: ❌ FAILED`);
        lines.push(`**Duration**: ${regression.duration}ms`);
        
        if (regression.errors.length > 0) {
          lines.push('**Error Details**:');
          regression.errors.forEach(error => {
            lines.push(`- ${error.message || error}`);
          });
        }
        
        if (regression.attachments.length > 0) {
          lines.push('**Visual Artifacts**:');
          regression.attachments.forEach(attachment => {
            if (attachment.name.includes('screenshot') || attachment.name.includes('diff')) {
              lines.push(`- [${attachment.name}](${attachment.path || attachment.name})`);
            }
          });
        }
        
        lines.push('');
      });
    } else {
      lines.push('', '## ✅ No Visual Regressions Detected', '');
      lines.push('All visual tests passed successfully. No visual changes detected.');
    }
    
    // Recommendations
    lines.push('', '## Recommendations', '');
    
    if (this.summary.regressions.length === 0) {
      lines.push('- Continue with current development practices');
      lines.push('- Consider expanding visual test coverage to new components');
      lines.push('- Review baseline images periodically for outdated references');
    } else {
      lines.push('**Action Required**: Visual regressions detected that need investigation:');
      lines.push('');
      lines.push('1. **Review Diff Images**: Examine the visual differences carefully');
      lines.push('2. **Determine Intent**: Are changes intentional (new features) or bugs?');
      lines.push('3. **Update Baselines**: If changes are intentional, update reference images');
      lines.push('4. **Fix Bugs**: If changes are unintended, investigate and fix the root cause');
      lines.push('5. **Re-run Tests**: Verify fixes resolve the visual regressions');
    }
    
    return lines.join('\n');
  }

  async generateJSONReport() {
    console.log('📋 Generating JSON report...');
    
    const jsonReport = {
      timestamp: new Date().toISOString(),
      summary: this.summary,
      results: this.results,
      metadata: {
        generator: 'visual-regression-reporter',
        version: '1.0.0',
        environment: process.env.NODE_ENV || 'development',
      },
    };
    
    const reportPath = path.join(OUTPUT_DIR, 'visual-regression-data.json');
    fs.writeFileSync(reportPath, JSON.stringify(jsonReport, null, 2));
    console.log(`   Saved: ${reportPath}`);
  }

  async generateHTMLReport() {
    console.log('🌐 Generating HTML report...');
    
    const htmlContent = this.buildHTMLReport();
    const reportPath = path.join(OUTPUT_DIR, 'visual-regression-report.html');
    
    fs.writeFileSync(reportPath, htmlContent);
    console.log(`   Saved: ${reportPath}`);
  }

  buildHTMLReport() {
    const passRate = (this.summary.passedTests / this.summary.totalTests * 100).toFixed(1);
    const regressionRate = this.summary.visualTests?.regressionRate || 0;
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Regression Test Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8fafc; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .content { padding: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric { background: #f7fafc; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #4299e1; }
        .metric.success { border-left-color: #48bb78; }
        .metric.warning { border-left-color: #ed8936; }
        .metric.error { border-left-color: #e53e3e; }
        .metric-value { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .metric-label { color: #718096; font-size: 0.9em; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #2d3748; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #f7fafc; font-weight: 600; }
        .status-pass { color: #48bb78; }
        .status-fail { color: #e53e3e; }
        .status-skip { color: #ed8936; }
        .regression { background: #fed7d7; border-left: 4px solid #e53e3e; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .no-regressions { background: #c6f6d5; border-left: 4px solid #48bb78; padding: 15px; margin: 10px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Visual Regression Test Report</h1>
            <p>Generated: ${new Date().toLocaleString()}</p>
        </div>
        
        <div class="content">
            <div class="summary">
                <div class="metric ${passRate >= 90 ? 'success' : passRate >= 70 ? 'warning' : 'error'}">
                    <div class="metric-value">${passRate}%</div>
                    <div class="metric-label">Pass Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${this.summary.totalTests}</div>
                    <div class="metric-label">Total Tests</div>
                </div>
                <div class="metric success">
                    <div class="metric-value">${this.summary.passedTests}</div>
                    <div class="metric-label">Passed</div>
                </div>
                <div class="metric error">
                    <div class="metric-value">${this.summary.failedTests}</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric ${regressionRate === '0.0' ? 'success' : 'error'}">
                    <div class="metric-value">${regressionRate}%</div>
                    <div class="metric-label">Regression Rate</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Component Test Results</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>Total</th>
                            <th>Passed</th>
                            <th>Failed</th>
                            <th>Success Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.generateComponentRows()}
                    </tbody>
                </table>
            </div>
            
            ${this.generateRegressionsSection()}
        </div>
    </div>
</body>
</html>
    `;
  }

  generateComponentRows() {
    if (!this.summary.visualTests?.byComponent) return '<tr><td colspan="5">No component data available</td></tr>';
    
    return Object.entries(this.summary.visualTests.byComponent)
      .map(([component, stats]) => {
        const successRate = ((stats.passed / stats.total) * 100).toFixed(1);
        const statusClass = stats.failed > 0 ? 'status-fail' : 'status-pass';
        
        return `
          <tr>
            <td>${component}</td>
            <td>${stats.total}</td>
            <td class="status-pass">${stats.passed}</td>
            <td class="status-fail">${stats.failed}</td>
            <td class="${statusClass}">${successRate}%</td>
          </tr>
        `;
      }).join('');
  }

  generateRegressionsSection() {
    if (this.summary.regressions.length === 0) {
      return `
        <div class="section">
          <h2>Visual Regressions</h2>
          <div class="no-regressions">
            ✅ No visual regressions detected. All tests passed successfully!
          </div>
        </div>
      `;
    }
    
    const regressionItems = this.summary.regressions
      .map(regression => `
        <div class="regression">
          <strong>${regression.testName}</strong><br>
          <small>Suite: ${regression.suiteName} | Duration: ${regression.duration}ms</small>
        </div>
      `).join('');
    
    return `
      <div class="section">
        <h2>Visual Regressions (${this.summary.regressions.length})</h2>
        ${regressionItems}
      </div>
    `;
  }

  async copyVisualArtifacts() {
    console.log('📁 Copying visual artifacts...');
    
    const visualDir = path.join(RESULTS_DIR, 'visual-artifacts');
    const targetDir = path.join(OUTPUT_DIR, 'artifacts');
    
    if (fs.existsSync(visualDir)) {
      this.ensureDirectoryExists(targetDir);
      this.copyDirectory(visualDir, targetDir);
      console.log(`   Copied visual artifacts to ${targetDir}`);
    }
    
    // Also copy HTML report if it exists
    const htmlReportPath = path.join(VISUAL_RESULTS_DIR, 'index.html');
    if (fs.existsSync(htmlReportPath)) {
      const targetHtmlPath = path.join(OUTPUT_DIR, 'playwright-report.html');
      fs.copyFileSync(htmlReportPath, targetHtmlPath);
      console.log(`   Copied Playwright HTML report to ${targetHtmlPath}`);
    }
  }

  ensureDirectoryExists(dir) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  copyDirectory(source, target) {
    if (!fs.existsSync(target)) {
      fs.mkdirSync(target, { recursive: true });
    }
    
    const files = fs.readdirSync(source);
    files.forEach(file => {
      const sourcePath = path.join(source, file);
      const targetPath = path.join(target, file);
      
      if (fs.statSync(sourcePath).isDirectory()) {
        this.copyDirectory(sourcePath, targetPath);
      } else {
        fs.copyFileSync(sourcePath, targetPath);
      }
    });
  }
}

// Run the report generator
if (require.main === module) {
  const generator = new VisualReportGenerator();
  generator.generateReport()
    .then(() => {
      console.log('🎉 Visual regression report generation complete!');
      process.exit(0);
    })
    .catch(error => {
      console.error('💥 Report generation failed:', error);
      process.exit(1);
    });
}

module.exports = VisualReportGenerator;