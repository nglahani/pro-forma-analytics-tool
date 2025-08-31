/**
 * Market Data Hook
 * Manages market data fetching, caching, and real-time updates
 */

'use client';

import { useState, useCallback, useEffect, useMemo } from 'react';
import { apiClient } from '@/lib/api/client';
import { MarketData, MarketForecast } from '@/types/analysis';
import { useToast } from '@/hooks/useToast';

export interface MSAInfo {
  msa_code: string;
  name: string;
  state: string;
  data_availability: {
    parameters: string[];
    date_range: {
      start: string;
      end: string;
    };
  };
}

export interface MarketDataFilters {
  parameters?: string[];
  startDate?: string;
  endDate?: string;
  includeForecasts?: boolean;
}

export interface ForecastOptions {
  horizonMonths?: number;
  confidenceLevel?: number;
  includeHistorical?: boolean;
}

interface UseMarketDataOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  cacheTimeout?: number;
  onError?: (error: string) => void;
}

interface MarketDataCache {
  [key: string]: {
    data: MarketData | MarketForecast;
    timestamp: number;
    expiresAt: number;
  };
}

export function useMarketData(options: UseMarketDataOptions = {}) {
  const {
    autoRefresh = false,
    refreshInterval = 300000, // 5 minutes
    cacheTimeout = 600000, // 10 minutes
    onError,
  } = options;

  const { toast } = useToast();

  // State management
  const [availableMSAs, setAvailableMSAs] = useState<MSAInfo[]>([]);
  const [marketDataCache, setMarketDataCache] = useState<MarketDataCache>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFetchTime, setLastFetchTime] = useState<number>(0);

  // Cache key generation
  const generateCacheKey = useCallback((
    type: 'market' | 'forecast',
    msaCode: string,
    options: any
  ): string => {
    const optionsKey = JSON.stringify(options);
    return `${type}_${msaCode}_${btoa(optionsKey)}`;
  }, []);

  // Check if cached data is still valid
  const isCacheValid = useCallback((cacheKey: string): boolean => {
    const cached = marketDataCache[cacheKey];
    return cached && Date.now() < cached.expiresAt;
  }, [marketDataCache]);

  // Get data from cache or return null
  const getFromCache = useCallback(<T>(cacheKey: string): T | null => {
    if (isCacheValid(cacheKey)) {
      return marketDataCache[cacheKey].data as T;
    }
    return null;
  }, [marketDataCache, isCacheValid]);

  // Store data in cache
  const setCache = useCallback((cacheKey: string, data: MarketData | MarketForecast) => {
    const now = Date.now();
    setMarketDataCache(prev => ({
      ...prev,
      [cacheKey]: {
        data,
        timestamp: now,
        expiresAt: now + cacheTimeout,
      },
    }));
  }, [cacheTimeout]);

  // Handle errors
  const handleError = useCallback((err: any, context: string) => {
    const errorMessage = err instanceof Error ? err.message : `Error in ${context}`;
    setError(errorMessage);
    
    if (onError) {
      onError(errorMessage);
    }

    toast({
      title: 'Market Data Error',
      description: errorMessage,
      variant: 'destructive',
    });
  }, [onError, toast]);

  // Fetch available MSAs
  const fetchAvailableMSAs = useCallback(async () => {
    const cacheKey = 'available_msas';
    
    // Check cache first
    const cached = getFromCache<MSAInfo[]>(cacheKey);
    if (cached) {
      setAvailableMSAs(cached);
      return cached;
    }

    try {
      setIsLoading(true);
      const msas = await apiClient.getAvailableMSAs();
      setAvailableMSAs(msas);
      setCache(cacheKey, msas as any);
      setLastFetchTime(Date.now());
      return msas;
    } catch (err) {
      handleError(err, 'fetching available MSAs');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [getFromCache, setCache, handleError]);

  // Fetch market data for specific MSA
  const fetchMarketData = useCallback(async (
    msaCode: string,
    filters: MarketDataFilters = {}
  ): Promise<MarketData | null> => {
    const cacheKey = generateCacheKey('market', msaCode, filters);
    
    // Check cache first
    const cached = getFromCache<MarketData>(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      setIsLoading(true);
      setError(null);

      const data = await apiClient.getMarketData(msaCode, {
        parameters: filters.parameters,
        startDate: filters.startDate,
        endDate: filters.endDate,
        includeForecasts: filters.includeForecasts,
      });

      setCache(cacheKey, data);
      setLastFetchTime(Date.now());
      return data;
    } catch (err) {
      handleError(err, `fetching market data for ${msaCode}`);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [generateCacheKey, getFromCache, setCache, handleError]);

  // Fetch forecast data
  const fetchForecastData = useCallback(async (
    parameter: string,
    msaCode: string,
    options: ForecastOptions = {}
  ): Promise<MarketForecast | null> => {
    const cacheKey = generateCacheKey('forecast', `${parameter}_${msaCode}`, options);
    
    // Check cache first
    const cached = getFromCache<MarketForecast>(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      setIsLoading(true);
      setError(null);

      const data = await apiClient.getForecastData(parameter, msaCode, options);
      
      setCache(cacheKey, data);
      setLastFetchTime(Date.now());
      return data;
    } catch (err) {
      handleError(err, `fetching forecast for ${parameter} in ${msaCode}`);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [generateCacheKey, getFromCache, setCache, handleError]);

  // Fetch multiple parameter forecasts
  const fetchMultiParameterForecast = useCallback(async (
    parameters: string[],
    msaCode: string,
    options: ForecastOptions = {}
  ): Promise<{ msa_code: string; forecasts: MarketForecast[]; } | null> => {
    const cacheKey = generateCacheKey('forecast', `multi_${msaCode}`, { parameters, ...options });
    
    // Check cache first
    const cached = getFromCache<{ msa_code: string; forecasts: MarketForecast[]; }>(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      setIsLoading(true);
      setError(null);

      const data = await apiClient.getMultiParameterForecast(parameters, msaCode, {
        horizonMonths: options.horizonMonths,
        confidenceLevel: options.confidenceLevel,
      });

      setCache(cacheKey, data as any);
      setLastFetchTime(Date.now());
      return data;
    } catch (err) {
      handleError(err, `fetching multi-parameter forecasts for ${msaCode}`);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [generateCacheKey, getFromCache, setCache, handleError]);

  // Compare market data across MSAs
  const compareMarketData = useCallback(async (
    msaCodes: string[],
    parameters: string[],
    options: { startDate?: string; endDate?: string } = {}
  ): Promise<{
    comparison_id: string;
    msas: Array<{
      msa_code: string;
      name: string;
      data: MarketData;
    }>;
  } | null> => {
    try {
      setIsLoading(true);
      setError(null);

      const comparison = await apiClient.compareMarketData(msaCodes, parameters, options);
      setLastFetchTime(Date.now());
      return comparison;
    } catch (err) {
      handleError(err, 'comparing market data');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  // Clear cache
  const clearCache = useCallback(() => {
    setMarketDataCache({});
    setError(null);
  }, []);

  // Invalidate cache for specific MSA
  const invalidateCache = useCallback((msaCode?: string) => {
    if (msaCode) {
      setMarketDataCache(prev => {
        const newCache = { ...prev };
        Object.keys(newCache).forEach(key => {
          if (key.includes(msaCode)) {
            delete newCache[key];
          }
        });
        return newCache;
      });
    } else {
      clearCache();
    }
  }, [clearCache]);

  // Auto-refresh logic
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      // Refresh MSAs list
      fetchAvailableMSAs();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchAvailableMSAs]);

  // Load MSAs on mount
  useEffect(() => {
    fetchAvailableMSAs();
  }, []);

  // Computed values
  const cacheStats = useMemo(() => {
    const entries = Object.entries(marketDataCache);
    return {
      totalEntries: entries.length,
      validEntries: entries.filter(([key]) => isCacheValid(key)).length,
      expiredEntries: entries.filter(([key]) => !isCacheValid(key)).length,
      cacheSize: JSON.stringify(marketDataCache).length,
    };
  }, [marketDataCache, isCacheValid]);

  const isDataStale = useMemo(() => {
    return lastFetchTime > 0 && (Date.now() - lastFetchTime) > cacheTimeout;
  }, [lastFetchTime, cacheTimeout]);

  return {
    // State
    availableMSAs,
    isLoading,
    error,
    lastFetchTime,
    isDataStale,
    cacheStats,

    // Actions
    fetchMarketData,
    fetchForecastData,
    fetchMultiParameterForecast,
    compareMarketData,
    fetchAvailableMSAs,
    clearCache,
    invalidateCache,

    // Utils
    getFromCache,
    isCacheValid,
    generateCacheKey,
  };
}