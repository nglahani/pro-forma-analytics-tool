/**
 * Lazy Chart Loader Component
 * Intelligent lazy loading system for heavy chart components with intersection observer
 */

'use client';

import React, { 
  Suspense, 
  lazy, 
  useState, 
  useEffect, 
  useRef, 
  ReactNode, 
  ComponentType,
  LazyExoticComponent,
} from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  LineChart,
  BarChart3,
  PieChart,
  Loader2,
  Eye,
  Download,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';
import { textColors } from '@/lib/utils';

// Lazy load chart components
const LazyTimeSeriesChart = lazy(() => 
  import('./TimeSeriesChart').then(module => ({ default: module.TimeSeriesChart }))
);

const LazyDistributionChart = lazy(() => 
  import('./DistributionChart').then(module => ({ default: module.DistributionChart }))
);

const LazyForecastChart = lazy(() => 
  import('./ForecastChart').then(module => ({ default: module.ForecastChart }))
);

const LazyMonteCarloResults = lazy(() => 
  import('../analysis/MonteCarloResults').then(module => ({ default: module.MonteCarloResults }))
);

const LazyScenarioAnalysisCharts = lazy(() => 
  import('../analysis/ScenarioAnalysisCharts').then(module => ({ default: module.ScenarioAnalysisCharts }))
);

export type ChartType = 
  | 'timeseries'
  | 'distribution' 
  | 'forecast'
  | 'monte-carlo'
  | 'scenario-analysis';

interface LazyChartLoaderProps {
  chartType: ChartType;
  data: any;
  title?: string;
  description?: string;
  className?: string;
  loadOnScroll?: boolean;
  threshold?: number;
  rootMargin?: string;
  enableManualLoad?: boolean;
  preloadOnHover?: boolean;
  fallbackComponent?: ReactNode;
  onLoad?: () => void;
  onError?: (error: Error) => void;
  onVisible?: () => void;
  [key: string]: any; // Allow additional props to pass through
}

interface ChartConfig {
  component: LazyExoticComponent<ComponentType<any>>;
  icon: ComponentType<any>;
  displayName: string;
  estimatedSize: string;
  description: string;
}

const CHART_CONFIGS: Record<ChartType, ChartConfig> = {
  'timeseries': {
    component: LazyTimeSeriesChart,
    icon: LineChart,
    displayName: 'Time Series Chart',
    estimatedSize: '~45KB',
    description: 'Interactive time series visualization with zoom and pan',
  },
  'distribution': {
    component: LazyDistributionChart,
    icon: BarChart3,
    displayName: 'Distribution Chart',
    estimatedSize: '~38KB',
    description: 'Probability distributions with histograms and box plots',
  },
  'forecast': {
    component: LazyForecastChart,
    icon: LineChart,
    displayName: 'Forecast Chart',
    estimatedSize: '~42KB',
    description: 'Prophet forecasts with confidence intervals',
  },
  'monte-carlo': {
    component: LazyMonteCarloResults,
    icon: BarChart3,
    displayName: 'Monte Carlo Results',
    estimatedSize: '~52KB',
    description: 'Comprehensive Monte Carlo simulation results',
  },
  'scenario-analysis': {
    component: LazyScenarioAnalysisCharts,
    icon: PieChart,
    displayName: 'Scenario Analysis',
    estimatedSize: '~48KB',
    description: 'Multi-scenario analysis and comparison charts',
  },
};

interface LoadingPlaceholderProps {
  chartType: ChartType;
  title?: string;
  description?: string;
  onManualLoad?: () => void;
  enableManualLoad: boolean;
  isLoading: boolean;
}

function LoadingPlaceholder({ 
  chartType, 
  title, 
  description, 
  onManualLoad, 
  enableManualLoad,
  isLoading,
}: LoadingPlaceholderProps) {
  const config = CHART_CONFIGS[chartType];
  const IconComponent = config.icon;

  return (
    <Card className="border-2 border-dashed border-gray-200 bg-gray-50/50">
      <CardHeader>
        <CardTitle className="flex items-center space-x-3">
          <div className="h-10 w-10 bg-blue-50 rounded-lg flex items-center justify-center">
            {isLoading ? (
              <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
            ) : (
              <IconComponent className="h-5 w-5 text-blue-600" />
            )}
          </div>
          <div>
            <span className="text-lg">
              {title || config.displayName}
            </span>
            <div className="text-sm text-gray-500 font-normal">
              {isLoading ? 'Loading...' : 'Ready to load'} • {config.estimatedSize}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <p className={`text-sm ${textColors.secondary}`}>
          {description || config.description}
        </p>
        
        {/* Skeleton Chart Placeholder */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-16" />
          </div>
          <Skeleton className="h-64 w-full rounded-lg" />
          <div className="flex justify-center space-x-4">
            <Skeleton className="h-3 w-20" />
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>

        {/* Manual Load Button */}
        {enableManualLoad && !isLoading && (
          <div className="flex items-center justify-center pt-4 border-t border-gray-200">
            <Button
              onClick={onManualLoad}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <Eye className="h-4 w-4" />
              <span>Load Chart</span>
            </Button>
          </div>
        )}

        {isLoading && (
          <div className="flex items-center justify-center pt-4 border-t border-gray-200">
            <div className="flex items-center space-x-3 text-sm text-gray-500">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Loading chart components...</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface ChartErrorBoundaryProps {
  chartType: ChartType;
  onRetry: () => void;
  error: Error;
}

function ChartErrorBoundary({ chartType, onRetry, error }: ChartErrorBoundaryProps) {
  const config = CHART_CONFIGS[chartType];

  return (
    <Card className="border-red-200 bg-red-50/50">
      <CardContent className="p-6">
        <div className="flex items-start space-x-4">
          <div className="h-10 w-10 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="h-5 w-5 text-red-600" />
          </div>
          <div className="flex-1 space-y-3">
            <div>
              <h3 className="text-sm font-medium text-red-800">
                Failed to load {config.displayName}
              </h3>
              <p className="text-xs text-red-600 mt-1">
                {error.message}
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                className="text-red-700 border-red-200 hover:bg-red-100"
              >
                <RefreshCw className="h-3 w-3 mr-2" />
                Retry
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function LazyChartLoader({
  chartType,
  data,
  title,
  description,
  className = '',
  loadOnScroll = true,
  threshold = 0.1,
  rootMargin = '50px',
  enableManualLoad = false,
  preloadOnHover = true,
  fallbackComponent,
  onLoad,
  onError,
  onVisible,
  ...chartProps
}: LazyChartLoaderProps) {
  const [isVisible, setIsVisible] = useState(!loadOnScroll);
  const [shouldLoad, setShouldLoad] = useState(!loadOnScroll && !enableManualLoad);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [isPreloaded, setIsPreloaded] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  const config = CHART_CONFIGS[chartType];

  // Set up intersection observer for scroll-based loading
  useEffect(() => {
    if (!loadOnScroll || shouldLoad) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (onVisible) {
            onVisible();
          }
          // Auto-load after becoming visible (with slight delay)
          setTimeout(() => {
            if (!enableManualLoad) {
              setShouldLoad(true);
            }
          }, 100);
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    const currentContainer = containerRef.current;
    if (currentContainer) {
      observer.observe(currentContainer);
      observerRef.current = observer;
    }

    return () => {
      if (observerRef.current && currentContainer) {
        observerRef.current.unobserve(currentContainer);
      }
    };
  }, [loadOnScroll, shouldLoad, threshold, rootMargin, enableManualLoad, onVisible]);

  // Preload on hover
  const handleMouseEnter = () => {
    if (preloadOnHover && !isPreloaded && !shouldLoad) {
      setIsPreloaded(true);
      // Preload the component
      config.component;
    }
  };

  // Manual load trigger
  const handleManualLoad = () => {
    setIsLoading(true);
    setShouldLoad(true);
  };

  // Retry after error
  const handleRetry = () => {
    setError(null);
    setIsLoading(true);
    setShouldLoad(false);
    
    // Retry after a short delay
    setTimeout(() => {
      setShouldLoad(true);
    }, 500);
  };

  // Loading callback
  const handleComponentLoad = () => {
    setIsLoading(false);
    if (onLoad) {
      onLoad();
    }
  };

  // Error callback
  const handleComponentError = (err: Error) => {
    setIsLoading(false);
    setError(err);
    if (onError) {
      onError(err);
    }
  };

  // If there's an error, show error boundary
  if (error) {
    return (
      <div ref={containerRef} className={className}>
        <ChartErrorBoundary
          chartType={chartType}
          onRetry={handleRetry}
          error={error}
        />
      </div>
    );
  }

  // If shouldn't load yet, show placeholder
  if (!shouldLoad) {
    return (
      <div 
        ref={containerRef} 
        className={className}
        onMouseEnter={handleMouseEnter}
      >
        {fallbackComponent || (
          <LoadingPlaceholder
            chartType={chartType}
            title={title}
            description={description}
            onManualLoad={handleManualLoad}
            enableManualLoad={enableManualLoad && isVisible}
            isLoading={isLoading}
          />
        )}
      </div>
    );
  }

  // Load the component
  const ChartComponent = config.component;

  return (
    <div ref={containerRef} className={className}>
      <Suspense
        fallback={
          <LoadingPlaceholder
            chartType={chartType}
            title={title}
            description={description}
            onManualLoad={handleManualLoad}
            enableManualLoad={false}
            isLoading={true}
          />
        }
      >
        <ErrorBoundary
          onError={handleComponentError}
          fallback={
            <ChartErrorBoundary
              chartType={chartType}
              onRetry={handleRetry}
              error={error || new Error('Unknown error')}
            />
          }
        >
          <ChartComponent
            {...chartProps}
            data={data}
            title={title}
            onLoad={handleComponentLoad}
          />
        </ErrorBoundary>
      </Suspense>
    </div>
  );
}

// Simple error boundary component
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<
  { 
    children: ReactNode; 
    fallback: ReactNode; 
    onError: (error: Error) => void 
  },
  ErrorBoundaryState
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Chart loading error:', error, errorInfo);
    this.props.onError(error);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}

// Utility hooks for chart loading management
export function useChartPreloader() {
  const preloadChart = (chartType: ChartType) => {
    // Preload chart component
    return CHART_CONFIGS[chartType].component;
  };

  const preloadAllCharts = () => {
    Object.values(CHART_CONFIGS).forEach(config => {
      config.component;
    });
  };

  return {
    preloadChart,
    preloadAllCharts,
  };
}

// Batch chart loader for loading multiple charts efficiently
interface BatchChartLoaderProps {
  charts: Array<{
    id: string;
    chartType: ChartType;
    data: any;
    props?: any;
  }>;
  loadConcurrency?: number;
  onBatchComplete?: () => void;
  className?: string;
}

export function BatchChartLoader({
  charts,
  loadConcurrency = 2,
  onBatchComplete,
  className = '',
}: BatchChartLoaderProps) {
  const [loadedCharts, setLoadedCharts] = useState<Set<string>>(new Set());
  const [loadingCharts, setLoadingCharts] = useState<Set<string>>(new Set());

  const handleChartLoad = (chartId: string) => {
    setLoadedCharts(prev => new Set([...prev, chartId]));
    setLoadingCharts(prev => {
      const next = new Set(prev);
      next.delete(chartId);
      return next;
    });

    // Check if batch is complete
    if (loadedCharts.size === charts.length - 1) {
      setTimeout(() => {
        if (onBatchComplete) {
          onBatchComplete();
        }
      }, 0);
    }
  };

  return (
    <div className={`grid gap-6 ${className}`}>
      {charts.map((chart, index) => (
        <LazyChartLoader
          key={chart.id}
          chartType={chart.chartType}
          data={chart.data}
          loadOnScroll={index < loadConcurrency}
          enableManualLoad={index >= loadConcurrency}
          onLoad={() => handleChartLoad(chart.id)}
          {...chart.props}
        />
      ))}
    </div>
  );
}