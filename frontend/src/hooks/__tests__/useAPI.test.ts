/**
 * Tests for useAPI Hook
 * Comprehensive coverage for API state management and error handling
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { 
  useHealthCheck,
  useDCFAnalysis,
  useBatchDCFAnalysis,
  useMonteCarloSimulation,
  useMarketData,
  useForecastData,
  useSystemConfig,
  useMultipleAPICalls
} from '../useAPI';
import { apiService } from '@/lib/api/service';
import { SimplifiedPropertyInput } from '@/types/property';

// Mock the API service
jest.mock('@/lib/api/service', () => ({
  apiService: {
    checkHealth: jest.fn(),
    analyzeDCF: jest.fn(),
    analyzeBatchDCF: jest.fn(),
    runMonteCarloSimulation: jest.fn(),
    getMarketData: jest.fn(),
    getForecastData: jest.fn(),
    getSystemConfig: jest.fn(),
  },
}));

const mockApiService = apiService as jest.Mocked<typeof apiService>;

// Test data
const mockProperty: SimplifiedPropertyInput = {
  property_id: 'test-123',
  property_name: 'Test Property',
  property_type: 'residential' as any,
  address: {
    street: '123 Main St',
    city: 'New York',
    state: 'NY',
    zip_code: '10001'
  },
  residential_units: {
    total_units: 24,
    average_rent_per_unit: 2800
  },
  commercial_units: {
    total_units: 0,
    average_rent_per_unit: 0
  },
  total_square_feet: 1000,
  year_built: 2020,
  renovation_info: { status: 'NOT_NEEDED' as any },
  equity_structure: { 
    investor_equity_share_pct: 75.0,
    self_cash_percentage: 30.0 
  },
  financials: {
    purchase_price: 0,
    down_payment_percentage: 0,
    loan_terms: { loan_term_years: 30 },
    monthly_rent_per_unit: 0,
    other_monthly_income: 0,
    monthly_operating_expenses: 0,
    annual_property_taxes: 0,
    annual_insurance: 0,
    capex_percentage: 0
  },
  analysis_parameters: {
    analysis_period_years: 6
  },
  analysis_date: '2024-01-01'
};

const mockDCFResponse = {
  success: true,
  data: {
    financial_metrics: {
      npv: 1500000,
      irr: 0.15,
      equity_multiple: 2.5
    },
    investment_recommendation: 'STRONG_BUY'
  },
  error: null
};

describe('useAPI Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useHealthCheck', () => {
    it('should handle successful health check', async () => {
      const mockResponse = { 
        success: true, 
        data: { 
          status: 'healthy' as const, 
          timestamp: '2023-01-01T00:00:00Z',
          version: '1.0.0',
          environment: 'test',
          uptime_seconds: 3600,
          dependencies: {}
        }, 
        error: null 
      };
      mockApiService.checkHealth.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useHealthCheck());

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.data).toEqual({ status: 'healthy' });
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(mockApiService.checkHealth).toHaveBeenCalledTimes(1);
    });

    it('should handle API error response', async () => {
      const mockResponse = { success: false, data: null, error: 'Service unavailable' };
      mockApiService.checkHealth.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useHealthCheck());

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Service unavailable');
    });

    it('should handle network/exception errors', async () => {
      mockApiService.checkHealth.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useHealthCheck());

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Network error');
    });

    it('should handle non-Error exceptions', async () => {
      mockApiService.checkHealth.mockRejectedValue('String error');

      const { result } = renderHook(() => useHealthCheck());

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.error).toBe('Unknown error occurred');
    });

    it('should reset state correctly', async () => {
      const mockResponse = { 
        success: true, 
        data: { 
          status: 'healthy' as const, 
          timestamp: '2023-01-01T00:00:00Z',
          version: '1.0.0',
          environment: 'test',
          uptime_seconds: 3600,
          dependencies: {}
        }, 
        error: null 
      };
      mockApiService.checkHealth.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useHealthCheck());

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.data).not.toBeNull();

      act(() => {
        result.current.reset();
      });

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should set loading state during execution', async () => {
      let resolvePromise: (value: { success: boolean; data: any; error: string | null; }) => void;
      const promise = new Promise<{ success: boolean; data: any; error: string | null; }>(resolve => { resolvePromise = resolve; });
      mockApiService.checkHealth.mockReturnValue(promise);

      const { result } = renderHook(() => useHealthCheck());

      act(() => {
        result.current.execute();
      });

      expect(result.current.loading).toBe(true);
      expect(result.current.error).toBeNull();

      act(() => {
        resolvePromise!({ success: true, data: { status: 'healthy' }, error: null });
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });
  });

  describe('useDCFAnalysis', () => {
    it('should handle successful DCF analysis', async () => {
      mockApiService.analyzeDCF.mockResolvedValue(mockDCFResponse);

      const { result } = renderHook(() => useDCFAnalysis());

      await act(async () => {
        await result.current.execute(mockProperty);
      });

      expect(result.current.data).toEqual(mockDCFResponse.data);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(mockApiService.analyzeDCF).toHaveBeenCalledWith(mockProperty);
    });

    it('should handle DCF analysis errors', async () => {
      const errorResponse = { success: false, data: null, error: 'Invalid property data' };
      mockApiService.analyzeDCF.mockResolvedValue(errorResponse);

      const { result } = renderHook(() => useDCFAnalysis());

      await act(async () => {
        await result.current.execute(mockProperty);
      });

      expect(result.current.data).toBeNull();
      expect(result.current.error).toBe('Invalid property data');
    });
  });

  describe('useBatchDCFAnalysis', () => {
    it('should handle batch DCF analysis', async () => {
      const batchResponse = { success: true, data: [mockDCFResponse.data], error: null };
      mockApiService.analyzeBatchDCF.mockResolvedValue(batchResponse);

      const { result } = renderHook(() => useBatchDCFAnalysis());

      await act(async () => {
        await result.current.execute([mockProperty]);
      });

      expect(result.current.data).toEqual([mockDCFResponse.data]);
      expect(mockApiService.analyzeBatchDCF).toHaveBeenCalledWith([mockProperty]);
    });
  });

  describe('useMonteCarloSimulation', () => {
    it('should handle Monte Carlo simulation with scenarios', async () => {
      const mcResponse = { 
        success: true, 
        data: { scenarios_completed: 1000, distribution: {} }, 
        error: null 
      };
      mockApiService.runMonteCarloSimulation.mockResolvedValue(mcResponse);

      const { result } = renderHook(() => useMonteCarloSimulation());

      await act(async () => {
        await result.current.execute(mockProperty, 1000);
      });

      expect(result.current.data).toEqual(mcResponse.data);
      expect(mockApiService.runMonteCarloSimulation).toHaveBeenCalledWith(mockProperty, 1000);
    });

    it('should handle Monte Carlo simulation without scenarios parameter', async () => {
      const mcResponse = { 
        success: true, 
        data: { scenarios_completed: 500, distribution: {} }, 
        error: null 
      };
      mockApiService.runMonteCarloSimulation.mockResolvedValue(mcResponse);

      const { result } = renderHook(() => useMonteCarloSimulation());

      await act(async () => {
        await result.current.execute(mockProperty);
      });

      expect(mockApiService.runMonteCarloSimulation).toHaveBeenCalledWith(mockProperty, undefined);
    });
  });

  describe('useMarketData', () => {
    it('should handle market data retrieval', async () => {
      const marketResponse = { 
        success: true, 
        data: { msa: 'NYC', parameters: [] }, 
        error: null 
      };
      mockApiService.getMarketData.mockResolvedValue(marketResponse);

      const { result } = renderHook(() => useMarketData());

      await act(async () => {
        await result.current.execute('NYC', ['interest_rates']);
      });

      expect(result.current.data).toEqual(marketResponse.data);
      expect(mockApiService.getMarketData).toHaveBeenCalledWith('NYC', ['interest_rates']);
    });
  });

  describe('useForecastData', () => {
    it('should handle forecast data retrieval', async () => {
      const forecastResponse = { 
        success: true, 
        data: { parameter: 'interest_rates', forecast: [] }, 
        error: null 
      };
      mockApiService.getForecastData.mockResolvedValue(forecastResponse);

      const { result } = renderHook(() => useForecastData());

      await act(async () => {
        await result.current.execute('interest_rates', 'NYC', 60);
      });

      expect(result.current.data).toEqual(forecastResponse.data);
      expect(mockApiService.getForecastData).toHaveBeenCalledWith('interest_rates', 'NYC', 60);
    });
  });

  describe('useSystemConfig', () => {
    it('should handle system configuration retrieval', async () => {
      const configResponse = { 
        success: true, 
        data: { 
          database_info: {},
          api_settings: {},
          forecast_settings: {}
        }, 
        error: null 
      };
      mockApiService.getSystemConfig.mockResolvedValue(configResponse);

      const { result } = renderHook(() => useSystemConfig());

      await act(async () => {
        await result.current.execute();
      });

      expect(result.current.data).toEqual(configResponse.data);
      expect(mockApiService.getSystemConfig).toHaveBeenCalledTimes(1);
    });
  });

  describe('useMultipleAPICalls', () => {
    it('should handle multiple API calls independently', async () => {
      const { result } = renderHook(() => useMultipleAPICalls());

      const healthResponse = { 
        success: true, 
        data: { 
          status: 'healthy' as const, 
          timestamp: '2023-01-01T00:00:00Z',
          version: '1.0.0',
          environment: 'test',
          uptime_seconds: 3600,
          dependencies: {}
        }, 
        error: null 
      };
      const configResponse = { 
        success: true, 
        data: { 
          database_info: {},
          api_settings: {},
          forecast_settings: {}
        }, 
        error: null 
      };

      mockApiService.checkHealth.mockResolvedValue(healthResponse);
      mockApiService.getSystemConfig.mockResolvedValue(configResponse);

      await act(async () => {
        await result.current.executeCall('health', mockApiService.checkHealth);
      });

      await act(async () => {
        await result.current.executeCall('config', mockApiService.getSystemConfig);
      });

      expect(result.current.getState('health').data).toEqual(healthResponse.data);
      expect(result.current.getState('config').data).toEqual(configResponse.data);
      expect(result.current.allLoading).toBe(false);
      expect(result.current.hasErrors).toBe(false);
    });

    it('should track loading states correctly', async () => {
      const { result } = renderHook(() => useMultipleAPICalls());

      let resolvePromise: (value: { success: boolean; data: unknown; error: string | null; }) => void;
      const promise = new Promise<{ success: boolean; data: unknown; error: string | null; }>(resolve => { resolvePromise = resolve; });
      
      act(() => {
        result.current.executeCall('test', () => promise);
      });

      expect(result.current.getState('test').loading).toBe(true);
      expect(result.current.allLoading).toBe(true);

      act(() => {
        resolvePromise!({ success: true, data: 'test', error: null });
      });

      await waitFor(() => {
        expect(result.current.getState('test').loading).toBe(false);
        expect(result.current.allLoading).toBe(false);
      });
    });

    it('should handle errors in multiple calls', async () => {
      const { result } = renderHook(() => useMultipleAPICalls());

      const errorResponse = { success: false, data: null, error: 'API error' };

      await act(async () => {
        await result.current.executeCall('error-test', () => Promise.resolve(errorResponse));
      });

      expect(result.current.getState('error-test').error).toBe('API error');
      expect(result.current.hasErrors).toBe(true);
    });

    it('should handle exceptions in multiple calls', async () => {
      const { result } = renderHook(() => useMultipleAPICalls());

      await act(async () => {
        await result.current.executeCall('exception-test', () => Promise.reject(new Error('Network error')));
      });

      expect(result.current.getState('exception-test').error).toBe('Network error');
      expect(result.current.hasErrors).toBe(true);
    });

    it('should reset individual states', () => {
      const { result } = renderHook(() => useMultipleAPICalls());

      act(() => {
        result.current.executeCall('test', () => Promise.resolve({ success: true, data: 'test', error: null }));
      });

      act(() => {
        result.current.reset('test');
      });

      expect(result.current.getState('test').data).toBeNull();
      expect(result.current.getState('test').loading).toBe(false);
      expect(result.current.getState('test').error).toBeNull();
    });

    it('should reset all states', () => {
      const { result } = renderHook(() => useMultipleAPICalls());

      act(() => {
        result.current.executeCall('test1', () => Promise.resolve({ success: true, data: 'test1', error: null }));
        result.current.executeCall('test2', () => Promise.resolve({ success: true, data: 'test2', error: null }));
      });

      act(() => {
        result.current.reset();
      });

      expect(result.current.getState('test1').data).toBeNull();
      expect(result.current.getState('test2').data).toBeNull();
    });

    it('should return default state for unknown keys', () => {
      const { result } = renderHook(() => useMultipleAPICalls());

      const state = result.current.getState('nonexistent');
      expect(state.data).toBeNull();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle null error with fallback message', async () => {
      const { result } = renderHook(() => useMultipleAPICalls());

      const errorResponse = { success: false, data: null, error: null };

      await act(async () => {
        await result.current.executeCall('null-error-test', () => Promise.resolve(errorResponse));
      });

      expect(result.current.getState('null-error-test').error).toBe('Unknown error occurred');
    });
  });
});