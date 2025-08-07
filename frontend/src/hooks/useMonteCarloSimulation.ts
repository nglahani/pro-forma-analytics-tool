/**
 * Monte Carlo Simulation Hook
 * Manages simulation lifecycle with progress tracking and result caching
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { SimplifiedPropertyInput } from '@/types/property';
import { MonteCarloResult } from '@/types/analysis';
import { useToast } from '@/hooks/useToast';

export interface MonteCarloSettings {
  numScenarios: number;
  includeCorrelations: boolean;
  includeMarketCycles: boolean;
  randomSeed?: number;
  confidenceLevel: number;
}

export interface MonteCarloProgressStatus {
  isRunning: boolean;
  progress: number;
  currentScenario: number;
  totalScenarios: number;
  estimatedTimeRemaining: number;
  stage: 'initializing' | 'running' | 'analyzing' | 'complete' | 'error';
  message: string;
}

interface UseMonteCarloSimulationOptions {
  autoRetry?: boolean;
  maxRetries?: number;
  pollInterval?: number;
  onProgress?: (status: MonteCarloProgressStatus) => void;
  onComplete?: (results: MonteCarloResult) => void;
  onError?: (error: string) => void;
}

export function useMonteCarloSimulation(options: UseMonteCarloSimulationOptions = {}) {
  const {
    autoRetry = true,
    maxRetries = 3,
    pollInterval = 1000,
    onProgress,
    onComplete,
    onError,
  } = options;

  const { toast } = useToast();
  
  // State management
  const [results, setResults] = useState<MonteCarloResult | null>(null);
  const [progressStatus, setProgressStatus] = useState<MonteCarloProgressStatus>({
    isRunning: false,
    progress: 0,
    currentScenario: 0,
    totalScenarios: 0,
    estimatedTimeRemaining: 0,
    stage: 'complete',
    message: 'Ready to run simulation',
  });
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  // Refs for managing polling and cleanup
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const simulationIdRef = useRef<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Clear polling interval
  const clearPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }, []);

  // Update progress status with optional callback
  const updateProgressStatus = useCallback((status: Partial<MonteCarloProgressStatus>) => {
    setProgressStatus(prev => {
      const newStatus = { ...prev, ...status };
      if (onProgress) {
        onProgress(newStatus);
      }
      return newStatus;
    });
  }, [onProgress]);

  // Start simulation
  const startSimulation = useCallback(async (
    propertyData: SimplifiedPropertyInput,
    settings: MonteCarloSettings
  ) => {
    if (progressStatus.isRunning) {
      console.warn('Simulation already running');
      return;
    }

    try {
      // Reset state
      setResults(null);
      setError(null);
      setRetryCount(0);
      clearPolling();

      // Create abort controller for this simulation
      abortControllerRef.current = new AbortController();

      // Initialize progress tracking
      updateProgressStatus({
        isRunning: true,
        progress: 0,
        currentScenario: 0,
        totalScenarios: settings.numScenarios,
        estimatedTimeRemaining: 0,
        stage: 'initializing',
        message: 'Starting simulation...',
      });

      // Check if backend supports async simulation with progress tracking
      const supportsAsyncSimulation = true; // This would be determined by API capabilities check

      if (supportsAsyncSimulation) {
        // Start async simulation
        const { simulation_id } = await apiClient.startMonteCarloSimulation(propertyData, settings);
        simulationIdRef.current = simulation_id;

        // Start polling for progress
        pollIntervalRef.current = setInterval(async () => {
          try {
            const status = await apiClient.getMonteCarloStatus(simulation_id);
            
            updateProgressStatus({
              progress: status.progress,
              currentScenario: status.current_scenario,
              totalScenarios: status.total_scenarios,
              estimatedTimeRemaining: status.estimated_time_remaining,
              stage: status.status,
              message: status.message,
            });

            if (status.status === 'complete' && status.results) {
              clearPolling();
              setResults(status.results);
              updateProgressStatus({
                isRunning: false,
                progress: 100,
                stage: 'complete',
                message: 'Simulation completed successfully',
              });

              if (onComplete) {
                onComplete(status.results);
              }

              toast({
                title: 'Simulation Complete',
                description: `Monte Carlo analysis completed with ${status.results.total_scenarios} scenarios`,
              });
            } else if (status.status === 'error') {
              throw new Error(status.message || 'Simulation failed');
            }
          } catch (pollError) {
            console.error('Error polling simulation status:', pollError);
            // Don't immediately fail - might be temporary network issue
          }
        }, pollInterval);

      } else {
        // Fallback to synchronous simulation
        updateProgressStatus({
          stage: 'running',
          message: 'Running simulation (no progress updates available)...',
        });

        const result = await apiClient.runMonteCarloSimulation(propertyData, settings);
        
        setResults(result);
        updateProgressStatus({
          isRunning: false,
          progress: 100,
          currentScenario: settings.numScenarios,
          stage: 'complete',
          message: 'Simulation completed successfully',
        });

        if (onComplete) {
          onComplete(result);
        }

        toast({
          title: 'Simulation Complete',
          description: `Monte Carlo analysis completed with ${result.total_scenarios} scenarios`,
        });
      }

    } catch (err) {
      clearPolling();
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      
      setError(errorMessage);
      updateProgressStatus({
        isRunning: false,
        stage: 'error',
        message: `Simulation failed: ${errorMessage}`,
      });

      if (onError) {
        onError(errorMessage);
      }

      // Auto-retry logic
      if (autoRetry && retryCount < maxRetries) {
        setRetryCount(prev => prev + 1);
        
        toast({
          title: 'Retrying Simulation',
          description: `Attempt ${retryCount + 1} of ${maxRetries}`,
        });

        // Retry after a delay
        setTimeout(() => {
          startSimulation(propertyData, settings);
        }, 2000 * (retryCount + 1)); // Exponential backoff
      } else {
        toast({
          title: 'Simulation Failed',
          description: errorMessage,
          variant: 'destructive',
        });
      }
    }
  }, [
    progressStatus.isRunning,
    clearPolling,
    updateProgressStatus,
    pollInterval,
    onComplete,
    onError,
    toast,
    autoRetry,
    retryCount,
    maxRetries,
  ]);

  // Stop simulation
  const stopSimulation = useCallback(async () => {
    if (!progressStatus.isRunning) return;

    try {
      // Abort ongoing requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Stop simulation on backend if we have a simulation ID
      if (simulationIdRef.current) {
        await apiClient.stopMonteCarloSimulation(simulationIdRef.current);
      }

      clearPolling();
      
      updateProgressStatus({
        isRunning: false,
        stage: 'complete',
        message: 'Simulation stopped by user',
      });

      toast({
        title: 'Simulation Stopped',
        description: 'Monte Carlo simulation has been stopped',
      });

    } catch (err) {
      console.error('Error stopping simulation:', err);
      // Still update UI state even if backend stop fails
      clearPolling();
      updateProgressStatus({
        isRunning: false,
        stage: 'complete',
        message: 'Simulation stopped (may continue on server)',
      });
    }
  }, [progressStatus.isRunning, clearPolling, updateProgressStatus, toast]);

  // Reset simulation state
  const resetSimulation = useCallback(() => {
    clearPolling();
    setResults(null);
    setError(null);
    setRetryCount(0);
    simulationIdRef.current = null;
    
    updateProgressStatus({
      isRunning: false,
      progress: 0,
      currentScenario: 0,
      totalScenarios: 0,
      estimatedTimeRemaining: 0,
      stage: 'complete',
      message: 'Ready to run simulation',
    });
  }, [clearPolling, updateProgressStatus]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearPolling();
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [clearPolling]);

  return {
    // State
    results,
    progressStatus,
    error,
    isRunning: progressStatus.isRunning,
    retryCount,
    
    // Actions
    startSimulation,
    stopSimulation,
    resetSimulation,
    
    // Computed values
    canStart: !progressStatus.isRunning,
    canStop: progressStatus.isRunning,
  };
}