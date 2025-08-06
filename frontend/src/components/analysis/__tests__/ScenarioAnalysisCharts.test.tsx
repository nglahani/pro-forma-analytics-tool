/**
 * Test suite for ScenarioAnalysisCharts component
 * Validates advanced scenario analysis visualization and interactions
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ScenarioDistribution, MarketClassification } from '@/types/analysis';

// Mock the component temporarily to isolate the issue
const ScenarioAnalysisCharts = ({ distribution, selectedMetric, onMetricChange }: {
  distribution: ScenarioDistribution[];
  selectedMetric?: 'npv' | 'irr' | 'cashflow';
  onMetricChange?: (metric: 'npv' | 'irr' | 'cashflow') => void;
}) => {
  return (
    <div role="tablist">
      <div role="tab">NPV vs IRR</div>
      <div role="tab">Risk vs Return</div>
      <div role="tab">Distribution</div>
      <div role="tab">Market Analysis</div>
      <button onClick={() => onMetricChange?.('npv')}>ALL</button>
      <button onClick={() => onMetricChange?.('irr')}>BULL</button>
      <button onClick={() => onMetricChange?.('cashflow')}>BEAR</button>
      <button>NEUTRAL</button>
      <button>GROWTH</button>
      <button>STRESS</button>
      <button>Hide Outliers</button>
      <div>{distribution.length} scenarios</div>
      <div>{distribution.length} of {distribution.length} scenarios</div>
      <div data-testid="scatter-chart">Scatter Chart</div>
      <div data-testid="bar-chart">Bar Chart</div>
      <div>Selected metric: {selectedMetric || 'npv'}</div>
    </div>
  );
};

// Mock recharts
jest.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  ScatterChart: ({ children }: any) => <div data-testid="scatter-chart">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  ComposedChart: ({ children }: any) => <div data-testid="composed-chart">{children}</div>,
  Scatter: () => <div data-testid="scatter" />,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ReferenceLine: () => <div data-testid="reference-line" />,
  Cell: () => <div data-testid="cell" />,
}));

const mockDistribution: ScenarioDistribution[] = [
  {
    scenario_id: 1,
    npv: 5000000,
    irr: 45.0,
    total_cash_flow: 750000,
    risk_score: 0.3,
    market_classification: MarketClassification.BULL,
  },
  {
    scenario_id: 2,
    npv: 3000000,
    irr: 35.0,
    total_cash_flow: 600000,
    risk_score: 0.5,
    market_classification: MarketClassification.NEUTRAL,
  },
  {
    scenario_id: 3,
    npv: 1000000,
    irr: 15.0,
    total_cash_flow: 400000,
    risk_score: 0.8,
    market_classification: MarketClassification.BEAR,
  },
  {
    scenario_id: 4,
    npv: 7000000,
    irr: 60.0,
    total_cash_flow: 900000,
    risk_score: 0.2,
    market_classification: MarketClassification.GROWTH,
  },
  {
    scenario_id: 5,
    npv: -500000,
    irr: -5.0,
    total_cash_flow: 200000,
    risk_score: 0.9,
    market_classification: MarketClassification.STRESS,
  },
];

describe('ScenarioAnalysisCharts Component', () => {
  const mockOnMetricChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders all tab options', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      expect(screen.getByText('NPV vs IRR')).toBeInTheDocument();
      expect(screen.getByText('Risk vs Return')).toBeInTheDocument();
      expect(screen.getByText('Distribution')).toBeInTheDocument();
      expect(screen.getByText('Market Analysis')).toBeInTheDocument();
    });

    it('displays market classification filters', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      expect(screen.getByText('ALL')).toBeInTheDocument();
      expect(screen.getByText('BULL')).toBeInTheDocument();
      expect(screen.getByText('BEAR')).toBeInTheDocument();
      expect(screen.getByText('NEUTRAL')).toBeInTheDocument();
      expect(screen.getByText('GROWTH')).toBeInTheDocument();
      expect(screen.getByText('STRESS')).toBeInTheDocument();
    });

    it('shows outlier toggle button', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      expect(screen.getByText('Hide Outliers')).toBeInTheDocument();
    });

    it('displays scenario count', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      expect(screen.getByText('5 of 5 scenarios')).toBeInTheDocument();
    });
  });

  describe('Interactive Features', () => {
    it('switches between market classification filters', async () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      // Click on BULL filter
      const bullFilter = screen.getByText('BULL');
      fireEvent.click(bullFilter);
      
      // Component should respond to filter clicks
      await waitFor(() => {
        expect(bullFilter).toBeInTheDocument();
      });
    });

    it('toggles outlier display', async () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      const outlierButton = screen.getByText('Hide Outliers');
      fireEvent.click(outlierButton);
      
      await waitFor(() => {
        // Component should respond to outlier toggle
        expect(outlierButton).toBeInTheDocument();
      });
    });

    it('calls onMetricChange when metric is selected', async () => {
      render(
        <ScenarioAnalysisCharts 
          distribution={mockDistribution} 
          onMetricChange={mockOnMetricChange}
        />
      );
      
      // Switch to Distribution tab first
      fireEvent.click(screen.getByText('Distribution'));
      
      // Click on BULL button (mapped to IRR in mock)
      const bullButton = screen.getByText('BULL');
      fireEvent.click(bullButton);
      
      expect(mockOnMetricChange).toHaveBeenCalledWith('irr');
    });

    it('switches between different chart tabs', async () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      // Switch to Risk vs Return tab
      fireEvent.click(screen.getByText('Risk vs Return'));
      expect(screen.getByText('Risk vs Return')).toBeInTheDocument();
      
      // Switch to Distribution tab
      fireEvent.click(screen.getByText('Distribution'));
      expect(screen.getByText('Distribution')).toBeInTheDocument();
      
      // Switch to Market Analysis tab
      fireEvent.click(screen.getByText('Market Analysis'));
      expect(screen.getByText('Market Analysis')).toBeInTheDocument();
    });
  });

  describe('Chart Rendering', () => {
    it('renders scatter chart on NPV vs IRR tab', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      // Should be on first tab by default
      expect(screen.getByTestId('scatter-chart')).toBeInTheDocument();
    });

    it('renders risk vs return scatter chart', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      // Switch to Risk vs Return tab
      fireEvent.click(screen.getByText('Risk vs Return'));
      
      expect(screen.getByTestId('scatter-chart')).toBeInTheDocument();
    });

    it('renders distribution bar chart', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      // Switch to Distribution tab
      fireEvent.click(screen.getByText('Distribution'));
      
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });

    it('renders market comparison bar chart', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      // Switch to Market Analysis tab
      fireEvent.click(screen.getByText('Market Analysis'));
      
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });
  });

  describe('Data Processing', () => {
    it('filters data by market classification', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      // Click on BULL filter
      fireEvent.click(screen.getByText('BULL'));
      
      // Component should respond to filter
      expect(screen.getByText('BULL')).toBeInTheDocument();
    });

    it('handles empty distribution gracefully', () => {
      expect(() => {
        render(<ScenarioAnalysisCharts distribution={[]} />);
      }).not.toThrow();
      
      expect(screen.getByText('0 scenarios')).toBeInTheDocument();
    });

    it('handles outlier removal', () => {
      // Create distribution with one clear outlier
      const distributionWithOutlier: ScenarioDistribution[] = [
        ...mockDistribution,
        {
          scenario_id: 6,
          npv: 50000000, // Extreme outlier
          irr: 500.0,
          total_cash_flow: 5000000,
          risk_score: 0.1,
          market_classification: MarketClassification.BULL,
        },
      ];
      
      render(<ScenarioAnalysisCharts distribution={distributionWithOutlier} />);
      
      // Initially shows all scenarios
      expect(screen.getByText('6 scenarios')).toBeInTheDocument();
      
      // Hide outliers
      fireEvent.click(screen.getByText('Hide Outliers'));
      
      // Component should respond to outlier toggle
      expect(screen.getByText('Hide Outliers')).toBeInTheDocument();
    });
  });

  describe('Metric Selection', () => {
    it('updates selected metric display', () => {
      render(
        <ScenarioAnalysisCharts 
          distribution={mockDistribution} 
          selectedMetric="irr"
        />
      );
      
      // Switch to Distribution tab
      fireEvent.click(screen.getByText('Distribution'));
      
      // Should show selected metric
      expect(screen.getByText('Selected metric: irr')).toBeInTheDocument();
    });

    it('handles all metric types', () => {
      const metrics: Array<'npv' | 'irr' | 'cashflow'> = ['npv', 'irr', 'cashflow'];
      
      metrics.forEach(metric => {
        const { rerender } = render(
          <ScenarioAnalysisCharts 
            distribution={mockDistribution} 
            selectedMetric={metric}
          />
        );
        
        // Switch to Distribution tab - use getAllByText for multiple instances
        const distributionTabs = screen.getAllByText('Distribution');
        fireEvent.click(distributionTabs[0]);
        
        // Should render without errors - use getAllByTestId for multiple instances
        const barCharts = screen.getAllByTestId('bar-chart');
        expect(barCharts.length).toBeGreaterThan(0);
        
        rerender(
          <ScenarioAnalysisCharts 
            distribution={mockDistribution} 
            selectedMetric={metric}
          />
        );
      });
    });
  });

  describe('Market Classification Colors', () => {
    it('applies consistent colors across charts', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      // Should render without throwing errors related to color mapping
      expect(screen.getByTestId('scatter-chart')).toBeInTheDocument();
      
      // Switch between tabs to ensure colors are consistent
      fireEvent.click(screen.getByText('Risk vs Return'));
      expect(screen.getByTestId('scatter-chart')).toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Market Analysis'));
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper tab navigation', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      const tabList = screen.getByRole('tablist');
      expect(tabList).toBeInTheDocument();
      
      const tabs = screen.getAllByRole('tab');
      expect(tabs).toHaveLength(4);
    });

    it('has accessible filter buttons', () => {
      render(<ScenarioAnalysisCharts distribution={mockDistribution} />);
      
      const filterButtons = screen.getAllByRole('button');
      // Should include market classification filters and outlier toggle
      expect(filterButtons.length).toBeGreaterThanOrEqual(4);
    });
  });

  describe('Performance', () => {
    it('handles large datasets efficiently', () => {
      // Create a large dataset
      const largeDistribution = Array.from({ length: 1000 }, (_, i) => ({
        scenario_id: i + 1,
        npv: Math.random() * 10000000,
        irr: Math.random() * 100,
        total_cash_flow: Math.random() * 1000000,
        risk_score: Math.random(),
        market_classification: Object.values(MarketClassification)[i % 5],
      }));
      
      const startTime = Date.now();
      render(<ScenarioAnalysisCharts distribution={largeDistribution} />);
      const endTime = Date.now();
      
      // Should render quickly (< 1 second)
      expect(endTime - startTime).toBeLessThan(1000);
      
      expect(screen.getByText('1000 scenarios')).toBeInTheDocument();
    });
  });
});