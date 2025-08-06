/**
 * Market Data Page
 * Market trends, forecasts and economic indicators
 */

'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus, Globe, BarChart3 } from 'lucide-react';

export default function MarketDataPage() {
  const marketIndicators = [
    { name: 'Interest Rates', value: '7.2%', change: '+0.3%', trend: 'up' },
    { name: 'Cap Rates', value: '5.8%', change: '-0.1%', trend: 'down' },
    { name: 'Vacancy Rate', value: '4.2%', change: '0.0%', trend: 'neutral' },
    { name: 'Rent Growth', value: '3.5%', change: '+0.8%', trend: 'up' }
  ];

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTrendColor = (trend: string) => {
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
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">
            Market Data
          </h1>
          <p className="text-gray-600 mt-1">
            Real estate market trends, forecasts, and economic indicators
          </p>
        </div>

        {/* Market Indicators */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {marketIndicators.map((indicator) => (
            <Card key={indicator.name}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {indicator.name}
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {indicator.value}
                    </p>
                  </div>
                  <div className="h-12 w-12 bg-blue-50 rounded-lg flex items-center justify-center">
                    {getTrendIcon(indicator.trend)}
                  </div>
                </div>
                <div className="mt-4 flex items-center">
                  <span className={`text-sm ${getTrendColor(indicator.trend)}`}>
                    {indicator.change} from last month
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Regional Markets */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Regional Markets</CardTitle>
              <CardDescription>
                Market performance across different MSAs
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">New York Metro</h4>
                  <p className="text-sm text-gray-500">MSA: 35620</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">Cap Rate: 4.2%</p>
                  <Badge variant="success">Active</Badge>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Los Angeles Metro</h4>
                  <p className="text-sm text-gray-500">MSA: 31080</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">Cap Rate: 3.8%</p>
                  <Badge variant="success">Active</Badge>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Chicago Metro</h4>
                  <p className="text-sm text-gray-500">MSA: 16980</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">Cap Rate: 5.1%</p>
                  <Badge variant="success">Active</Badge>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Miami Metro</h4>
                  <p className="text-sm text-gray-500">MSA: 33100</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">Cap Rate: 4.6%</p>
                  <Badge variant="success">Active</Badge>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Washington DC Metro</h4>
                  <p className="text-sm text-gray-500">MSA: 47900</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">Cap Rate: 4.8%</p>
                  <Badge variant="success">Active</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Economic Forecasts */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Economic Forecasts</CardTitle>
              <CardDescription>
                Prophet-generated forecasts for key parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Interest Rates (6 months)</span>
                  <span className="text-sm text-gray-900">7.5% ± 0.3%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Cap Rates (6 months)</span>
                  <span className="text-sm text-gray-900">5.9% ± 0.2%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Rent Growth (6 months)</span>
                  <span className="text-sm text-gray-900">3.8% ± 0.5%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-amber-600 h-2 rounded-full" style={{ width: '38%' }}></div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Property Values (6 months)</span>
                  <span className="text-sm text-gray-900">2.1% ± 0.4%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: '21%' }}></div>
                </div>
              </div>

              <div className="mt-6 p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-blue-800">
                  <strong>Forecast Confidence:</strong> Based on 15+ years of historical data using Meta&apos;s Prophet algorithm
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Data Sources */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Data Sources & Coverage</CardTitle>
            <CardDescription>
              Real-time market data integration and historical coverage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center p-4">
                <div className="h-12 w-12 bg-blue-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Globe className="h-6 w-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900">FRED API</h4>
                <p className="text-sm text-gray-500 mt-1">Federal economic data</p>
                <Badge variant="success" className="mt-2">Connected</Badge>
              </div>

              <div className="text-center p-4">
                <div className="h-12 w-12 bg-green-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <BarChart3 className="h-6 w-6 text-green-600" />
                </div>
                <h4 className="font-medium text-gray-900">Market Data</h4>
                <p className="text-sm text-gray-500 mt-1">2,174+ data points</p>
                <Badge variant="success" className="mt-2">Active</Badge>
              </div>

              <div className="text-center p-4">
                <div className="h-12 w-12 bg-amber-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="h-6 w-6 text-amber-600" />
                </div>
                <h4 className="font-medium text-gray-900">Forecasts</h4>
                <p className="text-sm text-gray-500 mt-1">Prophet engine</p>
                <Badge variant="success" className="mt-2">Running</Badge>
              </div>

              <div className="text-center p-4">
                <div className="h-12 w-12 bg-purple-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <BarChart3 className="h-6 w-6 text-purple-600" />
                </div>
                <h4 className="font-medium text-gray-900">Coverage</h4>
                <p className="text-sm text-gray-500 mt-1">5 major MSAs</p>
                <Badge variant="success" className="mt-2">Complete</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Coming Soon Notice */}
        <div className="mt-8">
          <Card className="border-purple-200 bg-purple-50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-purple-900">
                    Interactive Market Data Visualization Coming Soon
                  </h3>
                  <p className="text-purple-700 mt-1">
                    We&apos;re building interactive charts and detailed market analysis tools that will integrate 
                    with your FastAPI backend&apos;s market data endpoints for real-time insights.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}