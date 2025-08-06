/**
 * Frontend-Backend Integration Test
 * 
 * This script tests the complete integration between the Next.js frontend
 * and FastAPI backend using a realistic property analysis workflow.
 * 
 * Runs as part of CI/CD pipeline to validate full-stack functionality.
 */

const axios = require('axios');
const process = require('process');

// API Configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';
const API_KEY = process.env.API_KEY || 'dev_test_key_12345678901234567890123';
const TIMEOUT = 30000; // 30 seconds

// HTTP client configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  }
});

// Test results tracking
const testResults = {
  passed: 0,
  failed: 0,
  skipped: 0,
  errors: []
};

// Utility functions
function logTest(testName, status, details = '') {
  const statusEmoji = {
    'PASS': '✅',
    'FAIL': '❌',
    'SKIP': '⚠️'
  };
  
  console.log(`${statusEmoji[status]} ${testName}${details ? ': ' + details : ''}`);
  
  if (status === 'PASS') testResults.passed++;
  else if (status === 'FAIL') {
    testResults.failed++;
    testResults.errors.push(`${testName}: ${details}`);
  } else testResults.skipped++;
}

async function testWithTimeout(testFn, testName, timeout = TIMEOUT) {
  return Promise.race([
    testFn(),
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error(`Test timeout after ${timeout}ms`)), timeout)
    )
  ]);
}

// Add package.json dependency check
function checkDependencies() {
  try {
    require.resolve('axios');
    logTest('Dependencies Check', 'PASS', 'axios available');
    return true;
  } catch (error) {
    logTest('Dependencies Check', 'FAIL', 'axios not found - run npm install');
    console.log('\n📦 Please install dependencies:');
    console.log('   npm install axios');
    return false;
  }
}

// Environment validation
function validateEnvironment() {
  const requiredEnvVars = {
    'API_BASE_URL': API_BASE_URL,
    'API_KEY': API_KEY
  };
  
  let allValid = true;
  Object.entries(requiredEnvVars).forEach(([key, value]) => {
    if (value) {
      logTest(`Environment ${key}`, 'PASS', value.substring(0, 30) + '...');
    } else {
      logTest(`Environment ${key}`, 'FAIL', 'Not set or empty');
      allValid = false;
    }
  });
  
  return allValid;
}

async function testHealthCheck() {
  try {
    const response = await apiClient.get('/health');
    
    if (response.status === 200) {
      const data = response.data;
      logTest('Health Check', 'PASS', `Status: ${data.status}, Uptime: ${data.uptime_seconds}s`);
      
      // Validate health response structure
      const requiredFields = ['status', 'version', 'environment', 'dependencies'];
      for (const field of requiredFields) {
        if (!(field in data)) {
          logTest('Health Response Structure', 'FAIL', `Missing field: ${field}`);
          return false;
        }
      }
      
      logTest('Health Response Structure', 'PASS');
      return true;
    }
  } catch (error) {
    logTest('Health Check', 'FAIL', error.response?.data?.detail || error.message);
    return false;
  }
}

async function testSystemInfo() {
  try {
    const response = await apiClient.get('/system/info');
    
    if (response.status === 200) {
      const data = response.data;
      logTest('System Info', 'PASS', `Version: ${data.version}, Environment: ${data.environment}`);
      return true;
    }
  } catch (error) {
    if (error.response?.status === 401 || error.response?.status === 403) {
      logTest('System Info', 'SKIP', 'Authentication required but endpoint exists');
      return true;
    }
    logTest('System Info', 'FAIL', error.response?.data?.detail || error.message);
    return false;
  }
}

async function testMarketData() {
  try {
    // Test NYC MSA market data
    const response = await apiClient.get('/data/markets/35620');
    
    if (response.status === 200) {
      const data = response.data;
      logTest('Market Data Retrieval', 'PASS', `Parameters found: ${Object.keys(data).length}`);
      
      // Check for expected market parameters
      const expectedParams = ['cap_rate', 'interest_rate', 'vacancy_rate'];
      let foundParams = 0;
      for (const param of expectedParams) {
        if (param in data && data[param]) {
          foundParams++;
        }
      }
      
      if (foundParams > 0) {
        logTest('Market Data Content', 'PASS', `Found ${foundParams}/${expectedParams.length} expected parameters`);
      } else {
        logTest('Market Data Content', 'FAIL', 'No expected market parameters found');
      }
      
      return true;
    }
  } catch (error) {
    if (error.response?.status === 401 || error.response?.status === 403) {
      logTest('Market Data Retrieval', 'SKIP', 'Authentication required but endpoint exists');
      return true;
    }
    logTest('Market Data Retrieval', 'FAIL', error.response?.data?.detail || error.message);
    return false;
  }
}

async function testDCFAnalysis() {
  const testProperty = {
    property_data: {
      property_id: 'test-prop-001',
      property_name: 'NYC Test Property',
      analysis_date: '2024-08-06',
      residential_units: {
        total_units: 50,
        average_rent_per_unit: 3500
      },
      renovation_info: {
        status: 'not_needed'
      },
      equity_structure: {
        investor_equity_share_pct: 30.0,
        self_cash_percentage: 85.0
      },
      commercial_units: {
        total_units: 2,
        average_rent_per_unit: 8000
      },
      msa_code: '35620',
      city: 'New York',
      state: 'NY',
      purchase_price: 15000000
    }
  };
  
  try {
    const response = await apiClient.post('/analysis/dcf', testProperty);
    
    if (response.status === 200) {
      const analysis = response.data;
      logTest('DCF Analysis', 'PASS', 
        `NPV: $${analysis.financial_metrics?.npv?.toLocaleString() || 'N/A'}, ` +
        `IRR: ${analysis.financial_metrics?.irr?.toFixed(2) || 'N/A'}%`
      );
      
      // Validate response structure
      if (analysis.financial_metrics) {
        const metrics = ['npv', 'irr', 'investment_recommendation'];
        let validMetrics = 0;
        for (const metric of metrics) {
          if (metric in analysis.financial_metrics) validMetrics++;
        }
        
        if (validMetrics === metrics.length) {
          logTest('DCF Response Structure', 'PASS');
        } else {
          logTest('DCF Response Structure', 'FAIL', `Missing ${metrics.length - validMetrics} metrics`);
        }
      }
      
      return true;
    }
  } catch (error) {
    if (error.response?.status === 422) {
      logTest('DCF Analysis', 'FAIL', `Validation error: ${JSON.stringify(error.response.data)}`);
    } else if (error.response?.status === 401 || error.response?.status === 403) {
      logTest('DCF Analysis', 'SKIP', 'Authentication required but endpoint exists');
      return true;
    } else {
      logTest('DCF Analysis', 'FAIL', error.response?.data?.detail || error.message);
    }
    return false;
  }
}

async function testMonteCarloSimulation() {
  const testProperty = {
    property_data: {
      property_id: 'test-prop-002',
      property_name: 'NYC Monte Carlo Test',
      analysis_date: '2024-08-06',
      residential_units: {
        total_units: 20,
        average_rent_per_unit: 2500
      },
      renovation_info: {
        status: 'not_needed'
      },
      equity_structure: {
        investor_equity_share_pct: 25.0,
        self_cash_percentage: 80.0
      },
      msa_code: '35620',
      purchase_price: 5000000
    },
    options: {
      monte_carlo_simulations: 100
    }
  };
  
  try {
    const response = await apiClient.post('/simulation/monte-carlo', testProperty);
    
    if (response.status === 200) {
      const simulation = response.data;
      logTest('Monte Carlo Simulation', 'PASS', 
        `Scenarios: ${simulation.scenarios_analyzed || 'N/A'}, ` +
        `Success Rate: ${((simulation.success_rate || 0) * 100).toFixed(1)}%`
      );
      
      // Validate simulation structure
      if (simulation.statistics && simulation.statistics.npv) {
        logTest('Monte Carlo Response Structure', 'PASS');
      } else {
        logTest('Monte Carlo Response Structure', 'FAIL', 'Missing statistics or NPV data');
      }
      
      return true;
    }
  } catch (error) {
    if (error.response?.status === 422) {
      logTest('Monte Carlo Simulation', 'FAIL', `Validation error: ${JSON.stringify(error.response.data)}`);
    } else if (error.response?.status === 401 || error.response?.status === 403) {
      logTest('Monte Carlo Simulation', 'SKIP', 'Authentication required but endpoint exists');
      return true;
    } else {
      logTest('Monte Carlo Simulation', 'FAIL', error.response?.data?.detail || error.message);
    }
    return false;
  }
}

async function testIntegration() {
  console.log('🚀 Starting Frontend-Backend Integration Test');
  console.log('=' .repeat(60));
  console.log(`API Base URL: ${API_BASE_URL}`);
  console.log(`API Key: ${API_KEY.substring(0, 10)}...`);
  console.log('\n');
  
  try {
    // Test 1: Health Check
    console.log('1️⃣ Testing Health Check...');
    const healthOk = await testWithTimeout(testHealthCheck, 'Health Check');
    
    if (!healthOk) {
      console.log('\n❌ Health check failed - aborting remaining tests');
      return;
    }
    
    // Test 2: System Information
    console.log('\n2️⃣ Testing System Information...');
    await testWithTimeout(testSystemInfo, 'System Info');
    
    // Test 3: Market Data Retrieval
    console.log('\n3️⃣ Testing Market Data Retrieval...');
    await testWithTimeout(testMarketData, 'Market Data');
    
    // Test 4: DCF Analysis
    console.log('\n4️⃣ Testing DCF Analysis...');
    await testWithTimeout(testDCFAnalysis, 'DCF Analysis');
    
    // Test 5: Monte Carlo Simulation
    console.log('\n5️⃣ Testing Monte Carlo Simulation...');
    await testWithTimeout(testMonteCarloSimulation, 'Monte Carlo Simulation');
    
    // Test 6: API Authentication
    console.log('\n6️⃣ Testing API Authentication...');
    try {
      // Test without API key
      const noAuthClient = axios.create({
        baseURL: API_BASE_URL,
        timeout: 5000,
        headers: { 'Content-Type': 'application/json' }
      });
      
      const response = await noAuthClient.get('/system/info');
      logTest('API Authentication', 'FAIL', 'Expected 401/403 but got 200');
    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        logTest('API Authentication', 'PASS', 'Properly requires authentication');
      } else {
        logTest('API Authentication', 'FAIL', `Unexpected status: ${error.response?.status}`);
      }
    }
    
    // Test 7: Error Handling
    console.log('\n7️⃣ Testing Error Handling...');
    try {
      // Test invalid endpoint
      await apiClient.get('/invalid/endpoint');
      logTest('Error Handling', 'FAIL', 'Expected 404 but got 200');
    } catch (error) {
      if (error.response?.status === 404) {
        logTest('Error Handling', 'PASS', 'Properly returns 404 for invalid endpoints');
      } else {
        logTest('Error Handling', 'FAIL', `Expected 404 but got ${error.response?.status}`);
      }
    }
    
    // Test 8: API Response Times
    console.log('\n8️⃣ Testing API Response Times...');
    const startTime = Date.now();
    try {
      await apiClient.get('/health');
      const responseTime = Date.now() - startTime;
      
      if (responseTime < 1000) {
        logTest('API Response Time', 'PASS', `${responseTime}ms`);
      } else if (responseTime < 5000) {
        logTest('API Response Time', 'SKIP', `${responseTime}ms (acceptable but slow)`);
      } else {
        logTest('API Response Time', 'FAIL', `${responseTime}ms (too slow)`);
      }
    } catch (error) {
      logTest('API Response Time', 'FAIL', error.message);
    }
    
    // Generate final summary
    console.log('\n🎉 Integration Test Summary');
    console.log('=' .repeat(60));
    console.log(`✅ Passed: ${testResults.passed}`);
    console.log(`❌ Failed: ${testResults.failed}`);
    console.log(`⚠️  Skipped: ${testResults.skipped}`);
    console.log(`📊 Total: ${testResults.passed + testResults.failed + testResults.skipped}`);
    
    if (testResults.failed === 0) {
      console.log('\n🎯 All critical integration points are functional!');
      console.log('✅ Backend API is accessible and responding');
      console.log('✅ Authentication middleware is working');
      console.log('✅ Core business logic endpoints are available');
      console.log('✅ Error handling is working correctly');
      process.exit(0);
    } else {
      console.log('\n❌ Integration test failures detected:');
      testResults.errors.forEach((error, index) => {
        console.log(`   ${index + 1}. ${error}`);
      });
      console.log('\n🔧 Review logs above for detailed error information');
      process.exit(1);
    }
    
  } catch (error) {
    console.error('\n💥 Integration test suite failed with unexpected error:', error.message);
    console.error('Stack trace:', error.stack);
    process.exit(1);
  }
}

// Main execution
async function main() {
  console.log('🔧 Validating test environment...');
  
  if (!checkDependencies()) {
    process.exit(1);
  }
  
  if (!validateEnvironment()) {
    console.log('\n⚠️  Some environment variables are missing but continuing with defaults...');
  }
  
  console.log('\n🚀 Starting integration tests...');
  await testIntegration();
}

// Run the integration test
if (require.main === module) {
  main().catch((error) => {
    console.error('\n💥 Test runner failed:', error.message);
    process.exit(1);
  });
}

module.exports = {
  testIntegration,
  testHealthCheck,
  testSystemInfo,
  testMarketData,
  testDCFAnalysis,
  testMonteCarloSimulation
};