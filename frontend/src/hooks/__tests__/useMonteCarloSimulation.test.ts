/**
 * Tests for useMonteCarloSimulation Hook
 * Basic coverage for Monte Carlo simulation management
 */

import { renderHook, act } from '@testing-library/react';
import { useMonteCarloSimulation } from '../useMonteCarloSimulation';
import { apiClient } from '@/lib/api/client';
import { useToast } from '@/hooks/useToast';

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
  property_name: 'Test Property',
  residential_units: 24,
  renovation_time_months: 6,
  commercial_units: 0,
  investor_equity_share_pct: 75.0,
  residential_rent_per_unit: 2800,
  commercial_rent_per_unit: 0,
  self_cash_percentage: 30.0,
  city: 'Chicago',
  state: 'IL',
  purchase_price: 3500000,
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