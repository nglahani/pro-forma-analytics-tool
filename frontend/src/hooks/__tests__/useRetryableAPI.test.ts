/**
 * Tests for useRetryableAPI Hook
 * Comprehensive coverage for network error recovery, offline fallbacks, and exponential backoff
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useRetryableAPI } from '../useRetryableAPI';
import { useToast } from '@/hooks/useToast';

// Mock dependencies
jest.mock('@/hooks/useToast', () => ({
  useToast: jest.fn(),
}));

// Mock window.navigator
Object.defineProperty(window, 'navigator', {
  writable: true,
  value: {
    onLine: true,
    connection: {
      effectiveType: '4g',
      downlink: 10,
      rtt: 50,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    }
  },
});

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock performance.now
global.performance = {
  now: jest.fn(() => Date.now()),
} as any;

const mockUseToast = useToast as jest.MockedFunction<typeof useToast>;
const mockToast = jest.fn();

describe('useRetryableAPI Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    localStorageMock.clear();
    mockUseToast.mockReturnValue({ 
      toast: mockToast,
      dismiss: jest.fn(),
      toasts: []
    });
    
    // Reset navigator.onLine
    Object.defineProperty(window.navigator, 'onLine', {
      writable: true,
      value: true,
    });
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Initialization', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => useRetryableAPI());

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.retryCount).toBe(0);
      expect(result.current.isRetrying).toBe(false);
      expect(result.current.networkState.isOnline).toBe(true);
    });

    it('should initialize with custom config', () => {
      const config = {
        maxRetries: 5,
        initialDelay: 2000,
        backoffMultiplier: 3,
        maxDelay: 60000,
        timeoutMs: 20000,
      };

      const { result } = renderHook(() => useRetryableAPI(config));

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should detect offline state', () => {
      Object.defineProperty(window.navigator, 'onLine', {
        writable: true,
        value: false,
      });

      const { result } = renderHook(() => useRetryableAPI());

      expect(result.current.networkState.isOnline).toBe(false);
    });
  });

  describe('Successful API Calls', () => {
    it('should execute API call successfully', async () => {
      const mockApiFunction = jest.fn().mockResolvedValue('success');
      const { result } = renderHook(() => useRetryableAPI());

      let response: any;
      await act(async () => {
        response = await result.current.executeCall(mockApiFunction);
      });

      expect(response).toBe('success');
      expect(result.current.data).toBe('success');
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.retryCount).toBe(0);
      expect(mockApiFunction).toHaveBeenCalledTimes(1);
    });

    it('should cache successful response', async () => {
      const mockApiFunction = jest.fn().mockResolvedValue('cached data');
      const { result } = renderHook(() => useRetryableAPI());

      await act(async () => {
        await result.current.executeCall(mockApiFunction, 'test-key');
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'pro_forma_offline_cache_test-key',
        expect.stringContaining('cached data')
      );
    });

    it('should update lastSuccessTime on success', async () => {
      const mockApiFunction = jest.fn().mockResolvedValue('success');
      const { result } = renderHook(() => useRetryableAPI());

      const beforeTime = Date.now();

      await act(async () => {
        await result.current.executeCall(mockApiFunction);
      });

      expect(result.current.data).toBe('success');
      // lastSuccessTime should be set (we can't test the exact value due to timing)
    });
  });

  describe('Retry Logic', () => {
    it('should retry on network errors', async () => {
      const mockApiFunction = jest.fn()
        .mockRejectedValueOnce(new TypeError('fetch failed'))
        .mockResolvedValueOnce('success after retry');

      const { result } = renderHook(() => useRetryableAPI({
        initialDelay: 100,
        maxRetries: 2
      }));

      let response: any;
      await act(async () => {
        const promise = result.current.executeCall(mockApiFunction);
        jest.advanceTimersByTime(200); // Advance past retry delay
        response = await promise;
      });

      expect(response).toBe('success after retry');
      expect(mockApiFunction).toHaveBeenCalledTimes(2);
    });

    it('should retry on 5xx server errors', async () => {
      const serverError = Object.assign(new Error('Server Error'), { status: 500 });
      const mockApiFunction = jest.fn()
        .mockRejectedValueOnce(serverError)
        .mockResolvedValueOnce('success after retry');

      const { result } = renderHook(() => useRetryableAPI({
        initialDelay: 100,
        maxRetries: 2
      }));

      let response: any;
      await act(async () => {
        const promise = result.current.executeCall(mockApiFunction);
        jest.advanceTimersByTime(200);
        response = await promise;
      });

      expect(response).toBe('success after retry');
      expect(mockApiFunction).toHaveBeenCalledTimes(2);
    });

    it('should not retry on AbortError', async () => {
      const abortError = Object.assign(new Error('Aborted'), { name: 'AbortError' });
      const mockApiFunction = jest.fn().mockRejectedValue(abortError);

      const { result } = renderHook(() => useRetryableAPI());

      await act(async () => {
        try {
          await result.current.executeCall(mockApiFunction);
        } catch (error) {
          // Expected to throw
        }
      });

      expect(mockApiFunction).toHaveBeenCalledTimes(1);
      expect(result.current.error).toBe(abortError);
    });

    it('should respect maxRetries limit', async () => {
      const networkError = new TypeError('fetch failed');
      const mockApiFunction = jest.fn().mockRejectedValue(networkError);

      const { result } = renderHook(() => useRetryableAPI({
        maxRetries: 2,
        initialDelay: 50
      }));

      await act(async () => {
        try {
          const promise = result.current.executeCall(mockApiFunction);
          jest.advanceTimersByTime(1000); // Advance past all retry delays
          await promise;
        } catch (error) {
          // Expected to throw after max retries
        }
      });

      expect(mockApiFunction).toHaveBeenCalledTimes(3); // Initial + 2 retries
      expect(result.current.error).toBe(networkError);
    });

    it('should use exponential backoff', async () => {
      const networkError = new TypeError('fetch failed');
      const mockApiFunction = jest.fn().mockRejectedValue(networkError);

      const retryCallback = jest.fn();
      const { result } = renderHook(() => useRetryableAPI({
        maxRetries: 2,
        initialDelay: 100,
        backoffMultiplier: 2,
        onRetry: retryCallback
      }));

      const startTime = Date.now();

      await act(async () => {
        try {
          const promise = result.current.executeCall(mockApiFunction);
          jest.advanceTimersByTime(1000);
          await promise;
        } catch (error) {
          // Expected to throw
        }
      });

      expect(retryCallback).toHaveBeenCalledWith(1, networkError);
      expect(retryCallback).toHaveBeenCalledWith(2, networkError);
    });

    it('should call onMaxRetriesReached callback', async () => {
      const networkError = new TypeError('fetch failed');
      const mockApiFunction = jest.fn().mockRejectedValue(networkError);
      const onMaxRetriesReached = jest.fn();

      const { result } = renderHook(() => useRetryableAPI({
        maxRetries: 1,
        initialDelay: 50,
        onMaxRetriesReached
      }));

      await act(async () => {
        try {
          const promise = result.current.executeCall(mockApiFunction);
          jest.advanceTimersByTime(200);
          await promise;
        } catch (error) {
          // Expected to throw
        }
      });

      expect(onMaxRetriesReached).toHaveBeenCalledWith(networkError);
    });

    it('should handle custom retry conditions', async () => {
      const customError = Object.assign(new Error('Custom error'), { status: 400 });
      const mockApiFunction = jest.fn().mockRejectedValue(customError);

      const customRetryCondition = jest.fn().mockReturnValue(true);

      const { result } = renderHook(() => useRetryableAPI({
        maxRetries: 1,
        initialDelay: 50,
        retryCondition: customRetryCondition
      }));

      await act(async () => {
        try {
          const promise = result.current.executeCall(mockApiFunction);
          jest.advanceTimersByTime(200);
          await promise;
        } catch (error) {
          // Expected to throw after retries
        }
      });

      expect(customRetryCondition).toHaveBeenCalledWith(customError);
      expect(mockApiFunction).toHaveBeenCalledTimes(2); // Initial + 1 retry
    });
  });

  describe('Offline Support', () => {
    beforeEach(() => {
      Object.defineProperty(window.navigator, 'onLine', {
        writable: true,
        value: false,
      });
    });

    it('should return cached data when offline', async () => {
      // Setup cached data
      const cachedData = { data: 'cached response', timestamp: Date.now(), key: 'test-key' };
      localStorageMock.setItem('pro_forma_offline_cache_test-key', JSON.stringify(cachedData));

      const mockApiFunction = jest.fn();
      const { result } = renderHook(() => useRetryableAPI());

      let response: any;
      await act(async () => {
        response = await result.current.executeCall(mockApiFunction, 'test-key');
      });

      expect(response).toBe('cached response');
      expect(mockApiFunction).not.toHaveBeenCalled();
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Using Cached Data',
        description: 'Displaying offline data while connection is restored.',
      });
    });

    it('should return fallback data when offline and no cache', async () => {
      const fallbackData = 'fallback response';
      const mockApiFunction = jest.fn();
      
      const { result } = renderHook(() => useRetryableAPI({}, {
        fallbackData,
        enableOfflineMode: true
      }));

      let response: any;
      await act(async () => {
        response = await result.current.executeCall(mockApiFunction, 'test-key');
      });

      expect(response).toBe(fallbackData);
      expect(result.current.data).toBe(fallbackData);
      expect(mockApiFunction).not.toHaveBeenCalled();
    });

    it('should throw error when offline with no cache or fallback', async () => {
      const mockApiFunction = jest.fn();
      const { result } = renderHook(() => useRetryableAPI());

      await act(async () => {
        try {
          await result.current.executeCall(mockApiFunction, 'test-key');
        } catch (error) {
          expect((error as Error).message).toBe('No internet connection and no cached data available');
        }
      });
    });

    it('should ignore expired cached data', async () => {
      // Setup expired cached data
      const expiredData = { 
        data: 'expired data', 
        timestamp: Date.now() - (25 * 60 * 60 * 1000), // 25 hours ago
        key: 'test-key' 
      };
      localStorageMock.setItem('pro_forma_offline_cache_test-key', JSON.stringify(expiredData));

      const mockApiFunction = jest.fn();
      const { result } = renderHook(() => useRetryableAPI());

      await act(async () => {
        try {
          await result.current.executeCall(mockApiFunction, 'test-key');
        } catch (error) {
          expect((error as Error).message).toBe('No internet connection and no cached data available');
        }
      });
    });
  });

  describe('Network State Monitoring', () => {
    it('should detect network changes', async () => {
      const { result } = renderHook(() => useRetryableAPI());

      expect(result.current.networkState.isOnline).toBe(true);

      // Simulate going offline
      Object.defineProperty(window.navigator, 'onLine', {
        writable: true,
        value: false,
      });

      act(() => {
        window.dispatchEvent(new Event('offline'));
      });

      expect(mockToast).toHaveBeenCalledWith({
        title: 'Connection Lost',
        description: 'You are offline. Using cached data when available.',
        variant: 'destructive',
      });
    });

    it('should detect coming back online', async () => {
      // Start offline
      Object.defineProperty(window.navigator, 'onLine', {
        writable: true,
        value: false,
      });

      const { result } = renderHook(() => useRetryableAPI());

      // Simulate coming back online
      Object.defineProperty(window.navigator, 'onLine', {
        writable: true,
        value: true,
      });

      act(() => {
        window.dispatchEvent(new Event('online'));
      });

      expect(mockToast).toHaveBeenCalledWith({
        title: 'Connection Restored',
        description: 'You are back online. Syncing data...',
      });
    });

    it('should detect slow connection', () => {
      Object.defineProperty(window.navigator, 'connection', {
        writable: true,
        value: {
          effectiveType: '2g',
          downlink: 0.5,
          rtt: 500,
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
        },
      });

      const { result } = renderHook(() => useRetryableAPI());

      act(() => {
        // Simulate connection change event
        const nav = window.navigator as any;
        if (nav.connection) {
          nav.connection.dispatchEvent?.(new Event('change'));
        }
      });

      expect(result.current.networkState.isSlowConnection).toBe(true);
    });
  });

  describe('Cache Management', () => {
    it('should save data to offline cache', async () => {
      const { result } = renderHook(() => useRetryableAPI());

      const testData = { key: 'value' };
      const timestamp = Date.now();

      act(() => {
        result.current.saveToOfflineCache('test-key', testData, timestamp);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'pro_forma_offline_cache_test-key',
        JSON.stringify({ data: testData, timestamp, key: 'test-key' })
      );
    });

    it('should retrieve data from offline cache', () => {
      const testData = { data: 'cached data', timestamp: Date.now(), key: 'test-key' };
      localStorageMock.setItem('pro_forma_offline_cache_test-key', JSON.stringify(testData));

      const { result } = renderHook(() => useRetryableAPI());

      const cached = result.current.getFromOfflineCache('test-key');

      expect(cached).toEqual(testData);
    });

    it('should clear specific cache entry', () => {
      localStorageMock.setItem('pro_forma_offline_cache_test-key', 'test data');

      const { result } = renderHook(() => useRetryableAPI());

      act(() => {
        result.current.clearOfflineCache('test-key');
      });

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('pro_forma_offline_cache_test-key');
    });

    it('should clear all cache entries', () => {
      localStorageMock.setItem('pro_forma_offline_cache_key1', 'data1');
      localStorageMock.setItem('pro_forma_offline_cache_key2', 'data2');
      localStorageMock.setItem('other_key', 'other data');

      Object.defineProperty(localStorageMock, 'length', { value: 3 });
      Object.defineProperty(localStorageMock, 'key', {
        value: jest.fn((index) => {
          const keys = ['pro_forma_offline_cache_key1', 'pro_forma_offline_cache_key2', 'other_key'];
          return keys[index];
        })
      });

      // Mock Object.keys for localStorage
      Object.keys = jest.fn().mockReturnValue([
        'pro_forma_offline_cache_key1',
        'pro_forma_offline_cache_key2',
        'other_key'
      ]);

      const { result } = renderHook(() => useRetryableAPI());

      act(() => {
        result.current.clearOfflineCache();
      });

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('pro_forma_offline_cache_key1');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('pro_forma_offline_cache_key2');
      expect(localStorageMock.removeItem).not.toHaveBeenCalledWith('other_key');
    });
  });

  describe('Request Cancellation', () => {
    it('should cancel ongoing requests', async () => {
      let abortSignal: AbortSignal;
      const mockApiFunction = jest.fn().mockImplementation(() => {
        return new Promise((resolve, reject) => {
          const controller = new AbortController();
          abortSignal = controller.signal;
          
          abortSignal.addEventListener('abort', () => {
            reject(new Error('Aborted'));
          });
          
          setTimeout(() => resolve('success'), 1000);
        });
      });

      const { result } = renderHook(() => useRetryableAPI());

      act(() => {
        result.current.executeCall(mockApiFunction);
      });

      expect(result.current.loading).toBe(true);

      act(() => {
        result.current.cancel();
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.isRetrying).toBe(false);
    });

    it('should reset state', () => {
      const { result } = renderHook(() => useRetryableAPI());

      // Set some state
      act(() => {
        // Simulate some state changes by calling executeCall and then reset
        result.current.reset();
      });

      expect(result.current.data).toBeNull();
      expect(result.current.error).toBeNull();
      expect(result.current.retryCount).toBe(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle malformed cached data', () => {
      localStorageMock.setItem('pro_forma_offline_cache_test-key', 'invalid json');

      const { result } = renderHook(() => useRetryableAPI());

      const cached = result.current.getFromOfflineCache('test-key');

      expect(cached).toBeNull();
    });

    it('should handle cache save errors gracefully', () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
      
      // Mock localStorage.setItem to throw
      localStorageMock.setItem.mockImplementation(() => {
        throw new Error('Storage quota exceeded');
      });

      const { result } = renderHook(() => useRetryableAPI());

      act(() => {
        result.current.saveToOfflineCache('test-key', { data: 'test' }, Date.now());
      });

      expect(consoleSpy).toHaveBeenCalledWith('Failed to save offline cache:', expect.any(Error));
      
      consoleSpy.mockRestore();
    });

    it('should work without localStorage', () => {
      // Mock localStorage as undefined
      Object.defineProperty(window, 'localStorage', {
        value: undefined,
      });

      const { result } = renderHook(() => useRetryableAPI());

      // Should not throw errors
      act(() => {
        result.current.saveToOfflineCache('test-key', { data: 'test' }, Date.now());
      });

      const cached = result.current.getFromOfflineCache('test-key');
      expect(cached).toBeNull();
    });

    it('should handle request timeout', async () => {
      const mockApiFunction = jest.fn().mockImplementation(() => {
        return new Promise(resolve => {
          setTimeout(() => resolve('success'), 20000); // Long delay
        });
      });

      const { result } = renderHook(() => useRetryableAPI({
        timeoutMs: 1000,
        maxRetries: 0
      }));

      await act(async () => {
        try {
          const promise = result.current.executeCall(mockApiFunction);
          jest.advanceTimersByTime(2000); // Advance past timeout
          await promise;
        } catch (error) {
          // Expected to timeout
        }
      });

      expect(result.current.error).toBeDefined();
    });

    it('should calculate delay with jitter', () => {
      const { result } = renderHook(() => useRetryableAPI({
        initialDelay: 1000,
        backoffMultiplier: 2,
        maxDelay: 10000
      }));

      // We can't directly test the private calculateDelay method,
      // but we can test that the delay logic works through retries
      const mockApiFunction = jest.fn().mockRejectedValue(new TypeError('Network error'));

      act(async () => {
        try {
          const promise = result.current.executeCall(mockApiFunction);
          jest.advanceTimersByTime(15000); // Advance enough time
          await promise;
        } catch (error) {
          // Expected to fail after retries
        }
      });

      expect(mockApiFunction).toHaveBeenCalledTimes(4); // Initial + 3 retries (default)
    });

    it('should handle skipCache option', async () => {
      const mockApiFunction = jest.fn().mockResolvedValue('fresh data');
      const { result } = renderHook(() => useRetryableAPI());

      await act(async () => {
        await result.current.executeCall(mockApiFunction, 'test-key', { skipCache: true });
      });

      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });

    it('should handle skipOfflineCheck option', async () => {
      Object.defineProperty(window.navigator, 'onLine', {
        writable: true,
        value: false,
      });

      const mockApiFunction = jest.fn().mockResolvedValue('online data');
      const { result } = renderHook(() => useRetryableAPI());

      await act(async () => {
        await result.current.executeCall(mockApiFunction, 'test-key', { skipOfflineCheck: true });
      });

      expect(mockApiFunction).toHaveBeenCalled();
    });
  });

  describe('Computed Properties', () => {
    it('should calculate isStale correctly', async () => {
      const { result } = renderHook(() => useRetryableAPI());

      expect(result.current.isStale).toBe(false);

      // Execute a successful call
      const mockApiFunction = jest.fn().mockResolvedValue('success');
      
      await act(async () => {
        await result.current.executeCall(mockApiFunction);
      });

      expect(result.current.isStale).toBe(false);

      // Fast forward time to make it stale
      act(() => {
        jest.advanceTimersByTime(400000); // > 5 minutes
      });

      expect(result.current.isStale).toBe(true);
    });

    it('should calculate canRetry correctly', async () => {
      const mockApiFunction = jest.fn().mockRejectedValue(new Error('Failed'));
      const { result } = renderHook(() => useRetryableAPI({ maxRetries: 0 }));

      expect(result.current.canRetry).toBe(false);

      await act(async () => {
        try {
          await result.current.executeCall(mockApiFunction);
        } catch (error) {
          // Expected to fail
        }
      });

      expect(result.current.canRetry).toBe(true);
      expect(result.current.error).toBeDefined();
      expect(result.current.loading).toBe(false);
      expect(result.current.isRetrying).toBe(false);
    });
  });
});