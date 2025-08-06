/**
 * Dashboard Home Page
 * Protected route that requires authentication
 */

'use client';

import { useEffect } from 'react';
import { useAuth } from '@/lib/auth/authContext';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calculator, TrendingUp, Building2, BarChart3, DollarSign, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { useHealthCheck } from '@/hooks/useAPI';

function DashboardContent() {
  const { user } = useAuth();
  const healthCheck = useHealthCheck();

  // Check backend health on component mount
  useEffect(() => {
    healthCheck.execute();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [healthCheck.execute]);

  const stats = [
    {
      name: 'Total Properties',
      value: '0',
      icon: Building2,
      change: '+0%',
      changeType: 'neutral' as const
    },
    {
      name: 'Portfolio Value',
      value: '$0',
      icon: DollarSign,
      change: '+0%',
      changeType: 'neutral' as const
    },
    {
      name: 'Avg. IRR',
      value: '0%',
      icon: TrendingUp,
      change: '+0%',
      changeType: 'neutral' as const
    },
    {
      name: 'Analyses Run',
      value: '0',
      icon: BarChart3,
      change: '+0%',
      changeType: 'neutral' as const
    }
  ];

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.email?.split('@')[0]}
          </h1>
          <p className="text-gray-600 mt-1">
            Here&apos;s what&apos;s happening with your real estate portfolio today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => {
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
                    <div className="h-12 w-12 bg-blue-50 rounded-lg flex items-center justify-center">
                      <Icon className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                  <div className="mt-4 flex items-center">
                    <span className="text-sm text-gray-500">
                      {stat.change} from last month
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* API Key Display */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Your API Key</CardTitle>
              <CardDescription>
                This key is automatically used for all backend requests
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-100 p-3 rounded-md font-mono text-sm break-all">
                {user?.api_key}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Generated automatically on registration
              </p>
            </CardContent>
          </Card>

          {/* Account Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Account Information</CardTitle>
              <CardDescription>
                Your account details and statistics
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Email:</span>
                <span className="font-medium">{user?.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Account ID:</span>
                <span className="font-mono text-sm">{user?.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Member since:</span>
                <span className="text-sm">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
            <CardDescription>
              Get started with your financial analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button 
                className="h-20 flex flex-col items-center justify-center" 
                onClick={() => window.location.href = '/property-input'}
              >
                <Calculator className="h-6 w-6 mb-2" />
                <span className="font-semibold">Add New Property</span>
                <span className="text-xs opacity-75">Ready</span>
              </Button>
              
              <Button variant="outline" className="h-20 flex flex-col items-center justify-center" disabled>
                <TrendingUp className="h-6 w-6 mb-2" />
                <span className="font-semibold">View Market Data</span>
                <span className="text-xs opacity-75">Coming Soon</span>
              </Button>
              
              <Button variant="outline" className="h-20 flex flex-col items-center justify-center" disabled>
                <BarChart3 className="h-6 w-6 mb-2" />
                <span className="font-semibold">Monte Carlo Simulation</span>
                <span className="text-xs opacity-75">Coming Soon</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Backend Status */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="text-lg">Backend System Status</CardTitle>
            <CardDescription>
              Real-time status of the FastAPI backend services
            </CardDescription>
          </CardHeader>
          <CardContent>
            {healthCheck.loading && (
              <div className="text-center py-4">
                <div className="inline-flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  <span>Checking backend status...</span>
                </div>
              </div>
            )}

            {healthCheck.error && (
              <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg">
                <XCircle className="h-5 w-5 text-red-600 mr-3" />
                <div>
                  <p className="font-medium text-red-900">Backend Unavailable</p>
                  <p className="text-red-700 text-sm">{healthCheck.error}</p>
                </div>
              </div>
            )}

            {healthCheck.data && (
              <div className="space-y-4">
                {/* Overall Status */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {healthCheck.data.status === 'healthy' ? (
                      <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                    ) : healthCheck.data.status === 'degraded' ? (
                      <AlertCircle className="h-5 w-5 text-yellow-600 mr-2" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600 mr-2" />
                    )}
                    <span className="font-medium">Overall Status</span>
                  </div>
                  <Badge 
                    variant={
                      healthCheck.data.status === 'healthy' ? 'success' : 
                      healthCheck.data.status === 'degraded' ? 'secondary' : 'destructive'
                    }
                  >
                    {healthCheck.data.status.toUpperCase()}
                  </Badge>
                </div>

                {/* Database Status */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Database Status</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {Object.entries(healthCheck.data.dependencies)
                      .filter(([key]) => key.includes('_data') || key.includes('cache'))
                      .map(([db, status]) => (
                      <div key={db} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm">{db.replace('_', ' ')}</span>
                        {status === 'healthy' ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* API Status */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">System Services</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    {Object.entries(healthCheck.data.dependencies)
                      .filter(([key]) => !key.includes('_data') && !key.includes('cache'))
                      .map(([service, status]) => (
                      <div key={service} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm">{service.replace('_', ' ')}</span>
                        {status === 'healthy' ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* System Info */}
                <div className="flex justify-between text-xs text-gray-500 pt-2 border-t">
                  <span>Version: {healthCheck.data.version}</span>
                  <span>Last checked: {new Date(healthCheck.data.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <AuthGuard requireAuth={true}>
      <DashboardLayout>
        <DashboardContent />
      </DashboardLayout>
    </AuthGuard>
  );
}
