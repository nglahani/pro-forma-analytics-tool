/**
 * Market Defaults Panel Component
 * 
 * Displays current market data defaults for the selected MSA
 * and allows users to apply these defaults to their property analysis.
 */

'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  DollarSign, 
  Percent, 
  Calendar,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Loader2,
  Info
} from 'lucide-react';
import { MarketDataDefaults } from '@/types/property';
import { textColors } from '@/lib/utils';

interface MarketDefaultsPanelProps {
  msaCode?: string;
  msaName?: string;
  marketDefaults: MarketDataDefaults | null;
  loading: boolean;
  error?: string | null;
  onApplyDefaults?: () => void;
  onRefresh?: () => void;
  className?: string;
}

export function MarketDefaultsPanel({
  msaCode,
  msaName,
  marketDefaults,
  loading,
  error,
  onApplyDefaults,
  onRefresh,
  className = ''
}: MarketDefaultsPanelProps) {
  
  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;
  const formatCurrency = (value: number) => `$${value.toLocaleString()}`;
  const formatMonths = (value: number) => `${value.toFixed(1)} months`;

  const getStatusColor = () => {
    if (loading) return 'border-blue-300 bg-blue-50';
    if (error) return 'border-red-300 bg-red-50';
    if (marketDefaults) return 'border-green-300 bg-green-50';
    return 'border-gray-200';
  };

  const getStatusIcon = () => {
    if (loading) return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
    if (error) return <AlertCircle className="h-4 w-4 text-red-500" />;
    if (marketDefaults) return <CheckCircle className="h-4 w-4 text-green-500" />;
    return <Info className="h-4 w-4 text-gray-400" />;
  };

  if (!msaCode) {
    return (
      <Card className={`border-gray-200 ${className}`}>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 text-gray-500">
            <Info className="h-4 w-4" />
            <span className="text-sm">Select a property address to view market defaults</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${getStatusColor()} transition-colors duration-200 ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <div>
              <CardTitle className="text-sm font-medium">Market Defaults</CardTitle>
              {msaName && (
                <CardDescription className="text-xs">
                  {msaName} • MSA {msaCode}
                </CardDescription>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {onRefresh && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRefresh}
                disabled={loading}
                className="h-7 w-7 p-0"
              >
                <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
              </Button>
            )}
            
            {marketDefaults && onApplyDefaults && (
              <Button
                variant="outline" 
                size="sm"
                onClick={onApplyDefaults}
                className="text-xs h-7"
              >
                Apply Defaults
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {loading && (
          <div className="flex items-center gap-2 text-blue-700 text-sm">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Loading market data...</span>
          </div>
        )}

        {error && (
          <div className="text-red-700 text-sm">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              <span>Unable to load market data</span>
            </div>
            <p className="text-xs mt-1 text-red-600">Using fallback defaults for this market</p>
          </div>
        )}

        {marketDefaults && (
          <div className="space-y-4">
            {/* Key Financial Metrics */}
            <div>
              <h4 className={`text-xs font-medium ${textColors.secondary} mb-2`}>
                Key Financial Metrics
              </h4>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Cap Rate:</span>
                  <Badge variant="secondary" className="text-xs">
                    {formatPercentage(marketDefaults.cap_rate)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Interest Rate:</span>
                  <Badge variant="secondary" className="text-xs">
                    {formatPercentage(marketDefaults.interest_rate)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Vacancy Rate:</span>
                  <Badge variant="secondary" className="text-xs">
                    {formatPercentage(marketDefaults.vacancy_rate)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>LTV Ratio:</span>
                  <Badge variant="secondary" className="text-xs">
                    {formatPercentage(marketDefaults.ltv_ratio)}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Growth Rates */}
            <div>
              <h4 className={`text-xs font-medium ${textColors.secondary} mb-2`}>
                Annual Growth Rates
              </h4>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Rent Growth:</span>
                  <Badge variant="outline" className="text-xs">
                    {formatPercentage(marketDefaults.rent_growth_rate)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Expense Growth:</span>
                  <Badge variant="outline" className="text-xs">
                    {formatPercentage(marketDefaults.expense_growth_rate)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Property Growth:</span>
                  <Badge variant="outline" className="text-xs">
                    {formatPercentage(marketDefaults.property_growth_rate)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Management Fee:</span>
                  <Badge variant="outline" className="text-xs">
                    {formatPercentage(marketDefaults.management_fee_pct)}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Other Parameters */}
            <div>
              <h4 className={`text-xs font-medium ${textColors.secondary} mb-2`}>
                Other Parameters
              </h4>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Closing Costs:</span>
                  <Badge variant="outline" className="text-xs">
                    {formatPercentage(marketDefaults.closing_cost_pct)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Lender Reserves:</span>
                  <Badge variant="outline" className="text-xs">
                    {formatMonths(marketDefaults.lender_reserves_months)}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className={textColors.muted}>Maintenance Reserve:</span>
                  <Badge variant="outline" className="text-xs">
                    {formatCurrency(marketDefaults.maintenance_reserve_per_unit)}/unit
                  </Badge>
                </div>
              </div>
            </div>

            {/* Apply Defaults Button */}
            {onApplyDefaults && (
              <div className="pt-2 border-t border-gray-200">
                <Button
                  onClick={onApplyDefaults}
                  className="w-full text-xs h-8"
                  variant="default"
                  size="sm"
                >
                  <DollarSign className="h-3 w-3 mr-1" />
                  Apply All Market Defaults to Analysis
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}