/**
 * Batch Progress Tracking Component
 * Real-time tracking of batch DCF analysis processing with results comparison
 */

'use client';

import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Play,
  Pause,
  Square,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Activity,
  BarChart3,
  Download,
  RefreshCw,
  Eye,
} from 'lucide-react';
import { SimplifiedPropertyInput } from '@/types/property';
import { DCFResult } from '@/types/analysis';
import { formatCurrency, formatPercentage, textColors } from '@/lib/utils';

export interface BatchAnalysisResult {
  property: SimplifiedPropertyInput;
  result?: DCFResult;
  status: 'pending' | 'processing' | 'completed' | 'error';
  startTime?: Date;
  completionTime?: Date;
  error?: string;
  progress?: number; // 0-100
}

export interface BatchProgressStats {
  total: number;
  completed: number;
  failed: number;
  processing: number;
  pending: number;
  averageTime?: number; // seconds
  estimatedRemaining?: number; // seconds
}

interface BatchProgressProps {
  properties: SimplifiedPropertyInput[];
  results: BatchAnalysisResult[];
  stats: BatchProgressStats;
  isRunning: boolean;
  onStart?: () => void;
  onPause?: () => void;
  onStop?: () => void;
  onRetry?: (propertyIndex: number) => void;
  onExport?: (format: 'csv' | 'excel') => void;
  onViewDetails?: (result: DCFResult) => void;
  className?: string;
}

export function BatchProgress({
  properties,
  results,
  stats,
  isRunning,
  onStart,
  onPause,
  onStop,
  onRetry,
  onExport,
  onViewDetails,
  className = '',
}: BatchProgressProps) {
  const [showCompleted, setShowCompleted] = useState(true);
  const [showFailed, setShowFailed] = useState(true);
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'npv' | 'irr'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Calculate overall progress
  const overallProgress = useMemo(() => {
    if (stats.total === 0) return 0;
    return (stats.completed / stats.total) * 100;
  }, [stats.completed, stats.total]);

  // Filter and sort results
  const filteredResults = useMemo(() => {
    let filtered = results.filter(result => {
      if (!showCompleted && result.status === 'completed') return false;
      if (!showFailed && result.status === 'error') return false;
      return true;
    });

    // Sort results
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'name':
          aValue = a.property.property_name;
          bValue = b.property.property_name;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'npv':
          aValue = a.result?.npv || 0;
          bValue = b.result?.npv || 0;
          break;
        case 'irr':
          aValue = a.result?.irr || 0;
          bValue = b.result?.irr || 0;
          break;
        default:
          return 0;
      }

      if (typeof aValue === 'string') {
        return sortOrder === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });

    return filtered;
  }, [results, showCompleted, showFailed, sortBy, sortOrder]);

  const getStatusIcon = (status: BatchAnalysisResult['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'processing':
        return <RefreshCw className="h-4 w-4 text-blue-600 animate-spin" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusBadge = (status: BatchAnalysisResult['status']) => {
    switch (status) {
      case 'completed':
        return <Badge variant="outline" className="text-green-600 border-green-300">Completed</Badge>;
      case 'processing':
        return <Badge variant="outline" className="text-blue-600 border-blue-300">Processing</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      default:
        return <Badge variant="outline" className="text-gray-600 border-gray-300">Pending</Badge>;
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(0)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
    return `${(seconds / 3600).toFixed(1)}h`;
  };

  const getInvestmentRecommendationColor = (recommendation?: string) => {
    switch (recommendation) {
      case 'STRONG_BUY':
        return 'text-green-700 bg-green-100';
      case 'BUY':
        return 'text-green-600 bg-green-50';
      case 'HOLD':
        return 'text-yellow-600 bg-yellow-50';
      case 'SELL':
        return 'text-red-600 bg-red-50';
      case 'STRONG_SELL':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-xl font-semibold ${textColors.primary} flex items-center`}>
            <BarChart3 className="h-5 w-5 mr-2" />
            Batch Analysis Progress
          </h2>
          <p className={`text-sm ${textColors.muted} mt-1`}>
            Track real-time progress of batch DCF analysis
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {!isRunning ? (
            <Button
              onClick={onStart}
              disabled={stats.total === 0}
              className="flex items-center space-x-2"
            >
              <Play className="h-4 w-4" />
              <span>Start Analysis</span>
            </Button>
          ) : (
            <>
              <Button
                variant="outline"
                onClick={onPause}
                className="flex items-center space-x-2"
              >
                <Pause className="h-4 w-4" />
                <span>Pause</span>
              </Button>
              <Button
                variant="outline"
                onClick={onStop}
                className="flex items-center space-x-2 text-red-600 hover:text-red-700"
              >
                <Square className="h-4 w-4" />
                <span>Stop</span>
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Total Properties
                </p>
                <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                  {stats.total}
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
                  Completed
                </p>
                <p className={`text-2xl font-bold text-green-600 mt-1`}>
                  {stats.completed}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Failed
                </p>
                <p className={`text-2xl font-bold text-red-600 mt-1`}>
                  {stats.failed}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Avg. Time
                </p>
                <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                  {stats.averageTime ? formatDuration(stats.averageTime) : '-'}
                </p>
              </div>
              <Clock className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Progress Bar */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-medium">Overall Progress</h3>
              <span className="text-sm text-gray-600">
                {stats.completed} of {stats.total} completed ({overallProgress.toFixed(1)}%)
              </span>
            </div>
            
            <Progress value={overallProgress} className="h-3" />
            
            {stats.estimatedRemaining && isRunning && (
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>
                  {stats.processing > 0 && `${stats.processing} processing • `}
                  {stats.pending} pending
                </span>
                <span>
                  Est. time remaining: {formatDuration(stats.estimatedRemaining)}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Analysis Results</CardTitle>
              <CardDescription>
                Individual property analysis results and status
              </CardDescription>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-2">
                <Button
                  variant={showCompleted ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowCompleted(!showCompleted)}
                  className="text-xs"
                >
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Completed ({stats.completed})
                </Button>
                
                <Button
                  variant={showFailed ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowFailed(!showFailed)}
                  className="text-xs"
                >
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Failed ({stats.failed})
                </Button>
              </div>
              
              {stats.completed > 0 && (
                <div className="flex items-center space-x-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onExport?.('csv')}
                    className="text-xs"
                  >
                    <Download className="h-3 w-3 mr-1" />
                    CSV
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onExport?.('excel')}
                    className="text-xs"
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Excel
                  </Button>
                </div>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => {
                      if (sortBy === 'name') {
                        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                      } else {
                        setSortBy('name');
                        setSortOrder('asc');
                      }
                    }}
                  >
                    Property Name
                    {sortBy === 'name' && (
                      sortOrder === 'asc' ? <TrendingUp className="h-3 w-3 inline ml-1" /> : <TrendingDown className="h-3 w-3 inline ml-1" />
                    )}
                  </TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => {
                      if (sortBy === 'status') {
                        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                      } else {
                        setSortBy('status');
                        setSortOrder('asc');
                      }
                    }}
                  >
                    Status
                    {sortBy === 'status' && (
                      sortOrder === 'asc' ? <TrendingUp className="h-3 w-3 inline ml-1" /> : <TrendingDown className="h-3 w-3 inline ml-1" />
                    )}
                  </TableHead>
                  <TableHead>Purchase Price</TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => {
                      if (sortBy === 'npv') {
                        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                      } else {
                        setSortBy('npv');
                        setSortOrder('desc');
                      }
                    }}
                  >
                    NPV
                    {sortBy === 'npv' && (
                      sortOrder === 'asc' ? <TrendingUp className="h-3 w-3 inline ml-1" /> : <TrendingDown className="h-3 w-3 inline ml-1" />
                    )}
                  </TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => {
                      if (sortBy === 'irr') {
                        setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                      } else {
                        setSortBy('irr');
                        setSortOrder('desc');
                      }
                    }}
                  >
                    IRR
                    {sortBy === 'irr' && (
                      sortOrder === 'asc' ? <TrendingUp className="h-3 w-3 inline ml-1" /> : <TrendingDown className="h-3 w-3 inline ml-1" />
                    )}
                  </TableHead>
                  <TableHead>Recommendation</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredResults.map((result, index) => {
                  const duration = result.startTime && result.completionTime
                    ? (result.completionTime.getTime() - result.startTime.getTime()) / 1000
                    : undefined;
                  
                  return (
                    <TableRow key={index} className={result.status === 'error' ? 'bg-red-50' : ''}>
                      <TableCell className="font-medium">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(result.status)}
                          <span>{result.property.property_name}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(result.status)}
                        {result.status === 'processing' && result.progress && (
                          <div className="mt-1">
                            <Progress value={result.progress} className="h-1" />
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="font-mono">
                        {formatCurrency(result.property.purchase_price)}
                      </TableCell>
                      <TableCell className="font-mono">
                        {result.result?.npv ? formatCurrency(result.result.npv) : '-'}
                      </TableCell>
                      <TableCell className="font-mono">
                        {result.result?.irr ? formatPercentage(result.result.irr / 100) : '-'}
                      </TableCell>
                      <TableCell>
                        {result.result?.investment_recommendation ? (
                          <Badge 
                            variant="outline" 
                            className={`text-xs ${getInvestmentRecommendationColor(result.result.investment_recommendation)}`}
                          >
                            {result.result.investment_recommendation.replace('_', ' ')}
                          </Badge>
                        ) : '-'}
                      </TableCell>
                      <TableCell className="text-sm text-gray-600">
                        {duration ? formatDuration(duration) : '-'}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-1">
                          {result.status === 'completed' && result.result && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => onViewDetails?.(result.result!)}
                              className="text-xs"
                            >
                              <Eye className="h-3 w-3 mr-1" />
                              View
                            </Button>
                          )}
                          {result.status === 'error' && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => onRetry?.(index)}
                              className="text-xs"
                            >
                              <RefreshCw className="h-3 w-3 mr-1" />
                              Retry
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
            
            {filteredResults.length === 0 && (
              <div className="text-center py-8">
                <BarChart3 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Results to Display
                </h3>
                <p className="text-gray-600">
                  {results.length === 0
                    ? 'Start the batch analysis to see results here.'
                    : 'Adjust your filters to view different results.'}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Error Details */}
      {stats.failed > 0 && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-lg text-red-700 flex items-center">
              <AlertCircle className="h-5 w-5 mr-2" />
              Failed Analysis Details
            </CardTitle>
            <CardDescription>
              Properties that failed during analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results
                .filter(result => result.status === 'error')
                .map((result, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                    <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-red-900">
                        {result.property.property_name}
                      </p>
                      <p className="text-sm text-red-700 mt-1">
                        {result.error || 'Analysis failed with unknown error'}
                      </p>
                      <div className="mt-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onRetry?.(results.indexOf(result))}
                          className="text-xs"
                        >
                          <RefreshCw className="h-3 w-3 mr-1" />
                          Retry Analysis
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}