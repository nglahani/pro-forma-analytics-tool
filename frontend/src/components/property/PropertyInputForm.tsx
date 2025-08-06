/**
 * Multi-Step Property Input Form
 * Comprehensive form for property data collection
 */

'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, ArrowRight, Building2, DollarSign, Settings, FileText } from 'lucide-react';
import { PropertyTemplate } from '@/types/propertyTemplates';
import { 
  SimplifiedPropertyInput, 
  RenovationStatus, 
  PropertyType,
  PropertyValidationErrors 
} from '@/types/property';
import { textColors } from '@/lib/utils';
import { AddressValidator } from './AddressValidator';
import { useMarketDefaults } from '@/hooks/useMarketDefaults';
import { MarketDefaultsPanel } from './MarketDefaultsPanel';

interface PropertyInputFormProps {
  template: PropertyTemplate;
  onBack: () => void;
  onSubmit: (data: SimplifiedPropertyInput) => void;
}

type FormStep = 'basic' | 'financial' | 'units' | 'renovation' | 'equity' | 'review';

const STEP_CONFIG = {
  basic: { title: 'Property Details', icon: Building2, step: 1 },
  financial: { title: 'Financial Information', icon: DollarSign, step: 2 },
  units: { title: 'Unit Information', icon: Building2, step: 3 },
  renovation: { title: 'Renovation & Costs', icon: Settings, step: 4 },
  equity: { title: 'Equity Structure', icon: DollarSign, step: 5 },
  review: { title: 'Review & Submit', icon: FileText, step: 6 }
};

export function PropertyInputForm({ template, onBack, onSubmit }: PropertyInputFormProps) {
  const [currentStep, setCurrentStep] = useState<FormStep>('basic');
  const [isAddressValid, setIsAddressValid] = useState(false);
  const [formData, setFormData] = useState<Partial<SimplifiedPropertyInput>>({
    property_id: `prop_${Date.now()}`,
    analysis_date: new Date().toISOString().split('T')[0],
    property_name: '',
    city: '',
    state: '',
    property_address: '',
    msa_code: '',
    purchase_price: undefined,
    notes: '',
    residential_units: template.defaultConfig.residential_units || { total_units: 0, average_rent_per_unit: 0 },
    commercial_units: template.defaultConfig.commercial_units,
    renovation_info: template.defaultConfig.renovation_info || { status: RenovationStatus.NOT_NEEDED },
    equity_structure: template.defaultConfig.equity_structure || { investor_equity_share_pct: 0, self_cash_percentage: 0 },
  });

  // Market defaults hook
  const { data: marketDefaults, loading: loadingDefaults } = useMarketDefaults(formData.msa_code);

  const totalSteps = 5;
  const currentStepNumber = STEP_CONFIG[currentStep].step;
  const progress = (currentStepNumber / totalSteps) * 100;

  const updateFormData = (updates: Partial<SimplifiedPropertyInput>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  };

  const handleAddressChange = (addressData: any) => {
    updateFormData({
      property_address: `${addressData.street}, ${addressData.city}, ${addressData.state} ${addressData.zip_code}`,
      city: addressData.city,
      state: addressData.state,
      msa_code: addressData.msa_code,
    });
  };

  const handleApplyMarketDefaults = () => {
    if (marketDefaults) {
      // Apply market defaults to relevant form fields
      updateFormData({
        // These would typically be applied to financial parameters
        // For now, we'll store them in a market_defaults field
        market_defaults: marketDefaults,
      });
    }
  };

  const canProceedFromStep = (step: FormStep): boolean => {
    switch (step) {
      case 'basic':
        return !!(formData.property_name && formData.property_name.trim() && isAddressValid);
      case 'units':
        const hasResidential = !template.formConfig.showResidentialUnits || 
          !!(formData.residential_units?.total_units && formData.residential_units.total_units > 0);
        const hasCommercial = !template.formConfig.showCommercialUnits || 
          !!(formData.commercial_units?.total_units && formData.commercial_units.total_units > 0);
        return hasResidential && hasCommercial;
      case 'renovation':
        return !!(formData.renovation_info?.anticipated_duration_months && 
                 formData.renovation_info.estimated_cost !== undefined);
      case 'equity':
        return !!(formData.equity_structure?.investor_equity_share_pct && 
                 formData.equity_structure.self_cash_percentage);
      default:
        return true;
    }
  };

  const getNextStep = (step: FormStep): FormStep | null => {
    const steps: FormStep[] = ['basic', 'units', 'renovation', 'equity', 'review'];
    const currentIndex = steps.indexOf(step);
    return currentIndex < steps.length - 1 ? steps[currentIndex + 1] : null;
  };

  const getPreviousStep = (step: FormStep): FormStep | null => {
    const steps: FormStep[] = ['basic', 'units', 'renovation', 'equity', 'review'];
    const currentIndex = steps.indexOf(step);
    return currentIndex > 0 ? steps[currentIndex - 1] : null;
  };

  const handleNext = () => {
    const nextStep = getNextStep(currentStep);
    if (nextStep) {
      setCurrentStep(nextStep);
    }
  };

  const handlePrevious = () => {
    const previousStep = getPreviousStep(currentStep);
    if (previousStep) {
      setCurrentStep(previousStep);
    }
  };

  const handleSubmit = () => {
    if (canProceedFromStep('equity')) {
      onSubmit(formData as SimplifiedPropertyInput);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 'basic':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="property_name">Property Name *</Label>
                <Input
                  id="property_name"
                  value={formData.property_name || ''}
                  onChange={(e) => updateFormData({ property_name: e.target.value })}
                  placeholder="e.g., Sunset Apartments"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="purchase_price">Purchase Price</Label>
                <Input
                  id="purchase_price"
                  type="number"
                  value={formData.purchase_price || ''}
                  onChange={(e) => updateFormData({ purchase_price: e.target.value ? Number(e.target.value) : undefined })}
                  placeholder="2500000"
                />
              </div>
            </div>

            {/* Smart Address Validator */}
            <AddressValidator
              initialAddress={{
                street: formData.property_address?.split(',')[0] || '',
                city: formData.city || '',
                state: formData.state || '',
                zip_code: ''
              }}
              onAddressChange={handleAddressChange}
              onValidationChange={setIsAddressValid}
            />

            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                value={formData.notes || ''}
                onChange={(e) => updateFormData({ notes: e.target.value })}
                placeholder="Additional property details or analysis notes..."
                rows={3}
              />
            </div>
          </div>
        );

      case 'units':
        return (
          <div className="space-y-6">
            {template.formConfig.showResidentialUnits && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Residential Units</CardTitle>
                  <CardDescription>
                    Information about residential rental units
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="res_unit_count">Number of Units *</Label>
                      <Input
                        id="res_unit_count"
                        type="number"
                        value={formData.residential_units?.total_units || ''}
                        onChange={(e) => updateFormData({
                          residential_units: {
                            ...formData.residential_units,
                            total_units: Number(e.target.value),
                            average_rent_per_unit: formData.residential_units?.average_rent_per_unit || 0,
                            average_square_feet_per_unit: formData.residential_units?.average_square_feet_per_unit || 0
                          }
                        })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="res_avg_rent">Avg. Rent per Unit</Label>
                      <Input
                        id="res_avg_rent"
                        type="number"
                        value={formData.residential_units?.average_rent_per_unit || ''}
                        onChange={(e) => updateFormData({
                          residential_units: {
                            ...formData.residential_units,
                            total_units: formData.residential_units?.total_units || 0,
                            average_rent_per_unit: Number(e.target.value),
                            average_square_feet_per_unit: formData.residential_units?.average_square_feet_per_unit || 0
                          }
                        })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="res_avg_sqft">Avg. SqFt per Unit</Label>
                      <Input
                        id="res_avg_sqft"
                        type="number"
                        value={formData.residential_units?.average_square_feet_per_unit || ''}
                        onChange={(e) => updateFormData({
                          residential_units: {
                            ...formData.residential_units,
                            total_units: formData.residential_units?.total_units || 0,
                            average_rent_per_unit: formData.residential_units?.average_rent_per_unit || 0,
                            average_square_feet_per_unit: Number(e.target.value)
                          }
                        })}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {template.formConfig.showCommercialUnits && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Commercial Units</CardTitle>
                  <CardDescription>
                    Information about commercial rental units
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="com_unit_count">Number of Units *</Label>
                      <Input
                        id="com_unit_count"
                        type="number"
                        value={formData.commercial_units?.total_units || ''}
                        onChange={(e) => updateFormData({
                          commercial_units: {
                            ...formData.commercial_units,
                            total_units: Number(e.target.value),
                            average_rent_per_unit: formData.commercial_units?.average_rent_per_unit || 0,
                            average_square_feet_per_unit: formData.commercial_units?.average_square_feet_per_unit || 0
                          }
                        })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="com_avg_rent">Avg. Rent per Unit</Label>
                      <Input
                        id="com_avg_rent"
                        type="number"
                        value={formData.commercial_units?.average_rent_per_unit || ''}
                        onChange={(e) => updateFormData({
                          commercial_units: {
                            ...formData.commercial_units,
                            total_units: formData.commercial_units?.total_units || 0,
                            average_rent_per_unit: Number(e.target.value),
                            average_square_feet_per_unit: formData.commercial_units?.average_square_feet_per_unit || 0
                          }
                        })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="com_avg_sqft">Avg. SqFt per Unit</Label>
                      <Input
                        id="com_avg_sqft"
                        type="number"
                        value={formData.commercial_units?.average_square_feet_per_unit || ''}
                        onChange={(e) => updateFormData({
                          commercial_units: {
                            ...formData.commercial_units,
                            total_units: formData.commercial_units?.total_units || 0,
                            average_rent_per_unit: formData.commercial_units?.average_rent_per_unit || 0,
                            average_square_feet_per_unit: Number(e.target.value)
                          }
                        })}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        );

      case 'renovation':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Renovation Information */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Renovation Information</CardTitle>
                    <CardDescription>
                      Timeline and budget for property improvements
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="renovation_months">Renovation Period (months) *</Label>
                        <Input
                          id="renovation_months"
                          type="number"
                          value={formData.renovation_info?.anticipated_duration_months || ''}
                          onChange={(e) => updateFormData({
                            renovation_info: {
                              ...formData.renovation_info,
                              status: formData.renovation_info?.status || RenovationStatus.PLANNED,
                              anticipated_duration_months: Number(e.target.value),
                              estimated_cost: formData.renovation_info?.estimated_cost || 0
                            }
                          })}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="renovation_budget">Renovation Budget ($) *</Label>
                        <Input
                          id="renovation_budget"
                          type="number"
                          value={formData.renovation_info?.estimated_cost || ''}
                          onChange={(e) => updateFormData({
                            renovation_info: {
                              ...formData.renovation_info,
                              status: formData.renovation_info?.status || RenovationStatus.PLANNED,
                              anticipated_duration_months: formData.renovation_info?.anticipated_duration_months || 0,
                              estimated_cost: Number(e.target.value)
                            }
                          })}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Market Defaults Panel */}
              <div className="lg:col-span-1">
                <MarketDefaultsPanel
                  msaCode={formData.msa_code}
                  msaName={formData.city && formData.state ? `${formData.city}, ${formData.state}` : undefined}
                  marketDefaults={marketDefaults}
                  loading={loadingDefaults}
                  onApplyDefaults={handleApplyMarketDefaults}
                  onRefresh={() => {
                    // Refresh market defaults if needed - hook handles this automatically
                  }}
                />
              </div>
            </div>
          </div>
        );

      case 'equity':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Equity Structure</CardTitle>
                <CardDescription>
                  Investment and financing structure for the property
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="total_equity">Investor Equity Share (%) *</Label>
                    <Input
                      id="total_equity"
                      type="number"
                      step="0.1"
                      value={formData.equity_structure?.investor_equity_share_pct || ''}
                      onChange={(e) => updateFormData({
                        equity_structure: {
                          ...formData.equity_structure,
                          investor_equity_share_pct: Number(e.target.value),
                          self_cash_percentage: formData.equity_structure?.self_cash_percentage || 0
                        }
                      })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="cash_percentage">Self Cash Percentage *</Label>
                    <Input
                      id="cash_percentage"
                      type="number"
                      step="0.1"
                      value={formData.equity_structure?.self_cash_percentage || ''}
                      onChange={(e) => updateFormData({
                        equity_structure: {
                          ...formData.equity_structure,
                          investor_equity_share_pct: formData.equity_structure?.investor_equity_share_pct || 0,
                          self_cash_percentage: Number(e.target.value)
                        }
                      })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 'review':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Review Your Property Information</CardTitle>
                <CardDescription>
                  Please review all details before submitting for analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Property Details</h4>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Name:</span>
                        <span>{formData.property_name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Location:</span>
                        <span>{formData.city}, {formData.state}</span>
                      </div>
                      {formData.purchase_price && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Purchase Price:</span>
                          <span>${formData.purchase_price.toLocaleString()}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Unit Information</h4>
                    <div className="space-y-1">
                      {formData.residential_units && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Residential Units:</span>
                          <span>{formData.residential_units.total_units}</span>
                        </div>
                      )}
                      {formData.commercial_units && (
                        <div className="flex justify-between">
                          <span className="text-gray-500">Commercial Units:</span>
                          <span>{formData.commercial_units.total_units}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Renovation</h4>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Duration:</span>
                        <span>{formData.renovation_info?.anticipated_duration_months} months</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Budget:</span>
                        <span>${formData.renovation_info?.estimated_cost?.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Equity Structure</h4>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Total Equity:</span>
                        <span>{formData.equity_structure?.investor_equity_share_pct}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Cash Portion:</span>
                        <span>{formData.equity_structure?.self_cash_percentage}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  const StepIcon = STEP_CONFIG[currentStep].icon;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm" onClick={onBack}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Templates
          </Button>
          <Badge variant="outline" className="text-sm">
            {template.icon} {template.name}
          </Badge>
        </div>
      </div>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <StepIcon className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">
              {STEP_CONFIG[currentStep].title}
            </h2>
          </div>
          <span className="text-sm text-gray-500">
            Step {currentStepNumber} of {totalSteps}
          </span>
        </div>
        <Progress value={progress} className="w-full" />
      </div>

      {/* Form Content */}
      <Card>
        <CardContent className="p-6">
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentStep === 'basic'}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Previous
        </Button>

        {currentStep === 'review' ? (
          <Button
            onClick={handleSubmit}
            disabled={!canProceedFromStep('equity')}
          >
            Submit for Analysis
          </Button>
        ) : (
          <Button
            onClick={handleNext}
            disabled={!canProceedFromStep(currentStep)}
          >
            Next
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        )}
      </div>
    </div>
  );
}