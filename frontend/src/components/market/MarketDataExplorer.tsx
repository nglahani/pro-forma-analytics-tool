/**
 * Market Data Explorer Component
 * Interactive browser for historical and current market data across MSAs
 */

'use client';

import { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  ComposedChart,
  ReferenceLine,
} from 'recharts';
import {
  MapPin,
  TrendingUp,
  TrendingDown,
  Calendar,
  Filter,
  Search,
  Download,
  RefreshCw,
  BarChart3,
  Activity,
  AlertCircle,
  Info,
} from 'lucide-react';
import { MarketData, MarketForecast } from '@/types/analysis';
import { formatCurrency, formatPercentage, textColors } from '@/lib/utils';
import { TimeSeriesChart, TimeSeriesConfig, TimeSeriesDataPoint } from '@/components/charts/TimeSeriesChart';

export interface MSAInfo {
  msa_code: string;
  name: string;
  state: string;
  population: number;
  median_income: number;
  unemployment_rate: number;
  major_cities: string[];
  market_tier: 'primary' | 'secondary' | 'tertiary';
}

export interface MarketParameter {
  name: string;
  label: string;
  unit: string;
  category: 'rates' | 'growth' | 'costs' | 'ratios';
  importance: 'high' | 'medium' | 'low';
  description: string;
}

interface MarketDataExplorerProps {
  selectedMSA?: string;
  onMSAChange?: (msaCode: string) => void;
  onDataExport?: (format: 'csv' | 'excel', data: any) => void;
  isLoading?: boolean;
}

// Sample MSA data
const sampleMSAs: MSAInfo[] = [
  {
    msa_code: 'NYC',
    name: 'New York-Newark-Jersey City',
    state: 'NY-NJ-PA',
    population: 20140470,
    median_income: 82600,
    unemployment_rate: 4.1,
    major_cities: ['New York', 'Newark', 'Jersey City'],
    market_tier: 'primary',
  },
  {
    msa_code: 'LAX',
    name: 'Los Angeles-Long Beach-Anaheim',
    state: 'CA',
    population: 13214799,
    median_income: 71500,
    unemployment_rate: 4.8,
    major_cities: ['Los Angeles', 'Long Beach', 'Anaheim'],
    market_tier: 'primary',
  },
  {
    msa_code: 'CHI',
    name: 'Chicago-Naperville-Elgin',
    state: 'IL-IN-WI',
    population: 9618502,
    median_income: 68800,
    unemployment_rate: 4.2,
    major_cities: ['Chicago', 'Naperville', 'Elgin'],
    market_tier: 'primary',
  },
  {
    msa_code: 'DC',
    name: 'Washington-Arlington-Alexandria',
    state: 'DC-VA-MD-WV',
    population: 6385162,
    median_income: 98500,
    unemployment_rate: 3.5,
    major_cities: ['Washington', 'Arlington', 'Alexandria'],
    market_tier: 'primary',
  },
  {
    msa_code: 'MIA',
    name: 'Miami-Fort Lauderdale-West Palm Beach',
    state: 'FL',
    population: 6166488,
    median_income: 58900,
    unemployment_rate: 3.8,
    major_cities: ['Miami', 'Fort Lauderdale', 'West Palm Beach'],
    market_tier: 'secondary',
  },
];

// Sample market parameters
const marketParameters: MarketParameter[] = [
  {
    name: 'interest_rate',
    label: 'Interest Rate',
    unit: '%',
    category: 'rates',
    importance: 'high',
    description: 'Current mortgage interest rates',
  },
  {
    name: 'cap_rate',
    label: 'Cap Rate',
    unit: '%',
    category: 'rates',
    importance: 'high',
    description: 'Capitalization rates for commercial real estate',
  },
  {
    name: 'vacancy_rate',
    label: 'Vacancy Rate',
    unit: '%',
    category: 'ratios',
    importance: 'high',
    description: 'Rental property vacancy rates',
  },
  {
    name: 'rent_growth_rate',
    label: 'Rent Growth',
    unit: '%/year',
    category: 'growth',
    importance: 'high',
    description: 'Annual rental income growth rates',
  },
  {
    name: 'property_growth_rate',
    label: 'Property Appreciation',
    unit: '%/year',
    category: 'growth',
    importance: 'medium',
    description: 'Annual property value appreciation',
  },
  {
    name: 'expense_growth_rate',
    label: 'Expense Growth',
    unit: '%/year',
    category: 'growth',
    importance: 'medium',
    description: 'Operating expense inflation rates',
  },
];

// Generate sample market data
const generateSampleMarketData = (msaCode: string, parameter: string): MarketData[] => {
  const data: MarketData[] = [];
  const baseValue = {
    interest_rate: 6.5,
    cap_rate: 5.5,
    vacancy_rate: 5.0,
    rent_growth_rate: 3.0,
    property_growth_rate: 2.5,
    expense_growth_rate: 2.8,
  }[parameter] || 5.0;

  // Generate 36 months of data
  for (let i = 0; i < 36; i++) {
    const date = new Date();
    date.setMonth(date.getMonth() - (35 - i));
    
    const variation = (Math.random() - 0.5) * 2;
    const trend = parameter.includes('growth') ? 0.1 : -0.05;
    const value = baseValue + variation + (trend * i / 12);

    data.push({
      msa_code: msaCode,
      parameter_name: parameter,
      value: Math.max(0, value),
      date: date.toISOString().split('T')[0],
      source: 'FRED',
      confidence_level: 0.85 + Math.random() * 0.1,
    });
  }

  return data;
};

export function MarketDataExplorer({
  selectedMSA = 'NYC',
  onMSAChange,
  onDataExport,
  isLoading = false,
}: MarketDataExplorerProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedParameters, setSelectedParameters] = useState<string[]>(['interest_rate', 'cap_rate', 'vacancy_rate']);
  const [timeRange, setTimeRange] = useState<'6m' | '1y' | '2y' | '3y'>('1y');
  const [activeTab, setActiveTab] = useState('overview');

  // Filter MSAs based on search
  const filteredMSAs = useMemo(() => {
    if (!searchTerm) return sampleMSAs;
    return sampleMSAs.filter(msa =>
      msa.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      msa.msa_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      msa.major_cities.some(city => city.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [searchTerm]);

  // Get current MSA info
  const currentMSA = sampleMSAs.find(msa => msa.msa_code === selectedMSA) || sampleMSAs[0];

  // Generate market data for selected MSA and parameters
  const marketData = useMemo(() => {
    const data: Record<string, MarketData[]> = {};
    selectedParameters.forEach(param => {
      data[param] = generateSampleMarketData(selectedMSA, param);
    });
    return data;
  }, [selectedMSA, selectedParameters]);

  // Prepare chart data
  const chartData = useMemo(() => {
    const months = timeRange === '6m' ? 6 : timeRange === '1y' ? 12 : timeRange === '2y' ? 24 : 36;
    
    if (selectedParameters.length === 0) return [];

    const firstParam = selectedParameters[0];
    const baseData = marketData[firstParam]?.slice(-months) || [];

    return baseData.map(item => {
      const chartPoint: any = {
        date: item.date,
        month: new Date(item.date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
      };

      selectedParameters.forEach(param => {
        const paramData = marketData[param]?.find(d => d.date === item.date);
        if (paramData) {
          chartPoint[param] = paramData.value;
        }
      });

      return chartPoint;
    });
  }, [marketData, selectedParameters, timeRange]);

  const handleMSASelect = useCallback((msaCode: string) => {
    onMSAChange?.(msaCode);
  }, [onMSAChange]);

  const handleParameterToggle = useCallback((paramName: string) => {
    setSelectedParameters(prev => {
      if (prev.includes(paramName)) {
        return prev.filter(p => p !== paramName);
      } else {
        return [...prev, paramName];
      }
    });
  }, []);

  const handleExportData = useCallback((format: 'csv' | 'excel') => {
    const exportData = {
      msa: currentMSA,
      parameters: selectedParameters,
      data: marketData,
      timeRange,
    };
    onDataExport?.(format, exportData);
  }, [currentMSA, selectedParameters, marketData, timeRange, onDataExport]);

  const getParameterColor = (paramName: string, index: number) => {
    const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];
    return colors[index % colors.length];
  };

  const getMarketTierColor = (tier: MSAInfo['market_tier']) => {
    switch (tier) {
      case 'primary':
        return 'text-green-700 bg-green-100 border-green-200';
      case 'secondary':
        return 'text-blue-700 bg-blue-100 border-blue-200';
      case 'tertiary':
        return 'text-amber-700 bg-amber-100 border-amber-200';
    }
  };

  const getCurrentValue = (paramName: string) => {
    const data = marketData[paramName];
    if (!data || data.length === 0) return null;
    return data[data.length - 1];
  };

  const getParameterTrend = (paramName: string) => {
    const data = marketData[paramName];
    if (!data || data.length < 2) return 'neutral';
    
    const current = data[data.length - 1].value;
    const previous = data[data.length - 2].value;
    
    if (current > previous * 1.01) return 'up';
    if (current < previous * 0.99) return 'down';
    return 'neutral';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-xl font-semibold ${textColors.primary} flex items-center`}>
            <MapPin className="h-5 w-5 mr-2" />
            Market Data Explorer
          </h2>
          <p className={`text-sm ${textColors.muted} mt-1`}>
            Explore real estate market data across major metropolitan areas
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExportData('csv')}
            disabled={isLoading || selectedParameters.length === 0}
          >
            <Download className="h-4 w-4 mr-1" />
            CSV
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExportData('excel')}
            disabled={isLoading || selectedParameters.length === 0}
          >
            <Download className="h-4 w-4 mr-1" />
            Excel
          </Button>
        </div>
      </div>

      {/* MSA Selection */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Select Market</CardTitle>
            <CardDescription>
              Choose a metropolitan statistical area to explore
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search MSAs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredMSAs.map((msa) => (
                <div
                  key={msa.msa_code}
                  onClick={() => handleMSASelect(msa.msa_code)}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedMSA === msa.msa_code
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{msa.msa_code}</span>
                    <Badge variant="outline" className={`text-xs ${getMarketTierColor(msa.market_tier)}`}>
                      {msa.market_tier}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">{msa.name}</p>
                  <p className="text-xs text-gray-500">
                    Pop: {(msa.population / 1000000).toFixed(1)}M • 
                    Income: {formatCurrency(msa.median_income)}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Current MSA Info */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">{currentMSA.name}</CardTitle>
                <CardDescription>{currentMSA.state}</CardDescription>
              </div>
              <Badge variant="outline" className={`${getMarketTierColor(currentMSA.market_tier)}`}>
                {currentMSA.market_tier} market
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Population</p>
                <p className="font-semibold">{(currentMSA.population / 1000000).toFixed(1)}M</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Median Income</p>
                <p className="font-semibold">{formatCurrency(currentMSA.median_income)}</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Unemployment</p>
                <p className="font-semibold">{currentMSA.unemployment_rate}%</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Major Cities</p>
                <p className="font-semibold text-xs">{currentMSA.major_cities.slice(0, 2).join(', ')}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Parameter Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Market Parameters
          </CardTitle>
          <CardDescription>
            Select parameters to visualize and analyze
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {marketParameters.map((param, index) => {
              const isSelected = selectedParameters.includes(param.name);
              const currentValue = getCurrentValue(param.name);
              const trend = getParameterTrend(param.name);
              
              return (
                <div
                  key={param.name}
                  onClick={() => handleParameterToggle(param.name)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: isSelected ? getParameterColor(param.name, index) : '#E5E7EB' }}
                      />
                      <span className="font-medium text-sm">{param.label}</span>
                    </div>
                    {trend !== 'neutral' && (
                      <div className={`text-xs ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                        {trend === 'up' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      </div>
                    )}
                  </div>
                  
                  {currentValue && (
                    <div className="text-xs text-gray-600 mb-1">
                      Current: {currentValue.value.toFixed(2)}{param.unit}
                    </div>
                  )}
                  
                  <p className="text-xs text-gray-500">{param.description}</p>
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center space-x-4">
              <Label className="text-sm font-medium">Time Range:</Label>
              <div className="flex space-x-1">
                {(['6m', '1y', '2y', '3y'] as const).map((range) => (
                  <Button
                    key={range}
                    variant={timeRange === range ? "default" : "outline"}
                    size="sm"
                    onClick={() => setTimeRange(range)}
                    className="text-xs"
                  >
                    {range}
                  </Button>
                ))}
              </div>
            </div>
            
            <div className="text-sm text-gray-600">
              {selectedParameters.length} parameter{selectedParameters.length !== 1 ? 's' : ''} selected
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Chart Display */}
      {selectedParameters.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Market Trends</CardTitle>
            <CardDescription>
              Historical data for {currentMSA.name} over the past {timeRange}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="month"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `${value.toFixed(1)}%`}
                  />
                  <Tooltip 
                    formatter={(value: number, name: string) => [
                      `${value.toFixed(2)}${marketParameters.find(p => p.name === name)?.unit || '%'}`,
                      marketParameters.find(p => p.name === name)?.label || name
                    ]}
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Legend />
                  {selectedParameters.map((param, index) => (
                    <Line
                      key={param}
                      type="monotone"
                      dataKey={param}
                      stroke={getParameterColor(param, index)}
                      strokeWidth={2}
                      dot={{ fill: getParameterColor(param, index), strokeWidth: 2, r: 3 }}
                      activeDot={{ r: 5 }}
                      name={marketParameters.find(p => p.name === param)?.label || param}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No data state */}
      {selectedParameters.length === 0 && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <BarChart3 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Select Parameters to View Data
              </h3>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Choose one or more market parameters above to visualize historical trends and current market conditions.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}