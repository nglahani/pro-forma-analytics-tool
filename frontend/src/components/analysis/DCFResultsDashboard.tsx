/**
 * DCF Results Dashboard
 * Comprehensive display of DCF analysis results with financial metrics
 */

'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Percent, 
  Calendar,
  Download,
  Share,
  Calculator,
  AlertTriangle,
  CheckCircle,
  Activity
} from 'lucide-react';
import { DCFAnalysisResult, InvestmentRecommendation, RiskAssessment } from '@/types/analysis';
import { 
  formatCurrency, 
  formatPercentage, 
  formatNumber, 
  getRecommendationStyle,
  textColors 
} from '@/lib/utils';

interface DCFResultsDashboardProps {
  analysis: DCFAnalysisResult;
  onExport?: (format: 'pdf' | 'excel') => void;
  onRunMonteCarlos?: () => void;
  isExporting?: boolean;
}

export function DCFResultsDashboard({ 
  analysis, 
  onExport,
  onRunMonteCarlos,
  isExporting = false
}: DCFResultsDashboardProps) {
  const { financial_metrics, cash_flow_projections, initial_numbers } = analysis;
  const recommendationStyle = getRecommendationStyle(financial_metrics.investment_recommendation);

  // Calculate summary metrics
  const totalCashFlow = cash_flow_projections.reduce((sum, cf) => sum + cf.net_cash_flow, 0);
  const avgAnnualCashFlow = totalCashFlow / cash_flow_projections.length;
  const cashFlowGrowth = cash_flow_projections.length > 1 ? 
    ((cash_flow_projections[cash_flow_projections.length - 1].net_cash_flow - cash_flow_projections[0].net_cash_flow) / cash_flow_projections[0].net_cash_flow) * 100 : 0;

  const getRiskColor = (risk: RiskAssessment) => {
    switch (risk) {
      case RiskAssessment.LOW:
        return 'text-green-600 bg-green-50 border-green-200';
      case RiskAssessment.MODERATE:
        return 'text-amber-600 bg-amber-50 border-amber-200';
      case RiskAssessment.HIGH:
        return 'text-red-600 bg-red-50 border-red-200';
      case RiskAssessment.VERY_HIGH:
        return 'text-red-700 bg-red-100 border-red-300';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const MetricCard = ({ 
    title, 
    value, 
    subtitle, 
    icon: Icon, 
    trend, 
    color = 'blue' 
  }: {
    title: string;
    value: string;
    subtitle?: string;
    icon: any;
    trend?: 'up' | 'down' | 'neutral';
    color?: 'blue' | 'green' | 'red' | 'amber';
  }) => {
    const colorClasses = {
      blue: 'bg-blue-50 text-blue-600',
      green: 'bg-green-50 text-green-600',
      red: 'bg-red-50 text-red-600',
      amber: 'bg-amber-50 text-amber-600',
    };

    const trendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : null;

    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <p className={`text-sm font-medium ${textColors.muted}`}>
                {title}
              </p>
              <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                {value}
              </p>
              {subtitle && (
                <div className="flex items-center mt-2">
                  {trendIcon && (
                    <trendIcon className={`h-3 w-3 mr-1 ${
                      trend === 'up' ? 'text-green-600' : 'text-red-600'
                    }`} />
                  )}
                  <p className={`text-xs ${textColors.muted}`}>
                    {subtitle}
                  </p>
                </div>
              )}
            </div>
            <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>
              <Icon className="h-6 w-6" />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-2xl font-bold ${textColors.primary}`}>
            DCF Analysis Results
          </h1>
          <p className={`${textColors.muted} mt-1`}>
            Property ID: {analysis.property_id} • Analyzed on {new Date(analysis.analysis_date).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {onRunMonteCarlos && (
            <Button variant="outline" onClick={onRunMonteCarlos}>
              <Activity className="h-4 w-4 mr-2" />
              Run Monte Carlo
            </Button>
          )}
          {onExport && (
            <div className="flex space-x-1">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => onExport('pdf')}
                disabled={isExporting}
              >
                <Download className="h-4 w-4 mr-1" />
                PDF
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => onExport('excel')}
                disabled={isExporting}
              >
                <Download className="h-4 w-4 mr-1" />
                Excel
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Investment Recommendation */}
      <Card className={recommendationStyle.bgColor}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${recommendationStyle.bgColor}`}>
                {financial_metrics.investment_recommendation === InvestmentRecommendation.STRONG_BUY || 
                 financial_metrics.investment_recommendation === InvestmentRecommendation.BUY ? (
                  <CheckCircle className={`h-6 w-6 ${recommendationStyle.color}`} />
                ) : (
                  <AlertTriangle className={`h-6 w-6 ${recommendationStyle.color}`} />
                )}
              </div>
              <div>
                <h3 className={`text-lg font-semibold ${recommendationStyle.color}`}>
                  Investment Recommendation
                </h3>
                <p className={`text-2xl font-bold ${recommendationStyle.color} mt-1`}>
                  {recommendationStyle.label}
                </p>
              </div>
            </div>
            <Badge variant="outline" className={`${getRiskColor(financial_metrics.risk_assessment)} border`}>
              {financial_metrics.risk_assessment.replace('_', ' ')} Risk
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Key Financial Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Net Present Value"
          value={formatCurrency(financial_metrics.npv, { compact: true })}
          subtitle={financial_metrics.npv > 0 ? "Positive NPV" : "Negative NPV"}
          icon={DollarSign}
          trend={financial_metrics.npv > 0 ? 'up' : 'down'}
          color={financial_metrics.npv > 0 ? 'green' : 'red'}
        />
        
        <MetricCard
          title="Internal Rate of Return"
          value={formatPercentage(financial_metrics.irr / 100)}
          subtitle={`vs ${formatPercentage(0.08)} market avg`}
          icon={Percent}
          trend={financial_metrics.irr > 8 ? 'up' : 'down'}
          color={financial_metrics.irr > 8 ? 'green' : 'red'}
        />
        
        <MetricCard
          title="Equity Multiple"
          value={`${financial_metrics.equity_multiple.toFixed(2)}x`}
          subtitle={`${formatPercentage(financial_metrics.total_return / 100)} total return`}
          icon={TrendingUp}
          trend={financial_metrics.equity_multiple > 2 ? 'up' : 'down'}
          color={financial_metrics.equity_multiple > 2 ? 'green' : 'amber'}
        />
        
        <MetricCard
          title="Payback Period"
          value={`${financial_metrics.payback_period.toFixed(1)} yrs`}
          subtitle="Time to recover investment"
          icon={Calendar}
          trend={financial_metrics.payback_period < 10 ? 'up' : 'down'}
          color={financial_metrics.payback_period < 10 ? 'green' : 'amber'}
        />
      </div>

      {/* Investment Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Investment Summary</CardTitle>
            <CardDescription>
              Key financial metrics and cash flow overview
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Total Cash Invested:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {formatCurrency(financial_metrics.total_cash_invested)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Total Proceeds:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {formatCurrency(financial_metrics.total_proceeds)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Terminal Value:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {formatCurrency(financial_metrics.terminal_value)}
                  </span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Avg. Annual Return:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {formatPercentage(financial_metrics.average_annual_return / 100)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Total Cash Flow:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {formatCurrency(totalCashFlow)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Cash Flow Growth:</span>
                  <span className={`font-medium ${cashFlowGrowth > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercentage(cashFlowGrowth / 100)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Analysis Details</CardTitle>
            <CardDescription>
              Property assumptions and calculation parameters
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Purchase Price:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {formatCurrency(initial_numbers.purchase_price)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Loan Amount:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {formatCurrency(initial_numbers.loan_amount)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Total Investment:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {formatCurrency(initial_numbers.total_cash_investment)}
                  </span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className={textColors.muted}>Analysis Period:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {cash_flow_projections.length} years
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Execution Time:</span>
                  <span className={`font-medium ${textColors.body}`}>
                    {analysis.execution_time_ms}ms
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className={textColors.muted}>Analysis Status:</span>
                  <Badge variant={analysis.success ? "success" : "destructive"} className="text-xs">
                    {analysis.success ? "Completed" : "Failed"}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Cash Flow Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Cash Flow Progression</CardTitle>
          <CardDescription>
            Year-over-year cash flow performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {cash_flow_projections.slice(0, 3).map((cf, index) => (
              <div key={cf.year} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className={`text-sm font-medium ${textColors.secondary}`}>
                    Year {cf.year}
                  </span>
                  <span className={`font-semibold ${cf.net_cash_flow > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(cf.net_cash_flow)}
                  </span>
                </div>
                <Progress 
                  value={Math.max(0, Math.min(100, (cf.net_cash_flow / avgAnnualCashFlow) * 50))} 
                  className="h-2"
                />
              </div>
            ))}
            {cash_flow_projections.length > 3 && (
              <div className="text-center">
                <Badge variant="outline" className="text-xs">
                  +{cash_flow_projections.length - 3} more years
                </Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}