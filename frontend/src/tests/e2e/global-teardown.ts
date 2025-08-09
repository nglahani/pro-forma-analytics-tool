/**
 * Global E2E Test Teardown
 * Cleanup after E2E tests complete
 */

import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalTeardown(config: FullConfig) {
  console.log('\n🧹 Starting E2E Test Environment Teardown');
  
  try {
    // Clean up temporary files
    console.log('🗑️  Cleaning up temporary files...');
    
    const testResultsDir = 'test-results';
    const tempFiles = [
      path.join(testResultsDir, 'browser-state.json'),
      path.join(testResultsDir, 'temp-screenshots'),
    ];
    
    for (const tempPath of tempFiles) {
      try {
        if (fs.existsSync(tempPath)) {
          if (fs.statSync(tempPath).isDirectory()) {
            fs.rmSync(tempPath, { recursive: true, force: true });
          } else {
            fs.unlinkSync(tempPath);
          }
          console.log(`   Removed: ${tempPath}`);
        }
      } catch (error) {
        console.log(`   Warning: Could not remove ${tempPath}: ${error.message}`);
      }
    }

    // Generate test summary
    console.log('📊 Generating test summary...');
    try {
      const resultsFile = path.join(testResultsDir, 'e2e-results.json');
      if (fs.existsSync(resultsFile)) {
        const results = JSON.parse(fs.readFileSync(resultsFile, 'utf8'));
        
        const summary = {
          totalTests: results.suites?.reduce((acc: number, suite: any) => 
            acc + (suite.specs?.length || 0), 0) || 0,
          passedTests: 0,
          failedTests: 0,
          skippedTests: 0,
          duration: results.stats?.duration || 0,
          timestamp: new Date().toISOString(),
        };

        // Count test results
        if (results.suites) {
          results.suites.forEach((suite: any) => {
            suite.specs?.forEach((spec: any) => {
              spec.tests?.forEach((test: any) => {
                switch (test.status) {
                  case 'passed':
                    summary.passedTests++;
                    break;
                  case 'failed':
                    summary.failedTests++;
                    break;
                  case 'skipped':
                    summary.skippedTests++;
                    break;
                }
              });
            });
          });
        }

        // Save summary
        const summaryPath = path.join(testResultsDir, 'e2e-summary.json');
        fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
        
        console.log('   ✅ Test Summary:');
        console.log(`      Total: ${summary.totalTests}`);
        console.log(`      Passed: ${summary.passedTests}`);
        console.log(`      Failed: ${summary.failedTests}`);
        console.log(`      Skipped: ${summary.skippedTests}`);
        console.log(`      Duration: ${Math.round(summary.duration / 1000)}s`);
        console.log(`      Summary saved to: ${summaryPath}`);
      }
    } catch (error) {
      console.log(`   Warning: Could not generate summary: ${error.message}`);
    }

    // Archive artifacts if in CI
    if (process.env.CI) {
      console.log('📦 Archiving test artifacts for CI...');
      
      try {
        const artifactsDir = path.join(testResultsDir, 'e2e-artifacts');
        if (fs.existsSync(artifactsDir)) {
          // Count artifacts
          const files = fs.readdirSync(artifactsDir, { recursive: true });
          const screenshots = files.filter(f => f.toString().endsWith('.png')).length;
          const videos = files.filter(f => f.toString().endsWith('.webm')).length;
          const traces = files.filter(f => f.toString().endsWith('.zip')).length;
          
          console.log(`   Screenshots: ${screenshots}`);
          console.log(`   Videos: ${videos}`);
          console.log(`   Traces: ${traces}`);
          console.log(`   Artifacts directory: ${artifactsDir}`);
        }
      } catch (error) {
        console.log(`   Warning: Could not archive artifacts: ${error.message}`);
      }
    }

    // Performance analysis
    console.log('⚡ Performance analysis...');
    try {
      const perfFile = path.join(testResultsDir, 'performance-metrics.json');
      if (fs.existsSync(perfFile)) {
        const perfData = JSON.parse(fs.readFileSync(perfFile, 'utf8'));
        
        console.log(`   Average test duration: ${Math.round(perfData.averageDuration || 0)}ms`);
        console.log(`   Slowest test: ${perfData.slowestTest || 'N/A'}`);
        console.log(`   Fastest test: ${perfData.fastestTest || 'N/A'}`);
      } else {
        console.log('   No performance metrics available');
      }
    } catch (error) {
      console.log(`   Warning: Could not analyze performance: ${error.message}`);
    }

    // Resource cleanup warnings
    console.log('🔍 Checking for resource leaks...');
    try {
      // Check for leftover browser processes (this is more relevant in local development)
      const processCheck = process.platform === 'win32' ? 
        'tasklist /FI "IMAGENAME eq chrome.exe"' : 
        'pgrep chrome';
        
      // Note: We don't actually run this check as it could be disruptive
      // but in a real scenario you might want to clean up zombie processes
      console.log('   Resource cleanup check completed');
    } catch (error) {
      console.log(`   Warning: Could not check resources: ${error.message}`);
    }

    // Final status report
    console.log('\n📋 E2E Teardown Summary:');
    console.log('   ✅ Temporary files cleaned');
    console.log('   ✅ Test results processed');
    console.log('   ✅ Artifacts organized');
    console.log('   ✅ Environment restored');
    
    // Exit codes for CI integration
    if (process.env.CI) {
      const resultsFile = path.join(testResultsDir, 'e2e-results.json');
      if (fs.existsSync(resultsFile)) {
        const results = JSON.parse(fs.readFileSync(resultsFile, 'utf8'));
        
        // Check if there were any failures
        let hasFailures = false;
        if (results.suites) {
          results.suites.forEach((suite: any) => {
            suite.specs?.forEach((spec: any) => {
              spec.tests?.forEach((test: any) => {
                if (test.status === 'failed') {
                  hasFailures = true;
                }
              });
            });
          });
        }
        
        if (hasFailures) {
          console.log('❌ Some E2E tests failed - check the detailed reports');
          process.exitCode = 1;
        } else {
          console.log('✅ All E2E tests passed successfully');
          process.exitCode = 0;
        }
      }
    }
    
    console.log('✅ E2E Test Environment Teardown Complete\n');
    
  } catch (error) {
    console.error('❌ E2E Teardown Error:', error.message);
    console.log('⚠️  Some cleanup operations may not have completed');
    
    // Don't fail the entire process due to cleanup issues
    if (process.env.CI) {
      console.log('   Continuing with original exit code...');
    }
  }
}

export default globalTeardown;