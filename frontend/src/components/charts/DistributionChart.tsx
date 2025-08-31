/**
 * Distribution Chart Component
 * Interactive histograms and box plots for probability distributions
 */

'use client';

import { useState, useMemo, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Line,
  Area,
  ComposedChart,
  ReferenceLine,
  Scatter,
  ScatterChart,
  Cell,
} from 'recharts';
import {
  BarChart3,
  Download,
  Eye,
  EyeOff,
  Target,
} from 'lucide-react';
import { formatCurrency, formatPercentage } from '@/lib/utils';

export interface DistributionDataPoint {
  value: number;
  frequency: number;
  percentile: number;
  label: string;
}


interface DistributionChartProps {
  data: number[];
  title: string;
  metric: 'npv' | 'irr' | 'cashflow';
  percentiles?: {
    p5: number;
    p25: number;
    median: number;
    p75: number;
    p95: number;
  };
  onExport?: (format: 'png' | 'svg' | 'csv') => void;
  className?: string;
}

export function DistributionChart({
  data,
  title,
  metric,
  percentiles,
  onExport,
  className = '',
}: DistributionChartProps) {
  const [chartType, setChartType] = useState<'histogram' | 'density' | 'boxplot' | 'scatter'>('histogram');
  const [bins, setBins] = useState(25);
  const [showPercentiles, setShowPercentiles] = useState(true);
  const [showOutliers, setShowOutliers] = useState(true);

  // Process data into histogram
  const histogramData = useMemo(() => {
    if (!data.length) return [];

    const min = Math.min(...data);
    const max = Math.max(...data);
    const binSize = (max - min) / bins;
    
    const histogram = Array.from({ length: bins }, (_, i) => {
      const binMin = min + (i * binSize);
      const binMax = min + ((i + 1) * binSize);
      const binCenter = (binMin + binMax) / 2;
      
      const count = data.filter(value => 
        value >= binMin && (i === bins - 1 ? value <= binMax : value < binMax)
      ).length;
      
      const frequency = count / data.length;
      const percentile = (data.filter(value => value <= binCenter).length / data.length) * 100;
      
      return {
        binCenter,
        binMin,
        binMax,
        count,
        frequency: frequency * 100, // Convert to percentage
        percentile,
        label: formatValue(binCenter, metric),
        range: `${formatValue(binMin, metric)} - ${formatValue(binMax, metric)}`,
      };
    });

    return histogram;
  }, [data, bins, metric]);

  // Process data for density curve (smoothed distribution)
  const densityData = useMemo(() => {
    if (!data.length) return [];

    const sortedData = [...data].sort((a, b) => a - b);
    const min = sortedData[0];
    const max = sortedData[sortedData.length - 1];
    const points = 100;
    const step = (max - min) / points;
    
    const density = Array.from({ length: points }, (_, i) => {
      const x = min + (i * step);
      
      // Simple kernel density estimation using Gaussian kernel
      const bandwidth = (max - min) / 20;
      let sum = 0;
      
      for (const value of sortedData) {
        const u = (x - value) / bandwidth;
        sum += Math.exp(-0.5 * u * u);
      }
      
      const density = sum / (sortedData.length * bandwidth * Math.sqrt(2 * Math.PI));
      
      return {
        x,
        density: density * 100, // Scale for visibility
        value: x,
        label: formatValue(x, metric),
      };
    });

    return density;
  }, [data, metric]);

  // Process data for box plot
  const boxPlotData = useMemo(() => {
    if (!data.length) return null;

    const sorted = [...data].sort((a, b) => a - b);
    const n = sorted.length;
    
    const q1Index = Math.floor(n * 0.25);
    const medianIndex = Math.floor(n * 0.5);
    const q3Index = Math.floor(n * 0.75);
    
    const q1 = sorted[q1Index];
    const median = sorted[medianIndex];
    const q3 = sorted[q3Index];
    const iqr = q3 - q1;
    
    // Calculate outliers (values beyond 1.5 * IQR from quartiles)
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;
    const outliers = sorted.filter(value => value < lowerBound || value > upperBound);
    
    // Find min and max excluding outliers
    const min = sorted.find(value => value >= lowerBound) || sorted[0];
    const max = sorted.reverse().find(value => value <= upperBound) || sorted[0];

    return {
      metric: title,
      min,
      q1,
      median,
      q3,
      max,
      outliers,
    };
  }, [data, title]);

  // Scatter plot data (value vs frequency)
  const scatterData = useMemo(() => {
    return data.map((value, index) => ({
      index,
      value,
      label: formatValue(value, metric),
    }));
  }, [data, metric]);

  const formatValue = useCallback((value: number, metricType: string) => {
    switch (metricType) {
      case 'npv':
      case 'cashflow':
        return formatCurrency(value, { compact: true });
      case 'irr':
        return formatPercentage(value / 100);
      default:
        return value.toLocaleString();
    }
  }, []);

  const getMetricUnit = () => {
    switch (metric) {
      case 'npv':
      case 'cashflow':
        return 'USD';
      case 'irr':
        return '%';
      default:
        return '';
    }
  };

  const getColor = (value: number) => {
    if (!percentiles) return '#3B82F6';
    
    if (value <= percentiles.p25) return '#EF4444'; // Red
    if (value <= percentiles.p75) return '#F59E0B'; // Amber
    return '#10B981'; // Green
  };

  const percentileLines = percentiles ? [
    { key: 'p5', value: percentiles.p5, color: '#EF4444', label: '5th Percentile' },
    { key: 'p25', value: percentiles.p25, color: '#F59E0B', label: '25th Percentile' },
    { key: 'median', value: percentiles.median, color: '#3B82F6', label: 'Median' },
    { key: 'p75', value: percentiles.p75, color: '#10B981', label: '75th Percentile' },
    { key: 'p95', value: percentiles.p95, color: '#059669', label: '95th Percentile' },
  ] : [];

  return (
    <div className={`space-y-6 ${className}`}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                {title} Distribution
              </CardTitle>
              <CardDescription>
                Probability distribution analysis with {data.length.toLocaleString()} data points
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                {(['histogram', 'density', 'boxplot', 'scatter'] as const).map((type) => (
                  <Badge
                    key={type}
                    variant={chartType === type ? "default" : "outline"}
                    className="cursor-pointer hover:bg-gray-100 transition-colors"
                    onClick={() => setChartType(type)}
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </Badge>
                ))}
              </div>
              {onExport && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onExport('png')}
                  className="flex items-center space-x-1"
                >
                  <Download className="h-3 w-3" />
                  <span>Export</span>
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <Tabs value={chartType} onValueChange={(value) => setChartType(value as 'histogram' | 'density' | 'boxplot' | 'scatter')}>
            <div className="flex items-center justify-between mb-6">
              <TabsList className="grid w-auto grid-cols-4">
                <TabsTrigger value="histogram">Histogram</TabsTrigger>
                <TabsTrigger value="density">Density</TabsTrigger>
                <TabsTrigger value="boxplot">Box Plot</TabsTrigger>
                <TabsTrigger value="scatter">Scatter</TabsTrigger>
              </TabsList>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <label className="text-sm">Bins:</label>
                  <select
                    value={bins}
                    onChange={(e) => setBins(parseInt(e.target.value))}
                    className="px-2 py-1 border rounded text-sm"
                    disabled={chartType !== 'histogram'}
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                  </select>
                </div>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPercentiles(!showPercentiles)}
                  className="flex items-center space-x-1"
                >
                  {showPercentiles ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
                  <span>Percentiles</span>
                </Button>
              </div>
            </div>

            {/* Histogram View */}
            <TabsContent value="histogram">
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={histogramData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="binCenter"
                      tickFormatter={(value) => formatValue(value, metric)}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis 
                      yAxisId="frequency"
                      label={{ value: 'Frequency (%)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip
                      formatter={(value, name) => {
                        if (name === 'frequency' && typeof value === 'number') return [`${value.toFixed(2)}%`, 'Frequency'];
                        return [value, name];
                      }}
                      labelFormatter={(label, payload) => {
                        if (payload?.[0]?.payload) {
                          const data = payload[0].payload;
                          return `Range: ${data.range}`;
                        }
                        return label;
                      }}
                    />
                    <Bar
                      yAxisId="frequency"
                      dataKey="frequency"
                      fill="#3B82F6"
                      fillOpacity={0.7}
                      stroke="#1E40AF"
                      strokeWidth={1}
                    >
                      {histogramData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getColor(entry.binCenter)} />
                      ))}
                    </Bar>
                    
                    {/* Percentile Lines */}
                    {showPercentiles && percentileLines.map((line) => (
                      <ReferenceLine
                        key={line.key}
                        x={line.value}
                        stroke={line.color}
                        strokeDasharray="4 4"
                        strokeWidth={2}
                        label={{ value: line.label, position: 'top' }}
                      />
                    ))}
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </TabsContent>

            {/* Density Curve View */}
            <TabsContent value="density">
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={densityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="x"
                      tickFormatter={(value) => formatValue(value, metric)}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis label={{ value: 'Density', angle: -90, position: 'insideLeft' }} />
                    <Tooltip
                      formatter={(value, name) => [`${typeof value === 'number' ? value.toFixed(3) : value}`, 'Density']}
                      labelFormatter={(label) => `Value: ${formatValue(label, metric)}`}
                    />
                    <Area
                      type="monotone"
                      dataKey="density"
                      stroke="#3B82F6"
                      fill="#3B82F6"
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="density"
                      stroke="#1E40AF"
                      strokeWidth={2}
                      dot={false}
                    />
                    
                    {/* Percentile Lines */}
                    {showPercentiles && percentileLines.map((line) => (
                      <ReferenceLine
                        key={line.key}
                        x={line.value}
                        stroke={line.color}
                        strokeDasharray="4 4"
                        strokeWidth={2}
                        label={{ value: line.label, position: 'top' }}
                      />
                    ))}
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </TabsContent>

            {/* Box Plot View */}
            <TabsContent value="boxplot">
              <div className="h-96">
                {boxPlotData && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-5 gap-4 text-sm">
                      <div className="text-center p-3 bg-red-50 rounded-lg">
                        <div className="text-red-600 font-medium">Minimum</div>
                        <div className="font-mono">{formatValue(boxPlotData.min, metric)}</div>
                      </div>
                      <div className="text-center p-3 bg-amber-50 rounded-lg">
                        <div className="text-amber-600 font-medium">Q1 (25th)</div>
                        <div className="font-mono">{formatValue(boxPlotData.q1, metric)}</div>
                      </div>
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="text-blue-600 font-medium">Median</div>
                        <div className="font-mono">{formatValue(boxPlotData.median, metric)}</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-green-600 font-medium">Q3 (75th)</div>
                        <div className="font-mono">{formatValue(boxPlotData.q3, metric)}</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-green-600 font-medium">Maximum</div>
                        <div className="font-mono">{formatValue(boxPlotData.max, metric)}</div>
                      </div>
                    </div>
                    
                    {/* Visual Box Plot Representation */}
                    <div className="relative bg-gray-50 p-8 rounded-lg">
                      <div className="relative h-32">
                        <div className="absolute top-1/2 transform -translate-y-1/2 w-full">
                          <div 
                            className="bg-white border-2 border-blue-500 h-16 relative"
                            style={{
                              left: `${((boxPlotData.q1 - boxPlotData.min) / (boxPlotData.max - boxPlotData.min)) * 100}%`,
                              width: `${((boxPlotData.q3 - boxPlotData.q1) / (boxPlotData.max - boxPlotData.min)) * 100}%`,
                            }}
                          >
                            {/* Median line */}
                            <div 
                              className="absolute bg-blue-600 w-1 h-full"
                              style={{
                                left: `${((boxPlotData.median - boxPlotData.q1) / (boxPlotData.q3 - boxPlotData.q1)) * 100}%`,
                              }}
                            />
                          </div>
                          
                          {/* Whiskers */}
                          <div 
                            className="absolute bg-blue-500 h-0.5 top-1/2"
                            style={{
                              left: '0%',
                              width: `${((boxPlotData.q1 - boxPlotData.min) / (boxPlotData.max - boxPlotData.min)) * 100}%`,
                            }}
                          />
                          <div 
                            className="absolute bg-blue-500 h-0.5 top-1/2"
                            style={{
                              left: `${((boxPlotData.q3 - boxPlotData.min) / (boxPlotData.max - boxPlotData.min)) * 100}%`,
                              width: `${((boxPlotData.max - boxPlotData.q3) / (boxPlotData.max - boxPlotData.min)) * 100}%`,
                            }}
                          />
                          
                          {/* End caps */}
                          <div className="absolute bg-blue-500 w-0.5 h-4 top-1/2 transform -translate-y-1/2 left-0" />
                          <div className="absolute bg-blue-500 w-0.5 h-4 top-1/2 transform -translate-y-1/2 right-0" />
                        </div>
                      </div>
                    </div>
                    
                    {/* Outliers */}
                    {showOutliers && boxPlotData.outliers.length > 0 && (
                      <div className="p-3 bg-red-50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Target className="h-4 w-4 text-red-600" />
                          <span className="text-red-600 font-medium">Outliers ({boxPlotData.outliers.length})</span>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {boxPlotData.outliers.slice(0, 20).map((outlier, index) => (
                            <Badge key={index} variant="secondary" className="text-xs font-mono">
                              {formatValue(outlier, metric)}
                            </Badge>
                          ))}
                          {boxPlotData.outliers.length > 20 && (
                            <Badge variant="outline" className="text-xs">
                              +{boxPlotData.outliers.length - 20} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </TabsContent>

            {/* Scatter Plot View */}
            <TabsContent value="scatter">
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart data={scatterData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="index"
                      label={{ value: 'Scenario Index', position: 'insideBottom', offset: -10 }}
                    />
                    <YAxis
                      dataKey="value"
                      tickFormatter={(value) => formatValue(value, metric)}
                      label={{ value: `${title} (${getMetricUnit()})`, angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip
                      formatter={(value, name) => [formatValue(value as number, metric), title]}
                      labelFormatter={(label) => `Scenario #${label}`}
                    />
                    <Scatter
                      dataKey="value"
                      fill="#3B82F6"
                      fillOpacity={0.6}
                    >
                      {scatterData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getColor(entry.value)} />
                      ))}
                    </Scatter>
                    
                    {/* Percentile Lines */}
                    {showPercentiles && percentileLines.map((line) => (
                      <ReferenceLine
                        key={line.key}
                        y={line.value}
                        stroke={line.color}
                        strokeDasharray="4 4"
                        strokeWidth={2}
                        label={{ value: line.label, position: 'insideTopLeft' }}
                      />
                    ))}
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}