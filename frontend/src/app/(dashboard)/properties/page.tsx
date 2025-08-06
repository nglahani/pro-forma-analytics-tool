/**
 * Properties Page
 * Manage property portfolio and property data
 */

'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Building2, Plus, Search, Filter } from 'lucide-react';
import { Input } from '@/components/ui/input';

export default function PropertiesPage() {
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Properties
            </h1>
            <p className="text-gray-600 mt-1">
              Manage your real estate portfolio
            </p>
          </div>
          <Button className="flex items-center space-x-2" disabled>
            <Plus className="h-4 w-4" />
            <span>Add Property</span>
          </Button>
        </div>

        {/* Search and Filter Bar */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search properties..."
              className="pl-10"
              disabled
            />
          </div>
          <Button variant="outline" className="flex items-center space-x-2" disabled>
            <Filter className="h-4 w-4" />
            <span>Filter</span>
          </Button>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Total Properties
                  </p>
                  <p className="text-2xl font-bold text-gray-900">0</p>
                </div>
                <Building2 className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Portfolio Value
                  </p>
                  <p className="text-2xl font-bold text-gray-900">$0</p>
                </div>
                <div className="text-2xl">💰</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Active Analyses
                  </p>
                  <p className="text-2xl font-bold text-gray-900">0</p>
                </div>
                <div className="text-2xl">📊</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Avg. IRR
                  </p>
                  <p className="text-2xl font-bold text-gray-900">0%</p>
                </div>
                <div className="text-2xl">📈</div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Properties List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Your Properties</CardTitle>
            <CardDescription>
              View and manage all your real estate investments
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">
              <Building2 className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-sm font-medium text-gray-900">
                No properties yet
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Get started by adding your first property to analyze
              </p>
              <div className="mt-6">
                <Button disabled>
                  Add Your First Property
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Property Types Guide */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Supported Property Types</CardTitle>
              <CardDescription>
                Types of properties you can analyze with Pro Forma Analytics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-3xl mb-2">🏢</div>
                  <h4 className="font-medium text-gray-900">Multifamily</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Apartment buildings and residential complexes
                  </p>
                  <Badge variant="success" className="mt-2">Supported</Badge>
                </div>

                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-3xl mb-2">🏪</div>
                  <h4 className="font-medium text-gray-900">Commercial</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Office buildings and business centers
                  </p>
                  <Badge variant="success" className="mt-2">Supported</Badge>
                </div>

                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-3xl mb-2">🏬</div>
                  <h4 className="font-medium text-gray-900">Mixed-Use</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Residential with ground-floor commercial
                  </p>
                  <Badge variant="success" className="mt-2">Supported</Badge>
                </div>

                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-3xl mb-2">🛍️</div>
                  <h4 className="font-medium text-gray-900">Retail</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Strip malls and shopping centers
                  </p>
                  <Badge variant="success" className="mt-2">Supported</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Coming Soon Notice */}
        <div className="mt-8">
          <Card className="border-green-200 bg-green-50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <Building2 className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-green-900">
                    Property Management Coming Soon
                  </h3>
                  <p className="text-green-700 mt-1">
                    We&apos;re building comprehensive property management features including property input forms, 
                    portfolio tracking, and integration with your FastAPI backend for real-time data management.
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