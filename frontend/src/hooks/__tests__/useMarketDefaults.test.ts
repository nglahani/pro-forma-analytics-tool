/**
 * Tests for useMarketDefaults Hook
 * Following TDD practices - tests written before implementation
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useMarketDefaults, formatMarketDefault, getParameterDisplayName } from '../useMarketDefaults';
import { apiService } from '@/lib/api/service';

// Mock the API service
jest.mock('@/lib/api/service', () => ({
  apiService: {
    getMarketDataDefaults: jest.fn(),
  },
}));

const mockApiService = apiService as jest.Mocked<typeof apiService>;

describe('useMarketDefaults', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with correct default state', () => {
      const { result } = renderHook(() => useMarketDefaults());

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.lastUpdated).toBeNull();
      expect(result.current.msaCode).toBeNull();
    });

    it('should provide all required methods', () => {
      const { result } = renderHook(() => useMarketDefaults());

      expect(typeof result.current.fetchDefaults).toBe('function');
      expect(typeof result.current.applyDefaults).toBe('function');
      expect(typeof result.current.getDefaultValue).toBe('function');
      expect(typeof result.current.isDataFresh).toBe('function');
      expect(typeof result.current.refresh).toBe('function');
    });
  });

  describe('fetchDefaults', () => {
    it('should handle missing MSA code', async () => {
      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('');
      });

      expect(result.current.data).toBeNull();
      expect(result.current.error).toBe('MSA code is required');
      expect(result.current.loading).toBe(false);
    });

    it('should fetch market defaults from API successfully', async () => {
      const mockData = {
        cap_rate: 0.045,
        interest_rate: 0.070,
        vacancy_rate: 0.050,
        rent_growth_rate: 0.035,
        expense_growth_rate: 0.025,
        property_growth_rate: 0.030,
        ltv_ratio: 0.750,
        closing_cost_pct: 0.030,
        lender_reserves_months: 3.0,
        management_fee_pct: 0.080,
        maintenance_reserve_per_unit: 600,
      };

      mockApiService.getMarketDataDefaults.mockResolvedValue({
        success: true,
        data: mockData,
        error: null,
      });

      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(result.current.data).toEqual(mockData);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.msaCode).toBe('35620');
      expect(result.current.lastUpdated).toBeInstanceOf(Date);
    });

    it('should use fallback defaults when API fails', async () => {
      mockApiService.getMarketDataDefaults.mockRejectedValue(
        new Error('API unavailable')
      );

      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.cap_rate).toBe(0.045); // NYC fallback
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should show loading state during fetch', async () => {
      mockApiService.getMarketDataDefaults.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          success: true,
          data: {},
          error: null
        }), 100))
      );

      const { result } = renderHook(() => useMarketDefaults());

      act(() => {
        result.current.fetchDefaults('35620');
      });

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });
  });

  describe('applyDefaults', () => {
    it('should apply all defaults to target object', async () => {
      const mockData = {
        cap_rate: 0.045,
        interest_rate: 0.070,
        vacancy_rate: 0.050,
      };

      mockApiService.getMarketDataDefaults.mockResolvedValue({
        success: true,
        data: mockData,
        error: null,
      });

      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      const targetObject = { existing_field: 'value' };
      const updatedObject = result.current.applyDefaults(targetObject);

      expect(updatedObject).toEqual({
        existing_field: 'value',
        cap_rate: 0.045,
        interest_rate: 0.070,
        vacancy_rate: 0.050,
      });
    });

    it('should apply only specified fields when provided', async () => {
      const mockData = {
        cap_rate: 0.045,
        interest_rate: 0.070,
        vacancy_rate: 0.050,
      };

      mockApiService.getMarketDataDefaults.mockResolvedValue({
        success: true,
        data: mockData,
        error: null,
      });

      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      const targetObject = { existing_field: 'value' };
      const updatedObject = result.current.applyDefaults(
        targetObject, 
        ['cap_rate']
      );

      expect(updatedObject).toEqual({
        existing_field: 'value',
        cap_rate: 0.045,
      });
    });

    it('should return original object when no data available', () => {
      const { result } = renderHook(() => useMarketDefaults());
      const targetObject = { existing_field: 'value' };
      const updatedObject = result.current.applyDefaults(targetObject);

      expect(updatedObject).toEqual(targetObject);
    });
  });

  describe('getDefaultValue', () => {
    it('should return correct parameter value', async () => {
      const mockData = {
        cap_rate: 0.045,
        interest_rate: 0.070,
      };

      mockApiService.getMarketDataDefaults.mockResolvedValue({
        success: true,
        data: mockData,
        error: null,
      });

      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(result.current.getDefaultValue('cap_rate')).toBe(0.045);
      expect(result.current.getDefaultValue('interest_rate')).toBe(0.070);
    });

    it('should return null when no data available', () => {
      const { result } = renderHook(() => useMarketDefaults());
      expect(result.current.getDefaultValue('cap_rate')).toBeNull();
    });
  });

  describe('Cache Management', () => {
    it('should use cached data when fresh', async () => {
      const mockData = { cap_rate: 0.045 };
      mockApiService.getMarketDataDefaults.mockResolvedValue({
        success: true,
        data: mockData,
        error: null,
      });

      const { result } = renderHook(() => useMarketDefaults());

      // First fetch
      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(mockApiService.getMarketDataDefaults).toHaveBeenCalledTimes(1);

      // Second fetch should use cache
      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(mockApiService.getMarketDataDefaults).toHaveBeenCalledTimes(1);
    });

    it('should indicate when data is fresh', async () => {
      const mockData = { cap_rate: 0.045 };
      mockApiService.getMarketDataDefaults.mockResolvedValue({
        success: true,
        data: mockData,
        error: null,
      });

      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(result.current.isDataFresh()).toBe(true);
    });
  });
});

describe('Helper Functions', () => {
  describe('formatMarketDefault', () => {
    it('should format percentage fields correctly', () => {
      expect(formatMarketDefault('cap_rate', 0.045)).toBe('4.5%');
      expect(formatMarketDefault('interest_rate', 0.070)).toBe('7.0%');
      expect(formatMarketDefault('vacancy_rate', 0.050)).toBe('5.0%');
    });

    it('should format special fields correctly', () => {
      expect(formatMarketDefault('lender_reserves_months', 3.0)).toBe('3.0 months');
      expect(formatMarketDefault('maintenance_reserve_per_unit', 600)).toBe('$600/unit');
    });
  });

  describe('getParameterDisplayName', () => {
    it('should return correct display names', () => {
      expect(getParameterDisplayName('cap_rate')).toBe('Cap Rate');
      expect(getParameterDisplayName('interest_rate')).toBe('Interest Rate');
      expect(getParameterDisplayName('vacancy_rate')).toBe('Vacancy Rate');
    });
  });
});