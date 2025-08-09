/**
 * Custom Jest Reporter for Performance Tests
 * Generates detailed performance reports and tracks benchmarks
 */

const fs = require('fs');
const path = require('path');

class PerformanceReporter {
  constructor(globalConfig, options) {
    this._globalConfig = globalConfig;
    this._options = options || {};
    this.outputPath = this._options.outputPath || './performance-results';
    this.generateReport = this._options.generateReport !== false;
    this.results = [];
    this.startTime = null;
  }

  onRunStart() {
    this.startTime = Date.now();
    console.log('🚀 Performance Benchmarking Started');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    if (!fs.existsSync(this.outputPath)) {
      fs.mkdirSync(this.outputPath, { recursive: true });
    }
  }

  onTestResult(test, testResult) {
    const testFile = path.relative(process.cwd(), test.path);
    
    testResult.testResults.forEach(result => {
      if (result.duration) {
        this.results.push({
          testFile,
          testName: result.fullName,
          duration: result.duration,
          status: result.status,
          failureMessages: result.failureMessages,
          timestamp: Date.now(),
        });
        
        // Real-time logging with status indicators
        const statusIcon = result.status === 'passed' ? '✅' : result.status === 'failed' ? '❌' : '⚠️';
        const durationFormatted = result.duration ? `${result.duration}ms` : 'N/A';
        
        console.log(`${statusIcon} ${result.title.substring(0, 50)}... ${durationFormatted}`);
      }
    });
  }

  onRunComplete(contexts, results) {
    const endTime = Date.now();
    const totalDuration = endTime - this.startTime;
    
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 Performance Test Summary');
    console.log(`Total Duration: ${totalDuration}ms`);
    console.log(`Tests Run: ${results.numTotalTests}`);
    console.log(`Passed: ${results.numPassedTests}`);
    console.log(`Failed: ${results.numFailedTests}`);
    
    if (this.generateReport) {
      this.generatePerformanceReport(results);
      this.generateBenchmarkReport();
      this.generateTrendsReport();
    }
    
    console.log('✅ Performance Benchmarking Completed');
  }

  generatePerformanceReport(jestResults) {
    // Group results by test category
    const groupedResults = this.results.reduce((acc, result) => {
      const category = this.extractTestCategory(result.testName);
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(result);
      return acc;
    }, {});

    // Performance benchmarks
    const benchmarks = {
      'DCF Analysis': 3000,
      'Monte Carlo': 10000,
      'Market Data': 2000,
      'Authentication': 500,
      'Templates': 1000,
    };

    // Generate report content
    const reportLines = [
      '# API Performance Benchmarking Report',
      '',
      `**Generated**: ${new Date().toISOString()}`,
      `**Total Tests**: ${this.results.length}`,
      `**Test Duration**: ${Date.now() - this.startTime}ms`,
      '',
      '## Executive Summary',
      '',
    ];

    let overallStatus = 'PASS';
    const summaryTable = ['| Category | Tests | Avg Duration | Benchmark | Status |', '|----------|-------|--------------|-----------|--------|'];
    
    Object.entries(groupedResults).forEach(([category, tests]) => {
      const avgDuration = tests.reduce((sum, t) => sum + (t.duration || 0), 0) / tests.length;
      const benchmark = benchmarks[category] || 5000;
      const status = avgDuration <= benchmark ? 'PASS' : 'FAIL';
      
      if (status === 'FAIL') {
        overallStatus = 'FAIL';
      }
      
      const statusIcon = status === 'PASS' ? '✅' : '❌';
      summaryTable.push(
        `| ${category} | ${tests.length} | ${avgDuration.toFixed(1)}ms | ${benchmark}ms | ${statusIcon} ${status} |`
      );
    });
    
    reportLines.push(`**Overall Status**: ${overallStatus === 'PASS' ? '✅ PASS' : '❌ FAIL'}`, '');
    reportLines.push(...summaryTable, '');

    // Detailed results by category
    reportLines.push('## Detailed Results', '');
    
    Object.entries(groupedResults).forEach(([category, tests]) => {
      reportLines.push(`### ${category}`, '');
      
      const durations = tests.map(t => t.duration || 0);
      const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
      const minDuration = Math.min(...durations);
      const maxDuration = Math.max(...durations);
      const stdDev = Math.sqrt(durations.reduce((sum, d) => sum + Math.pow(d - avgDuration, 2), 0) / durations.length);
      
      reportLines.push(
        `- **Average Duration**: ${avgDuration.toFixed(1)}ms`,
        `- **Min Duration**: ${minDuration}ms`,
        `- **Max Duration**: ${maxDuration}ms`,
        `- **Standard Deviation**: ${stdDev.toFixed(1)}ms`,
        `- **Test Count**: ${tests.length}`,
        ''
      );
      
      // Performance analysis
      const benchmark = benchmarks[category] || 5000;
      const performanceRatio = avgDuration / benchmark;
      
      if (performanceRatio <= 0.5) {
        reportLines.push('**Analysis**: 🚀 Excellent performance - significantly under benchmark');
      } else if (performanceRatio <= 0.8) {
        reportLines.push('**Analysis**: ✅ Good performance - comfortably within benchmark');
      } else if (performanceRatio <= 1.0) {
        reportLines.push('**Analysis**: ⚠️ Acceptable performance - meeting benchmark');
      } else {
        reportLines.push('**Analysis**: ❌ Performance concern - exceeding benchmark');
      }
      
      reportLines.push('');
    });

    // Recommendations
    reportLines.push('## Recommendations', '');
    
    const failedCategories = Object.entries(groupedResults).filter(([category, tests]) => {
      const avgDuration = tests.reduce((sum, t) => sum + (t.duration || 0), 0) / tests.length;
      const benchmark = benchmarks[category] || 5000;
      return avgDuration > benchmark;
    });
    
    if (failedCategories.length === 0) {
      reportLines.push('All performance benchmarks are being met. Continue monitoring performance.');
    } else {
      reportLines.push('The following areas need performance optimization:');
      reportLines.push('');
      
      failedCategories.forEach(([category, tests]) => {
        const avgDuration = tests.reduce((sum, t) => sum + (t.duration || 0), 0) / tests.length;
        const benchmark = benchmarks[category] || 5000;
        
        reportLines.push(`### ${category} Performance Issues`);
        reportLines.push(`Current: ${avgDuration.toFixed(1)}ms | Benchmark: ${benchmark}ms`);
        reportLines.push('');
        
        // Category-specific recommendations
        if (category.includes('DCF')) {
          reportLines.push('**Recommended Actions**:');
          reportLines.push('- Optimize financial calculation algorithms');
          reportLines.push('- Implement intelligent result caching');
          reportLines.push('- Review and optimize database queries');
          reportLines.push('- Consider parallel processing for complex calculations');
        } else if (category.includes('Monte Carlo')) {
          reportLines.push('**Recommended Actions**:');
          reportLines.push('- Implement parallel scenario generation');
          reportLines.push('- Optimize correlation matrix calculations');
          reportLines.push('- Consider progressive result streaming');
          reportLines.push('- Review memory usage during large simulations');
        } else if (category.includes('Market Data')) {
          reportLines.push('**Recommended Actions**:');
          reportLines.push('- Implement aggressive caching for market data');
          reportLines.push('- Pre-load frequently accessed MSA data');
          reportLines.push('- Optimize database indexing for time series');
          reportLines.push('- Consider CDN for static market data');
        }
        
        reportLines.push('');
      });
    }

    // Write report
    const reportPath = path.join(this.outputPath, 'performance-report.md');
    fs.writeFileSync(reportPath, reportLines.join('\n'));
    console.log(`📄 Performance report generated: ${reportPath}`);
  }

  generateBenchmarkReport() {
    // Generate JSON report for programmatic analysis
    const benchmarkData = {
      timestamp: new Date().toISOString(),
      summary: {
        totalTests: this.results.length,
        passedTests: this.results.filter(r => r.status === 'passed').length,
        failedTests: this.results.filter(r => r.status === 'failed').length,
        averageDuration: this.results.reduce((sum, r) => sum + (r.duration || 0), 0) / this.results.length,
      },
      results: this.results.map(r => ({
        testName: r.testName,
        duration: r.duration,
        status: r.status,
        timestamp: r.timestamp,
      })),
      benchmarks: {
        'DCF Analysis': 3000,
        'Monte Carlo Simulation': 10000,
        'Market Data Fetch': 2000,
        'Authentication': 500,
        'Property Templates': 1000,
      },
    };

    const benchmarkPath = path.join(this.outputPath, 'benchmark-data.json');
    fs.writeFileSync(benchmarkPath, JSON.stringify(benchmarkData, null, 2));
    console.log(`📊 Benchmark data saved: ${benchmarkPath}`);
  }

  generateTrendsReport() {
    // Load historical data if it exists
    const trendsPath = path.join(this.outputPath, 'performance-trends.json');
    let trendsData = [];
    
    if (fs.existsSync(trendsPath)) {
      try {
        trendsData = JSON.parse(fs.readFileSync(trendsPath, 'utf8'));
      } catch (error) {
        console.warn('Could not load historical trends data');
      }
    }

    // Add current results to trends
    const currentTrend = {
      timestamp: new Date().toISOString(),
      date: new Date().toISOString().split('T')[0],
      averageDuration: this.results.reduce((sum, r) => sum + (r.duration || 0), 0) / this.results.length,
      testCount: this.results.length,
      passRate: this.results.filter(r => r.status === 'passed').length / this.results.length,
    };

    trendsData.push(currentTrend);
    
    // Keep only last 30 entries
    if (trendsData.length > 30) {
      trendsData = trendsData.slice(-30);
    }

    fs.writeFileSync(trendsPath, JSON.stringify(trendsData, null, 2));
    console.log(`📈 Performance trends updated: ${trendsPath}`);
  }

  extractTestCategory(testName) {
    const lowerTestName = testName.toLowerCase();
    
    if (lowerTestName.includes('dcf') || lowerTestName.includes('analysis')) {
      return 'DCF Analysis';
    } else if (lowerTestName.includes('monte carlo') || lowerTestName.includes('simulation')) {
      return 'Monte Carlo';
    } else if (lowerTestName.includes('market') || lowerTestName.includes('data')) {
      return 'Market Data';
    } else if (lowerTestName.includes('auth') || lowerTestName.includes('login')) {
      return 'Authentication';
    } else if (lowerTestName.includes('template')) {
      return 'Templates';
    } else {
      return 'Other';
    }
  }
}

module.exports = PerformanceReporter;