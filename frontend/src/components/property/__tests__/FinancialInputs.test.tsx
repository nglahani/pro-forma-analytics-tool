/**
 * Tests for FinancialInputs Component
 * 
 * Tests the financial inputs form with market data defaults integration.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FinancialInputs } from '../FinancialInputs';
import { PropertyFinancials } from '@/types/property';

// Mock the useMarketDefaults hook
jest.mock('@/hooks/useMarketDefaults', () => ({
  useMarketDefaults: jest.fn(() => ({
    defaults: {
      interest_rate: 0.065,
      cap_rate: 0.055,
      rent_growth: 0.03,
      vacancy_rate: 0.05,
    },
    loading: false,
    error: null,
    fetchDefaults: jest.fn(),
    refresh: jest.fn(),
    applyDefaults: jest.fn(),
    getDefaultValue: jest.fn((key: string) => {
      const defaults: Record<string, number> = {
        interest_rate: 0.065,
        cap_rate: 0.055,
        rent_growth: 0.03,
        vacancy_rate: 0.05,
      };
      return defaults[key];
    }),
    isDataFresh: jest.fn(() => true),
  })),
}));

// Mock utility functions
jest.mock('@/lib/utils', () => ({
  textColors: {
    success: 'text-green-600',
    warning: 'text-yellow-600',
    error: 'text-red-600',
  },
  formatPercentage: (value: number) => `${(value * 100).toFixed(2)}%`,
  formatCurrency: (value: number) => `$${value.toLocaleString()}`,
}));

describe('FinancialInputs', () => {
  const mockFinancials: Partial<PropertyFinancials> = {
    purchase_price: 1000000,
    down_payment_percentage: 0.25,
    monthly_rent_per_unit: 2000,
    monthly_operating_expenses: 500,
    annual_property_taxes: 12000,
    annual_insurance: 3000,
    capex_percentage: 0.05,
    loan_terms: {
      interest_rate: 0.065,
      loan_term_years: 30,
    },
  };

  const mockOnChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all financial input fields', () => {
    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    expect(screen.getByLabelText(/purchase price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/down payment/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/interest rate/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/loan term/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/monthly rent/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/operating expenses/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/property taxes/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/insurance/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/capex/i)).toBeInTheDocument();
  });

  it('displays current values correctly', () => {
    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    expect(screen.getByDisplayValue('1000000')).toBeInTheDocument();
    expect(screen.getByDisplayValue('25')).toBeInTheDocument();
    expect(screen.getByDisplayValue('2000')).toBeInTheDocument();
    expect(screen.getByDisplayValue('500')).toBeInTheDocument();
  });

  it('calls onChange when input values change', () => {
    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    const purchasePriceInput = screen.getByDisplayValue('1000000');
    fireEvent.change(purchasePriceInput, { target: { value: '1500000' } });

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockFinancials,
      purchase_price: 1500000,
    });
  });

  it('handles percentage inputs correctly', () => {
    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    const downPaymentInput = screen.getByDisplayValue('25');
    fireEvent.change(downPaymentInput, { target: { value: '30' } });

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockFinancials,
      down_payment_percentage: 0.30,
    });
  });

  it('handles nested loan terms updates', () => {
    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    const interestRateInput = screen.getByDisplayValue('6.5');
    fireEvent.change(interestRateInput, { target: { value: '7' } });

    expect(mockOnChange).toHaveBeenCalledWith({
      ...mockFinancials,
      loan_terms: {
        ...mockFinancials.loan_terms,
        interest_rate: 0.07,
      },
    });
  });

  it('displays market defaults when available', () => {
    render(
      <FinancialInputs
        financials={{}}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    // Should display market default suggestions
    expect(screen.getByText(/market default/i)).toBeInTheDocument();
  });

  it('shows loading state when fetching market data', () => {
    // Mock loading state
    const { useMarketDefaults } = require('@/hooks/useMarketDefaults');
    useMarketDefaults.mockReturnValue({
      defaults: {},
      loading: true,
      error: null,
      fetchDefaults: jest.fn(),
      refresh: jest.fn(),
      applyDefaults: jest.fn(),
      getDefaultValue: jest.fn(),
      isDataFresh: jest.fn(() => false),
    });

    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('handles market data errors gracefully', () => {
    // Mock error state
    const { useMarketDefaults } = require('@/hooks/useMarketDefaults');
    useMarketDefaults.mockReturnValue({
      defaults: {},
      loading: false,
      error: new Error('Failed to fetch market data'),
      fetchDefaults: jest.fn(),
      refresh: jest.fn(),
      applyDefaults: jest.fn(),
      getDefaultValue: jest.fn(),
      isDataFresh: jest.fn(() => false),
    });

    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    // Should still render inputs even with error
    expect(screen.getByLabelText(/purchase price/i)).toBeInTheDocument();
  });

  it('validates numeric inputs', () => {
    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    const purchasePriceInput = screen.getByDisplayValue('1000000');
    fireEvent.change(purchasePriceInput, { target: { value: 'invalid' } });

    // Should not call onChange with invalid value
    expect(mockOnChange).not.toHaveBeenCalled();
  });

  it('displays validation errors when provided', () => {
    const errors = {
      purchase_price: 'Purchase price is required',
      down_payment_percentage: 'Down payment must be between 1% and 50%',
    };

    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
        errors={errors}
      />
    );

    expect(screen.getByText('Purchase price is required')).toBeInTheDocument();
    expect(screen.getByText('Down payment must be between 1% and 50%')).toBeInTheDocument();
  });

  it('refreshes market data when refresh button is clicked', async () => {
    const mockRefresh = jest.fn();
    const { useMarketDefaults } = require('@/hooks/useMarketDefaults');
    useMarketDefaults.mockReturnValue({
      defaults: {},
      loading: false,
      error: null,
      fetchDefaults: jest.fn(),
      refresh: mockRefresh,
      applyDefaults: jest.fn(),
      getDefaultValue: jest.fn(),
      isDataFresh: jest.fn(() => true),
    });

    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    const refreshButton = screen.getByLabelText(/refresh/i);
    fireEvent.click(refreshButton);

    expect(mockRefresh).toHaveBeenCalledTimes(1);
  });

  it('applies market defaults when apply button is clicked', async () => {
    const mockApplyDefaults = jest.fn();
    const { useMarketDefaults } = require('@/hooks/useMarketDefaults');
    useMarketDefaults.mockReturnValue({
      defaults: { interest_rate: 0.065 },
      loading: false,
      error: null,
      fetchDefaults: jest.fn(),
      refresh: jest.fn(),
      applyDefaults: mockApplyDefaults,
      getDefaultValue: jest.fn(),
      isDataFresh: jest.fn(() => true),
    });

    render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    const applyButton = screen.getByText(/apply defaults/i);
    fireEvent.click(applyButton);

    expect(mockApplyDefaults).toHaveBeenCalledWith(mockFinancials);
  });

  it('handles empty financials object', () => {
    render(
      <FinancialInputs
        financials={{}}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    // Should render without crashing
    expect(screen.getByLabelText(/purchase price/i)).toBeInTheDocument();
    
    // Fields should be empty
    const purchasePriceInput = screen.getByLabelText(/purchase price/i);
    expect(purchasePriceInput).toHaveValue('');
  });

  it('fetches market defaults when MSA code changes', () => {
    const mockFetchDefaults = jest.fn();
    const { useMarketDefaults } = require('@/hooks/useMarketDefaults');
    useMarketDefaults.mockReturnValue({
      defaults: {},
      loading: false,
      error: null,
      fetchDefaults: mockFetchDefaults,
      refresh: jest.fn(),
      applyDefaults: jest.fn(),
      getDefaultValue: jest.fn(),
      isDataFresh: jest.fn(() => true),
    });

    const { rerender } = render(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="35620"
      />
    );

    // Change MSA code
    rerender(
      <FinancialInputs
        financials={mockFinancials}
        onChange={mockOnChange}
        msaCode="31080"
      />
    );

    expect(mockFetchDefaults).toHaveBeenCalledWith('31080');
  });
});