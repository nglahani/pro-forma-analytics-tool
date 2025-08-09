/**
 * Custom Load Test Reporter
 * Generates comprehensive load testing reports with performance metrics
 */

const fs = require('fs');
const path = require('path');

class LoadTestReporter {
  constructor(globalConfig, options) {
    this._globalConfig = globalConfig;
    this._options = options || {};
    this.outputPath = this._options.outputPath || './load-reports';
    this.results = [];
    this.startTime = null;
    this.performanceMetrics = {
      concurrentUsers: 0,
      totalOperations: 0,
      successfulOperations: 0,
      failedOperations: 0,
      averageResponseTime: 0,
      throughput: 0,
      memoryUsage: [],
      errorsByType: {},
    };
  }

  onRunStart() {
    this.startTime = Date.now();
    console.log('🚀 Load Testing Started');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    if (!fs.existsSync(this.outputPath)) {
      fs.mkdirSync(this.outputPath, { recursive: true });
    }
  }

  onTestResult(test, testResult) {
    const testFile = path.relative(process.cwd(), test.path);
    
    testResult.testResults.forEach(result => {
      const testData = {
        testFile,
        testName: result.fullName,
        status: result.status,
        duration: result.duration || 0,
        errors: result.failureMessages || [],
        timestamp: Date.now(),
        isLoadTest: this.isLoadTest(result.title),
      };
      
      this.results.push(testData);
      this.updatePerformanceMetrics(testData);
      
      // Real-time console output
      const statusIcon = result.status === 'passed' ? '✅' : result.status === 'failed' ? '❌' : '⚠️';
      const duration = result.duration ? `${result.duration}ms` : 'N/A';
      
      if (testData.isLoadTest) {
        console.log(`${statusIcon} ${result.title.substring(0, 60)}... ${duration}`);
        
        if (result.status === 'failed' && result.failureMessages?.length > 0) {
          console.log(`   Error: ${result.failureMessages[0].split('\n')[0]}`);
        }
      }
    });
  }

  onRunComplete(contexts, results) {
    const endTime = Date.now();
    const totalDuration = endTime - this.startTime;
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 Load Testing Summary');
    console.log(`Total Duration: ${Math.round(totalDuration / 1000)}s`);
    console.log(`Tests Run: ${results.numTotalTests}`);
    console.log(`Passed: ${results.numPassedTests}`);
    console.log(`Failed: ${results.numFailedTests}`);
    
    // Finalize performance metrics
    this.finalizeMetrics(totalDuration);
    
    // Generate reports
    this.generateLoadTestReport(results, totalDuration);
    this.generatePerformanceReport();
    this.generateMetricsReport();
    
    console.log(`📄 Load test reports generated in ${this.outputPath}/`);
    console.log('✅ Load Testing Completed');
  }

  isLoadTest(testTitle) {
    const loadTestKeywords = [
      'concurrent', 'load', 'stress', 'memory', 'performance', 
      'throughput', 'scalability', 'users', 'database'
    ];
    
    return loadTestKeywords.some(keyword => 
      testTitle.toLowerCase().includes(keyword)
    );
  }

  updatePerformanceMetrics(testData) {
    if (!testData.isLoadTest) return;

    this.performanceMetrics.totalOperations++;
    
    if (testData.status === 'passed') {
      this.performanceMetrics.successfulOperations++;
    } else {
      this.performanceMetrics.failedOperations++;
      
      // Categorize errors
      if (testData.errors.length > 0) {
        const errorType = this.categorizeError(testData.errors[0]);
        this.performanceMetrics.errorsByType[errorType] = 
          (this.performanceMetrics.errorsByType[errorType] || 0) + 1;
      }
    }
    
    // Extract concurrent user count from test name
    const userMatch = testData.testName.match(/(\d+).*users?/i);
    if (userMatch) {
      this.performanceMetrics.concurrentUsers = Math.max(
        this.performanceMetrics.concurrentUsers,
        parseInt(userMatch[1])
      );
    }
    
    // Update average response time
    if (testData.duration > 0) {
      const currentAvg = this.performanceMetrics.averageResponseTime;
      const count = this.performanceMetrics.successfulOperations;
      this.performanceMetrics.averageResponseTime = 
        (currentAvg * (count - 1) + testData.duration) / count;
    }
  }

  categorizeError(errorMessage) {
    const lowerError = errorMessage.toLowerCase();
    
    if (lowerError.includes('timeout')) return 'Timeout';
    if (lowerError.includes('memory')) return 'Memory';
    if (lowerError.includes('connection')) return 'Connection';
    if (lowerError.includes('network')) return 'Network';
    if (lowerError.includes('database')) return 'Database';
    if (lowerError.includes('assertion')) return 'Assertion';
    
    return 'Other';
  }

  finalizeMetrics(totalDuration) {
    // Calculate throughput (operations per second)
    this.performanceMetrics.throughput = 
      (this.performanceMetrics.totalOperations / totalDuration) * 1000;
    
    // Calculate success rate
    this.performanceMetrics.successRate = 
      (this.performanceMetrics.successfulOperations / this.performanceMetrics.totalOperations) * 100;
  }

  generateLoadTestReport(jestResults, totalDuration) {
    const loadTests = this.results.filter(r => r.isLoadTest);
    
    const reportLines = [
      '# Load Testing Report',
      '',
      `**Generated**: ${new Date().toISOString()}`,
      `**Duration**: ${Math.round(totalDuration / 1000)} seconds`,
      `**Environment**: ${process.env.NODE_ENV || 'test'}`,
      '',
      '## Executive Summary',
      '',
      `- **Concurrent Users Tested**: ${this.performanceMetrics.concurrentUsers}`,
      `- **Total Operations**: ${this.performanceMetrics.totalOperations}`,
      `- **Success Rate**: ${this.performanceMetrics.successRate.toFixed(1)}%`,
      `- **Average Response Time**: ${Math.round(this.performanceMetrics.averageResponseTime)}ms`,
      `- **Throughput**: ${this.performanceMetrics.throughput.toFixed(2)} ops/sec`,
      '',
    ];
    
    // Performance benchmarks
    const benchmarks = {
      successRate: 95, // 95% minimum
      responseTime: 5000, // 5 seconds max
      throughput: 1, // 1 ops/sec minimum
    };
    
    reportLines.push('## Performance Analysis', '');
    
    const successRateStatus = this.performanceMetrics.successRate >= benchmarks.successRate ? '✅ PASS' : '❌ FAIL';
    const responseTimeStatus = this.performanceMetrics.averageResponseTime <= benchmarks.responseTime ? '✅ PASS' : '❌ FAIL';
    const throughputStatus = this.performanceMetrics.throughput >= benchmarks.throughput ? '✅ PASS' : '❌ FAIL';
    
    reportLines.push(
      '| Metric | Target | Actual | Status |',
      '|--------|---------|---------|---------|',
      `| Success Rate | ≥${benchmarks.successRate}% | ${this.performanceMetrics.successRate.toFixed(1)}% | ${successRateStatus} |`,
      `| Avg Response Time | ≤${benchmarks.responseTime}ms | ${Math.round(this.performanceMetrics.averageResponseTime)}ms | ${responseTimeStatus} |`,
      `| Throughput | ≥${benchmarks.throughput} ops/s | ${this.performanceMetrics.throughput.toFixed(2)} ops/s | ${throughputStatus} |`,
      ''
    );
    
    // Test results breakdown
    reportLines.push('## Test Results Breakdown', '');
    reportLines.push('| Test | Status | Duration | Users |');
    reportLines.push('|------|--------|----------|-------|');
    
    loadTests.forEach(test => {
      const status = test.status === 'passed' ? '✅ PASS' : test.status === 'failed' ? '❌ FAIL' : '⚠️ SKIP';
      const duration = `${test.duration}ms`;
      const userMatch = test.testName.match(/(\d+).*users?/i);
      const users = userMatch ? userMatch[1] : 'N/A';
      
      reportLines.push(`| ${test.testName.substring(0, 40)}... | ${status} | ${duration} | ${users} |`);
    });
    
    // Error analysis
    if (Object.keys(this.performanceMetrics.errorsByType).length > 0) {
      reportLines.push('', '## Error Analysis', '');
      reportLines.push('| Error Type | Count | Percentage |');
      reportLines.push('|------------|-------|------------|');
      
      Object.entries(this.performanceMetrics.errorsByType).forEach(([type, count]) => {
        const percentage = ((count / this.performanceMetrics.failedOperations) * 100).toFixed(1);
        reportLines.push(`| ${type} | ${count} | ${percentage}% |`);
      });
    }
    
    // Recommendations
    reportLines.push('', '## Recommendations', '');
    
    if (this.performanceMetrics.successRate >= 95 && 
        this.performanceMetrics.averageResponseTime <= 5000 &&
        this.performanceMetrics.throughput >= 1) {
      reportLines.push('✅ **System Performance: EXCELLENT**');
      reportLines.push('- All performance benchmarks met');
      reportLines.push('- System ready for production load');
      reportLines.push('- Consider testing with higher concurrent user counts');
    } else {
      reportLines.push('⚠️ **System Performance: NEEDS ATTENTION**');
      
      if (this.performanceMetrics.successRate < 95) {
        reportLines.push(`- **Success Rate Issue**: ${this.performanceMetrics.successRate.toFixed(1)}% < 95% target`);
        reportLines.push('  - Review error logs for common failure patterns');
        reportLines.push('  - Implement better error handling and retry logic');
      }
      
      if (this.performanceMetrics.averageResponseTime > 5000) {
        reportLines.push(`- **Response Time Issue**: ${Math.round(this.performanceMetrics.averageResponseTime)}ms > 5000ms target`);
        reportLines.push('  - Optimize database queries and API endpoints');
        reportLines.push('  - Consider implementing caching strategies');
        reportLines.push('  - Review server resource allocation');
      }
      
      if (this.performanceMetrics.throughput < 1) {
        reportLines.push(`- **Throughput Issue**: ${this.performanceMetrics.throughput.toFixed(2)} ops/s < 1 ops/s target`);
        reportLines.push('  - Investigate bottlenecks in the request pipeline');
        reportLines.push('  - Consider horizontal scaling options');
      }
    }
    
    // Write report
    const reportPath = path.join(this.outputPath, 'load-test-report.md');
    fs.writeFileSync(reportPath, reportLines.join('\n'));
    console.log(`📄 Load test report: ${reportPath}`);
  }

  generatePerformanceReport() {
    const performanceData = {
      timestamp: new Date().toISOString(),
      summary: this.performanceMetrics,
      testResults: this.results.filter(r => r.isLoadTest),
      benchmarks: {
        successRate: { target: 95, actual: this.performanceMetrics.successRate },
        responseTime: { target: 5000, actual: this.performanceMetrics.averageResponseTime },
        throughput: { target: 1, actual: this.performanceMetrics.throughput },
      },
      metadata: {
        generator: 'load-test-reporter',
        version: '1.0.0',
        environment: process.env.NODE_ENV || 'test',
      },
    };
    
    const reportPath = path.join(this.outputPath, 'performance-data.json');
    fs.writeFileSync(reportPath, JSON.stringify(performanceData, null, 2));
    console.log(`📊 Performance data: ${reportPath}`);
  }

  generateMetricsReport() {
    const metricsHtml = this.buildMetricsHTML();
    const reportPath = path.join(this.outputPath, 'load-metrics.html');
    
    fs.writeFileSync(reportPath, metricsHtml);
    console.log(`📈 Metrics dashboard: ${reportPath}`);
  }

  buildMetricsHTML() {
    const successRate = this.performanceMetrics.successRate.toFixed(1);
    const responseTime = Math.round(this.performanceMetrics.averageResponseTime);
    const throughput = this.performanceMetrics.throughput.toFixed(2);
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Load Test Metrics Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .metric-value { font-size: 3em; font-weight: bold; margin-bottom: 10px; }
        .metric-label { color: #718096; font-size: 1.1em; margin-bottom: 5px; }
        .metric-status { padding: 5px 15px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }
        .status-pass { background: #c6f6d5; color: #2f855a; }
        .status-fail { background: #fed7d7; color: #c53030; }
        .chart-container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .error-breakdown { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .error-item { background: #fed7d7; padding: 15px; border-radius: 6px; text-align: center; }
        .success { color: #48bb78; }
        .warning { color: #ed8936; }
        .error { color: #e53e3e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Load Test Metrics Dashboard</h1>
            <p>Generated: ${new Date().toLocaleString()}</p>
            <p>Concurrent Users: ${this.performanceMetrics.concurrentUsers} | Total Operations: ${this.performanceMetrics.totalOperations}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value ${successRate >= 95 ? 'success' : 'error'}">${successRate}%</div>
                <div class="metric-label">Success Rate</div>
                <div class="metric-status ${successRate >= 95 ? 'status-pass' : 'status-fail'}">
                    ${successRate >= 95 ? 'PASS' : 'FAIL'} (Target: ≥95%)
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value ${responseTime <= 5000 ? 'success' : 'error'}">${responseTime}ms</div>
                <div class="metric-label">Avg Response Time</div>
                <div class="metric-status ${responseTime <= 5000 ? 'status-pass' : 'status-fail'}">
                    ${responseTime <= 5000 ? 'PASS' : 'FAIL'} (Target: ≤5000ms)
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value ${throughput >= 1 ? 'success' : 'error'}">${throughput}</div>
                <div class="metric-label">Throughput (ops/sec)</div>
                <div class="metric-status ${throughput >= 1 ? 'status-pass' : 'status-fail'}">
                    ${throughput >= 1 ? 'PASS' : 'FAIL'} (Target: ≥1 ops/s)
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">${this.performanceMetrics.failedOperations}</div>
                <div class="metric-label">Failed Operations</div>
                <div class="metric-status ${this.performanceMetrics.failedOperations === 0 ? 'status-pass' : 'status-fail'}">
                    ${this.performanceMetrics.failedOperations === 0 ? 'No Failures' : 'Has Failures'}
                </div>
            </div>
        </div>
        
        ${this.generateErrorBreakdownHTML()}
        
        <div class="chart-container">
            <h2>Performance Summary</h2>
            <p><strong>Total Tests:</strong> ${this.results.length}</p>
            <p><strong>Load Tests:</strong> ${this.results.filter(r => r.isLoadTest).length}</p>
            <p><strong>Peak Concurrent Users:</strong> ${this.performanceMetrics.concurrentUsers}</p>
            <p><strong>Test Duration:</strong> Varies by test scenario</p>
            
            <h3>Key Findings</h3>
            ${this.generateFindingsHTML()}
        </div>
    </div>
</body>
</html>
    `;
  }

  generateErrorBreakdownHTML() {
    if (Object.keys(this.performanceMetrics.errorsByType).length === 0) {
      return '<div class="chart-container"><h2>✅ No Errors Detected</h2><p>All load tests completed successfully without errors.</p></div>';
    }
    
    const errorItems = Object.entries(this.performanceMetrics.errorsByType)
      .map(([type, count]) => `
        <div class="error-item">
          <h3>${type}</h3>
          <div style="font-size: 2em; font-weight: bold;">${count}</div>
          <div>errors</div>
        </div>
      `).join('');
    
    return `
      <div class="chart-container">
        <h2>Error Breakdown</h2>
        <div class="error-breakdown">
          ${errorItems}
        </div>
      </div>
    `;
  }

  generateFindingsHTML() {
    const findings = [];
    
    if (this.performanceMetrics.successRate >= 95) {
      findings.push('<li class="success">✅ Success rate exceeds 95% threshold</li>');
    } else {
      findings.push('<li class="error">❌ Success rate below 95% threshold</li>');
    }
    
    if (this.performanceMetrics.averageResponseTime <= 5000) {
      findings.push('<li class="success">✅ Response time within acceptable limits</li>');
    } else {
      findings.push('<li class="error">❌ Response time exceeds 5000ms threshold</li>');
    }
    
    if (this.performanceMetrics.throughput >= 1) {
      findings.push('<li class="success">✅ Throughput meets minimum requirements</li>');
    } else {
      findings.push('<li class="error">❌ Throughput below minimum threshold</li>');
    }
    
    return `<ul>${findings.join('')}</ul>`;
  }
}

module.exports = LoadTestReporter;