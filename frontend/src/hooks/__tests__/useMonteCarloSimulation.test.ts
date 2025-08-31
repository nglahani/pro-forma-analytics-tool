/**
 * Tests for useMonteCarloSimulation Hook
 * Basic coverage for Monte Carlo simulation management
 */

import { renderHook, act } from '@testing-library/react';
import { useMonteCarloSimulation } from '../useMonteCarloSimulation';
import { apiClient } from '@/lib/api/client';
import { useToast } from '@/hooks/useToast';
import { PropertyType, RenovationStatus } from '@/types/property';

// Mock dependencies
jest.mock('@/lib/api/client', () => ({
  apiClient: {
    runMonteCarloSimulation: jest.fn(),
    startMonteCarloSimulation: jest.fn(),
    getMonteCarloStatus: jest.fn(),
    stopMonteCarloSimulation: jest.fn(),
  },
}));

jest.mock('@/hooks/useToast', () => ({
  useToast: jest.fn(),
}));

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockUseToast = useToast as jest.MockedFunction<typeof useToast>;

// Mock property data
const mockProperty = {
  property_id: 'test-property-123',
  property_name: 'Test Property',
  property_type: PropertyType.MULTIFAMILY,
  address: {
    street: '123 Test Street',
    city: 'Chicago',
    state: 'IL',
    zip_code: '60601',
    msa_code: 'CHI'
  },
  residential_units: {
    total_units: 24,
    average_rent_per_unit: 2800,
    unit_types: 'Studio, 1BR, 2BR'
  },
  commercial_units: {
    total_units: 0,
    average_rent_per_unit: 0
  },
  total_square_feet: 24000,
  year_built: 2010,
  renovation_info: {
    status: RenovationStatus.PLANNED,
    anticipated_duration_months: 6,
    estimated_cost: 500000
  },
  equity_structure: {
    investor_equity_share_pct: 75.0,
    self_cash_percentage: 30.0,
    number_of_investors: 2
  },
  financials: {
    purchase_price: 3500000,
    down_payment_percentage: 25,
    loan_terms: {
      loan_term_years: 30,
      loan_to_value_ratio: 0.75
    },
    monthly_rent_per_unit: 2800,
    other_monthly_income: 2000,
    vacancy_rate: 0.05,
    monthly_operating_expenses: 15000,
    annual_property_taxes: 35000,
    annual_insurance: 12000,
    capex_percentage: 0.10
  },
  analysis_parameters: {
    analysis_period_years: 6,
    exit_cap_rate: 0.05
  },
  analysis_date: '2024-01-01'
};

describe('useMonteCarloSimulation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseToast.mockReturnValue({
      toast: jest.fn(),
      dismiss: jest.fn(),
      toasts: [],
    });
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useMonteCarloSimulation());

    expect(result.current.results).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.progressStatus.isRunning).toBe(false);
    expect(result.current.progressStatus.progress).toBe(0);
    expect(result.current.progressStatus.stage).toBe('complete');
  });

  it('should start simulation with provided settings', async () => {
    mockApiClient.startMonteCarloSimulation.mockResolvedValue({
      simulation_id: 'sim-123',
    });
    
    const { result } = renderHook(() => useMonteCarloSimulation());

    const settings = {
      numScenarios: 1000,
      includeCorrelations: true,
      includeMarketCycles: false,
      confidenceLevel: 0.95,
    };

    await act(async () => {
      await result.current.startSimulation(mockProperty, settings);
    });

    // The hook should try async simulation first
    expect(mockApiClient.startMonteCarloSimulation).toHaveBeenCalledWith(
      mockProperty,
      settings
    );
    
    expect(result.current.progressStatus.stage).toBe('initializing');
    expect(result.current.isRunning).toBe(true);
  });

  it('should handle simulation start error', async () => {
    mockApiClient.startMonteCarloSimulation.mockRejectedValue(
      new Error('Async failed')
    );

    const { result } = renderHook(() => useMonteCarloSimulation());

    const settings = {
      numScenarios: 1000,
      includeCorrelations: true,
      includeMarketCycles: false,
      confidenceLevel: 0.95,
    };

    await act(async () => {
      await result.current.startSimulation(mockProperty, settings);
    });

    expect(result.current.error).toBe('Async failed');
    expect(result.current.progressStatus.stage).toBe('error');
  });

  it('should provide stop simulation functionality', async () => {
    const { result } = renderHook(() => useMonteCarloSimulation());

    await act(async () => {
      await result.current.stopSimulation();
    });

    expect(result.current.progressStatus.isRunning).toBe(false);
    expect(result.current.progressStatus.stage).toBe('complete');
  });

  it('should reset simulation state', () => {
    const { result } = renderHook(() => useMonteCarloSimulation());

    // Then reset
    act(() => {
      result.current.resetSimulation();
    });

    expect(result.current.results).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.progressStatus.isRunning).toBe(false);
    expect(result.current.progressStatus.progress).toBe(0);
  });

  it('should handle options callbacks', () => {
    const onProgress = jest.fn();
    const onComplete = jest.fn();
    const onError = jest.fn();

    const { result } = renderHook(() =>
      useMonteCarloSimulation({
        onProgress,
        onComplete,
        onError,
      })
    );

    expect(result.current).toBeDefined();
    // Callbacks are used internally but not directly testable without triggering actual simulations
  });

  it('should support custom retry settings', () => {
    const { result } = renderHook(() =>
      useMonteCarloSimulation({
        autoRetry: false,
        maxRetries: 5,
        pollInterval: 2000,
      })
    );

    expect(result.current).toBeDefined();
  });

  it('should provide basic simulation controls', () => {
    const { result } = renderHook(() => useMonteCarloSimulation());

    expect(result.current.canStart).toBe(true);
    expect(result.current.canStop).toBe(false);
    expect(result.current.startSimulation).toBeDefined();
    expect(result.current.stopSimulation).toBeDefined();
    expect(result.current.resetSimulation).toBeDefined();
  });
});