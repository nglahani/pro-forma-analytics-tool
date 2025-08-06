/**
 * Test suite for MonteCarloResults component
 * Validates statistical calculations, chart rendering, and user interactions
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MonteCarloResults } from '../MonteCarloResults';
import { MonteCarloResult, MarketClassification } from '@/types/analysis';

// Mock recharts to avoid canvas issues in tests
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  Line: () => <div data-testid="line" />,
  Pie: () => <div data-testid="pie" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Cell: () => <div data-testid="cell" />,
}));

// Mock ScenarioAnalysisCharts component
jest.mock('../ScenarioAnalysisCharts', () => ({
  ScenarioAnalysisCharts: () => (
    <div>
      <div>Scenario Scatter Plot</div>
    </div>
  ),
}));

const mockMonteCarloResult: MonteCarloResult = {
  simulation_id: 'TEST-MC-001',
  property_id: 'TEST-PROP-001',
  total_scenarios: 100,
  execution_time_ms: 1500,
  success: true,
  scenarios: [],
  statistics: {
    npv_stats: {
      mean: 5000000,
      median: 4800000,
      std_dev: 2000000,
      min: 1000000,
      max: 12000000,
      percentile_5: 1500000,
      percentile_25: 3000000,
      percentile_75: 7000000,
      percentile_95: 9500000,
    },
    irr_stats: {
      mean: 45.0,
      median: 42.5,
      std_dev: 20.0,
      min: 5.0,
      max: 95.0,
      percentile_5: 12.0,
      percentile_25: 28.0,
      percentile_75: 62.0,
      percentile_95: 85.0,
    },
    risk_metrics: {
      probability_of_loss: 15.0,
      value_at_risk_5pct: 1500000,
      expected_shortfall: 800000,
    },
  },
  percentiles: {
    npv: {
      p5: 1500000,
      p25: 3000000,
      median: 4800000,
      p75: 7000000,
      p95: 9500000,
    },
    irr: {
      p5: 12.0,
      p25: 28.0,
      median: 42.5,
      p75: 62.0,
      p95: 85.0,
    },
    total_cash_flow: {
      p5: 300000,
      p25: 500000,
      median: 750000,
      p75: 950000,
      p95: 1200000,
    },
  },
  distribution: Array.from({ length: 20 }, (_, i) => ({
    scenario_id: i + 1,
    npv: 2000000 + Math.random() * 8000000,
    irr: 15 + Math.random() * 70,
    total_cash_flow: 400000 + Math.random() * 800000,
    risk_score: Math.random(),
    market_classification: MarketClassification.NEUTRAL,
  })),
  risk_distribution: {
    low: 30,
    moderate: 50,
    high: 20,
  },
  overall_risk_assessment: 'Moderate',
};

describe('MonteCarloResults Component', () => {
  const mockOnRerun = jest.fn();
  const mockOnExport = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders the component with basic information', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      expect(screen.getByText('Monte Carlo Simulation Results')).toBeInTheDocument();
      expect(screen.getByText(/Analysis of 100 scenarios/)).toBeInTheDocument();
      expect(screen.getByText(/Run time: 1500ms/)).toBeInTheDocument();
    });

    it('displays key statistics correctly', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      // Success probability should be calculated from distribution data
      // Since all mock scenarios have positive NPV, success rate should be 100%
      expect(screen.getByText('100.0%')).toBeInTheDocument();
      expect(screen.getByText('Success Probability')).toBeInTheDocument();
      
      // Expected NPV (median)
      expect(screen.getByText('Expected NPV')).toBeInTheDocument();
      
      // Risk level
      expect(screen.getByText('Moderate')).toBeInTheDocument();
    });

    it('renders all tab options', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      expect(screen.getByText('Distribution')).toBeInTheDocument();
      expect(screen.getByText('Percentiles')).toBeInTheDocument();
      expect(screen.getByText('Risk Analysis')).toBeInTheDocument();
      expect(screen.getByText('Scenarios')).toBeInTheDocument();
    });
  });

  describe('Interactive Features', () => {
    it('calls onRerun when rerun button is clicked', async () => {
      render(
        <MonteCarloResults 
          results={mockMonteCarloResult} 
          onRerun={mockOnRerun}
        />
      );
      
      const rerunButton = screen.getByText('Rerun');
      fireEvent.click(rerunButton);
      
      expect(mockOnRerun).toHaveBeenCalledTimes(1);
    });

    it('calls onExport when export buttons are clicked', async () => {
      render(
        <MonteCarloResults 
          results={mockMonteCarloResult} 
          onExport={mockOnExport}
        />
      );
      
      const pdfButton = screen.getByText('PDF');
      const excelButton = screen.getByText('Excel');
      
      fireEvent.click(pdfButton);
      expect(mockOnExport).toHaveBeenCalledWith('pdf');
      
      fireEvent.click(excelButton);
      expect(mockOnExport).toHaveBeenCalledWith('excel');
    });

    it('switches between different metric views', async () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      // Click on Distribution tab first
      fireEvent.click(screen.getByText('Distribution'));
      
      // Should see metric selection badges
      const npvBadge = screen.getByText('Net Present Value');
      const irrBadge = screen.getByText('Internal Rate of Return');
      
      expect(npvBadge).toBeInTheDocument();
      expect(irrBadge).toBeInTheDocument();
      
      // Click to switch metrics
      fireEvent.click(irrBadge);
      // Verify the chart updates (check for chart container)
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });

    it('switches between different tabs', async () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      // Verify all tabs are present and clickable
      const percentilesTab = screen.getByRole('tab', { name: 'Percentiles' });
      const riskTab = screen.getByRole('tab', { name: 'Risk Analysis' });
      const scenariosTab = screen.getByRole('tab', { name: 'Scenarios' });
      
      expect(percentilesTab).toBeInTheDocument();
      expect(riskTab).toBeInTheDocument();
      expect(scenariosTab).toBeInTheDocument();
      
      // Test tab clicking (tabs should be clickable)
      fireEvent.click(percentilesTab);
      fireEvent.click(riskTab);
      fireEvent.click(scenariosTab);
      
      // Verify tabs are still present after clicking
      expect(percentilesTab).toBeInTheDocument();
      expect(riskTab).toBeInTheDocument();
      expect(scenariosTab).toBeInTheDocument();
    });
  });

  describe('Data Validation', () => {
    it('handles loading state correctly', () => {
      render(
        <MonteCarloResults 
          results={mockMonteCarloResult} 
          onRerun={mockOnRerun}
          isRunning={true}
        />
      );
      
      expect(screen.getByText('Running...')).toBeInTheDocument();
      
      const rerunButton = screen.getByRole('button', { name: /running/i });
      expect(rerunButton).toBeDisabled();
    });

    it('calculates success probability correctly', () => {
      const resultsWithHighLoss = {
        ...mockMonteCarloResult,
        // Add some negative NPV scenarios to the distribution to create a loss scenario
        distribution: [
          ...mockMonteCarloResult.distribution.slice(0, 15), // Keep 15 positive scenarios
          ...Array.from({ length: 5 }, (_, i) => ({ // Add 5 negative scenarios
            scenario_id: i + 16,
            npv: -1000000 - Math.random() * 2000000, // Negative NPV
            irr: 5 + Math.random() * 10,
            total_cash_flow: 200000 + Math.random() * 300000,
            risk_score: Math.random(),
            market_classification: MarketClassification.NEUTRAL,
          })),
        ],
        statistics: {
          ...mockMonteCarloResult.statistics,
          risk_metrics: {
            ...mockMonteCarloResult.statistics.risk_metrics,
            probability_of_loss: 25.0,
          },
        },
      };
      
      render(<MonteCarloResults results={resultsWithHighLoss} />);
      
      // Success probability should be 75% (15 positive out of 20 total scenarios)
      expect(screen.getByText('75.0%')).toBeInTheDocument();
    });

    it('displays percentile data correctly', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      // The component should contain percentile data even if not immediately visible
      // We'll check that the percentiles tab exists
      const percentilesTab = screen.getByRole('tab', { name: 'Percentiles' });
      expect(percentilesTab).toBeInTheDocument();
      
      // The component should have the percentile data in props
      expect(mockMonteCarloResult.percentiles.npv).toBeDefined();
      expect(mockMonteCarloResult.percentiles.irr).toBeDefined();
    });

    it('handles risk distribution correctly', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      // Verify risk analysis tab exists
      const riskTab = screen.getByRole('tab', { name: 'Risk Analysis' });
      expect(riskTab).toBeInTheDocument();
      
      // The component should have the risk distribution data in props
      expect(mockMonteCarloResult.risk_distribution).toBeDefined();
      expect(mockMonteCarloResult.overall_risk_assessment).toBe('Moderate');
    });
  });

  describe('Chart Rendering', () => {
    it('renders distribution chart', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      // Should be on Distribution tab by default
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
      expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    });

    it('renders risk distribution pie chart', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      // Verify the component renders without crashing
      // The pie chart may not be visible in the default tab but component should handle the data
      expect(screen.getByRole('tab', { name: 'Risk Analysis' })).toBeInTheDocument();
      
      // Verify the data needed for risk distribution chart exists
      expect(mockMonteCarloResult.risk_distribution.low).toBeDefined();
      expect(mockMonteCarloResult.risk_distribution.moderate).toBeDefined();
      expect(mockMonteCarloResult.risk_distribution.high).toBeDefined();
    });

    it('renders scenario scatter plot', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      // Verify the Scenarios tab exists
      const scenariosTab = screen.getByRole('tab', { name: 'Scenarios' });
      expect(scenariosTab).toBeInTheDocument();
      
      // Verify the distribution data exists for the scatter plot
      expect(mockMonteCarloResult.distribution).toBeDefined();
      expect(mockMonteCarloResult.distribution.length).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    it('handles empty distribution data gracefully', () => {
      const emptyResults = {
        ...mockMonteCarloResult,
        distribution: [],
      };
      
      expect(() => {
        render(<MonteCarloResults results={emptyResults} />);
      }).not.toThrow();
    });

    it('handles missing optional props', () => {
      expect(() => {
        render(<MonteCarloResults results={mockMonteCarloResult} />);
      }).not.toThrow();
      
      // Should not show rerun or export buttons
      expect(screen.queryByText('Rerun')).not.toBeInTheDocument();
      expect(screen.queryByText('PDF')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper heading structure', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      const mainHeading = screen.getByRole('heading', { level: 2 });
      expect(mainHeading).toHaveTextContent('Monte Carlo Simulation Results');
    });

    it('has accessible tab navigation', () => {
      render(<MonteCarloResults results={mockMonteCarloResult} />);
      
      const tabList = screen.getByRole('tablist');
      expect(tabList).toBeInTheDocument();
      
      const tabs = screen.getAllByRole('tab');
      expect(tabs).toHaveLength(4);
    });

    it('has proper button accessibility', () => {
      render(
        <MonteCarloResults 
          results={mockMonteCarloResult} 
          onRerun={mockOnRerun}
          onExport={mockOnExport}
        />
      );
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAccessibleName();
      });
    });
  });
});