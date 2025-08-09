/**
 * Retryable API Hook
 * Provides robust network error recovery with offline fallbacks and exponential backoff
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { useToast } from '@/hooks/useToast';

export interface RetryConfig {
  maxRetries?: number;
  initialDelay?: number;
  backoffMultiplier?: number;
  maxDelay?: number;
  timeoutMs?: number;
  retryCondition?: (error: any) => boolean;
  onRetry?: (attempt: number, error: any) => void;
  onMaxRetriesReached?: (error: any) => void;
}

export interface OfflineConfig {
  enableOfflineMode?: boolean;
  offlineStorageKey?: string;
  maxOfflineTime?: number;
  fallbackData?: any;
  onOffline?: () => void;
  onOnline?: () => void;
}

export interface NetworkState {
  isOnline: boolean;
  isSlowConnection: boolean;
  effectiveType: string;
  downlink: number;
  rtt: number;
}

interface APICallState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  retryCount: number;
  isRetrying: boolean;
  lastSuccessTime: number | null;
  networkState: NetworkState;
}

const DEFAULT_RETRY_CONFIG: Required<RetryConfig> = {
  maxRetries: 3,
  initialDelay: 1000,
  backoffMultiplier: 2,
  maxDelay: 30000,
  timeoutMs: 10000,
  retryCondition: (error) => {
    // Retry on network errors, timeouts, and 5xx server errors
    if (error?.name === 'TypeError' && error?.message?.includes('fetch')) return true;
    if (error?.name === 'AbortError') return false; // Don't retry cancelled requests
    if (error?.status >= 500) return true;
    if (error?.code === 'NETWORK_ERROR') return true;
    return false;
  },
  onRetry: () => {},
  onMaxRetriesReached: () => {},
};

const DEFAULT_OFFLINE_CONFIG: Required<OfflineConfig> = {
  enableOfflineMode: true,
  offlineStorageKey: 'pro_forma_offline_cache',
  maxOfflineTime: 24 * 60 * 60 * 1000, // 24 hours
  fallbackData: null,
  onOffline: () => {},
  onOnline: () => {},
};

export function useRetryableAPI<T = any>(
  retryConfig: RetryConfig = {},
  offlineConfig: OfflineConfig = {}
) {
  const config = { ...DEFAULT_RETRY_CONFIG, ...retryConfig };
  const offline = { ...DEFAULT_OFFLINE_CONFIG, ...offlineConfig };
  const { toast } = useToast();

  // State management
  const [state, setState] = useState<APICallState<T>>({
    data: null,
    loading: false,
    error: null,
    retryCount: 0,
    isRetrying: false,
    lastSuccessTime: null,
    networkState: {
      isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
      isSlowConnection: false,
      effectiveType: 'unknown',
      downlink: 0,
      rtt: 0,
    },
  });

  // Refs for cleanup and cancellation
  const abortControllerRef = useRef<AbortController | null>(null);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Network state monitoring
  useEffect(() => {
    if (typeof navigator === 'undefined') return;

    const updateNetworkState = () => {
      const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
      
      setState(prev => ({
        ...prev,
        networkState: {
          isOnline: navigator.onLine,
          isSlowConnection: connection?.effectiveType === '2g' || connection?.effectiveType === 'slow-2g',
          effectiveType: connection?.effectiveType || 'unknown',
          downlink: connection?.downlink || 0,
          rtt: connection?.rtt || 0,
        },
      }));
    };

    const handleOnline = () => {
      updateNetworkState();
      offline.onOnline();
      
      toast({
        title: 'Connection Restored',
        description: 'You are back online. Syncing data...',
      });
    };

    const handleOffline = () => {
      updateNetworkState();
      offline.onOffline();
      
      toast({
        title: 'Connection Lost',
        description: 'You are offline. Using cached data when available.',
        variant: 'destructive',
      });
    };

    // Initial network state
    updateNetworkState();

    // Event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    if ((navigator as any).connection) {
      (navigator as any).connection.addEventListener('change', updateNetworkState);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if ((navigator as any).connection) {
        (navigator as any).connection.removeEventListener('change', updateNetworkState);
      }
    };
  }, [offline, toast]);

  // Offline storage utilities
  const saveToOfflineCache = useCallback((key: string, data: T, timestamp: number) => {
    if (!offline.enableOfflineMode || typeof localStorage === 'undefined') return;

    try {
      const cacheData = {
        data,
        timestamp,
        key,
      };
      localStorage.setItem(`${offline.offlineStorageKey}_${key}`, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Failed to save offline cache:', error);
    }
  }, [offline.enableOfflineMode, offline.offlineStorageKey]);

  const getFromOfflineCache = useCallback((key: string): { data: T; timestamp: number } | null => {
    if (!offline.enableOfflineMode || typeof localStorage === 'undefined') return null;

    try {
      const cached = localStorage.getItem(`${offline.offlineStorageKey}_${key}`);
      if (!cached) return null;

      const cacheData = JSON.parse(cached);
      const age = Date.now() - cacheData.timestamp;

      if (age > offline.maxOfflineTime) {
        localStorage.removeItem(`${offline.offlineStorageKey}_${key}`);
        return null;
      }

      return cacheData;
    } catch (error) {
      console.warn('Failed to read offline cache:', error);
      return null;
    }
  }, [offline.enableOfflineMode, offline.offlineStorageKey, offline.maxOfflineTime]);

  const clearOfflineCache = useCallback((key?: string) => {
    if (typeof localStorage === 'undefined') return;

    if (key) {
      localStorage.removeItem(`${offline.offlineStorageKey}_${key}`);
    } else {
      // Clear all cache entries
      Object.keys(localStorage).forEach(storageKey => {
        if (storageKey.startsWith(offline.offlineStorageKey)) {
          localStorage.removeItem(storageKey);
        }
      });
    }
  }, [offline.offlineStorageKey]);

  // Calculate delay for retry with exponential backoff
  const calculateDelay = useCallback((attempt: number) => {
    const delay = Math.min(
      config.initialDelay * Math.pow(config.backoffMultiplier, attempt),
      config.maxDelay
    );
    
    // Add jitter to prevent thundering herd
    return delay + Math.random() * 1000;
  }, [config.initialDelay, config.backoffMultiplier, config.maxDelay]);

  // Main API call function with retry logic
  const executeCall = useCallback(async <R = T>(
    apiFunction: () => Promise<R>,
    cacheKey?: string,
    options: {
      skipCache?: boolean;
      skipOfflineCheck?: boolean;
    } = {}
  ): Promise<R> => {
    const { skipCache = false, skipOfflineCheck = false } = options;

    // Check if offline and try to get cached data
    if (!skipOfflineCheck && !state.networkState.isOnline && offline.enableOfflineMode) {
      const cached = cacheKey ? getFromOfflineCache(cacheKey) : null;
      
      if (cached) {
        setState(prev => ({
          ...prev,
          data: cached.data as T,
          loading: false,
          error: null,
        }));
        
        toast({
          title: 'Using Cached Data',
          description: 'Displaying offline data while connection is restored.',
        });
        
        return cached.data as R;
      } else if (offline.fallbackData) {
        setState(prev => ({
          ...prev,
          data: offline.fallbackData,
          loading: false,
          error: null,
        }));
        
        return offline.fallbackData as R;
      } else {
        throw new Error('No internet connection and no cached data available');
      }
    }

    let attempt = 0;
    let lastError: any;

    while (attempt <= config.maxRetries) {
      try {
        // Cancel any previous request
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }

        // Create new abort controller
        abortControllerRef.current = new AbortController();

        // Set loading state
        setState(prev => ({
          ...prev,
          loading: attempt === 0,
          isRetrying: attempt > 0,
          retryCount: attempt,
          error: null,
        }));

        // Add timeout to abort controller
        const timeoutId = setTimeout(() => {
          if (abortControllerRef.current) {
            abortControllerRef.current.abort();
          }
        }, config.timeoutMs);

        // Execute API call
        const result = await apiFunction();
        
        // Clear timeout
        clearTimeout(timeoutId);

        // Success - update state
        const now = Date.now();
        setState(prev => ({
          ...prev,
          data: result as T,
          loading: false,
          error: null,
          retryCount: 0,
          isRetrying: false,
          lastSuccessTime: now,
        }));

        // Cache successful result
        if (!skipCache && cacheKey && offline.enableOfflineMode) {
          saveToOfflineCache(cacheKey, result as T, now);
        }

        return result;

      } catch (error: any) {
        lastError = error;
        clearTimeout(timeoutId);

        // Check if we should retry
        const shouldRetry = attempt < config.maxRetries && config.retryCondition(error);

        if (!shouldRetry) {
          break;
        }

        // Call retry callback
        config.onRetry(attempt + 1, error);

        // Calculate delay and wait
        const delay = calculateDelay(attempt);
        
        await new Promise(resolve => {
          retryTimeoutRef.current = setTimeout(resolve, delay);
        });

        attempt++;
      }
    }

    // Max retries reached or non-retryable error
    config.onMaxRetriesReached(lastError);

    setState(prev => ({
      ...prev,
      loading: false,
      error: lastError,
      isRetrying: false,
    }));

    // Try to get cached data as last resort
    if (!skipOfflineCheck && cacheKey && offline.enableOfflineMode) {
      const cached = getFromOfflineCache(cacheKey);
      if (cached) {
        toast({
          title: 'Request Failed',
          description: 'Using cached data due to network error.',
          variant: 'destructive',
        });

        setState(prev => ({
          ...prev,
          data: cached.data,
          error: lastError, // Keep the error but show cached data
        }));

        return cached.data as R;
      }
    }

    throw lastError;
  }, [
    state.networkState.isOnline,
    config,
    offline,
    getFromOfflineCache,
    saveToOfflineCache,
    calculateDelay,
    toast,
  ]);

  // Cancel any ongoing requests
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }

    setState(prev => ({
      ...prev,
      loading: false,
      isRetrying: false,
    }));
  }, []);

  // Reset state
  const reset = useCallback(() => {
    cancel();
    setState(prev => ({
      ...prev,
      data: null,
      error: null,
      retryCount: 0,
      lastSuccessTime: null,
    }));
  }, [cancel]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cancel();
    };
  }, [cancel]);

  // Computed values
  const isStale = state.lastSuccessTime 
    ? (Date.now() - state.lastSuccessTime) > 300000 // 5 minutes
    : false;

  const canRetry = state.error && !state.loading && !state.isRetrying;

  return {
    // State
    data: state.data,
    loading: state.loading,
    error: state.error,
    retryCount: state.retryCount,
    isRetrying: state.isRetrying,
    networkState: state.networkState,
    isStale,
    canRetry,

    // Actions
    executeCall,
    cancel,
    reset,
    
    // Offline utilities
    saveToOfflineCache,
    getFromOfflineCache,
    clearOfflineCache,
  };
}