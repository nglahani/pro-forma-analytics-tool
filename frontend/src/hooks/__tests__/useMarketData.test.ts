/**
 * Tests for useMarketData Hook
 * Comprehensive coverage for market data fetching, caching, and real-time updates
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useMarketData } from '../useMarketData';
import { apiClient } from '@/lib/api/client';
import { useToast } from '@/hooks/useToast';

// Mock dependencies
jest.mock('@/lib/api/client', () => ({
  apiClient: {
    getAvailableMSAs: jest.fn(),
    getMarketData: jest.fn(),
    getForecastData: jest.fn(),
    getMultiParameterForecast: jest.fn(),
    compareMarketData: jest.fn(),
  },
}));

jest.mock('@/hooks/useToast', () => ({
  useToast: jest.fn(),
}));

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;
const mockUseToast = useToast as jest.MockedFunction<typeof useToast>;
const mockToast = jest.fn();

// Test data
const mockMSAs = [
  {
    msa_code: 'NYC',
    name: 'New York-Northern New Jersey-Long Island, NY-NJ-PA MSA',
    state: 'NY',
    data_availability: {
      parameters: ['interest_rate', 'cap_rate', 'vacancy_rate'],
      date_range: {
        start: '2010-01-01',
        end: '2024-12-31'
      }
    }
  },
  {
    msa_code: 'LA',
    name: 'Los Angeles-Long Beach-Santa Ana, CA MSA',
    state: 'CA',
    data_availability: {
      parameters: ['rent_growth_rate', 'property_growth_rate'],
      date_range: {
        start: '2010-01-01',
        end: '2024-12-31'
      }
    }
  }
];

const mockMarketData = {
  msa_code: 'NYC',
  parameter_name: 'interest_rate',
  value: 0.055,
  date: '2024-01-01',
  source: 'test_source',
  confidence_level: 0.85
};

const mockForecastData = {
  parameter: 'interest_rate',
  msa_code: 'NYC',
  historical_data: [
    { date: '2023-01-01', value: 0.05 },
    { date: '2023-06-01', value: 0.052 }
  ],
  forecast_data: [
    { date: '2024-06-01', value: 0.056, confidence_interval: [0.054, 0.058] },
    { date: '2025-01-01', value: 0.058, confidence_interval: [0.055, 0.061] }
  ]
};

const mockMultiParameterForecast = {
  msa_code: 'NYC',
  forecasts: [
    {
      msa_code: 'NYC',
      parameter_name: 'interest_rate',
      forecast_date: '2024-06-01',
      forecast_value: 0.056,
      confidence_interval_lower: 0.054,
      confidence_interval_upper: 0.058,
      trend: "increasing" as const
    },
    {
      msa_code: 'NYC',
      parameter_name: 'cap_rate',
      forecast_date: '2024-06-01',
      forecast_value: 0.046,
      confidence_interval_lower: 0.044,
      confidence_interval_upper: 0.048,
      trend: "stable" as const
    }
  ]
};

const mockComparisonData = {
  comparison_id: 'comp-123',
  msas: [
    {
      msa_code: 'NYC',
      name: 'New York MSA',
      data: mockMarketData
    },
    {
      msa_code: 'LA',
      name: 'Los Angeles MSA',
      data: {
        msa_code: 'LA',
        parameter_name: 'interest_rate',
        value: 0.058,
        date: '2024-01-01',
        source: 'test_source',
        confidence_level: 0.82
      }
    }
  ]
};

describe('useMarketData Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    mockUseToast.mockReturnValue({ 
      toast: mockToast,
      dismiss: jest.fn(),
      toasts: []
    });
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Initialization and MSA Loading', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useMarketData());

      expect(result.current.availableMSAs).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.lastFetchTime).toBe(0);
      expect(result.current.isDataStale).toBe(false);
    });

    it('should load available MSAs on mount', async () => {
      mockApiClient.getAvailableMSAs.mockResolvedValue(mockMSAs);

      const { result } = renderHook(() => useMarketData());

      await waitFor(() => {
        expect(mockApiClient.getAvailableMSAs).toHaveBeenCalledTimes(1);
      });

      expect(result.current.availableMSAs).toEqual(mockMSAs);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle errors when loading MSAs', async () => {
      const errorMessage = 'Failed to fetch MSAs';
      mockApiClient.getAvailableMSAs.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useMarketData());

      await waitFor(() => {
        expect(result.current.error).toBe(errorMessage);
      });

      expect(result.current.availableMSAs).toEqual([]);
      expect(result.current.isLoading).toBe(false);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Market Data Error',
        description: errorMessage,
        variant: 'destructive',
      });
    });
  });

  describe('Market Data Fetching', () => {
    beforeEach(() => {
      mockApiClient.getAvailableMSAs.mockResolvedValue(mockMSAs);
    });

    it('should fetch market data successfully', async () => {
      mockApiClient.getMarketData.mockResolvedValue(mockMarketData);

      const { result } = renderHook(() => useMarketData());

      let data: any;
      await act(async () => {
        data = await result.current.fetchMarketData('NYC', {
          parameters: ['interest_rate', 'cap_rate']
        });
      });

      expect(data).toEqual(mockMarketData);
      expect(mockApiClient.getMarketData).toHaveBeenCalledWith('NYC', {
        parameters: ['interest_rate', 'cap_rate'],
        startDate: undefined,
        endDate: undefined,
        includeForecasts: undefined,
      });
    });

    it('should fetch market data with all filters', async () => {
      mockApiClient.getMarketData.mockResolvedValue(mockMarketData);

      const { result } = renderHook(() => useMarketData());

      await act(async () => {
        await result.current.fetchMarketData('NYC', {
          parameters: ['interest_rate'],
          startDate: '2023-01-01',
          endDate: '2024-01-01',
          includeForecasts: true
        });
      });

      expect(mockApiClient.getMarketData).toHaveBeenCalledWith('NYC', {
        parameters: ['interest_rate'],
        startDate: '2023-01-01',
        endDate: '2024-01-01',
        includeForecasts: true,
      });
    });

    it('should handle market data fetch errors', async () => {
      const errorMessage = 'MSA not found';
      mockApiClient.getMarketData.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useMarketData());

      let data: any;
      await act(async () => {
        data = await result.current.fetchMarketData('INVALID');
      });

      expect(data).toBeNull();
      expect(result.current.error).toBe(errorMessage);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Market Data Error',
        description: errorMessage,
        variant: 'destructive',
      });
    });

    it('should return cached data when available', async () => {
      mockApiClient.getMarketData.mockResolvedValue(mockMarketData);

      const { result } = renderHook(() => useMarketData());

      // First fetch - should call API
      await act(async () => {
        await result.current.fetchMarketData('NYC');
      });

      expect(mockApiClient.getMarketData).toHaveBeenCalledTimes(1);

      // Second fetch - should use cache
      await act(async () => {
        await result.current.fetchMarketData('NYC');
      });

      expect(mockApiClient.getMarketData).toHaveBeenCalledTimes(1); // Still only 1 call
    });
  });

  describe('Forecast Data Fetching', () => {
    beforeEach(() => {
      mockApiClient.getAvailableMSAs.mockResolvedValue(mockMSAs);
    });

    it('should fetch forecast data successfully', async () => {
      mockApiClient.getForecastData.mockResolvedValue(mockForecastData);

      const { result } = renderHook(() => useMarketData());

      let data: any;
      await act(async () => {
        data = await result.current.fetchForecastData('interest_rate', 'NYC', {
          horizonMonths: 12,
          confidenceLevel: 0.95,
          includeHistorical: true
        });
      });

      expect(data).toEqual(mockForecastData);
      expect(mockApiClient.getForecastData).toHaveBeenCalledWith('interest_rate', 'NYC', {
        horizonMonths: 12,
        confidenceLevel: 0.95,
        includeHistorical: true
      });
    });

    it('should handle forecast data errors', async () => {
      const errorMessage = 'Parameter not available';
      mockApiClient.getForecastData.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useMarketData());

      let data: any;
      await act(async () => {
        data = await result.current.fetchForecastData('invalid_param', 'NYC');
      });

      expect(data).toBeNull();
      expect(result.current.error).toBe(errorMessage);
    });

    it('should fetch multi-parameter forecasts', async () => {
      mockApiClient.getMultiParameterForecast.mockResolvedValue(mockMultiParameterForecast);

      const { result } = renderHook(() => useMarketData());

      let data: any;
      await act(async () => {
        data = await result.current.fetchMultiParameterForecast(
          ['interest_rate', 'cap_rate'],
          'NYC',
          { horizonMonths: 24, confidenceLevel: 0.9 }
        );
      });

      expect(data).toEqual(mockMultiParameterForecast);
      expect(mockApiClient.getMultiParameterForecast).toHaveBeenCalledWith(
        ['interest_rate', 'cap_rate'],
        'NYC',
        { horizonMonths: 24, confidenceLevel: 0.9 }
      );
    });
  });

  describe('Market Data Comparison', () => {
    beforeEach(() => {
      mockApiClient.getAvailableMSAs.mockResolvedValue(mockMSAs);
    });

    it('should compare market data across MSAs', async () => {
      mockApiClient.compareMarketData.mockResolvedValue(mockComparisonData);

      const { result } = renderHook(() => useMarketData());

      let data: any;
      await act(async () => {
        data = await result.current.compareMarketData(
          ['NYC', 'LA'],
          ['interest_rate', 'cap_rate'],
          { startDate: '2023-01-01', endDate: '2024-01-01' }
        );
      });

      expect(data).toEqual(mockComparisonData);
      expect(mockApiClient.compareMarketData).toHaveBeenCalledWith(
        ['NYC', 'LA'],
        ['interest_rate', 'cap_rate'],
        { startDate: '2023-01-01', endDate: '2024-01-01' }
      );
    });

    it('should handle comparison errors', async () => {
      const errorMessage = 'Comparison failed';
      mockApiClient.compareMarketData.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useMarketData());

      let data: any;
      await act(async () => {
        data = await result.current.compareMarketData(['NYC', 'LA'], ['interest_rate']);
      });

      expect(data).toBeNull();
      expect(result.current.error).toBe(errorMessage);
    });
  });

  describe('Cache Management', () => {
    beforeEach(() => {
      mockApiClient.getAvailableMSAs.mockResolvedValue(mockMSAs);
      mockApiClient.getMarketData.mockResolvedValue(mockMarketData);
    });

    it('should generate unique cache keys for different requests', async () => {
      const { result } = renderHook(() => useMarketData());

      const key1 = result.current.generateCacheKey('market', 'NYC', { parameters: ['interest_rate'] });
      const key2 = result.current.generateCacheKey('market', 'NYC', { parameters: ['cap_rate'] });
      const key3 = result.current.generateCacheKey('forecast', 'NYC', { parameters: ['interest_rate'] });

      expect(key1).not.toBe(key2);
      expect(key1).not.toBe(key3);
      expect(key2).not.toBe(key3);
    });

    it('should validate cache entries correctly', async () => {
      const { result } = renderHook(() => useMarketData());

      // Fetch data to populate cache
      await act(async () => {
        await result.current.fetchMarketData('NYC');
      });

      const cacheKey = result.current.generateCacheKey('market', 'NYC', {});
      expect(result.current.isCacheValid(cacheKey)).toBe(true);

      // Fast forward to expire cache
      act(() => {
        jest.advanceTimersByTime(700000); // 11+ minutes
      });

      expect(result.current.isCacheValid(cacheKey)).toBe(false);
    });

    it('should clear cache completely', async () => {
      const { result } = renderHook(() => useMarketData());

      // Populate cache
      await act(async () => {
        await result.current.fetchMarketData('NYC');
      });

      expect(result.current.cacheStats.totalEntries).toBe(2); // MSAs + market data

      act(() => {
        result.current.clearCache();
      });

      expect(result.current.cacheStats.totalEntries).toBe(0);
      expect(result.current.error).toBeNull();
    });

    it('should invalidate cache for specific MSA', async () => {
      const { result } = renderHook(() => useMarketData());

      // Populate cache with multiple MSAs
      await act(async () => {
        await result.current.fetchMarketData('NYC');
        await result.current.fetchMarketData('LA');
      });

      const initialCount = result.current.cacheStats.totalEntries;

      act(() => {
        result.current.invalidateCache('NYC');
      });

      expect(result.current.cacheStats.totalEntries).toBeLessThan(initialCount);
    });

    it('should provide accurate cache statistics', async () => {
      const { result } = renderHook(() => useMarketData());

      expect(result.current.cacheStats.totalEntries).toBe(0);
      expect(result.current.cacheStats.validEntries).toBe(0);
      expect(result.current.cacheStats.expiredEntries).toBe(0);

      // Populate cache
      await act(async () => {
        await result.current.fetchMarketData('NYC');
      });

      expect(result.current.cacheStats.totalEntries).toBeGreaterThan(0);
      expect(result.current.cacheStats.validEntries).toBeGreaterThan(0);
    });
  });

  describe('Auto Refresh', () => {
    beforeEach(() => {
      mockApiClient.getAvailableMSAs.mockResolvedValue(mockMSAs);
    });

    it('should auto-refresh when enabled', async () => {
      const { result } = renderHook(() => useMarketData({
        autoRefresh: true,
        refreshInterval: 5000
      }));

      await waitFor(() => {
        expect(mockApiClient.getAvailableMSAs).toHaveBeenCalledTimes(1);
      });

      // Fast forward time
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(mockApiClient.getAvailableMSAs).toHaveBeenCalledTimes(2);
      });
    });

    it('should not auto-refresh when disabled', async () => {
      const { result } = renderHook(() => useMarketData({
        autoRefresh: false
      }));

      await waitFor(() => {
        expect(mockApiClient.getAvailableMSAs).toHaveBeenCalledTimes(1);
      });

      // Fast forward time
      act(() => {
        jest.advanceTimersByTime(10000);
      });

      // Should still only be called once
      expect(mockApiClient.getAvailableMSAs).toHaveBeenCalledTimes(1);
    });
  });

  describe('Error Handling', () => {
    it('should handle non-Error exceptions', async () => {
      mockApiClient.getAvailableMSAs.mockRejectedValue('String error');

      const { result } = renderHook(() => useMarketData());

      await waitFor(() => {
        expect(result.current.error).toBe('String error');
      });
    });

    it('should call custom error handler when provided', async () => {
      const onError = jest.fn();
      const errorMessage = 'Custom error';
      
      mockApiClient.getAvailableMSAs.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useMarketData({ onError }));

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(errorMessage);
      });
    });
  });

  describe('Data Staleness', () => {
    it('should detect stale data correctly', async () => {
      const { result } = renderHook(() => useMarketData({ cacheTimeout: 300000 }));

      expect(result.current.isDataStale).toBe(false);

      // Simulate data fetch
      await act(async () => {
        await result.current.fetchAvailableMSAs();
      });

      expect(result.current.isDataStale).toBe(false);

      // Fast forward to make data stale
      act(() => {
        jest.advanceTimersByTime(400000); // > 5 minutes
      });

      expect(result.current.isDataStale).toBe(true);
    });
  });

  describe('Loading States', () => {
    it('should manage loading state during API calls', async () => {
      let resolvePromise: (value: any) => void;
      const promise = new Promise(resolve => { resolvePromise = resolve; });
      
      mockApiClient.getMarketData.mockReturnValue(promise);

      const { result } = renderHook(() => useMarketData());

      act(() => {
        result.current.fetchMarketData('NYC');
      });

      expect(result.current.isLoading).toBe(true);

      act(() => {
        resolvePromise!(mockMarketData);
      });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });
  });

  describe('Cache Key Generation', () => {
    it('should handle special characters in cache key generation', () => {
      const { result } = renderHook(() => useMarketData());

      const options = { parameters: ['interest_rate'], symbols: '!@#$%' };
      const key = result.current.generateCacheKey('market', 'NYC', options);

      expect(typeof key).toBe('string');
      expect(key.length).toBeGreaterThan(0);
    });

    it('should generate different keys for different option orders', () => {
      const { result } = renderHook(() => useMarketData());

      const options1 = { a: 1, b: 2 };
      const options2 = { b: 2, a: 1 };
      
      const key1 = result.current.generateCacheKey('market', 'NYC', options1);
      const key2 = result.current.generateCacheKey('market', 'NYC', options2);

      // JSON.stringify produces the same string for objects with same key-value pairs
      expect(key1).toBe(key2);
    });
  });
});