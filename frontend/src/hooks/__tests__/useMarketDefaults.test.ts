/**
 * Working Tests for useMarketDefaults Hook
 * Focuses on actual behavior rather than complex mocking
 */

import { renderHook, act } from '@testing-library/react';
import { useMarketDefaults, formatMarketDefault, getParameterDisplayName } from '../useMarketDefaults';

describe('useMarketDefaults (Working Tests)', () => {
  describe('Basic Functionality', () => {
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
      expect(typeof result.current.refresh).toBe('function');
      expect(typeof result.current.applyDefaults).toBe('function');
      expect(typeof result.current.getDefaultValue).toBe('function');
      expect(typeof result.current.isDataFresh).toBe('function');
    });

    it('should handle missing MSA code', async () => {
      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('');
      });

      expect(result.current.data).toBeNull();
      expect(result.current.error).toBe('MSA code is required');
      expect(result.current.loading).toBe(false);
    });

    it('should fetch and provide fallback defaults', async () => {
      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.cap_rate).toBe(0.045);
      expect(result.current.data?.interest_rate).toBe(0.070);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.msaCode).toBe('35620');
      expect(result.current.lastUpdated).toBeInstanceOf(Date);
    });
  });

  describe('Data Operations', () => {
    it('should apply defaults to target object', async () => {
      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      const targetObject = { existing_field: 'value' };
      const updatedObject = result.current.applyDefaults(targetObject);

      expect(updatedObject.existing_field).toBe('value');
      expect(updatedObject.cap_rate).toBe(0.045);
      expect(updatedObject.interest_rate).toBe(0.070);
      expect(Object.keys(updatedObject).length).toBeGreaterThan(5);
    });

    it('should apply only specified fields when provided', async () => {
      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      const targetObject = { existing_field: 'value' };
      const updatedObject = result.current.applyDefaults(targetObject, ['cap_rate']);

      expect(updatedObject.existing_field).toBe('value');
      expect(updatedObject.cap_rate).toBe(0.045);
      expect(updatedObject.interest_rate).toBeUndefined(); // Should not be included
    });

    it('should return correct parameter values', async () => {
      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(result.current.getDefaultValue('cap_rate')).toBe(0.045);
      expect(result.current.getDefaultValue('interest_rate')).toBe(0.070);
      expect(result.current.getDefaultValue('nonexistent')).toBeFalsy();
    });

    it('should return original object when no data available', () => {
      const { result } = renderHook(() => useMarketDefaults());
      const targetObject = { existing_field: 'value' };
      const updatedObject = result.current.applyDefaults(targetObject);

      expect(updatedObject).toEqual(targetObject);
    });
  });

  describe('Data Freshness', () => {
    it('should indicate when data is fresh', async () => {
      const { result } = renderHook(() => useMarketDefaults());

      await act(async () => {
        await result.current.fetchDefaults('35620');
      });

      expect(result.current.isDataFresh()).toBe(true);
    });

    it('should return false when no data', () => {
      const { result } = renderHook(() => useMarketDefaults());
      expect(result.current.isDataFresh()).toBe(false);
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
      expect(formatMarketDefault('unknown_field', 123)).toBe('123');
    });
  });

  describe('getParameterDisplayName', () => {
    it('should return correct display names', () => {
      expect(getParameterDisplayName('cap_rate')).toBe('Cap Rate');
      expect(getParameterDisplayName('interest_rate')).toBe('Interest Rate');
      expect(getParameterDisplayName('vacancy_rate')).toBe('Vacancy Rate');
      expect(getParameterDisplayName('unknown_field')).toBe('Unknown Field');
    });
  });
});