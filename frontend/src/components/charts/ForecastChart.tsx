/**
 * Forecast Chart Component
 * Displays Prophet forecasts with confidence intervals and uncertainty bands
 */

'use client';

import { useState, useMemo, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ErrorBar,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Target,
  AlertTriangle,
  Calendar,
  BarChart3,
  Activity,
  Eye,
  EyeOff,
  Download,
  RefreshCw,
  Zap,
  Info,
} from 'lucide-react';
import { MarketForecast } from '@/types/analysis';
import { formatCurrency, formatPercentage, textColors } from '@/lib/utils';

export interface ForecastDataPoint {
  date: string;
  timestamp: number;
  historical?: number;
  forecast?: number;
  lower_bound?: number;
  upper_bound?: number;
  confidence_level?: number;
  trend?: 'increasing' | 'decreasing' | 'stable';
  seasonal_component?: number;
  trend_component?: number;
}

export interface ForecastConfig {
  parameter: string;
  label: string;
  unit: string;
  color: string;
  confidenceLevel: number;
  forecastHorizon: number; // months
  showHistorical: boolean;
  showConfidenceBands: boolean;
  showTrendComponents: boolean;
}

interface ForecastChartProps {
  data: ForecastDataPoint[];
  config: ForecastConfig;
  onConfigChange?: (config: ForecastConfig) => void;
  onRunForecast?: (parameter: string, horizon: number) => void;
  isLoading?: boolean;
  className?: string;
}

// Generate sample forecast data
const generateSampleForecastData = (parameter: string, months: number = 24): ForecastDataPoint[] => {
  const data: ForecastDataPoint[] = [];
  const baseValue = {
    interest_rate: 6.5,
    cap_rate: 5.5,
    vacancy_rate: 5.0,
    rent_growth_rate: 3.0,
  }[parameter] || 5.0;

  // Generate historical data (24 months)
  for (let i = -24; i < 0; i++) {
    const date = new Date();
    date.setMonth(date.getMonth() + i);
    
    const seasonality = Math.sin((i / 12) * 2 * Math.PI) * 0.5;
    const trend = parameter.includes('growth') ? i * 0.02 : i * -0.01;
    const noise = (Math.random() - 0.5) * 0.8;
    
    data.push({
      date: date.toISOString().split('T')[0],
      timestamp: date.getTime(),
      historical: Math.max(0.1, baseValue + trend + seasonality + noise),
    });
  }

  // Generate forecast data
  for (let i = 0; i < months; i++) {
    const date = new Date();
    date.setMonth(date.getMonth() + i);
    
    const seasonality = Math.sin((i / 12) * 2 * Math.PI) * 0.5;
    const trendGrowth = parameter.includes('growth') ? i * 0.02 : i * -0.01;
    const uncertainty = Math.sqrt(i / 12) * 0.5; // Increasing uncertainty over time
    
    const forecastValue = Math.max(0.1, baseValue + trendGrowth + seasonality);
    const lowerBound = Math.max(0.1, forecastValue - uncertainty * 1.96);
    const upperBound = forecastValue + uncertainty * 1.96;
    
    data.push({
      date: date.toISOString().split('T')[0],
      timestamp: date.getTime(),
      forecast: forecastValue,
      lower_bound: lowerBound,
      upper_bound: upperBound,
      confidence_level: Math.max(0.5, 0.95 - (i / months) * 0.3), // Decreasing confidence
      trend: trendGrowth > 0.1 ? 'increasing' : trendGrowth < -0.1 ? 'decreasing' : 'stable',
      seasonal_component: seasonality,
      trend_component: trendGrowth,
    });
  }

  return data;
};

export function ForecastChart({
  data,
  config,
  onConfigChange,
  onRunForecast,
  isLoading = false,
  className = '',
}: ForecastChartProps) {
  const [showComponents, setShowComponents] = useState(false);
  const [highlightUncertainty, setHighlightUncertainty] = useState(true);

  // Separate historical and forecast data
  const chartData = useMemo(() => {
    return data.map(point => ({
      ...point,
      month: new Date(point.timestamp).toLocaleDateString('en-US', {
        month: 'short',
        year: '2-digit',
      }),
      isHistorical: point.historical !== undefined,
      isForecast: point.forecast !== undefined,
    }));
  }, [data]);

  // Calculate forecast statistics
  const forecastStats = useMemo(() => {
    const forecastPoints = data.filter(d => d.forecast !== undefined);
    if (forecastPoints.length === 0) return null;

    const forecasts = forecastPoints.map(d => d.forecast!);
    const current = data.find(d => d.historical !== undefined)?.historical || 0;
    const finalForecast = forecasts[forecasts.length - 1];
    const totalChange = finalForecast - current;
    const changePercent = current !== 0 ? (totalChange / Math.abs(current)) * 100 : 0;
    
    const avgConfidence = forecastPoints.reduce((sum, d) => sum + (d.confidence_level || 0), 0) / forecastPoints.length;
    const uncertainty = forecasts.reduce((sum, f, i) => {
      const point = forecastPoints[i];
      return sum + ((point.upper_bound || f) - (point.lower_bound || f));
    }, 0) / forecasts.length;

    return {
      currentValue: current,
      finalForecast,
      totalChange,
      changePercent,
      avgConfidence,
      uncertainty,
      trend: changePercent > 1 ? 'increasing' : changePercent < -1 ? 'decreasing' : 'stable',
      forecastHorizon: forecastPoints.length,
    };
  }, [data]);

  const handleConfigUpdate = useCallback((updates: Partial<ForecastConfig>) => {
    if (!onConfigChange) return;
    onConfigChange({ ...config, ...updates });
  }, [config, onConfigChange]);

  const handleRunForecast = useCallback(() => {
    if (onRunForecast) {
      onRunForecast(config.parameter, config.forecastHorizon);
    }
  }, [onRunForecast, config.parameter, config.forecastHorizon]);

  const formatValue = (value: number) => {
    switch (config.unit) {
      case '$':
        return formatCurrency(value);
      case '%':
        return formatPercentage(value / 100);
      case '%/year':
        return `${value.toFixed(2)}%/yr`;
      default:
        return `${value.toFixed(2)}${config.unit}`;
    }
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length > 0) {
      const dataPoint = payload[0].payload;
      return (
        <div className="bg-white p-4 border rounded-lg shadow-lg">
          <p className="font-semibold mb-2">{new Date(label).toLocaleDateString()}</p>
          
          {dataPoint.historical !== undefined && (
            <div className="text-sm mb-1">
              <span className="font-medium">Historical:</span> {formatValue(dataPoint.historical)}
            </div>
          )}
          
          {dataPoint.forecast !== undefined && (
            <>
              <div className="text-sm mb-1">
                <span className="font-medium">Forecast:</span> {formatValue(dataPoint.forecast)}
              </div>
              {dataPoint.lower_bound !== undefined && dataPoint.upper_bound !== undefined && (
                <div className="text-xs text-gray-600 mb-1">
                  Range: {formatValue(dataPoint.lower_bound)} - {formatValue(dataPoint.upper_bound)}
                </div>
              )}
              {dataPoint.confidence_level !== undefined && (
                <div className="text-xs text-gray-600">
                  Confidence: {(dataPoint.confidence_level * 100).toFixed(1)}%
                </div>
              )}
            </>
          )}
        </div>
      );
    }
    return null;
  };

  const getTrendIcon = (trend: 'increasing' | 'decreasing' | 'stable') => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'decreasing':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTrendColor = (trend: 'increasing' | 'decreasing' | 'stable') => {
    switch (trend) {
      case 'increasing':
        return 'text-green-600';
      case 'decreasing':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className={`text-lg font-semibold ${textColors.primary} flex items-center`}>
            <Target className="h-5 w-5 mr-2" />
            {config.label} Forecast
          </h3>
          <p className={`text-sm ${textColors.muted} mt-1`}>
            Prophet-based forecasting with {config.confidenceLevel}% confidence intervals
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRunForecast}
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            {isLoading ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Zap className="h-4 w-4" />
            )}
            <span>Update Forecast</span>
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => {/* Export functionality */}}
            disabled={isLoading}
          >
            <Download className="h-4 w-4 mr-1" />
            Export
          </Button>
        </div>
      </div>

      {/* Forecast Statistics */}
      {forecastStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${textColors.muted}`}>
                    Current Value
                  </p>
                  <p className={`text-xl font-bold ${textColors.primary} mt-1`}>
                    {formatValue(forecastStats.currentValue)}
                  </p>
                </div>
                <Activity className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${textColors.muted}`}>
                    Forecast ({config.forecastHorizon}mo)
                  </p>
                  <p className={`text-xl font-bold ${textColors.primary} mt-1`}>
                    {formatValue(forecastStats.finalForecast)}
                  </p>
                </div>
                {getTrendIcon(forecastStats.trend)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${textColors.muted}`}>
                    Expected Change
                  </p>
                  <p className={`text-xl font-bold ${getTrendColor(forecastStats.trend)} mt-1`}>
                    {forecastStats.changePercent > 0 ? '+' : ''}{forecastStats.changePercent.toFixed(1)}%
                  </p>
                </div>
                <BarChart3 className="h-8 w-8 text-amber-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${textColors.muted}`}>
                    Avg. Confidence
                  </p>
                  <p className={`text-xl font-bold ${textColors.primary} mt-1`}>
                    {(forecastStats.avgConfidence * 100).toFixed(1)}%
                  </p>
                </div>
                <Target className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Chart Controls */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center">
            <BarChart3 className="h-4 w-4 mr-2" />
            Display Options
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <Button
                variant={config.showHistorical ? "default" : "outline"}
                size="sm"
                onClick={() => handleConfigUpdate({ showHistorical: !config.showHistorical })}
                className="text-xs"
              >
                {config.showHistorical ? <Eye className="h-3 w-3 mr-1" /> : <EyeOff className="h-3 w-3 mr-1" />}
                Historical Data
              </Button>
              
              <Button
                variant={config.showConfidenceBands ? "default" : "outline"}
                size="sm"
                onClick={() => handleConfigUpdate({ showConfidenceBands: !config.showConfidenceBands })}
                className="text-xs"
              >
                {config.showConfidenceBands ? <Eye className="h-3 w-3 mr-1" /> : <EyeOff className="h-3 w-3 mr-1" />}
                Confidence Bands
              </Button>
              
              <Button
                variant={showComponents ? "default" : "outline"}
                size="sm"
                onClick={() => setShowComponents(!showComponents)}
                className="text-xs"
              >
                {showComponents ? <Eye className="h-3 w-3 mr-1" /> : <EyeOff className="h-3 w-3 mr-1" />}
                Components
              </Button>
            </div>
            
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium">Forecast Horizon:</label>
              <select
                value={config.forecastHorizon}
                onChange={(e) => handleConfigUpdate({ forecastHorizon: Number(e.target.value) })}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value={6}>6 months</option>
                <option value={12}>12 months</option>
                <option value={18}>18 months</option>
                <option value={24}>24 months</option>
                <option value={36}>36 months</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Forecast Chart */}
      <Card>
        <CardContent className="p-6">
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="month"
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => formatValue(value)}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                
                {/* Historical Data */}
                {config.showHistorical && (
                  <Line
                    type="monotone"
                    dataKey="historical"
                    stroke={config.color}
                    strokeWidth={2}
                    dot={{ fill: config.color, strokeWidth: 2, r: 3 }}
                    name="Historical"
                    connectNulls={false}
                  />
                )}
                
                {/* Confidence Bands */}
                {config.showConfidenceBands && (
                  <Area
                    type="monotone"
                    dataKey="upper_bound"
                    stroke="none"
                    fill={config.color}
                    fillOpacity={0.1}
                    name="Confidence Band"
                  />
                )}
                
                {config.showConfidenceBands && (
                  <Area
                    type="monotone"
                    dataKey="lower_bound"
                    stroke="none"
                    fill="white"
                    fillOpacity={1}
                    name=""
                  />
                )}
                
                {/* Forecast Line */}
                <Line
                  type="monotone"
                  dataKey="forecast"
                  stroke={config.color}
                  strokeWidth={3}
                  strokeDasharray="5 5"
                  dot={{ fill: config.color, strokeWidth: 2, r: 4 }}
                  name="Forecast"
                  connectNulls={false}
                />
                
                {/* Reference line for current date */}
                <ReferenceLine
                  x={new Date().toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
                  stroke="#ef4444"
                  strokeDasharray="3 3"
                  label={{ value: "Today", position: "top" }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Components Analysis */}
      {showComponents && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Trend Component</CardTitle>
              <CardDescription>
                Long-term directional movement in the data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData.filter(d => d.trend_component !== undefined)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="trend_component"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Seasonal Component</CardTitle>
              <CardDescription>
                Recurring patterns and cyclical behavior
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData.filter(d => d.seasonal_component !== undefined)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="seasonal_component"
                      stroke="#10B981"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Forecast Quality Indicators */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Info className="h-5 w-5 mr-2 text-blue-600" />
            Forecast Quality & Assumptions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-3">Model Performance</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Confidence Level:</span>
                  <span className="font-mono">{config.confidenceLevel}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Forecast Horizon:</span>
                  <span className="font-mono">{config.forecastHorizon} months</span>
                </div>
                <div className="flex justify-between">
                  <span>Uncertainty Growth:</span>
                  <span className="font-mono">±{forecastStats ? (forecastStats.uncertainty / 2).toFixed(2) : '0.5'}{config.unit}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Key Assumptions</h4>
              <div className="text-sm space-y-1">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                  <span>Market conditions remain stable</span>
                </div>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                  <span>No major regulatory changes</span>
                </div>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                  <span>Economic trends continue</span>
                </div>
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                  <span>Seasonal patterns persist</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}