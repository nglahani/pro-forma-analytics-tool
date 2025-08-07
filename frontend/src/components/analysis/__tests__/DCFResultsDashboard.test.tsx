/**
 * Tests for DCFResultsDashboard Component
 * 
 * Tests the DCF analysis results dashboard including
 * financial metrics display and investment recommendations.
 */

import { render, screen } from '@testing-library/react';
import { DCFResultsDashboard } from '../DCFResultsDashboard';
import { DCFAnalysisResult } from '@/types/analysis';

// Mock utility functions
jest.mock('@/lib/utils', () => ({
  formatCurrency: (value: number) => `$${value.toLocaleString()}`,
  formatPercentage: (value: number) => `${(value * 100).toFixed(1)}%`,
  formatNumber: (value: number) => value.toFixed(1),
  getRecommendationStyle: (rec: string) => ({
    color: rec.includes('BUY') ? 'text-green-600' : 'text-red-600',
    bgColor: 'bg-gray-100',
  }),
  textColors: {
    success: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600',
  },
}));

describe('DCFResultsDashboard', () => {
  const mockAnalysisResult: DCFAnalysisResult = {
    property_id: 'test_prop_001',
    analysis_date: '2025-01-15',
    financial_metrics: {
      net_present_value: 2500000,
      internal_rate_return: 0.18,
      equity_multiple: 2.5,
      payback_period: 4.2,
      cash_on_cash_return: 0.12,
      return_on_investment: 0.25,
      investment_recommendation: 'STRONG_BUY',
      risk_assessment: 'MODERATE',
    },
    initial_numbers: {
      purchase_price: 1000000,
      total_cash_required: 250000,
      loan_amount: 750000,
    },
    cash_flow_projections: {
      annual_projections: [],
      total_distributions: 300000,
    },
  };

  it('renders financial metrics correctly', () => {
    render(<DCFResultsDashboard analysis={mockAnalysisResult} />);

    expect(screen.getByText('$2,500,000')).toBeInTheDocument(); // NPV
    expect(screen.getByText('18.0%')).toBeInTheDocument(); // IRR
    expect(screen.getByText('2.5x')).toBeInTheDocument(); // Equity Multiple
    expect(screen.getByText('4.2')).toBeInTheDocument(); // Payback Period
  });

  it('displays investment recommendation correctly', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    expect(screen.getByText('STRONG_BUY')).toBeInTheDocument();
    expect(screen.getByText('MODERATE')).toBeInTheDocument(); // Risk level
    expect(screen.getByText('92%')).toBeInTheDocument(); // Confidence score
    expect(screen.getByText(/strong positive npv/i)).toBeInTheDocument();
  });

  it('shows cash flow summary', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    expect(screen.getByText('$300,000')).toBeInTheDocument(); // Total pre-tax
    expect(screen.getByText('$210,000')).toBeInTheDocument(); // Total after-tax
  });

  it('displays scenario analysis results', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    // Base case
    expect(screen.getByText('$2,500,000')).toBeInTheDocument();
    expect(screen.getByText('18.0%')).toBeInTheDocument();

    // Optimistic case
    expect(screen.getByText('$3,200,000')).toBeInTheDocument();
    expect(screen.getByText('24.0%')).toBeInTheDocument();

    // Pessimistic case
    expect(screen.getByText('$1,800,000')).toBeInTheDocument();
    expect(screen.getByText('12.0%')).toBeInTheDocument();
  });

  it('shows sensitivity analysis information', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    expect(screen.getByText('High sensitivity to rent growth')).toBeInTheDocument();
    expect(screen.getByText('Moderate sensitivity to vacancy')).toBeInTheDocument();
    expect(screen.getByText('High sensitivity to cap rate changes')).toBeInTheDocument();
  });

  it('applies correct styling for STRONG_BUY recommendation', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    const recommendationElement = screen.getByText('STRONG_BUY');
    expect(recommendationElement).toHaveClass('text-green-600');
  });

  it('applies correct styling for MODERATE risk level', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    const riskElement = screen.getByText('MODERATE');
    expect(riskElement).toHaveClass('text-yellow-600');
  });

  it('handles SELL recommendation with appropriate styling', () => {
    const sellResult = {
      ...mockAnalysisResult,
      investment_recommendation: {
        ...mockAnalysisResult.investment_recommendation,
        recommendation: 'SELL' as const,
        risk_level: 'HIGH' as const,
      },
    };

    render(<DCFResultsDashboard result={sellResult} />);

    const recommendationElement = screen.getByText('SELL');
    expect(recommendationElement).toHaveClass('text-red-600');

    const riskElement = screen.getByText('HIGH');
    expect(riskElement).toHaveClass('text-red-600');
  });

  it('displays processing time and metadata', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    expect(screen.getByText('2.3s')).toBeInTheDocument();
    expect(screen.getByText('1.0.0')).toBeInTheDocument();
  });

  it('handles missing optional data gracefully', () => {
    const incompleteResult = {
      ...mockAnalysisResult,
      cash_flows: undefined,
      scenarios: undefined,
      sensitivity_analysis: undefined,
    };

    render(<DCFResultsDashboard result={incompleteResult} />);

    // Should still render core financial metrics
    expect(screen.getByText('$2,500,000')).toBeInTheDocument();
    expect(screen.getByText('18.0%')).toBeInTheDocument();
    expect(screen.getByText('STRONG_BUY')).toBeInTheDocument();
  });

  it('formats large numbers correctly', () => {
    const largeNumberResult = {
      ...mockAnalysisResult,
      financial_metrics: {
        ...mockAnalysisResult.financial_metrics,
        net_present_value: 15000000, // $15M
      },
    };

    render(<DCFResultsDashboard result={largeNumberResult} />);

    expect(screen.getByText('$15,000,000')).toBeInTheDocument();
  });

  it('handles negative NPV correctly', () => {
    const negativeResult = {
      ...mockAnalysisResult,
      financial_metrics: {
        ...mockAnalysisResult.financial_metrics,
        net_present_value: -500000,
      },
      investment_recommendation: {
        ...mockAnalysisResult.investment_recommendation,
        recommendation: 'STRONG_SELL' as const,
      },
    };

    render(<DCFResultsDashboard result={negativeResult} />);

    expect(screen.getByText('$-500,000')).toBeInTheDocument();
    expect(screen.getByText('STRONG_SELL')).toBeInTheDocument();
  });

  it('displays all required financial metrics labels', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    expect(screen.getByText(/net present value/i)).toBeInTheDocument();
    expect(screen.getByText(/internal rate of return/i)).toBeInTheDocument();
    expect(screen.getByText(/equity multiple/i)).toBeInTheDocument();
    expect(screen.getByText(/payback period/i)).toBeInTheDocument();
    expect(screen.getByText(/cash on cash/i)).toBeInTheDocument();
  });

  it('provides accessible content structure', () => {
    render(<DCFResultsDashboard result={mockAnalysisResult} />);

    // Should have proper heading structure
    const headings = screen.getAllByRole('heading');
    expect(headings.length).toBeGreaterThan(0);

    // Should have tabular data for metrics
    const cells = screen.getAllByRole('cell');
    expect(cells.length).toBeGreaterThan(0);
  });

  it('handles edge case with very high IRR', () => {
    const highIRRResult = {
      ...mockAnalysisResult,
      financial_metrics: {
        ...mockAnalysisResult.financial_metrics,
        internal_rate_return: 2.5, // 250% IRR
      },
    };

    render(<DCFResultsDashboard result={highIRRResult} />);

    expect(screen.getByText('250.0%')).toBeInTheDocument();
  });

  it('handles zero values appropriately', () => {
    const zeroValuesResult = {
      ...mockAnalysisResult,
      financial_metrics: {
        ...mockAnalysisResult.financial_metrics,
        payback_period: 0,
        cash_on_cash_return: 0,
      },
    };

    render(<DCFResultsDashboard result={zeroValuesResult} />);

    expect(screen.getByText('0')).toBeInTheDocument(); // Payback period
    expect(screen.getByText('0.0%')).toBeInTheDocument(); // Cash on cash return
  });
});