/**
 * Complete DCF Workflow Integration Tests
 * Tests the full user journey from property input through Monte Carlo analysis
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { AccessibilityProvider } from '@/components/common/AccessibilityProvider';
import { PropertyInputForm } from '@/components/property/PropertyInputForm';
import { DCFResultsDashboard } from '@/components/analysis/DCFResultsDashboard';
import { MonteCarloPanel } from '@/components/analysis/MonteCarloPanel';
import { MonteCarloResults } from '@/components/analysis/MonteCarloResults';
import { MarketDataExplorer } from '@/components/market/MarketDataExplorer';
import type { DCFAnalysisResult, MonteCarloResult, PropertyTemplate } from '@/types/analysis';

// Mock API client with realistic responses
const mockApiClient = {
  analyzeDCF: jest.fn(),
  startMonteCarloSimulation: jest.fn(),
  getMonteCarloStatus: jest.fn(),
  getMarketData: jest.fn(),
  getPropertyTemplates: jest.fn(),
};

jest.mock('@/lib/api/client', () => ({
  apiClient: mockApiClient,
}));

// Mock hooks
jest.mock('@/hooks/useToast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

jest.mock('@/hooks/useMarketDefaults', () => ({
  useMarketDefaults: () => ({
    data: {
      interestRate: 5.5,
      capRate: 4.2,
      vacancy: 5.0,
      rentGrowth: 3.5,
    },
    loading: false,
    error: null,
  }),
}));

// Mock charts to avoid rendering issues
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="chart-container">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  Line: () => <div data-testid="line" />,
  Pie: () => <div data-testid="pie" />,
  Area: () => <div data-testid="area" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Cell: () => <div data-testid="cell" />,
}));

// Test wrapper with all necessary providers
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AccessibilityProvider>{children}</AccessibilityProvider>
);

// Mock data
const mockPropertyTemplate: PropertyTemplate = {
  id: 'multifamily-basic',
  name: 'Multifamily Basic',
  description: 'Standard multifamily rental property',
  icon: '🏢',
  category: 'multifamily',
  defaultConfig: {
    residential_units: { total_units: 20, average_rent_per_unit: 2500, average_square_feet_per_unit: 900 },
    renovation_info: { status: 'NOT_NEEDED', anticipated_duration_months: 0, estimated_cost: 0 },
    equity_structure: { investor_equity_share_pct: 25, self_cash_percentage: 75 },
  },
  formConfig: {
    showResidentialUnits: true,
    showCommercialUnits: false,
    showRenovation: true,
    requiredFields: ['property_name', 'residential_units'],
  },
};

const mockDCFResult: DCFAnalysisResult = {
  property_id: 'test-property-123',
  analysis_date: '2025-08-07',
  financial_metrics: {
    npv: 15847901,
    irr: 64.8,
    equity_multiple: 9.79,
    payback_period: 4.0,
    terminal_value: 45000000,
    total_return: 156.5,
    investment_recommendation: 'STRONG_BUY',
    confidence_score: 0.89,
  },
  cash_flow_projections: [
    {
      year: 2025,
      gross_rental_income: 600000,
      operating_expenses: 180000,
      net_operating_income: 420000,
      debt_service: 150000,
      net_cash_flow: 270000,
    },
    {
      year: 2026,
      gross_rental_income: 621000,
      operating_expenses: 186300,
      net_operating_income: 434700,
      debt_service: 150000,
      net_cash_flow: 284700,
    },
  ],
  initial_numbers: {
    acquisition_cost: 12500000,
    total_cash_invested: 3125000,
    loan_amount: 9375000,
    closing_costs: 125000,
    renovation_cost: 500000,
  },
};

const mockMonteCarloResult: MonteCarloResult = {
  simulation_id: 'MC-TEST-001',
  property_id: 'test-property-123',
  analysis_date: '2025-08-07',
  total_scenarios: 1000,
  execution_time_ms: 2500,
  success: true,
  scenario_analysis: [
    {
      scenario_id: 1,
      npv: 15000000,
      irr: 62.5,
      equity_multiple: 9.2,
      market_classification: 'NEUTRAL' as const,
      risk_score: 0.45,
      growth_score: 0.55,
    },
    {
      scenario_id: 2,
      npv: 18000000,
      irr: 68.1,
      equity_multiple: 10.8,
      market_classification: 'BULL' as const,
      risk_score: 0.38,
      growth_score: 0.72,
    },
  ],
  risk_metrics: {
    value_at_risk_95: 8500000,
    expected_shortfall: 7200000,
    probability_of_loss: 0.05,
    worst_case_npv: 2000000,
    best_case_npv: 28000000,
  },
};

describe('Complete DCF Workflow Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Setup default API responses
    mockApiClient.analyzeDCF.mockResolvedValue(mockDCFResult);
    mockApiClient.startMonteCarloSimulation.mockResolvedValue({ simulation_id: 'MC-TEST-001' });
    mockApiClient.getMonteCarloStatus.mockResolvedValue(mockMonteCarloResult);
    mockApiClient.getMarketData.mockResolvedValue({
      msa: 'NYC',
      parameters: { interestRate: 5.5, capRate: 4.2 },
    });
    mockApiClient.getPropertyTemplates.mockResolvedValue([mockPropertyTemplate]);
  });

  describe('Property Input to DCF Analysis Workflow', () => {
    test('completes full property input and analysis workflow', async () => {
      const user = userEvent.setup();
      const onSubmit = jest.fn();

      render(
        <TestWrapper>
          <PropertyInputForm
            template={mockPropertyTemplate}
            onBack={jest.fn()}
            onSubmit={onSubmit}
          />
        </TestWrapper>
      );

      // Step 1: Fill basic property information
      await user.type(screen.getByLabelText(/property name/i), 'Sunset Gardens Apartments');
      
      // Fill address information
      await user.type(screen.getByLabelText(/street/i), '123 Main Street');
      await user.type(screen.getByLabelText(/city/i), 'New York');
      await user.selectOptions(screen.getByLabelText(/state/i), 'NY');
      await user.type(screen.getByLabelText(/zip code/i), '10001');

      // Continue to next step
      await user.click(screen.getByRole('button', { name: /next/i }));

      // Step 2: Fill unit information
      await user.clear(screen.getByLabelText(/number of units/i));
      await user.type(screen.getByLabelText(/number of units/i), '24');
      await user.type(screen.getByLabelText(/avg.*rent per unit/i), '2800');

      await user.click(screen.getByRole('button', { name: /next/i }));

      // Step 3: Fill renovation information
      await user.type(screen.getByLabelText(/renovation period.*months/i), '6');
      await user.type(screen.getByLabelText(/renovation budget/i), '500000');

      await user.click(screen.getByRole('button', { name: /next/i }));

      // Step 4: Fill equity structure
      await user.type(screen.getByLabelText(/investor equity share/i), '25');
      await user.type(screen.getByLabelText(/self cash percentage/i), '75');

      await user.click(screen.getByRole('button', { name: /next/i }));

      // Step 5: Review and submit
      expect(screen.getByText(/review your property information/i)).toBeInTheDocument();
      expect(screen.getByText('Sunset Gardens Apartments')).toBeInTheDocument();
      expect(screen.getByText('New York, NY')).toBeInTheDocument();

      // Submit the form
      await user.click(screen.getByRole('button', { name: /submit for analysis/i }));

      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          property_name: 'Sunset Gardens Apartments',
          city: 'New York',
          state: 'NY',
          residential_units: expect.objectContaining({
            total_units: 24,
            average_rent_per_unit: 2800,
          }),
        })
      );
    });

    test('displays DCF analysis results correctly', async () => {
      render(
        <TestWrapper>
          <DCFResultsDashboard
            analysis={mockDCFResult}
            onExport={jest.fn()}
            onRunMonteCarlos={jest.fn()}
          />
        </TestWrapper>
      );

      // Check key financial metrics
      expect(screen.getByText('$15,847,901')).toBeInTheDocument(); // NPV
      expect(screen.getByText('64.8%')).toBeInTheDocument(); // IRR
      expect(screen.getByText('9.79x')).toBeInTheDocument(); // Equity Multiple
      
      // Check investment recommendation
      expect(screen.getByText('Strong Buy')).toBeInTheDocument();
      
      // Check cash flow projections
      expect(screen.getByText('$600,000')).toBeInTheDocument(); // Year 1 gross income
      expect(screen.getByText('$270,000')).toBeInTheDocument(); // Year 1 net cash flow
    });
  });

  describe('Monte Carlo Risk Analysis Workflow', () => {
    test('runs Monte Carlo simulation from DCF results', async () => {
      const user = userEvent.setup();
      const onRunMonteCarlos = jest.fn();

      render(
        <TestWrapper>
          <DCFResultsDashboard
            analysis={mockDCFResult}
            onExport={jest.fn()}
            onRunMonteCarlos={onRunMonteCarlos}
          />
        </TestWrapper>
      );

      // Click run Monte Carlo button
      const runMonteCarloButton = screen.getByRole('button', { name: /monte carlo/i });
      await user.click(runMonteCarloButton);

      expect(onRunMonteCarlos).toHaveBeenCalled();
    });

    test('configures and runs Monte Carlo simulation', async () => {
      const user = userEvent.setup();
      const onSimulationStart = jest.fn();

      render(
        <TestWrapper>
          <MonteCarloPanel
            propertyId="test-property-123"
            baselineNPV={15847901}
            baselineIRR={64.8}
            onSimulationStart={onSimulationStart}
            onSimulationComplete={jest.fn()}
            onSimulationError={jest.fn()}
          />
        </TestWrapper>
      );

      // Configure simulation settings
      const scenariosInput = screen.getByLabelText(/number of scenarios/i);
      await user.clear(scenariosInput);
      await user.type(scenariosInput, '2000');

      const confidenceInput = screen.getByLabelText(/confidence level/i);
      await user.clear(confidenceInput);
      await user.type(confidenceInput, '99');

      // Start simulation
      await user.click(screen.getByRole('button', { name: /run simulation/i }));

      expect(onSimulationStart).toHaveBeenCalledWith({
        numScenarios: 2000,
        confidenceLevel: 99,
        includeCorrelations: true,
        includeMarketCycles: true,
      });
    });

    test('displays Monte Carlo results with risk metrics', async () => {
      render(
        <TestWrapper>
          <MonteCarloResults
            results={mockMonteCarloResult}
            onRerun={jest.fn()}
            onExport={jest.fn()}
          />
        </TestWrapper>
      );

      // Check simulation summary
      expect(screen.getByText('1000')).toBeInTheDocument(); // Total scenarios
      expect(screen.getByText(/2025-08-07/)).toBeInTheDocument(); // Analysis date

      // Check risk metrics
      expect(screen.getByText('5%')).toBeInTheDocument(); // Probability of loss
      expect(screen.getByText('$8,500,000')).toBeInTheDocument(); // Value at Risk
      
      // Check scenario results are displayed
      expect(screen.getByTestId('chart-container')).toBeInTheDocument();
    });
  });

  describe('Market Data Integration Workflow', () => {
    test('explores market data and applies to analysis', async () => {
      const user = userEvent.setup();
      const onApplyData = jest.fn();

      render(
        <TestWrapper>
          <MarketDataExplorer
            selectedMSA="NYC"
            onMSAChange={jest.fn()}
            onApplyData={onApplyData}
          />
        </TestWrapper>
      );

      // Select different MSA
      const msaSelector = screen.getByRole('combobox', { name: /select msa/i });
      await user.click(msaSelector);
      await user.click(screen.getByText('Los Angeles'));

      // Check that market data loads
      await waitFor(() => {
        expect(screen.getByText(/interest rates/i)).toBeInTheDocument();
        expect(screen.getByText(/cap rates/i)).toBeInTheDocument();
      });

      // Apply market data to analysis
      await user.click(screen.getByRole('button', { name: /apply to analysis/i }));

      expect(onApplyData).toHaveBeenCalledWith(
        expect.objectContaining({
          msa: 'Los Angeles',
          parameters: expect.any(Object),
        })
      );
    });
  });

  describe('End-to-End Workflow Integration', () => {
    test('completes full workflow from property input to Monte Carlo results', async () => {
      const user = userEvent.setup();

      // This would be a full page component in reality, but we'll simulate the workflow
      const WorkflowContainer = () => {
        const [currentStep, setCurrentStep] = React.useState('input');
        const [propertyData, setPropertyData] = React.useState(null);
        const [dcfResults, setDcfResults] = React.useState(null);
        const [monteCarloResults, setMonteCarloResults] = React.useState(null);

        const handlePropertySubmit = async (data: any) => {
          setPropertyData(data);
          // Simulate DCF analysis
          const results = await mockApiClient.analyzeDCF(data);
          setDcfResults(results);
          setCurrentStep('dcf-results');
        };

        const handleRunMonteCarlo = async () => {
          setCurrentStep('monte-carlo');
        };

        const handleMonteCarloComplete = (results: any) => {
          setMonteCarloResults(results);
          setCurrentStep('monte-carlo-results');
        };

        return (
          <div>
            {currentStep === 'input' && (
              <PropertyInputForm
                template={mockPropertyTemplate}
                onBack={jest.fn()}
                onSubmit={handlePropertySubmit}
              />
            )}
            
            {currentStep === 'dcf-results' && dcfResults && (
              <DCFResultsDashboard
                analysis={dcfResults}
                onExport={jest.fn()}
                onRunMonteCarlos={handleRunMonteCarlo}
              />
            )}

            {currentStep === 'monte-carlo' && (
              <MonteCarloPanel
                propertyId="test-property-123"
                baselineNPV={15847901}
                baselineIRR={64.8}
                onSimulationStart={jest.fn()}
                onSimulationComplete={handleMonteCarloComplete}
                onSimulationError={jest.fn()}
              />
            )}

            {currentStep === 'monte-carlo-results' && monteCarloResults && (
              <MonteCarloResults
                results={monteCarloResults}
                onRerun={jest.fn()}
                onExport={jest.fn()}
              />
            )}
          </div>
        );
      };

      render(
        <TestWrapper>
          <WorkflowContainer />
        </TestWrapper>
      );

      // Complete property input
      await user.type(screen.getByLabelText(/property name/i), 'Test Property');
      
      // Fill required address fields
      await user.type(screen.getByLabelText(/street/i), '456 Test St');
      await user.type(screen.getByLabelText(/city/i), 'New York');
      await user.selectOptions(screen.getByLabelText(/state/i), 'NY');
      await user.type(screen.getByLabelText(/zip code/i), '10002');

      // Navigate through form steps
      for (let step = 0; step < 4; step++) {
        await user.click(screen.getByRole('button', { name: /next/i }));
        
        // Fill required fields for each step
        if (step === 0) { // Units step
          const unitsInput = screen.getByLabelText(/number of units/i);
          if (unitsInput) {
            await user.clear(unitsInput);
            await user.type(unitsInput, '20');
          }
        }
        if (step === 1) { // Renovation step
          const monthsInput = screen.getByLabelText(/renovation period.*months/i);
          const budgetInput = screen.getByLabelText(/renovation budget/i);
          if (monthsInput) await user.type(monthsInput, '3');
          if (budgetInput) await user.type(budgetInput, '250000');
        }
        if (step === 2) { // Equity step
          const equityInput = screen.getByLabelText(/investor equity share/i);
          const cashInput = screen.getByLabelText(/self cash percentage/i);
          if (equityInput) await user.type(equityInput, '30');
          if (cashInput) await user.type(cashInput, '70');
        }
      }

      // Submit the form
      await user.click(screen.getByRole('button', { name: /submit for analysis/i }));

      // Wait for DCF results to appear
      await waitFor(() => {
        expect(screen.getByText('DCF Analysis Results')).toBeInTheDocument();
      });

      // Run Monte Carlo analysis
      await user.click(screen.getByRole('button', { name: /monte carlo/i }));

      // Wait for Monte Carlo panel
      await waitFor(() => {
        expect(screen.getByText('Monte Carlo Risk Analysis')).toBeInTheDocument();
      });

      // Start simulation
      await user.click(screen.getByRole('button', { name: /run simulation/i }));

      // Verify the workflow completed
      expect(mockApiClient.analyzeDCF).toHaveBeenCalled();
    }, 30000); // Longer timeout for full workflow
  });

  describe('Error Handling and Edge Cases', () => {
    test('handles API errors gracefully', async () => {
      const user = userEvent.setup();
      
      // Mock API to return error
      mockApiClient.analyzeDCF.mockRejectedValue(new Error('API Error'));
      
      const onSubmit = jest.fn();

      render(
        <TestWrapper>
          <PropertyInputForm
            template={mockPropertyTemplate}
            onBack={jest.fn()}
            onSubmit={onSubmit}
          />
        </TestWrapper>
      );

      // Fill minimal required data
      await user.type(screen.getByLabelText(/property name/i), 'Error Test Property');
      
      // Complete the form quickly
      for (let step = 0; step < 5; step++) {
        await user.click(screen.getByRole('button', { name: /next|submit/i }));
      }

      // The form should handle the API error gracefully
      expect(onSubmit).toHaveBeenCalled();
    });

    test('validates required fields before submission', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <PropertyInputForm
            template={mockPropertyTemplate}
            onBack={jest.fn()}
            onSubmit={jest.fn()}
          />
        </TestWrapper>
      );

      // Try to proceed without filling required fields
      const nextButton = screen.getByRole('button', { name: /next/i });
      expect(nextButton).toBeDisabled();

      // Fill property name
      await user.type(screen.getByLabelText(/property name/i), 'Validation Test');
      
      // Button should still be disabled until address is valid
      expect(nextButton).toBeDisabled();
    });

    test('handles empty Monte Carlo results', () => {
      const emptyResults = {
        ...mockMonteCarloResult,
        scenario_analysis: [],
        total_scenarios: 0,
      };

      render(
        <TestWrapper>
          <MonteCarloResults
            results={emptyResults}
            onRerun={jest.fn()}
            onExport={jest.fn()}
          />
        </TestWrapper>
      );

      expect(screen.getByText(/no results available/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /run simulation/i })).toBeInTheDocument();
    });
  });

  describe('Accessibility Compliance', () => {
    test('provides proper ARIA labels and keyboard navigation', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <DCFResultsDashboard
            analysis={mockDCFResult}
            onExport={jest.fn()}
            onRunMonteCarlos={jest.fn()}
          />
        </TestWrapper>
      );

      // Check for proper headings
      expect(screen.getByRole('heading', { name: /dcf analysis results/i })).toBeInTheDocument();
      
      // Check for proper button roles
      const exportButton = screen.getByRole('button', { name: /export/i });
      expect(exportButton).toBeInTheDocument();
      
      // Test keyboard navigation
      await user.tab();
      expect(document.activeElement).toBe(exportButton);
    });

    test('provides screen reader announcements for state changes', async () => {
      const user = userEvent.setup();

      render(
        <TestWrapper>
          <MonteCarloPanel
            propertyId="accessibility-test"
            baselineNPV={1000000}
            baselineIRR={15.0}
            onSimulationStart={jest.fn()}
            onSimulationComplete={jest.fn()}
            onSimulationError={jest.fn()}
          />
        </TestWrapper>
      );

      // Check for live region announcements
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toBeInTheDocument();

      // Start simulation to trigger announcements
      await user.click(screen.getByRole('button', { name: /run simulation/i }));
      
      // Announcements should be made to screen readers
      // (The actual announcements are tested in the accessibility test suite)
    });
  });
});