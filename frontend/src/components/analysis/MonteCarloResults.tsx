/**
 * Monte Carlo Results Visualization Component
 * Displays statistical analysis results from Monte Carlo simulations
 */

'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  TrendingUp,
  Target,
  AlertTriangle,
  Activity,
  Download,
  RefreshCw,
  BarChart3,
} from 'lucide-react';
import { MonteCarloResult } from '@/types/analysis';
import { formatCurrency, formatPercentage, textColors } from '@/lib/utils';
import { ScenarioAnalysisCharts } from './ScenarioAnalysisCharts';

interface MonteCarloResultsProps {
  results: MonteCarloResult;
  onRerun?: () => void;
  onExport?: (format: 'pdf' | 'excel') => void;
  isRunning?: boolean;
}

export function MonteCarloResults({ 
  results, 
  onRerun, 
  onExport, 
  isRunning = false 
}: MonteCarloResultsProps) {
  const [selectedMetric, setSelectedMetric] = useState<'npv' | 'irr' | 'total_cash_flow'>('npv');

  
  const percentiles = results.percentiles;
  const distribution = results.distribution;

  // Calculate probability of success (positive NPV)
  const successProbability = (distribution.filter(d => d.npv > 0).length / distribution.length) * 100;

  // Prepare data for charts
  const distributionData = distribution.map((scenario, index) => ({
    scenario: index + 1,
    npv: scenario.npv,
    irr: scenario.irr,
    total_cash_flow: scenario.total_cash_flow,
    risk_score: scenario.risk_score,
  }));

  // Create histogram data for selected metric
  const createHistogramData = (metric: 'npv' | 'irr' | 'total_cash_flow') => {
    const values = distributionData.map(d => d[metric]);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const buckets = 20;
    const bucketSize = (max - min) / buckets;
    
    const histogram = Array.from({ length: buckets }, (_, i) => {
      const bucketMin = min + (i * bucketSize);
      const bucketMax = min + ((i + 1) * bucketSize);
      const count = values.filter(v => v >= bucketMin && v < bucketMax).length;
      
      return {
        range: `${formatValue(bucketMin, metric)} - ${formatValue(bucketMax, metric)}`,
        count,
        probability: (count / values.length) * 100,
        midpoint: (bucketMin + bucketMax) / 2,
      };
    });
    
    return histogram;
  };

  const formatValue = (value: number, metric: 'npv' | 'irr' | 'total_cash_flow') => {
    switch (metric) {
      case 'npv':
      case 'total_cash_flow':
        return formatCurrency(value, { compact: true });
      case 'irr':
        return formatPercentage(value / 100);
      default:
        return value.toString();
    }
  };

  const getMetricLabel = (metric: 'npv' | 'irr' | 'total_cash_flow') => {
    switch (metric) {
      case 'npv':
        return 'Net Present Value';
      case 'irr':
        return 'Internal Rate of Return';
      case 'total_cash_flow':
        return 'Total Cash Flow';
    }
  };


  const getRiskLevelColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'moderate':
        return 'text-amber-600 bg-amber-50 border-amber-200';
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  // Risk distribution data for pie chart
  const riskDistribution = [
    { name: 'Low Risk', value: results.risk_distribution.low, color: '#10B981' },
    { name: 'Moderate Risk', value: results.risk_distribution.moderate, color: '#F59E0B' },
    { name: 'High Risk', value: results.risk_distribution.high, color: '#EF4444' },
  ].filter(item => item.value > 0);

  const histogramData = createHistogramData(selectedMetric);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-xl font-semibold ${textColors.primary}`}>
            Monte Carlo Simulation Results
          </h2>
          <p className={`text-sm ${textColors.muted} mt-1`}>
            Analysis of {results.total_scenarios.toLocaleString()} scenarios • 
            Run time: {results.execution_time_ms}ms
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {onRerun && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRerun}
              disabled={isRunning}
              className="flex items-center space-x-2"
            >
              {isRunning ? (
                <Activity className="h-4 w-4 animate-pulse" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              <span>{isRunning ? 'Running...' : 'Rerun'}</span>
            </Button>
          )}
          {onExport && (
            <div className="flex space-x-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onExport('pdf')}
                className="text-xs"
              >
                <Download className="h-3 w-3 mr-1" />
                PDF
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onExport('excel')}
                className="text-xs"
              >
                <Download className="h-3 w-3 mr-1" />
                Excel
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Key Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Success Probability
                </p>
                <p className={`text-2xl font-bold ${successProbability > 70 ? 'text-green-600' : successProbability > 40 ? 'text-amber-600' : 'text-red-600'} mt-1`}>
                  {successProbability.toFixed(1)}%
                </p>
                <p className={`text-xs ${textColors.muted} mt-1`}>
                  Positive NPV scenarios
                </p>
              </div>
              <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${
                successProbability > 70 ? 'bg-green-50' : successProbability > 40 ? 'bg-amber-50' : 'bg-red-50'
              }`}>
                <Target className={`h-6 w-6 ${
                  successProbability > 70 ? 'text-green-600' : successProbability > 40 ? 'text-amber-600' : 'text-red-600'
                }`} />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Expected NPV
                </p>
                <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                  {formatCurrency(percentiles.npv.median, { compact: true })}
                </p>
                <p className={`text-xs ${textColors.muted} mt-1`}>
                  Median value
                </p>
              </div>
              <div className="h-12 w-12 bg-blue-50 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Risk Level
                </p>
                <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                  {results.overall_risk_assessment}
                </p>
                <p className={`text-xs ${textColors.muted} mt-1`}>
                  Overall assessment
                </p>
              </div>
              <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${
                getRiskLevelColor(results.overall_risk_assessment).split(' ')[1]
              }`}>
                <AlertTriangle className={`h-6 w-6 ${
                  getRiskLevelColor(results.overall_risk_assessment).split(' ')[0]
                }`} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analysis Tabs */}
      <Tabs defaultValue="distribution" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="distribution">Distribution</TabsTrigger>
          <TabsTrigger value="percentiles">Percentiles</TabsTrigger>
          <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
          <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
        </TabsList>

        {/* Distribution Analysis */}
        <TabsContent value="distribution" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Probability Distribution</CardTitle>
                  <CardDescription>
                    Distribution of {getMetricLabel(selectedMetric)} across all scenarios
                  </CardDescription>
                </div>
                <div className="flex space-x-2">
                  {(['npv', 'irr', 'total_cash_flow'] as const).map((metric) => (
                    <Badge
                      key={metric}
                      variant={selectedMetric === metric ? "default" : "outline"}
                      className="cursor-pointer hover:bg-gray-100 transition-colors"
                      onClick={() => setSelectedMetric(metric)}
                    >
                      {getMetricLabel(metric)}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={histogramData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="midpoint"
                      tickFormatter={(value) => formatValue(value, selectedMetric)}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis 
                      label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      formatter={(value) => [`${typeof value === 'number' ? value.toFixed(1) : value}%`, 'Probability']}
                      labelFormatter={(label) => `Range: ${formatValue(label, selectedMetric)}`}
                    />
                    <Bar 
                      dataKey="probability" 
                      fill="#3B82F6" 
                      fillOpacity={0.7}
                      stroke="#1E40AF"
                      strokeWidth={1}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Percentiles Analysis */}
        <TabsContent value="percentiles" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* NPV Percentiles */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                  NPV Percentiles
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(percentiles.npv).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className={`text-sm font-medium ${textColors.secondary} capitalize`}>
                      {key === 'p5' ? '5th' : key === 'p25' ? '25th' : key === 'p75' ? '75th' : key === 'p95' ? '95th' : key} Percentile
                    </span>
                    <span className={`font-mono text-sm ${textColors.body}`}>
                      {formatCurrency(value)}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* IRR Percentiles */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                  IRR Percentiles
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(percentiles.irr).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className={`text-sm font-medium ${textColors.secondary} capitalize`}>
                      {key === 'p5' ? '5th' : key === 'p25' ? '25th' : key === 'p75' ? '75th' : key === 'p95' ? '95th' : key} Percentile
                    </span>
                    <span className={`font-mono text-sm ${textColors.body}`}>
                      {formatPercentage(value / 100)}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Cash Flow Percentiles */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center">
                  <Activity className="h-5 w-5 mr-2 text-amber-600" />
                  Cash Flow Percentiles
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(percentiles.total_cash_flow).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className={`text-sm font-medium ${textColors.secondary} capitalize`}>
                      {key === 'p5' ? '5th' : key === 'p25' ? '25th' : key === 'p75' ? '75th' : key === 'p95' ? '95th' : key} Percentile
                    </span>
                    <span className={`font-mono text-sm ${textColors.body}`}>
                      {formatCurrency(value)}
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Risk Analysis */}
        <TabsContent value="risk" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Risk Distribution</CardTitle>
                <CardDescription>
                  Breakdown of scenarios by risk level
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={riskDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {riskDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => `${value} scenarios`} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex justify-center space-x-4 mt-4">
                  {riskDistribution.map((item) => (
                    <div key={item.name} className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-sm text-gray-600">
                        {item.name}: {item.value}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Risk Metrics</CardTitle>
                <CardDescription>
                  Key risk indicators and probabilities
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className={`text-sm font-medium ${textColors.secondary}`}>
                      Value at Risk (5%)
                    </span>
                    <span className={`font-mono text-sm ${textColors.body}`}>
                      {formatCurrency(percentiles.npv.p5)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className={`text-sm font-medium ${textColors.secondary}`}>
                      Expected Shortfall
                    </span>
                    <span className={`font-mono text-sm ${textColors.body}`}>
                      {formatCurrency(Math.min(...distributionData.map(d => d.npv)))}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className={`text-sm font-medium ${textColors.secondary}`}>
                      Probability of Loss
                    </span>
                    <span className={`font-mono text-sm ${textColors.body}`}>
                      {(100 - successProbability).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className={`text-sm font-medium ${textColors.secondary}`}>
                      Maximum Potential Loss
                    </span>
                    <span className={`font-mono text-sm text-red-600`}>
                      {formatCurrency(Math.min(...distributionData.map(d => d.npv)))}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className={`text-sm font-medium ${textColors.secondary}`}>
                      Maximum Potential Gain
                    </span>
                    <span className={`font-mono text-sm text-green-600`}>
                      {formatCurrency(Math.max(...distributionData.map(d => d.npv)))}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Scenario Analysis */}
        <TabsContent value="scenarios" className="space-y-6 mt-6">
          <ScenarioAnalysisCharts
            distribution={distribution}
            selectedMetric={selectedMetric}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}