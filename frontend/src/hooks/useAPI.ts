/**
 * useAPI Hook
 * React hook for managing API calls with loading states and error handling
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiService } from '@/lib/api/service';
import { SimplifiedPropertyInput } from '@/types/property';

interface APIState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface APIResult<T, TArgs extends unknown[] = unknown[]> extends APIState<T> {
  execute: (...args: TArgs) => Promise<void>;
  reset: () => void;
}

// Generic hook for API calls
function useAPICall<T, TArgs extends unknown[]>(
  apiFunction: (...args: TArgs) => Promise<{ success: boolean; data: T | null; error: string | null }>
): APIResult<T, TArgs> {
  const [state, setState] = useState<APIState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  // Use ref to store the latest apiFunction to avoid stale closures
  const apiRef = useRef(apiFunction);
  useEffect(() => {
    apiRef.current = apiFunction;
  }, [apiFunction]);

  const execute = useCallback(async (...args: TArgs) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const result = await apiRef.current(...args);
      
      if (result.success) {
        setState({
          data: result.data,
          loading: false,
          error: null,
        });
      } else {
        setState({
          data: null,
          loading: false,
          error: result.error || 'Unknown error occurred',
        });
      }
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      });
    }
  }, []); // Stable reference, use apiRef.current for latest function

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

// Specific hooks for different API endpoints

export function useHealthCheck() {
  return useAPICall(apiService.checkHealth.bind(apiService));
}

export function useDCFAnalysis() {
  return useAPICall((propertyData: SimplifiedPropertyInput) =>
    apiService.analyzeDCF(propertyData)
  );
}

export function useBatchDCFAnalysis() {
  return useAPICall((properties: SimplifiedPropertyInput[]) =>
    apiService.analyzeBatchDCF(properties)
  );
}

export function useMonteCarloSimulation() {
  return useAPICall((propertyData: SimplifiedPropertyInput, scenarios?: number) =>
    apiService.runMonteCarloSimulation(propertyData, scenarios)
  );
}

export function useMarketData() {
  return useAPICall((msaCode: string, parameters?: string[]) =>
    apiService.getMarketData(msaCode, parameters)
  );
}

export function useForecastData() {
  return useAPICall((parameter: string, msaCode: string, months?: number) =>
    apiService.getForecastData(parameter, msaCode, months)
  );
}

export function useSystemConfig() {
  return useAPICall(apiService.getSystemConfig.bind(apiService));
}

// Utility hook for multiple API calls
export function useMultipleAPICalls() {
  const [states, setStates] = useState<Record<string, APIState<unknown>>>({});

  const executeCall = useCallback(async <T>(
    key: string,
    apiFunction: () => Promise<{ success: boolean; data: T | null; error: string | null }>
  ) => {
    setStates(prev => ({
      ...prev,
      [key]: { data: null, loading: true, error: null }
    }));

    try {
      const result = await apiFunction();
      
      setStates(prev => ({
        ...prev,
        [key]: {
          data: result.data,
          loading: false,
          error: result.success ? null : (result.error || 'Unknown error occurred')
        }
      }));
    } catch (error) {
      setStates(prev => ({
        ...prev,
        [key]: {
          data: null,
          loading: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred'
        }
      }));
    }
  }, []);

  const getState = useCallback(<T>(key: string): APIState<T> => {
    return states[key] as APIState<T> || { data: null, loading: false, error: null };
  }, [states]);

  const reset = useCallback((key?: string) => {
    if (key) {
      setStates(prev => ({
        ...prev,
        [key]: { data: null, loading: false, error: null }
      }));
    } else {
      setStates({});
    }
  }, []);

  return {
    executeCall,
    getState,
    reset,
    allLoading: Object.values(states).some(state => state.loading),
    hasErrors: Object.values(states).some(state => state.error),
  };
}