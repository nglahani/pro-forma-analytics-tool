/**
 * Monte Carlo Page
 * Risk analysis and probabilistic simulations
 */

'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BarChart3, Play, Settings, Download, TrendingUp, AlertTriangle } from 'lucide-react';

export default function MonteCarloPage() {
  const simulationStats = [
    { name: 'Total Simulations', value: '0', icon: BarChart3 },
    { name: 'Avg. NPV', value: '$0', icon: TrendingUp },
    { name: 'Success Rate', value: '0%', icon: AlertTriangle },
    { name: 'Risk Score', value: 'N/A', icon: BarChart3 }
  ];

  const riskMetrics = [
    { name: 'Value at Risk (5%)', value: 'N/A', description: '5th percentile NPV' },
    { name: 'Expected Shortfall', value: 'N/A', description: 'Average of worst 5% scenarios' },
    { name: 'Probability of Loss', value: 'N/A', description: 'Chance of negative NPV' },
    { name: 'Sharpe Ratio', value: 'N/A', description: 'Risk-adjusted returns' }
  ];

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Monte Carlo Simulation
            </h1>
            <p className="text-gray-600 mt-1">
              Risk analysis and probabilistic modeling for your investments
            </p>
          </div>
          <Button className="flex items-center space-x-2" disabled>
            <Play className="h-4 w-4" />
            <span>Run Simulation</span>
          </Button>
        </div>

        {/* Simulation Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {simulationStats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.name}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">
                        {stat.name}
                      </p>
                      <p className="text-2xl font-bold text-gray-900">
                        {stat.value}
                      </p>
                    </div>
                    <div className="h-12 w-12 bg-purple-50 rounded-lg flex items-center justify-center">
                      <Icon className="h-6 w-6 text-purple-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Simulation Controls */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Simulation Configuration</CardTitle>
              <CardDescription>
                Configure your Monte Carlo simulation parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Number of Scenarios</label>
                  <Badge variant="secondary">500 - 50,000</Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Correlation Matrix</label>
                  <Badge variant="success">23 Relationships</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Market Classifications</label>
                  <Badge variant="outline">Bull/Bear/Neutral</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-gray-700">Economic Indicators</label>
                  <Badge variant="outline">11 Parameters</Badge>
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="flex space-x-3">
                  <Button className="flex-1" disabled>
                    <Play className="h-4 w-4 mr-2" />
                    Run Simulation
                  </Button>
                  <Button variant="outline" size="icon" disabled>
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Risk Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Risk Metrics</CardTitle>
              <CardDescription>
                Key risk indicators from simulation results
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {riskMetrics.map((metric) => (
                <div key={metric.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-900">{metric.name}</h4>
                    <p className="text-sm text-gray-500">{metric.description}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-semibold text-gray-900">{metric.value}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Simulation Results Placeholder */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-lg">Simulation Results</CardTitle>
                <CardDescription>
                  Interactive scatter plot and statistical analysis
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" disabled>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-center py-16 bg-gray-50 rounded-lg">
              <BarChart3 className="mx-auto h-16 w-16 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                No Simulation Results Yet
              </h3>
              <p className="mt-2 text-sm text-gray-500 max-w-md mx-auto">
                Run your first Monte Carlo simulation to see the interactive NPV vs IRR scatter plot 
                with 500+ scenarios and market classification analysis.
              </p>
              <div className="mt-6">
                <Button disabled>
                  Run Your First Simulation
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Simulation Engine Info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Monte Carlo Engine Capabilities</CardTitle>
            <CardDescription>
              Advanced probabilistic modeling features
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="text-center p-4">
                <div className="h-12 w-12 bg-blue-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900">Scenario Generation</h4>
                <p className="text-sm text-gray-500 mt-1">500 to 50,000 scenarios</p>
                <Badge variant="success" className="mt-2">Ready</Badge>
              </div>

              <div className="text-center p-4">
                <div className="h-12 w-12 bg-green-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <h4 className="font-medium text-gray-900">Economic Correlations</h4>
                <p className="text-sm text-gray-500 mt-1">23 parameter relationships</p>
                <Badge variant="success" className="mt-2">Calibrated</Badge>
              </div>

              <div className="text-center p-4">
                <div className="h-12 w-12 bg-purple-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <AlertTriangle className="h-6 w-6 text-purple-600" />
                </div>
                <h4 className="font-medium text-gray-900">Risk Assessment</h4>
                <p className="text-sm text-gray-500 mt-1">Statistical validation</p>
                <Badge variant="success" className="mt-2">Validated</Badge>
              </div>

              <div className="text-center p-4">
                <div className="h-12 w-12 bg-amber-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <BarChart3 className="h-6 w-6 text-amber-600" />
                </div>
                <h4 className="font-medium text-gray-900">Market Classification</h4>
                <p className="text-sm text-gray-500 mt-1">Bull/Bear/Neutral/Growth/Stress</p>
                <Badge variant="success" className="mt-2">Active</Badge>
              </div>

              <div className="text-center p-4">
                <div className="h-12 w-12 bg-red-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <TrendingUp className="h-6 w-6 text-red-600" />
                </div>
                <h4 className="font-medium text-gray-900">Performance Metrics</h4>
                <p className="text-sm text-gray-500 mt-1">Growth & risk scores</p>
                <Badge variant="success" className="mt-2">Enabled</Badge>
              </div>

              <div className="text-center p-4">
                <div className="h-12 w-12 bg-indigo-50 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Download className="h-6 w-6 text-indigo-600" />
                </div>
                <h4 className="font-medium text-gray-900">Export Options</h4>
                <p className="text-sm text-gray-500 mt-1">CSV, Excel, PDF reports</p>
                <Badge variant="secondary" className="mt-2">Coming Soon</Badge>
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
                    Interactive Monte Carlo Simulation Coming Soon
                  </h3>
                  <p className="text-purple-700 mt-1">
                    We&apos;re building the interactive simulation interface that will connect directly to your 
                    FastAPI backend&apos;s Monte Carlo engine for real-time probabilistic analysis with 500+ scenarios.
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