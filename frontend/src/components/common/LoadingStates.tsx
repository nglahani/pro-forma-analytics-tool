/**
 * Loading States Components
 * Context-aware loading indicators and skeleton screens
 */

'use client';

import { ReactNode } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Loader2,
  Activity,
  BarChart3,
  TrendingUp,
  Calculator,
  Database,
  Zap,
  Clock,
} from 'lucide-react';
import { textColors } from '@/lib/utils';

// Generic loading spinner
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'primary' | 'secondary';
  className?: string;
}

export function LoadingSpinner({ 
  size = 'md', 
  variant = 'default',
  className = '' 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  };

  const variantClasses = {
    default: 'text-gray-500',
    primary: 'text-blue-600',
    secondary: 'text-gray-400',
  };

  return (
    <Loader2 
      className={`${sizeClasses[size]} ${variantClasses[variant]} animate-spin ${className}`} 
    />
  );
}

// Loading overlay
interface LoadingOverlayProps {
  isVisible: boolean;
  message?: string;
  progress?: number;
  children?: ReactNode;
  backdrop?: boolean;
}

export function LoadingOverlay({ 
  isVisible, 
  message, 
  progress, 
  children,
  backdrop = true 
}: LoadingOverlayProps) {
  if (!isVisible) return children || null;

  return (
    <div className="relative">
      {children && <div className="opacity-50 pointer-events-none">{children}</div>}
      
      <div className={`absolute inset-0 flex items-center justify-center ${
        backdrop ? 'bg-white/80 backdrop-blur-sm' : ''
      }`}>
        <div className="text-center space-y-4 p-6">
          <LoadingSpinner size="lg" variant="primary" />
          {message && (
            <p className={`text-sm font-medium ${textColors.secondary}`}>
              {message}
            </p>
          )}
          {progress !== undefined && progress >= 0 && (
            <div className="w-48">
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-gray-500 mt-1">
                {Math.round(progress)}% complete
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Context-specific loading indicators
interface AnalysisLoadingProps {
  stage?: 'initializing' | 'calculating' | 'analyzing' | 'finalizing';
  progress?: number;
  estimatedTime?: number;
  className?: string;
}

export function AnalysisLoading({ 
  stage = 'calculating', 
  progress, 
  estimatedTime,
  className = '' 
}: AnalysisLoadingProps) {
  const stageInfo = {
    initializing: {
      icon: Database,
      title: 'Initializing Analysis',
      message: 'Setting up calculation parameters...',
    },
    calculating: {
      icon: Calculator,
      title: 'Running DCF Analysis',
      message: 'Computing cash flows and financial metrics...',
    },
    analyzing: {
      icon: BarChart3,
      title: 'Analyzing Results',
      message: 'Calculating investment recommendations...',
    },
    finalizing: {
      icon: TrendingUp,
      title: 'Finalizing Report',
      message: 'Preparing final analysis results...',
    },
  };

  const StageIcon = stageInfo[stage].icon;

  return (
    <Card className={className}>
      <CardContent className="p-8">
        <div className="text-center space-y-6">
          <div className="h-16 w-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto">
            <StageIcon className="h-8 w-8 text-blue-600 animate-pulse" />
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {stageInfo[stage].title}
            </h3>
            <p className="text-sm text-gray-600">
              {stageInfo[stage].message}
            </p>
          </div>

          {progress !== undefined && progress >= 0 && (
            <div className="space-y-2">
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-gray-500">
                {Math.round(progress)}% complete
              </p>
            </div>
          )}

          {estimatedTime && estimatedTime > 0 && (
            <div className="flex items-center justify-center space-x-2 text-xs text-gray-500">
              <Clock className="h-3 w-3" />
              <span>Est. {Math.ceil(estimatedTime)}s remaining</span>
            </div>
          )}

          <div className="flex justify-center space-x-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="h-2 w-2 bg-blue-600 rounded-full animate-pulse"
                style={{
                  animationDelay: `${i * 0.3}s`,
                  animationDuration: '1.5s',
                }}
              />
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Monte Carlo specific loading
interface MonteCarloLoadingProps {
  currentScenario?: number;
  totalScenarios?: number;
  progress?: number;
  stage?: 'initializing' | 'running' | 'analyzing';
  className?: string;
}

export function MonteCarloLoading({ 
  currentScenario, 
  totalScenarios, 
  progress,
  stage = 'running',
  className = '' 
}: MonteCarloLoadingProps) {
  const stageInfo = {
    initializing: {
      icon: Database,
      title: 'Initializing Monte Carlo',
      message: 'Building correlation matrices...',
    },
    running: {
      icon: Activity,
      title: 'Running Simulations',
      message: 'Generating probabilistic scenarios...',
    },
    analyzing: {
      icon: BarChart3,
      title: 'Analyzing Results',
      message: 'Computing statistical distributions...',
    },
  };

  const StageIcon = stageInfo[stage].icon;

  return (
    <Card className={className}>
      <CardContent className="p-8">
        <div className="text-center space-y-6">
          <div className="h-16 w-16 bg-amber-50 rounded-full flex items-center justify-center mx-auto">
            <StageIcon className="h-8 w-8 text-amber-600 animate-pulse" />
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {stageInfo[stage].title}
            </h3>
            <p className="text-sm text-gray-600">
              {stageInfo[stage].message}
            </p>
          </div>

          {currentScenario && totalScenarios && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-gray-700">
                Scenario {currentScenario.toLocaleString()} of {totalScenarios.toLocaleString()}
              </div>
              <Progress 
                value={(currentScenario / totalScenarios) * 100} 
                className="h-3" 
              />
            </div>
          )}

          {progress !== undefined && progress >= 0 && !currentScenario && (
            <div className="space-y-2">
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-gray-500">
                {Math.round(progress)}% complete
              </p>
            </div>
          )}

          <div className="flex justify-center">
            <Zap className="h-5 w-5 text-amber-500 animate-bounce" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Market data loading
interface MarketDataLoadingProps {
  dataType?: 'historical' | 'forecasts' | 'comparison';
  msaName?: string;
  className?: string;
}

export function MarketDataLoading({ 
  dataType = 'historical', 
  msaName,
  className = '' 
}: MarketDataLoadingProps) {
  const dataTypeInfo = {
    historical: {
      title: 'Loading Market Data',
      message: 'Fetching historical market trends...',
    },
    forecasts: {
      title: 'Generating Forecasts',
      message: 'Computing Prophet forecasts...',
    },
    comparison: {
      title: 'Comparing Markets',
      message: 'Analyzing multi-market data...',
    },
  };

  return (
    <Card className={className}>
      <CardContent className="p-6">
        <div className="flex items-center space-x-4">
          <div className="h-12 w-12 bg-green-50 rounded-lg flex items-center justify-center">
            <TrendingUp className="h-6 w-6 text-green-600 animate-pulse" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">
              {dataTypeInfo[dataType].title}
              {msaName && ` for ${msaName}`}
            </h4>
            <p className="text-sm text-gray-600 mt-1">
              {dataTypeInfo[dataType].message}
            </p>
            <div className="flex items-center space-x-2 mt-3">
              <LoadingSpinner size="sm" variant="primary" />
              <span className="text-xs text-gray-500">Processing...</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Skeleton components for different content types
export function DCFResultsSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header skeleton */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32" />
        </div>
        <Skeleton className="h-8 w-24" />
      </div>

      {/* Metrics cards skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[0, 1, 2].map((i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-8 w-24" />
                </div>
                <Skeleton className="h-12 w-12 rounded-lg" />
              </div>
            </CardHeader>
            <CardContent>
              <Skeleton className="h-3 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Chart skeleton */}
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-64" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-80 w-full" />
        </CardContent>
      </Card>
    </div>
  );
}

export function MarketDataSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Controls skeleton */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-4">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-24" />
        </div>
        <Skeleton className="h-10 w-20" />
      </div>

      {/* Chart skeleton */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <Skeleton className="h-5 w-48" />
              <Skeleton className="h-4 w-64" />
            </div>
            <div className="flex space-x-2">
              <Skeleton className="h-6 w-16" />
              <Skeleton className="h-6 w-16" />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-96 w-full" />
        </CardContent>
      </Card>

      {/* Data table skeleton */}
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-32" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-4 w-12" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Wrapper for async components
interface AsyncComponentProps {
  loading?: boolean;
  error?: string | Error | null;
  loadingSkeleton?: ReactNode;
  errorFallback?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function AsyncComponent({ 
  loading = false, 
  error, 
  loadingSkeleton,
  errorFallback,
  children,
  className = '' 
}: AsyncComponentProps) {
  if (loading) {
    return loadingSkeleton || <LoadingSpinner size="lg" className={className} />;
  }

  if (error) {
    if (errorFallback) {
      return errorFallback;
    }
    
    const errorMessage = error instanceof Error ? error.message : String(error);
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="text-red-600 mb-2">Error loading content</div>
        <div className="text-sm text-gray-500">{errorMessage}</div>
      </div>
    );
  }

  return <>{children}</>;
}