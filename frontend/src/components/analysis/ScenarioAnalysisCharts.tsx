/**
 * Enhanced Scenario Analysis Charts Component
 * Advanced visualization of Monte Carlo scenario analysis with interactive charts
 */

'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Bar,
  BarChart,
  ReferenceLine,
} from 'recharts';
import {
  Target,
  Filter,
  BarChart3,
  Activity,
} from 'lucide-react';
import { ScenarioDistribution } from '@/types/analysis';
import { formatCurrency, formatPercentage } from '@/lib/utils';

interface ScenarioAnalysisChartsProps {
  distribution: ScenarioDistribution[];
  selectedMetric?: 'npv' | 'irr' | 'cashflow';
  onMetricChange?: (metric: 'npv' | 'irr' | 'cashflow') => void;
}

export function ScenarioAnalysisCharts({ 
  distribution, 
  selectedMetric = 'npv',
  onMetricChange 
}: ScenarioAnalysisChartsProps) {
  const [selectedClassification, setSelectedClassification] = useState<MarketClassification | 'ALL'>('ALL');
  const [showOutliers, setShowOutliers] = useState(true);

  // Filter data based on selected classification
  const filteredData = useMemo(() => {
    if (selectedClassification === 'ALL') {
      return distribution;
    }
    return distribution.filter(d => d.market_classification === selectedClassification);
  }, [distribution, selectedClassification]);

  // Remove outliers if needed (beyond 2 standard deviations)
  const cleanedData = useMemo(() => {
    if (showOutliers) return filteredData;

    const values = filteredData.map(d => d[selectedMetric]);
    const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
    const stdDev = Math.sqrt(values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length);
    const threshold = 2 * stdDev;

    return filteredData.filter(d => Math.abs(d[selectedMetric] - mean) <= threshold);
  }, [filteredData, selectedMetric, showOutliers]);

  // Prepare data for different chart types
  const scatterData = cleanedData.map(d => ({
    ...d,
    x: d.irr,
    y: d.npv,
    z: d.total_cash_flow,
    size: Math.abs(d.npv) / 1000000, // Size based on NPV magnitude
    color: getMarketClassificationColor(d.market_classification),
  }));

  // Risk vs Return analysis
  const riskReturnData = cleanedData.map(d => ({
    risk: d.risk_score,
    return: d.irr,
    npv: d.npv,
    classification: d.market_classification,
    color: getMarketClassificationColor(d.market_classification),
  }));

  // Distribution buckets for histogram
  const createHistogramData = (metric: 'npv' | 'irr' | 'cashflow') => {
    const values = cleanedData.map(d => d[metric]);
    if (values.length === 0) return [];

    const min = Math.min(...values);
    const max = Math.max(...values);
    const buckets = 25;
    const bucketSize = (max - min) / buckets;

    const histogram = Array.from({ length: buckets }, (_, i) => {
      const bucketMin = min + (i * bucketSize);
      const bucketMax = min + ((i + 1) * bucketSize);
      const scenarios = values.filter(v => v >= bucketMin && v < bucketMax);
      
      return {
        range: `${formatValue(bucketMin, metric)} - ${formatValue(bucketMax, metric)}`,
        count: scenarios.length,
        probability: (scenarios.length / values.length) * 100,
        midpoint: (bucketMin + bucketMax) / 2,
        bucketMin,
        bucketMax,
      };
    });

    return histogram.filter(h => h.count > 0);
  };

  // Market performance comparison
  const marketPerformanceData = useMemo(() => {
    const classifications = Object.values(MarketClassification);
    return classifications.map(classification => {
      const classificationData = distribution.filter(d => d.market_classification === classification);
      if (classificationData.length === 0) return null;

      const avgNpv = classificationData.reduce((sum, d) => sum + d.npv, 0) / classificationData.length;
      const avgIrr = classificationData.reduce((sum, d) => sum + d.irr, 0) / classificationData.length;
      const avgCashFlow = classificationData.reduce((sum, d) => sum + d.total_cash_flow, 0) / classificationData.length;
      const avgRisk = classificationData.reduce((sum, d) => sum + d.risk_score, 0) / classificationData.length;

      return {
        classification,
        avgNpv,
        avgIrr,
        avgCashFlow,
        avgRisk,
        count: classificationData.length,
        color: getMarketClassificationColor(classification),
      };
    }).filter(Boolean);
  }, [distribution]);

  const histogramData = createHistogramData(selectedMetric);

  function getMarketClassificationColor(classification: MarketClassification): string {
    switch (classification) {
      case MarketClassification.BULL:
        return '#10B981'; // Green
      case MarketClassification.BEAR:
        return '#EF4444'; // Red
      case MarketClassification.NEUTRAL:
        return '#6B7280'; // Gray
      case MarketClassification.GROWTH:
        return '#3B82F6'; // Blue
      case MarketClassification.STRESS:
        return '#F59E0B'; // Amber
      default:
        return '#6B7280';
    }
  }

  function formatValue(value: number, metric: 'npv' | 'irr' | 'cashflow') {
    switch (metric) {
      case 'npv':
      case 'cashflow':
        return formatCurrency(value, { compact: true });
      case 'irr':
        return formatPercentage(value / 100);
      default:
        return value.toString();
    }
  }

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ value: number; dataKey: string; color: string; payload: Record<string, unknown> }>; label?: string }) => {
    if (active && payload && payload.length > 0) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-semibold">Scenario #{data.scenario_id}</p>
          <p className="text-sm">
            <span className="font-medium">NPV:</span> {formatCurrency(data.npv)}
          </p>
          <p className="text-sm">
            <span className="font-medium">IRR:</span> {formatPercentage(data.irr / 100)}
          </p>
          <p className="text-sm">
            <span className="font-medium">Cash Flow:</span> {formatCurrency(data.total_cash_flow)}
          </p>
          <p className="text-sm">
            <span className="font-medium">Risk Score:</span> {data.risk_score.toFixed(2)}
          </p>
          <p className="text-sm">
            <span className="font-medium">Market:</span> {data.market_classification}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-600" />
            <span className="text-sm font-medium">Market Filter:</span>
            <div className="flex space-x-1">
              {['ALL', ...Object.values(MarketClassification)].map((classification) => (
                <Badge
                  key={classification}
                  variant={selectedClassification === classification ? "default" : "outline"}
                  className="cursor-pointer hover:bg-gray-100 transition-colors text-xs"
                  onClick={() => setSelectedClassification(classification as MarketClassification | 'ALL')}
                >
                  {classification}
                </Badge>
              ))}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant={showOutliers ? "default" : "outline"}
            size="sm"
            onClick={() => setShowOutliers(!showOutliers)}
            className="text-xs"
          >
            {showOutliers ? 'Hide' : 'Show'} Outliers
          </Button>
          <span className="text-sm text-gray-600">
            {cleanedData.length} of {distribution.length} scenarios
          </span>
        </div>
      </div>

      {/* Analysis Tabs */}
      <Tabs defaultValue="scatter" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="scatter">NPV vs IRR</TabsTrigger>
          <TabsTrigger value="risk-return">Risk vs Return</TabsTrigger>
          <TabsTrigger value="distribution">Distribution</TabsTrigger>
          <TabsTrigger value="market-comparison">Market Analysis</TabsTrigger>
        </TabsList>

        {/* NPV vs IRR Scatter Plot */}
        <TabsContent value="scatter" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <Activity className="h-5 w-5 mr-2 text-blue-600" />
                NPV vs IRR Analysis
              </CardTitle>
              <CardDescription>
                Correlation between Net Present Value and Internal Rate of Return across scenarios
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart data={scatterData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="x"
                      name="IRR"
                      unit="%"
                      label={{ value: 'Internal Rate of Return (%)', position: 'insideBottom', offset: -10 }}
                      tickFormatter={(value) => `${value.toFixed(1)}%`}
                    />
                    <YAxis 
                      dataKey="y"
                      name="NPV"
                      unit="$"
                      label={{ value: 'Net Present Value ($)', angle: -90, position: 'insideLeft' }}
                      tickFormatter={(value) => formatCurrency(value, { compact: true })}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <ReferenceLine x={0} stroke="#ef4444" strokeDasharray="5 5" />
                    <ReferenceLine y={0} stroke="#ef4444" strokeDasharray="5 5" />
                    {Object.values(MarketClassification).map((classification) => {
                      const classificationData = scatterData.filter(d => d.market_classification === classification);
                      if (classificationData.length === 0) return null;
                      
                      return (
                        <Scatter
                          key={classification}
                          name={classification}
                          data={classificationData}
                          fill={getMarketClassificationColor(classification)}
                          fillOpacity={0.7}
                        />
                      );
                    })}
                    <Legend />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Risk vs Return Analysis */}
        <TabsContent value="risk-return" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <Target className="h-5 w-5 mr-2 text-amber-600" />
                Risk vs Return Profile
              </CardTitle>
              <CardDescription>
                Investment efficiency analysis showing risk-adjusted returns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart data={riskReturnData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="risk"
                      name="Risk Score"
                      label={{ value: 'Risk Score (0-1)', position: 'insideBottom', offset: -10 }}
                      domain={[0, 1]}
                    />
                    <YAxis 
                      dataKey="return"
                      name="IRR"
                      unit="%"
                      label={{ value: 'Return (IRR %)', angle: -90, position: 'insideLeft' }}
                      tickFormatter={(value) => `${value.toFixed(1)}%`}
                    />
                    <Tooltip 
                      formatter={(value, name) => [
                        name === 'return' ? `${value.toFixed(1)}%` : value.toFixed(3),
                        name === 'return' ? 'IRR' : 'Risk Score'
                      ]}
                    />
                    {Object.values(MarketClassification).map((classification) => {
                      const classificationData = riskReturnData.filter(d => d.classification === classification);
                      if (classificationData.length === 0) return null;
                      
                      return (
                        <Scatter
                          key={classification}
                          name={classification}
                          data={classificationData}
                          fill={getMarketClassificationColor(classification)}
                          fillOpacity={0.7}
                        />
                      );
                    })}
                    <Legend />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Distribution Analysis */}
        <TabsContent value="distribution" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2 text-green-600" />
                    Distribution Analysis
                  </CardTitle>
                  <CardDescription>
                    Frequency distribution of {selectedMetric === 'npv' ? 'NPV' : selectedMetric === 'irr' ? 'IRR' : 'Cash Flow'} values
                  </CardDescription>
                </div>
                <div className="flex space-x-2">
                  {(['npv', 'irr', 'cashflow'] as const).map((metric) => (
                    <Badge
                      key={metric}
                      variant={selectedMetric === metric ? "default" : "outline"}
                      className="cursor-pointer hover:bg-gray-100 transition-colors"
                      onClick={() => onMetricChange?.(metric)}
                    >
                      {metric === 'npv' ? 'NPV' : metric === 'irr' ? 'IRR' : 'Cash Flow'}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-96">
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
                      label={{ value: 'Frequency', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      formatter={(value) => [value, 'Scenarios']}
                      labelFormatter={(label) => `Range: ${formatValue(label, selectedMetric)}`}
                    />
                    <Bar 
                      dataKey="count" 
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

        {/* Market Comparison */}
        <TabsContent value="market-comparison" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <Activity className="h-5 w-5 mr-2 text-purple-600" />
                Market Classification Performance
              </CardTitle>
              <CardDescription>
                Comparative analysis across different market scenarios
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={marketPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="classification"
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis 
                      yAxisId="npv"
                      orientation="left"
                      label={{ value: 'Average NPV ($)', angle: -90, position: 'insideLeft' }}
                      tickFormatter={(value) => formatCurrency(value, { compact: true })}
                    />
                    <YAxis 
                      yAxisId="irr"
                      orientation="right"
                      label={{ value: 'Average IRR (%)', angle: 90, position: 'insideRight' }}
                      tickFormatter={(value) => `${value.toFixed(1)}%`}
                    />
                    <Tooltip 
                      formatter={(value, name) => [
                        name.includes('NPV') || name.includes('Cash') ? formatCurrency(value) : 
                        name.includes('IRR') ? `${value.toFixed(1)}%` : value.toFixed(3),
                        name
                      ]}
                    />
                    <Bar 
                      yAxisId="npv"
                      dataKey="avgNpv" 
                      name="Average NPV"
                      fill="#3B82F6"
                      fillOpacity={0.7}
                    />
                    <Bar 
                      yAxisId="irr"
                      dataKey="avgIrr" 
                      name="Average IRR"
                      fill="#10B981"
                      fillOpacity={0.7}
                    />
                    <Legend />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}