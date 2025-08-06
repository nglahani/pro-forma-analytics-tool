/**
 * Property Analysis Page
 * DCF analysis and financial modeling interface
 */

'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calculator, Plus, FileText, TrendingUp } from 'lucide-react';

export default function AnalysisPage() {
  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Property Analysis
            </h1>
            <p className="text-gray-600 mt-1">
              DCF analysis and financial modeling for your properties
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline"
              onClick={() => window.location.href = '/analysis/demo'}
              className="flex items-center space-x-2"
            >
              <Calculator className="h-4 w-4" />
              <span>View Demo</span>
            </Button>
            <Button className="flex items-center space-x-2" disabled>
              <Plus className="h-4 w-4" />
              <span>New Analysis</span>
            </Button>
          </div>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Total Analyses
                  </p>
                  <p className="text-2xl font-bold text-gray-900">0</p>
                </div>
                <div className="h-12 w-12 bg-blue-50 rounded-lg flex items-center justify-center">
                  <Calculator className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Avg. NPV
                  </p>
                  <p className="text-2xl font-bold text-gray-900">$0</p>
                </div>
                <div className="h-12 w-12 bg-green-50 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
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
                <div className="h-12 w-12 bg-amber-50 rounded-lg flex items-center justify-center">
                  <Calculator className="h-6 w-6 text-amber-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Analyses */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recent Analyses</CardTitle>
              <CardDescription>
                Your latest property financial models
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">
                  No analyses yet
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Get started by creating your first property analysis
                </p>
                <div className="mt-6">
                  <Button disabled>
                    Create Analysis
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Templates */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Analysis Templates</CardTitle>
              <CardDescription>
                Quick start templates for common property types
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Multifamily Residential</h4>
                  <p className="text-sm text-gray-500">Apartment buildings and condos</p>
                </div>
                <Badge variant="secondary">Coming Soon</Badge>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Commercial Office</h4>
                  <p className="text-sm text-gray-500">Office buildings and business centers</p>
                </div>
                <Badge variant="secondary">Coming Soon</Badge>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Mixed-Use Property</h4>
                  <p className="text-sm text-gray-500">Residential with ground-floor commercial</p>
                </div>
                <Badge variant="secondary">Coming Soon</Badge>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Retail & Shopping</h4>
                  <p className="text-sm text-gray-500">Strip malls and shopping centers</p>
                </div>
                <Badge variant="secondary">Coming Soon</Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Coming Soon Notice */}
        <div className="mt-8">
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <Calculator className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-blue-900">
                    Property Analysis Coming Soon
                  </h3>
                  <p className="text-blue-700 mt-1">
                    We&apos;re building the property input form and DCF analysis interface. 
                    This will integrate directly with your FastAPI backend for real-time financial modeling.
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