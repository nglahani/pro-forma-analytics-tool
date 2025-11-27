/**
 * Analysis Results Modal Component
 * Displays DCF analysis results in a modal dialog with financial metrics and recommendation
 */

'use client';

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AnalysisResultsCard } from './AnalysisResultsCard';
import {
  formatCurrency,
  formatPercentage,
  formatMultiple,
  formatTimestamp,
  formatDuration,
  getRecommendationColor,
  formatRecommendation,
  getRecommendationIcon,
} from '@/lib/utils/formatters';
import {
  DollarSign,
  TrendingUp,
  BarChart3,
  Clock,
  Calendar,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';

interface FinancialMetrics {
  npv: number;
  irr: number;
  equity_multiple: number;
  payback_period?: number;
  total_cash_flow?: number;
}

interface AnalysisMetadata {
  processing_time_seconds?: number;
  analysis_timestamp?: string;
  data_sources?: Record<string, string>;
}

interface AnalysisResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  propertyName: string;
  financialMetrics: FinancialMetrics | null;
  investmentRecommendation: string | null;
  metadata?: AnalysisMetadata;
  onViewDetails?: () => void;
  onRunAnother?: () => void;
}

export function AnalysisResultsModal({
  isOpen,
  onClose,
  propertyName,
  financialMetrics,
  investmentRecommendation,
  metadata,
  onViewDetails,
  onRunAnother,
}: AnalysisResultsModalProps) {
  if (!financialMetrics) {
    return null;
  }

  const recommendationColor = getRecommendationColor(investmentRecommendation);
  const recommendationIcon = getRecommendationIcon(investmentRecommendation);
  const recommendationText = formatRecommendation(investmentRecommendation);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">DCF Analysis Results</DialogTitle>
          <DialogDescription>
            Property: <span className="font-medium text-foreground">{propertyName}</span>
            {metadata?.analysis_timestamp && (
              <span className="ml-2 text-muted-foreground">
                • Analyzed {formatTimestamp(metadata.analysis_timestamp, 'medium')}
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Financial Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <AnalysisResultsCard
              label="Net Present Value"
              value={formatCurrency(financialMetrics.npv)}
              icon={DollarSign}
              subtitle={financialMetrics.npv > 0 ? 'Positive NPV' : 'Negative NPV'}
              trend={financialMetrics.npv > 0 ? 'up' : 'down'}
            />

            <AnalysisResultsCard
              label="Internal Rate of Return"
              value={formatPercentage(financialMetrics.irr)}
              icon={TrendingUp}
              subtitle="Annualized return"
            />

            <AnalysisResultsCard
              label="Equity Multiple"
              value={formatMultiple(financialMetrics.equity_multiple)}
              icon={BarChart3}
              subtitle="Return on investment"
            />
          </div>

          {/* Additional Metrics */}
          {(financialMetrics.payback_period || financialMetrics.total_cash_flow) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {financialMetrics.payback_period && (
                <AnalysisResultsCard
                  label="Payback Period"
                  value={`${financialMetrics.payback_period.toFixed(1)} years`}
                  icon={Clock}
                />
              )}
              {financialMetrics.total_cash_flow && (
                <AnalysisResultsCard
                  label="Total Cash Flow"
                  value={formatCurrency(financialMetrics.total_cash_flow)}
                  icon={BarChart3}
                />
              )}
            </div>
          )}

          {/* Investment Recommendation */}
          {investmentRecommendation && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-muted-foreground mb-3">
                Investment Recommendation
              </h3>
              <div
                className={`p-6 rounded-lg border-2 ${recommendationColor}`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-4xl">{recommendationIcon}</span>
                  <div>
                    <div className="text-2xl font-bold">{recommendationText}</div>
                    <div className="text-sm mt-1 opacity-80">
                      Based on financial metrics and market conditions
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Analysis Metadata */}
          {metadata && (
            <div className="border-t pt-4 mt-6">
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div className="flex items-center gap-4">
                  {metadata.processing_time_seconds && (
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      <span>Processing: {formatDuration(metadata.processing_time_seconds)}</span>
                    </div>
                  )}
                  {metadata.analysis_timestamp && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>{formatTimestamp(metadata.analysis_timestamp, 'short')}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t">
            {onViewDetails && (
              <Button
                onClick={onViewDetails}
                variant="outline"
                className="flex-1"
              >
                <ArrowRight className="mr-2 h-4 w-4" />
                View Detailed Cash Flows
              </Button>
            )}
            {onRunAnother && (
              <Button
                onClick={onRunAnother}
                variant="outline"
                className="flex-1"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Analyze Another Property
              </Button>
            )}
            <Button onClick={onClose} className="flex-1">
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
