/**
 * Analysis Results Card Component
 * Displays a single financial metric with icon, label, and formatted value
 */

'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';

interface AnalysisResultsCardProps {
  label: string;
  value: string;
  icon?: LucideIcon;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export function AnalysisResultsCard({
  label,
  value,
  icon: Icon,
  subtitle,
  trend,
  className = '',
}: AnalysisResultsCardProps) {
  const getTrendColor = () => {
    if (!trend) return '';
    return trend === 'up'
      ? 'text-green-600'
      : trend === 'down'
      ? 'text-red-600'
      : 'text-gray-600';
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    return trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→';
  };

  return (
    <Card className={`hover:shadow-md transition-shadow ${className}`}>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
              {Icon && <Icon className="h-4 w-4" />}
              <span>{label}</span>
            </div>
            <div className="text-2xl font-bold tracking-tight">{value}</div>
            {subtitle && (
              <div className={`text-sm mt-1 ${getTrendColor()}`}>
                {getTrendIcon() && <span className="mr-1">{getTrendIcon()}</span>}
                {subtitle}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
