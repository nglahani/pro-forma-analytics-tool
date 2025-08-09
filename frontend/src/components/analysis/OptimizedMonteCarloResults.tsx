/**
 * Optimized Monte Carlo Results Visualization Component
 * Performance-enhanced version with lazy loading and monitoring
 */

'use client';

import React, { useState, useMemo, useCallback, Suspense, lazy } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AccessibleButton } from '@/components/ui/accessible-button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { LazyChartLoader } from '@/components/charts/LazyChartLoader';
import {
  AlertTriangle,
  Activity,
  Download,
  RefreshCw,
} from 'lucide-react';
import { MonteCarloResult } from '@/types/analysis';
import { formatCurrency, formatPercentage, textColors } from '@/lib/utils';
import { usePerformanceMeasure, performanceUtils, performanceMonitor } from '@/lib/performance';
import { useAccessibility } from '@/components/common/AccessibilityProvider';
import { focusRing } from '@/lib/accessibility';

// Lazy load heavy chart components
const DetailedCharts = lazy(() => import('./ScenarioAnalysisCharts').then(module => ({ 
  default: module.ScenarioAnalysisCharts 
})));

const StatisticsTable = lazy(() => import('./StatisticsTable').then(module => ({ 
  default: module.StatisticsTable 
})));

interface OptimizedMonteCarloResultsProps {
  results: MonteCarloResult;
  onRerun?: () => void;
  onExport?: (format: 'pdf' | 'excel') => void;
  isRunning?: boolean;
  enablePerformanceMode?: boolean;
}

export function OptimizedMonteCarloResults({ 
  results, 
  onRerun, 
  onExport,
  isRunning = false,
  enablePerformanceMode = false
}: OptimizedMonteCarloResultsProps) {
  // Performance monitoring
  usePerformanceMeasure('MonteCarloResults', [results]);
  
  // Accessibility
  const { announce } = useAccessibility();
  
  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [viewMode, setViewMode] = useState<'summary' | 'detailed'>('summary');
  
  // Memoized calculations to prevent unnecessary re-computations
  const statistics = useMemo(() => {
    return performanceUtils.measureFunction('calculate-statistics', () => {
      const scenarios = results.scenario_analysis || [];
      
      if (scenarios.length === 0) return null;
      
      const npvValues = scenarios.map(s => s.npv);
      const irrValues = scenarios.map(s => s.irr);
      
      return {
        npv: {
          mean: npvValues.reduce((sum, val) => sum + val, 0) / npvValues.length,
          median: npvValues.sort((a, b) => a - b)[Math.floor(npvValues.length / 2)],
          p5: npvValues.sort((a, b) => a - b)[Math.floor(npvValues.length * 0.05)],
          p95: npvValues.sort((a, b) => a - b)[Math.floor(npvValues.length * 0.95)],
          min: Math.min(...npvValues),
          max: Math.max(...npvValues),
        },
        irr: {
          mean: irrValues.reduce((sum, val) => sum + val, 0) / irrValues.length,
          median: irrValues.sort((a, b) => a - b)[Math.floor(irrValues.length / 2)],
          p5: irrValues.sort((a, b) => a - b)[Math.floor(irrValues.length * 0.05)],
          p95: irrValues.sort((a, b) => a - b)[Math.floor(irrValues.length * 0.95)],
          min: Math.min(...irrValues),
          max: Math.max(...irrValues),
        }
      };
    });
  }, [results.scenario_analysis]);

  // Memoized risk assessment
  const riskAssessment = useMemo(() => {
    if (!statistics) return null;
    
    const negativeScenarios = (results.scenario_analysis || [])
      .filter(s => s.npv < 0).length;
    const totalScenarios = (results.scenario_analysis || []).length;
    const probabilityOfLoss = (negativeScenarios / totalScenarios) * 100;
    
    return {
      probabilityOfLoss,
      valueAtRisk: statistics.npv.p5,
      expectedShortfall: statistics.npv.p5, // Simplified calculation
      confidenceLevel: 95,
    };
  }, [statistics, results.scenario_analysis]);

  // Optimized chart data preparation
  const chartData = useMemo(() => {
    if (!results.scenario_analysis) return { histogram: [], percentiles: [] };
    
    return performanceUtils.measureFunction('prepare-chart-data', () => {
      // Create NPV histogram data
      const npvValues = results.scenario_analysis!.map(s => s.npv);
      const bins = 20;
      const min = Math.min(...npvValues);
      const max = Math.max(...npvValues);
      const binSize = (max - min) / bins;
      
      const histogram = Array.from({ length: bins }, (_, i) => {
        const binStart = min + i * binSize;
        const binEnd = min + (i + 1) * binSize;
        const count = npvValues.filter(val => val >= binStart && val < binEnd).length;
        
        return {
          range: `${formatCurrency(binStart, { compact: true })} - ${formatCurrency(binEnd, { compact: true })}`,
          count,
          percentage: (count / npvValues.length) * 100,
          binStart,
          binEnd,
        };
      });
      
      // Create percentile data
      const sortedNpvs = [...npvValues].sort((a, b) => a - b);
      const percentiles = [5, 10, 25, 50, 75, 90, 95].map(p => ({
        percentile: p,
        value: sortedNpvs[Math.floor((p / 100) * sortedNpvs.length)],
        label: `P${p}`,
      }));
      
      return { histogram, percentiles };
    });
  }, [results.scenario_analysis]);

  // Throttled tab change handler
  const handleTabChange = useCallback(
    performanceUtils.throttle((tab: string) => {
      setActiveTab(tab);
      announce(`Switched to ${tab} tab`, 'polite');
      
      // Track tab usage for performance insights
      performanceMonitor.startMeasure(`tab-${tab}-load`);
      setTimeout(() => {
        performanceMonitor.endMeasure(`tab-${tab}-load`);
      }, 100);
    }, 150),
    []
  );

  // Export handler with performance measurement
  const handleExport = useCallback(async (format: 'pdf' | 'excel') => {
    await performanceUtils.measureFunction(`export-${format}`, async () => {
      onExport?.(format);
      announce(`Exporting Monte Carlo results as ${format.toUpperCase()}`, 'polite');
    });
  }, [onExport, announce]);

  // Render summary statistics card
  const renderSummaryCard = useCallback(() => (
    <Card className={`${focusRing.default} transition-colors`} tabIndex={0}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-600" aria-hidden="true" />
          Summary Statistics
        </CardTitle>
        <CardDescription>
          Key metrics from {results.scenario_analysis?.length || 0} scenarios
        </CardDescription>
      </CardHeader>
      <CardContent>
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className={`font-medium ${textColors.primary}`}>Net Present Value</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Mean:</span>
                  <span className={`font-medium ${statistics.npv.mean >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                    {formatCurrency(statistics.npv.mean)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Median:</span>
                  <span>{formatCurrency(statistics.npv.median)}</span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>P5 - P95:</span>
                  <span>
                    {formatCurrency(statistics.npv.p5)} - {formatCurrency(statistics.npv.p95)}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className={`font-medium ${textColors.primary}`}>Internal Rate of Return</h4>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Mean:</span>
                  <span className="font-medium">
                    {formatPercentage(statistics.irr.mean / 100)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Median:</span>
                  <span>{formatPercentage(statistics.irr.median / 100)}</span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Range:</span>
                  <span>
                    {formatPercentage(statistics.irr.min / 100)} - {formatPercentage(statistics.irr.max / 100)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  ), [statistics, results.scenario_analysis]);

  // Render risk assessment card
  const renderRiskCard = useCallback(() => (
    <Card className={`border-amber-200 bg-amber-50 ${focusRing.default}`} tabIndex={0}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-amber-800">
          <AlertTriangle className="h-5 w-5" aria-hidden="true" />
          Risk Assessment
        </CardTitle>
      </CardHeader>
      <CardContent>
        {riskAssessment && (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-amber-700">Probability of Loss:</span>
              <Badge variant="outline" className="text-amber-800 border-amber-300">
                {formatPercentage(riskAssessment.probabilityOfLoss / 100)}
              </Badge>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-amber-700">Value at Risk (P5):</span>
              <span className="font-medium text-amber-900">
                {formatCurrency(riskAssessment.valueAtRisk)}
              </span>
            </div>
            
            <Progress 
              value={100 - riskAssessment.probabilityOfLoss} 
              className="h-2"
              aria-label={`Success probability: ${formatPercentage((100 - riskAssessment.probabilityOfLoss) / 100)}`}
            />
          </div>
        )}
      </CardContent>
    </Card>
  ), [riskAssessment]);

  if (!results.scenario_analysis || results.scenario_analysis.length === 0) {
    return (
      <Card className="text-center p-8">
        <CardContent>
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className={`text-lg font-medium ${textColors.primary} mb-2`}>No Results Available</h3>
          <p className={textColors.muted}>
            Run a Monte Carlo simulation to see detailed risk analysis.
          </p>
          {onRerun && (
            <AccessibleButton
              onClick={onRerun}
              className="mt-4"
              loading={isRunning}
              loadingText="Running simulation..."
            >
              <RefreshCw className="h-4 w-4 mr-2" aria-hidden="true" />
              Run Simulation
            </AccessibleButton>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6" role="region" aria-label="Monte Carlo simulation results">
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-2xl font-bold ${textColors.primary}`}>
            Monte Carlo Results
          </h2>
          <p className={textColors.muted}>
            Analysis of {results.scenario_analysis.length} scenarios • {results.analysis_date}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <AccessibleButton
            variant="outline"
            size="sm"
            onClick={() => setViewMode(viewMode === 'summary' ? 'detailed' : 'summary')}
            aria-label={`Switch to ${viewMode === 'summary' ? 'detailed' : 'summary'} view`}
          >
            {viewMode === 'summary' ? 'Detailed View' : 'Summary View'}
          </AccessibleButton>
          
          {onExport && (
            <AccessibleButton
              variant="outline"
              size="sm"
              onClick={() => handleExport('pdf')}
            >
              <Download className="h-4 w-4 mr-2" aria-hidden="true" />
              Export
            </AccessibleButton>
          )}
          
          {onRerun && (
            <AccessibleButton
              onClick={onRerun}
              loading={isRunning}
              loadingText="Running..."
              size="sm"
            >
              <RefreshCw className="h-4 w-4 mr-2" aria-hidden="true" />
              Re-run
            </AccessibleButton>
          )}
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderSummaryCard()}
        {renderRiskCard()}
      </div>

      {/* Detailed analysis tabs */}
      <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className={focusRing.default}>
            Overview
          </TabsTrigger>
          <TabsTrigger value="distribution" className={focusRing.default}>
            Distribution
          </TabsTrigger>
          <TabsTrigger value="scenarios" className={focusRing.default}>
            Scenarios
          </TabsTrigger>
          <TabsTrigger value="statistics" className={focusRing.default}>
            Statistics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <LazyChartLoader
              chartType="distribution"
              data={chartData.histogram}
              title="NPV Distribution"
              description="Histogram showing the distribution of Net Present Value across all scenarios"
              loadOnScroll={!enablePerformanceMode}
              enableManualLoad={enablePerformanceMode}
            />
            
            <LazyChartLoader
              chartType="distribution"
              data={chartData.percentiles}
              title="Risk Percentiles"
              description="Key percentile values for risk assessment"
              loadOnScroll={!enablePerformanceMode}
              enableManualLoad={enablePerformanceMode}
            />
          </div>
        </TabsContent>

        <TabsContent value="distribution" className="space-y-4">
          <LazyChartLoader
            chartType="distribution"
            data={results.scenario_analysis}
            title="Full Distribution Analysis"
            description="Comprehensive view of all Monte Carlo scenario results"
            loadOnScroll={!enablePerformanceMode}
            enableManualLoad={enablePerformanceMode}
          />
        </TabsContent>

        <TabsContent value="scenarios" className="space-y-4">
          {viewMode === 'detailed' ? (
            <Suspense fallback={<div className="h-64 bg-gray-100 rounded-lg animate-pulse" />}>
              <DetailedCharts 
                results={results.scenario_analysis} 
                onExport={onExport}
              />
            </Suspense>
          ) : (
            <LazyChartLoader
              chartType="scenario-analysis"
              data={results.scenario_analysis}
              title="Scenario Analysis"
              description="Analysis of different market scenarios and their outcomes"
              loadOnScroll={!enablePerformanceMode}
              enableManualLoad={enablePerformanceMode}
            />
          )}
        </TabsContent>

        <TabsContent value="statistics" className="space-y-4">
          <Suspense fallback={<div className="h-48 bg-gray-100 rounded-lg animate-pulse" />}>
            <StatisticsTable statistics={statistics} />
          </Suspense>
        </TabsContent>
      </Tabs>
    </div>
  );
}