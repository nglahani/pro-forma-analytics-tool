/**
 * Interactive Cash Flow Projection Table
 * Displays detailed year-by-year cash flow projections with interactive features
 */

'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  ChevronDown, 
  ChevronRight, 
  TrendingUp, 
  TrendingDown, 
  DollarSign,
  BarChart3,
  Download
} from 'lucide-react';
import { CashFlowProjection } from '@/types/analysis';
import { formatCurrency, formatPercentage, textColors } from '@/lib/utils';

interface CashFlowTableProps {
  projections: CashFlowProjection[];
  onExport?: (format: 'csv' | 'excel') => void;
  isExporting?: boolean;
}

export function CashFlowTable({ 
  projections, 
  onExport,
  isExporting = false 
}: CashFlowTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [selectedMetric, setSelectedMetric] = useState<string>('net_cash_flow');

  const toggleRowExpansion = (year: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(year)) {
      newExpanded.delete(year);
    } else {
      newExpanded.add(year);
    }
    setExpandedRows(newExpanded);
  };

  const expandAll = () => {
    setExpandedRows(new Set(projections.map(p => p.year)));
  };

  const collapseAll = () => {
    setExpandedRows(new Set());
  };

  const getYearOverYearChange = (currentValue: number, previousValue: number): { percentage: number; trend: 'up' | 'down' | 'neutral' } => {
    if (previousValue === 0) return { percentage: 0, trend: 'neutral' };
    
    const percentage = ((currentValue - previousValue) / Math.abs(previousValue)) * 100;
    const trend = percentage > 0 ? 'up' : percentage < 0 ? 'down' : 'neutral';
    
    return { percentage: Math.abs(percentage), trend };
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-3 w-3 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-3 w-3 text-red-600" />;
      default:
        return <div className="h-3 w-3" />;
    }
  };

  const getTrendColor = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const metrics = [
    { key: 'gross_rental_income', label: 'Gross Rental Income' },
    { key: 'effective_gross_income', label: 'Effective Gross Income' },
    { key: 'operating_expenses', label: 'Operating Expenses' },
    { key: 'net_operating_income', label: 'Net Operating Income' },
    { key: 'debt_service', label: 'Debt Service' },
    { key: 'net_cash_flow', label: 'Net Cash Flow' },
  ];


  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-xl font-semibold ${textColors.primary}`}>
            Cash Flow Projections
          </h2>
          <p className={`text-sm ${textColors.muted} mt-1`}>
            {projections.length} year analysis period
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={expandAll}
            className="text-xs"
          >
            <ChevronDown className="h-3 w-3 mr-1" />
            Expand All
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={collapseAll}
            className="text-xs"
          >
            <ChevronRight className="h-3 w-3 mr-1" />
            Collapse All
          </Button>
          {onExport && (
            <div className="flex space-x-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onExport('csv')}
                disabled={isExporting}
                className="text-xs"
              >
                <Download className="h-3 w-3 mr-1" />
                CSV
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onExport('excel')}
                disabled={isExporting}
                className="text-xs"
              >
                <Download className="h-3 w-3 mr-1" />
                Excel
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Metric Selector */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center">
            <BarChart3 className="h-4 w-4 mr-2" />
            Focus Metric
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {metrics.map((metric) => (
              <Badge
                key={metric.key}
                variant={selectedMetric === metric.key ? "default" : "outline"}
                className="cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => setSelectedMetric(metric.key)}
              >
                {metric.label}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Cash Flow Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-gray-50">
                  <TableHead className="w-20"></TableHead>
                  <TableHead className="font-semibold">Year</TableHead>
                  <TableHead className="font-semibold text-right">Gross Rental Income</TableHead>
                  <TableHead className="font-semibold text-right">Effective Gross Income</TableHead>
                  <TableHead className="font-semibold text-right">Operating Expenses</TableHead>
                  <TableHead className="font-semibold text-right">Net Operating Income</TableHead>
                  <TableHead className="font-semibold text-right">Debt Service</TableHead>
                  <TableHead className="font-semibold text-right">Net Cash Flow</TableHead>
                  <TableHead className="font-semibold text-center">YoY Change</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projections.map((projection, index) => {
                  const isExpanded = expandedRows.has(projection.year);
                  const previousProjection = index > 0 ? projections[index - 1] : null;
                  const cashFlowChange = previousProjection 
                    ? getYearOverYearChange(projection.net_cash_flow, previousProjection.net_cash_flow)
                    : { percentage: 0, trend: 'neutral' as const };

                  return (
                    <TableRow 
                      key={projection.year}
                      className={`hover:bg-gray-50 ${selectedMetric !== 'net_cash_flow' && isExpanded ? 'bg-blue-50' : ''}`}
                    >
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleRowExpansion(projection.year)}
                          className="h-6 w-6 p-0"
                        >
                          {isExpanded ? (
                            <ChevronDown className="h-3 w-3" />
                          ) : (
                            <ChevronRight className="h-3 w-3" />
                          )}
                        </Button>
                      </TableCell>
                      <TableCell className="font-medium">
                        <div className="flex items-center space-x-2">
                          <span>{projection.year}</span>
                          {selectedMetric !== 'net_cash_flow' && (
                            <Badge variant="secondary" className="text-xs">
                              Focus
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm">
                        {formatCurrency(projection.gross_rental_income)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm">
                        {formatCurrency(projection.effective_gross_income)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-red-600">
                        {formatCurrency(projection.operating_expenses)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm font-semibold">
                        {formatCurrency(projection.net_operating_income)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-red-600">
                        {formatCurrency(projection.debt_service)}
                      </TableCell>
                      <TableCell className={`text-right font-mono text-sm font-bold ${
                        projection.net_cash_flow > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatCurrency(projection.net_cash_flow)}
                      </TableCell>
                      <TableCell className="text-center">
                        {index > 0 && (
                          <div className="flex items-center justify-center space-x-1">
                            {getTrendIcon(cashFlowChange.trend)}
                            <span className={`text-xs font-medium ${getTrendColor(cashFlowChange.trend)}`}>
                              {cashFlowChange.percentage.toFixed(1)}%
                            </span>
                          </div>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Total Cash Flow
                </p>
                <p className={`text-xl font-bold ${textColors.primary} mt-1`}>
                  {formatCurrency(projections.reduce((sum, p) => sum + p.net_cash_flow, 0))}
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Average Annual CF
                </p>
                <p className={`text-xl font-bold ${textColors.primary} mt-1`}>
                  {formatCurrency(projections.reduce((sum, p) => sum + p.net_cash_flow, 0) / projections.length)}
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  CF Growth Rate
                </p>
                <p className={`text-xl font-bold ${textColors.primary} mt-1`}>
                  {projections.length > 1 ? 
                    formatPercentage(
                      ((projections[projections.length - 1].net_cash_flow - projections[0].net_cash_flow) / 
                       Math.abs(projections[0].net_cash_flow)) / projections.length
                    ) : '0%'
                  }
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}