/**
 * Market Data Defaults Hook
 * Fetches and manages market data defaults for property forms
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { apiService } from '@/lib/api/service';
import { MarketDataDefaults } from '@/types/property';

interface MarketDefaultsState {
  loading: boolean;
  data: MarketDataDefaults | null;
  error: string | null;
  lastUpdated: Date | null;
}

export function useMarketDefaults(msaCode?: string) {
  const [state, setState] = useState<MarketDefaultsState>({
    loading: false,
    data: null,
    error: null,
    lastUpdated: null,
  });

  const fetchDefaults = useCallback(async (code: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiService.getMarketDataDefaults(code);
      
      if (response.success && response.data) {
        setState({
          loading: false,
          data: response.data,
          error: null,
          lastUpdated: new Date(),
        });
      } else {
        setState({
          loading: false,
          data: null,
          error: response.error || 'Failed to fetch market defaults',
          lastUpdated: null,
        });
      }
    } catch (error) {
      setState({
        loading: false,
        data: null,
        error: error instanceof Error ? error.message : 'Failed to fetch market defaults',
        lastUpdated: null,
      });
    }
  }, []);

  // Auto-fetch when MSA code changes
  useEffect(() => {
    if (msaCode) {
      fetchDefaults(msaCode);
    } else {
      setState({
        loading: false,
        data: null,
        error: null,
        lastUpdated: null,
      });
    }
  }, [msaCode, fetchDefaults]);

  const refetch = useCallback(() => {
    if (msaCode) {
      fetchDefaults(msaCode);
    }
  }, [msaCode, fetchDefaults]);

  const applyDefaults = useCallback((propertyData: any) => {
    // Apply market defaults to property data
    if (state.data) {
      return { ...propertyData, ...state.data };
    }
    return propertyData;
  }, [state.data]);

  const getDefaultValue = useCallback((key: string) => {
    return state.data ? (state.data as any)[key] : null;
  }, [state.data]);

  const isDataFresh = useCallback(() => {
    const thirtyMinutes = 30 * 60 * 1000; // 30 minutes in milliseconds
    return Date.now() - (state.lastUpdated?.getTime() || 0) < thirtyMinutes;
  }, [state.lastUpdated]);

  return {
    ...state,
    fetchDefaults,
    refetch,
    applyDefaults,
    getDefaultValue,
    isDataFresh,
  };
}