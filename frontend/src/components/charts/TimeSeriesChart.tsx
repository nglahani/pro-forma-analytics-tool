/**
 * Enhanced Time Series Chart Component
 * Professional market trend visualization with advanced features
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
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
  ReferenceArea,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  Maximize2,
  Minimize2,
  Download,
  Settings,
  Eye,
  EyeOff,
  Zap,
} from 'lucide-react';
import { MarketData } from '@/types/analysis';
import { formatCurrency, formatPercentage, textColors } from '@/lib/utils';

export interface TimeSeriesDataPoint {
  date: string;
  timestamp: number;
  [key: string]: number | string;
}

export interface TimeSeriesConfig {
  title: string;
  description?: string;
  parameters: {
    key: string;
    label: string;
    color: string;
    type: 'line' | 'area' | 'bar';
    unit: string;
    visible: boolean;
    yAxisId?: 'left' | 'right';
  }[];
  dateRange?: {
    start: string;
    end: string;
  };
  annotations?: {
    date: string;
    label: string;
    color: string;
    type: 'vertical' | 'horizontal';
    value?: number;
  }[];
}

interface TimeSeriesChartProps {
  data: TimeSeriesDataPoint[];
  config: TimeSeriesConfig;
  onConfigChange?: (config: TimeSeriesConfig) => void;
  height?: number;
  showBrush?: boolean;
  showZoom?: boolean;
  showLegend?: boolean;
  className?: string;
}

const chartTypes = [
  { key: 'line', label: 'Line Chart', icon: Activity },
  { key: 'area', label: 'Area Chart', icon: BarChart3 },
  { key: 'composed', label: 'Composed Chart', icon: Maximize2 },
] as const;

export function TimeSeriesChart({
  data,
  config,
  onConfigChange,
  height = 400,
  showBrush = true,
  showZoom = true,
  showLegend = true,
  className = '',
}: TimeSeriesChartProps) {
  const [chartType, setChartType] = useState<'line' | 'area' | 'composed'>('line');
  const [isZoomed, setIsZoomed] = useState(false);
  const [zoomDomain, setZoomDomain] = useState<{ start?: number; end?: number }>({});
  const [selectedRange, setSelectedRange] = useState<{ start?: number; end?: number }>({});

  // Filter data based on date range and zoom
  const filteredData = useMemo(() => {
    let filtered = [...data];

    // Apply date range filter
    if (config.dateRange) {
      const startTime = new Date(config.dateRange.start).getTime();
      const endTime = new Date(config.dateRange.end).getTime();
      filtered = filtered.filter(d => d.timestamp >= startTime && d.timestamp <= endTime);
    }

    // Apply zoom filter
    if (isZoomed && zoomDomain.start && zoomDomain.end) {
      filtered = filtered.filter(d => d.timestamp >= zoomDomain.start! && d.timestamp <= zoomDomain.end!);
    }

    return filtered.sort((a, b) => a.timestamp - b.timestamp);
  }, [data, config.dateRange, isZoomed, zoomDomain]);

  // Get visible parameters
  const visibleParameters = config.parameters.filter(p => p.visible);

  // Calculate statistics for visible parameters
  const statistics = useMemo(() => {
    if (filteredData.length === 0) return {};

    const stats: Record<string, {
      current: number;
      min: number;
      max: number;
      avg: number;
      change: number;
      changePercent: number;
      trend: 'up' | 'down' | 'stable';
    }> = {};

    visibleParameters.forEach(param => {
      const values = filteredData.map(d => Number(d[param.key])).filter(v => !isNaN(v));
      if (values.length === 0) return;

      const current = values[values.length - 1];
      const previous = values[values.length - 2] || current;
      const min = Math.min(...values);
      const max = Math.max(...values);
      const avg = values.reduce((sum, v) => sum + v, 0) / values.length;
      const change = current - previous;
      const changePercent = previous !== 0 ? (change / Math.abs(previous)) * 100 : 0;

      let trend: 'up' | 'down' | 'stable' = 'stable';
      if (Math.abs(changePercent) > 1) {
        trend = changePercent > 0 ? 'up' : 'down';
      }

      stats[param.key] = {
        current,
        min,
        max,
        avg,
        change,
        changePercent,
        trend,
      };
    });

    return stats;
  }, [filteredData, visibleParameters]);

  const handleParameterToggle = useCallback((paramKey: string) => {
    if (!onConfigChange) return;

    const newConfig = {
      ...config,
      parameters: config.parameters.map(p =>
        p.key === paramKey ? { ...p, visible: !p.visible } : p
      ),
    };
    onConfigChange(newConfig);
  }, [config, onConfigChange]);

  const handleZoom = useCallback((domain: any) => {
    if (domain && domain.startIndex !== undefined && domain.endIndex !== undefined) {
      const start = filteredData[domain.startIndex]?.timestamp;
      const end = filteredData[domain.endIndex]?.timestamp;
      if (start && end) {
        setZoomDomain({ start, end });
        setIsZoomed(true);
      }
    }
  }, [filteredData]);

  const handleZoomOut = useCallback(() => {
    setIsZoomed(false);
    setZoomDomain({});
  }, []);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length > 0) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-semibold mb-2">{new Date(label).toLocaleDateString()}</p>
          {payload.map((entry: any, index: number) => {
            const param = config.parameters.find(p => p.key === entry.dataKey);
            return (
              <div key={index} className="flex items-center justify-between space-x-4 text-sm">
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: entry.color }}
                  />
                  <span>{param?.label || entry.dataKey}</span>
                </div>
                <span className="font-mono">
                  {formatValue(entry.value, param?.unit || '%')}
                </span>
              </div>
            );
          })}
        </div>
      );
    }
    return null;
  };

  const formatValue = (value: number, unit: string) => {
    switch (unit) {
      case '$':
        return formatCurrency(value);
      case '%':
        return formatPercentage(value / 100);
      case '%/year':
        return `${value.toFixed(2)}%/yr`;
      default:
        return value.toFixed(2) + unit;
    }
  };

  const renderChart = () => {
    const commonProps = {
      data: filteredData,
      margin: { top: 5, right: 30, left: 20, bottom: 60 },
    };

    const xAxisProps = {
      dataKey: 'timestamp',
      scale: 'time' as const,
      type: 'number' as const,
      domain: ['dataMin', 'dataMax'],
      tickFormatter: (timestamp: number) => new Date(timestamp).toLocaleDateString('en-US', {
        month: 'short',
        year: '2-digit',
      }),
    };

    const yAxisProps = {
      tick: { fontSize: 12 },
      tickFormatter: (value: number) => `${value.toFixed(1)}%`,
    };

    switch (chartType) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis {...xAxisProps} />
            <YAxis {...yAxisProps} />
            <Tooltip content={<CustomTooltip />} />
            {showLegend && <Legend />}
            {visibleParameters.map((param) => (
              <Area
                key={param.key}
                type="monotone"
                dataKey={param.key}
                stroke={param.color}
                fill={param.color}
                fillOpacity={0.3}
                strokeWidth={2}
                name={param.label}
              />
            ))}
            {config.annotations?.map((annotation, index) => (
              <ReferenceLine
                key={index}
                x={new Date(annotation.date).getTime()}
                stroke={annotation.color}
                strokeDasharray="5 5"
                label={{ value: annotation.label, position: 'top' }}
              />
            ))}
            {showBrush && <Brush dataKey="timestamp" height={30} />}
          </AreaChart>
        );

      case 'composed':
        return (
          <ComposedChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis {...xAxisProps} />
            <YAxis yAxisId="left" {...yAxisProps} />
            <YAxis yAxisId="right" orientation="right" {...yAxisProps} />
            <Tooltip content={<CustomTooltip />} />
            {showLegend && <Legend />}
            {visibleParameters.map((param) => {
              if (param.type === 'bar') {
                return (
                  <Bar
                    key={param.key}
                    yAxisId={param.yAxisId || 'left'}
                    dataKey={param.key}
                    fill={param.color}
                    fillOpacity={0.7}
                    name={param.label}
                  />
                );
              } else {
                return (
                  <Line
                    key={param.key}
                    yAxisId={param.yAxisId || 'left'}
                    type="monotone"
                    dataKey={param.key}
                    stroke={param.color}
                    strokeWidth={2}
                    dot={{ fill: param.color, strokeWidth: 2, r: 3 }}
                    name={param.label}
                  />
                );
              }
            })}
            {config.annotations?.map((annotation, index) => (
              <ReferenceLine
                key={index}
                x={new Date(annotation.date).getTime()}
                stroke={annotation.color}
                strokeDasharray="5 5"
                label={{ value: annotation.label, position: 'top' }}
              />
            ))}
            {showBrush && <Brush dataKey="timestamp" height={30} />}
          </ComposedChart>
        );

      default: // line
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis {...xAxisProps} />
            <YAxis {...yAxisProps} />
            <Tooltip content={<CustomTooltip />} />
            {showLegend && <Legend />}
            {visibleParameters.map((param) => (
              <Line
                key={param.key}
                type="monotone"
                dataKey={param.key}
                stroke={param.color}
                strokeWidth={2}
                dot={{ fill: param.color, strokeWidth: 2, r: 3 }}
                activeDot={{ r: 5 }}
                name={param.label}
              />
            ))}
            {config.annotations?.map((annotation, index) => (
              <ReferenceLine
                key={index}
                x={new Date(annotation.date).getTime()}
                stroke={annotation.color}
                strokeDasharray="5 5"
                label={{ value: annotation.label, position: 'top' }}
              />
            ))}
            {showBrush && <Brush dataKey="timestamp" height={30} onMouseUp={handleZoom} />}
          </LineChart>
        );
    }
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTrendColor = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className={`text-lg font-semibold ${textColors.primary}`}>
            {config.title}
          </h3>
          {config.description && (
            <p className={`text-sm ${textColors.muted} mt-1`}>
              {config.description}
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Chart Type Selector */}
          <div className="flex space-x-1">
            {chartTypes.map(({ key, label, icon: Icon }) => (
              <Button
                key={key}
                variant={chartType === key ? "default" : "outline"}
                size="sm"
                onClick={() => setChartType(key)}
                className="text-xs"
                title={label}
              >
                <Icon className="h-3 w-3" />
              </Button>
            ))}
          </div>

          {/* Zoom Controls */}
          {showZoom && (
            <div className="flex space-x-1">
              {isZoomed ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleZoomOut}
                  className="text-xs"
                >
                  <Minimize2 className="h-3 w-3 mr-1" />
                  Reset
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  disabled
                >
                  <Maximize2 className="h-3 w-3 mr-1" />
                  Zoom
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Parameter Statistics */}
      {visibleParameters.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {visibleParameters.slice(0, 4).map((param) => {
            const stat = statistics[param.key];
            if (!stat) return null;

            return (
              <Card key={param.key} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: param.color }}
                    />
                    <span className="text-sm font-medium">{param.label}</span>
                  </div>
                  {getTrendIcon(stat.trend)}
                </div>
                
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Current:</span>
                    <span className="font-mono">
                      {formatValue(stat.current, param.unit)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Change:</span>
                    <span className={`font-mono ${getTrendColor(stat.trend)}`}>
                      {stat.changePercent > 0 ? '+' : ''}{stat.changePercent.toFixed(2)}%
                    </span>
                  </div>
                  
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Range:</span>
                    <span className="font-mono">
                      {formatValue(stat.min, param.unit)} - {formatValue(stat.max, param.unit)}
                    </span>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Parameter Controls */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center">
            <Settings className="h-4 w-4 mr-2" />
            Chart Parameters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {config.parameters.map((param) => (
              <Badge
                key={param.key}
                variant={param.visible ? "default" : "outline"}
                className="cursor-pointer hover:bg-gray-100 transition-colors flex items-center space-x-1"
                onClick={() => handleParameterToggle(param.key)}
                style={{
                  backgroundColor: param.visible ? param.color : undefined,
                  borderColor: param.color,
                }}
              >
                {param.visible ? (
                  <Eye className="h-3 w-3" />
                ) : (
                  <EyeOff className="h-3 w-3" />
                )}
                <span>{param.label}</span>
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Chart Display */}
      <Card>
        <CardContent className="p-6">
          <div style={{ width: '100%', height: height }}>
            <ResponsiveContainer width="100%" height="100%">
              {renderChart()}
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Data Summary */}
      {filteredData.length > 0 && (
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            Showing {filteredData.length} data points
            {isZoomed && ' (zoomed view)'}
          </span>
          <span>
            {new Date(filteredData[0].timestamp).toLocaleDateString()} - {' '}
            {new Date(filteredData[filteredData.length - 1].timestamp).toLocaleDateString()}
          </span>
        </div>
      )}
    </div>
  );
}