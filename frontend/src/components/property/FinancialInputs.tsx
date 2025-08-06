/**
 * Financial Inputs Component with Market Data Defaults
 * Provides smart defaults from market data for financial parameters
 */

'use client';

import { useEffect, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, RefreshCw, TrendingUp, Info } from 'lucide-react';
import { PropertyFinancials, MarketDataDefaults } from '@/types/property';
import { useMarketDefaults } from '@/hooks/useMarketDefaults';
import { textColors, formatPercentage, formatCurrency } from '@/lib/utils';

interface FinancialInputsProps {
  financials: Partial<PropertyFinancials>;
  onChange: (financials: Partial<PropertyFinancials>) => void;
  msaCode?: string;
  errors?: {
    purchase_price?: string;
    down_payment_percentage?: string;
    loan_terms?: {
      interest_rate?: string;
      loan_term_years?: string;
    };
    monthly_rent_per_unit?: string;
    monthly_operating_expenses?: string;
    annual_property_taxes?: string;
    annual_insurance?: string;
    capex_percentage?: string;
  };
}

export function FinancialInputs({ 
  financials, 
  onChange, 
  msaCode,
  errors = {} 
}: FinancialInputsProps) {
  const { loading, data: marketDefaults, error, refetch } = useMarketDefaults(msaCode);
  const [appliedDefaults, setAppliedDefaults] = useState<Set<string>>(new Set());

  const handleFieldChange = (field: string, value: string | number) => {
    const numericValue = typeof value === 'string' ? 
      (value === '' ? undefined : Number(value)) : value;
    
    // Handle nested loan_terms fields
    if (field.startsWith('loan_terms.')) {
      const loanField = field.split('.')[1];
      onChange({
        ...financials,
        loan_terms: {
          ...financials.loan_terms,
          [loanField]: numericValue,
        },
      });
    } else {
      onChange({
        ...financials,
        [field]: numericValue,
      });
    }
  };

  const applyMarketDefault = (field: string, value: number) => {
    handleFieldChange(field, value);
    setAppliedDefaults(prev => new Set([...prev, field]));
  };

  const applyAllDefaults = () => {
    if (!marketDefaults) return;

    const updates: Partial<PropertyFinancials> = { ...financials };

    // Apply defaults only to empty fields
    if (!financials.loan_terms?.interest_rate) {
      updates.loan_terms = {
        ...updates.loan_terms,
        interest_rate: marketDefaults.interest_rate,
      };
      setAppliedDefaults(prev => new Set([...prev, 'loan_terms.interest_rate']));
    }

    if (!financials.vacancy_rate) {
      updates.vacancy_rate = marketDefaults.vacancy_rate;
      setAppliedDefaults(prev => new Set([...prev, 'vacancy_rate']));
    }

    onChange(updates);
  };

  const getDefaultValue = (field: string): number | undefined => {
    if (!marketDefaults) return undefined;
    
    switch (field) {
      case 'loan_terms.interest_rate':
        return marketDefaults.interest_rate;
      case 'vacancy_rate':
        return marketDefaults.vacancy_rate;
      default:
        return undefined;
    }
  };

  const isDefaultApplied = (field: string): boolean => {
    return appliedDefaults.has(field);
  };

  const MarketDefaultButton = ({ 
    field, 
    value, 
    label 
  }: { 
    field: string; 
    value: number; 
    label: string; 
  }) => (
    <Button
      type="button"
      variant="outline"
      size="sm"
      onClick={() => applyMarketDefault(field, value)}
      disabled={isDefaultApplied(field)}
      className="text-xs h-7"
    >
      <TrendingUp className="h-3 w-3 mr-1" />
      Use Market: {label}
    </Button>
  );

  return (
    <div className="space-y-6">
      {/* Market Data Status */}
      {msaCode && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Info className="h-4 w-4 text-blue-600" />
                <CardTitle className="text-sm text-blue-900">
                  Market Data Defaults
                </CardTitle>
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={refetch}
                disabled={loading}
                className="h-7"
              >
                {loading ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <RefreshCw className="h-3 w-3" />
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            {loading && (
              <div className="flex items-center space-x-2 text-sm text-blue-700">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Loading market data...</span>
              </div>
            )}
            
            {error && (
              <div className="text-sm text-red-600">
                Error loading market data: {error}
              </div>
            )}
            
            {marketDefaults && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-blue-800">
                    Current market rates available for MSA {msaCode}
                  </span>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={applyAllDefaults}
                    className="text-xs h-7"
                  >
                    Apply All Defaults
                  </Button>
                </div>
                <div className="text-xs text-blue-700">
                  Last updated: {new Date(marketDefaults.last_updated).toLocaleDateString()}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Purchase & Financing */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Purchase & Financing</CardTitle>
          <CardDescription>
            Property acquisition and loan details
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="purchase_price" className={textColors.secondary}>
                Purchase Price * ($)
              </Label>
              <Input
                id="purchase_price"
                type="number"
                value={financials.purchase_price || ''}
                onChange={(e) => handleFieldChange('purchase_price', e.target.value)}
                placeholder="2500000"
                className={errors.purchase_price ? 'border-red-500 focus:ring-red-500' : ''}
              />
              {errors.purchase_price && (
                <p className="text-sm text-red-600">{errors.purchase_price}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="down_payment" className={textColors.secondary}>
                Down Payment (%)
              </Label>
              <Input
                id="down_payment"
                type="number"
                step="0.1"
                value={financials.down_payment_percentage || ''}
                onChange={(e) => handleFieldChange('down_payment_percentage', e.target.value)}
                placeholder="25"
                className={errors.down_payment_percentage ? 'border-red-500 focus:ring-red-500' : ''}
              />
              {errors.down_payment_percentage && (
                <p className="text-sm text-red-600">{errors.down_payment_percentage}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="interest_rate" className={textColors.secondary}>
                Interest Rate (%)
              </Label>
              <div className="space-y-2">
                <Input
                  id="interest_rate"
                  type="number"
                  step="0.01"
                  value={financials.loan_terms?.interest_rate || ''}
                  onChange={(e) => handleFieldChange('loan_terms.interest_rate', e.target.value)}
                  placeholder="6.5"
                  className={errors.loan_terms?.interest_rate ? 'border-red-500 focus:ring-red-500' : ''}
                />
                {marketDefaults && !isDefaultApplied('loan_terms.interest_rate') && (
                  <MarketDefaultButton
                    field="loan_terms.interest_rate"
                    value={marketDefaults.interest_rate}
                    label={formatPercentage(marketDefaults.interest_rate / 100)}
                  />
                )}
                {isDefaultApplied('loan_terms.interest_rate') && (
                  <Badge variant="success" className="text-xs">
                    Market default applied
                  </Badge>
                )}
              </div>
              {errors.loan_terms?.interest_rate && (
                <p className="text-sm text-red-600">{errors.loan_terms.interest_rate}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="loan_term" className={textColors.secondary}>
                Loan Term (years)
              </Label>
              <Input
                id="loan_term"
                type="number"
                value={financials.loan_terms?.loan_term_years || ''}
                onChange={(e) => handleFieldChange('loan_terms.loan_term_years', e.target.value)}
                placeholder="30"
                className={errors.loan_terms?.loan_term_years ? 'border-red-500 focus:ring-red-500' : ''}
              />
              {errors.loan_terms?.loan_term_years && (
                <p className="text-sm text-red-600">{errors.loan_terms.loan_term_years}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Income & Expenses */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Income & Operating Expenses</CardTitle>
          <CardDescription>
            Monthly income and expense projections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="monthly_rent" className={textColors.secondary}>
                Monthly Rent per Unit ($)
              </Label>
              <Input
                id="monthly_rent"
                type="number"
                value={financials.monthly_rent_per_unit || ''}
                onChange={(e) => handleFieldChange('monthly_rent_per_unit', e.target.value)}
                placeholder="2500"
                className={errors.monthly_rent_per_unit ? 'border-red-500 focus:ring-red-500' : ''}
              />
              {errors.monthly_rent_per_unit && (
                <p className="text-sm text-red-600">{errors.monthly_rent_per_unit}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="other_income" className={textColors.secondary}>
                Other Monthly Income ($)
              </Label>
              <Input
                id="other_income"
                type="number"
                value={financials.other_monthly_income || ''}
                onChange={(e) => handleFieldChange('other_monthly_income', e.target.value)}
                placeholder="500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="vacancy_rate" className={textColors.secondary}>
                Vacancy Rate (%)
              </Label>
              <div className="space-y-2">
                <Input
                  id="vacancy_rate"
                  type="number"
                  step="0.1"
                  value={financials.vacancy_rate || ''}
                  onChange={(e) => handleFieldChange('vacancy_rate', e.target.value)}
                  placeholder="5"
                />
                {marketDefaults && !isDefaultApplied('vacancy_rate') && (
                  <MarketDefaultButton
                    field="vacancy_rate"
                    value={marketDefaults.vacancy_rate}
                    label={formatPercentage(marketDefaults.vacancy_rate / 100)}
                  />
                )}
                {isDefaultApplied('vacancy_rate') && (
                  <Badge variant="success" className="text-xs">
                    Market default applied
                  </Badge>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="operating_expenses" className={textColors.secondary}>
                Monthly Operating Expenses ($)
              </Label>
              <Input
                id="operating_expenses"
                type="number"
                value={financials.monthly_operating_expenses || ''}
                onChange={(e) => handleFieldChange('monthly_operating_expenses', e.target.value)}
                placeholder="8000"
                className={errors.monthly_operating_expenses ? 'border-red-500 focus:ring-red-500' : ''}
              />
              {errors.monthly_operating_expenses && (
                <p className="text-sm text-red-600">{errors.monthly_operating_expenses}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="property_taxes" className={textColors.secondary}>
                Annual Property Taxes ($)
              </Label>
              <Input
                id="property_taxes"
                type="number"
                value={financials.annual_property_taxes || ''}
                onChange={(e) => handleFieldChange('annual_property_taxes', e.target.value)}
                placeholder="25000"
                className={errors.annual_property_taxes ? 'border-red-500 focus:ring-red-500' : ''}
              />
              {errors.annual_property_taxes && (
                <p className="text-sm text-red-600">{errors.annual_property_taxes}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="insurance" className={textColors.secondary}>
                Annual Insurance ($)
              </Label>
              <Input
                id="insurance"
                type="number"
                value={financials.annual_insurance || ''}
                onChange={(e) => handleFieldChange('annual_insurance', e.target.value)}
                placeholder="12000"
                className={errors.annual_insurance ? 'border-red-500 focus:ring-red-500' : ''}
              />
              {errors.annual_insurance && (
                <p className="text-sm text-red-600">{errors.annual_insurance}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="capex_percentage" className={textColors.secondary}>
                CapEx Reserve (% of income)
              </Label>
              <Input
                id="capex_percentage"
                type="number"
                step="0.1"
                value={financials.capex_percentage || ''}
                onChange={(e) => handleFieldChange('capex_percentage', e.target.value)}
                placeholder="5"
                className={errors.capex_percentage ? 'border-red-500 focus:ring-red-500' : ''}
              />
              {errors.capex_percentage && (
                <p className="text-sm text-red-600">{errors.capex_percentage}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}