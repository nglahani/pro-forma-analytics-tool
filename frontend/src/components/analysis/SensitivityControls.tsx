/**
 * Sensitivity Analysis Controls Component
 * Interactive controls for configuring Monte Carlo simulation parameters
 */

'use client';

import { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Settings,
  Play,
  RefreshCw,
  Target,
  TrendingUp,
  AlertCircle,
  Info,
  Zap,
  BarChart3,
} from 'lucide-react';
import { textColors } from '@/lib/utils';

export interface SensitivityParameter {
  name: string;
  label: string;
  baseValue: number;
  minValue: number;
  maxValue: number;
  stepSize: number;
  unit: string;
  description: string;
  category: 'market' | 'property' | 'financing';
  importance: 'high' | 'medium' | 'low';
}

export interface SensitivityConfiguration {
  scenarioCount: number;
  correlationStrength: number;
  parameters: Record<string, {
    enabled: boolean;
    variationRange: number; // Percentage variation from base value
    distributionType: 'normal' | 'uniform' | 'triangular';
  }>;
}

interface SensitivityControlsProps {
  parameters: SensitivityParameter[];
  configuration: SensitivityConfiguration;
  onConfigurationChange: (config: SensitivityConfiguration) => void;
  onRunSimulation: (config: SensitivityConfiguration) => void;
  isRunning?: boolean;
  disabled?: boolean;
}

const defaultParameters: SensitivityParameter[] = [
  {
    name: 'interest_rate',
    label: 'Interest Rate',
    baseValue: 6.5,
    minValue: 3.0,
    maxValue: 12.0,
    stepSize: 0.1,
    unit: '%',
    description: 'Mortgage interest rate affecting debt service payments',
    category: 'financing',
    importance: 'high',
  },
  {
    name: 'cap_rate',
    label: 'Cap Rate',
    baseValue: 5.5,
    minValue: 3.0,
    maxValue: 10.0,
    stepSize: 0.1,
    unit: '%',
    description: 'Capitalization rate for terminal value calculation',
    category: 'market',
    importance: 'high',
  },
  {
    name: 'vacancy_rate',
    label: 'Vacancy Rate',
    baseValue: 5.0,
    minValue: 2.0,
    maxValue: 15.0,
    stepSize: 0.5,
    unit: '%',
    description: 'Expected vacancy rate affecting rental income',
    category: 'market',
    importance: 'high',
  },
  {
    name: 'rent_growth_rate',
    label: 'Rent Growth Rate',
    baseValue: 3.0,
    minValue: 0.0,
    maxValue: 8.0,
    stepSize: 0.1,
    unit: '%/year',
    description: 'Annual rental income growth rate',
    category: 'market',
    importance: 'high',
  },
  {
    name: 'expense_growth_rate',
    label: 'Expense Growth Rate',
    baseValue: 2.5,
    minValue: 0.0,
    maxValue: 6.0,
    stepSize: 0.1,
    unit: '%/year',
    description: 'Annual operating expense growth rate',
    category: 'property',
    importance: 'medium',
  },
  {
    name: 'property_growth_rate',
    label: 'Property Appreciation',
    baseValue: 2.5,
    minValue: -2.0,
    maxValue: 8.0,
    stepSize: 0.1,
    unit: '%/year',
    description: 'Annual property value appreciation rate',
    category: 'property',
    importance: 'medium',
  },
  {
    name: 'ltv_ratio',
    label: 'Loan-to-Value Ratio',
    baseValue: 75.0,
    minValue: 50.0,
    maxValue: 90.0,
    stepSize: 1.0,
    unit: '%',
    description: 'Financing percentage of property value',
    category: 'financing',
    importance: 'medium',
  },
  {
    name: 'closing_costs_pct',
    label: 'Closing Costs',
    baseValue: 3.0,
    minValue: 1.5,
    maxValue: 5.0,
    stepSize: 0.1,
    unit: '%',
    description: 'Transaction costs as percentage of property value',
    category: 'property',
    importance: 'low',
  },
];

export function SensitivityControls({
  parameters = defaultParameters,
  configuration,
  onConfigurationChange,
  onRunSimulation,
  isRunning = false,
  disabled = false,
}: SensitivityControlsProps) {
  const [activeTab, setActiveTab] = useState('parameters');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const updateParameter = useCallback(
    (paramName: string, updates: Partial<SensitivityConfiguration['parameters'][string]>) => {
      const newConfig = {
        ...configuration,
        parameters: {
          ...configuration.parameters,
          [paramName]: {
            ...configuration.parameters[paramName],
            ...updates,
          },
        },
      };
      onConfigurationChange(newConfig);
    },
    [configuration, onConfigurationChange]
  );

  const updateGlobalSetting = useCallback(
    (setting: keyof Omit<SensitivityConfiguration, 'parameters'>, value: number) => {
      const newConfig = {
        ...configuration,
        [setting]: value,
      };
      onConfigurationChange(newConfig);
    },
    [configuration, onConfigurationChange]
  );

  const validateConfiguration = useCallback((): string[] => {
    const errors: string[] = [];

    if (configuration.scenarioCount < 10) {
      errors.push('Scenario count should be at least 10 for statistical validity');
    }
    if (configuration.scenarioCount > 10000) {
      errors.push('Scenario count above 10,000 may cause performance issues');
    }

    const enabledParams = Object.entries(configuration.parameters).filter(([_, config]) => config.enabled);
    if (enabledParams.length === 0) {
      errors.push('At least one parameter must be enabled for sensitivity analysis');
    }

    enabledParams.forEach(([paramName, paramConfig]) => {
      if (paramConfig.variationRange <= 0) {
        const param = parameters.find(p => p.name === paramName);
        errors.push(`${param?.label || paramName} variation range must be greater than 0`);
      }
      if (paramConfig.variationRange > 50) {
        const param = parameters.find(p => p.name === paramName);
        errors.push(`${param?.label || paramName} variation range above 50% may be unrealistic`);
      }
    });

    return errors;
  }, [configuration, parameters]);

  const handleRunSimulation = useCallback(() => {
    const errors = validateConfiguration();
    setValidationErrors(errors);

    if (errors.length === 0) {
      onRunSimulation(configuration);
    }
  }, [configuration, onRunSimulation, validateConfiguration]);

  const getParametersByCategory = (category: SensitivityParameter['category']) => {
    return parameters.filter(p => p.category === category);
  };

  const getImportanceColor = (importance: SensitivityParameter['importance']) => {
    switch (importance) {
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'medium':
        return 'text-amber-600 bg-amber-50 border-amber-200';
      case 'low':
        return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  const enabledParametersCount = Object.values(configuration.parameters).filter(p => p.enabled).length;
  const totalVariationImpact = Object.entries(configuration.parameters)
    .filter(([_, config]) => config.enabled)
    .reduce((sum, [paramName, config]) => {
      const param = parameters.find(p => p.name === paramName);
      const importanceWeight = param?.importance === 'high' ? 3 : param?.importance === 'medium' ? 2 : 1;
      return sum + (config.variationRange * importanceWeight);
    }, 0);

  const ParameterControl = ({ parameter }: { parameter: SensitivityParameter }) => {
    const paramConfig = configuration.parameters[parameter.name] || {
      enabled: false,
      variationRange: 10,
      distributionType: 'normal' as const,
    };

    return (
      <Card className={`transition-all ${paramConfig.enabled ? 'ring-2 ring-blue-200 bg-blue-50' : ''}`}>
        <CardContent className="p-4">
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <input
                  type="checkbox"
                  id={`param-${parameter.name}`}
                  checked={paramConfig.enabled}
                  onChange={(e) => updateParameter(parameter.name, { enabled: e.target.checked })}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  disabled={disabled}
                />
                <Label htmlFor={`param-${parameter.name}`} className={`font-medium ${textColors.primary}`}>
                  {parameter.label}
                </Label>
                <Badge variant="outline" className={`text-xs ${getImportanceColor(parameter.importance)}`}>
                  {parameter.importance}
                </Badge>
              </div>
              <p className={`text-xs ${textColors.muted} mb-2`}>
                {parameter.description}
              </p>
              <p className={`text-xs font-mono ${textColors.secondary}`}>
                Base: {parameter.baseValue}{parameter.unit} 
                (Range: {parameter.minValue} - {parameter.maxValue}{parameter.unit})
              </p>
            </div>
          </div>

          {paramConfig.enabled && (
            <div className="space-y-3 pt-3 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <Label htmlFor={`variation-${parameter.name}`} className="text-xs font-medium">
                    Variation Range (±%)
                  </Label>
                  <Input
                    id={`variation-${parameter.name}`}
                    type="number"
                    min="1"
                    max="50"
                    step="1"
                    value={paramConfig.variationRange}
                    onChange={(e) => updateParameter(parameter.name, { variationRange: Number(e.target.value) })}
                    className="text-sm"
                    disabled={disabled}
                  />
                </div>
                <div>
                  <Label htmlFor={`distribution-${parameter.name}`} className="text-xs font-medium">
                    Distribution Type
                  </Label>
                  <select
                    id={`distribution-${parameter.name}`}
                    value={paramConfig.distributionType}
                    onChange={(e) => updateParameter(parameter.name, { distributionType: e.target.value as any })}
                    className="w-full text-sm border border-gray-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={disabled}
                  >
                    <option value="normal">Normal</option>
                    <option value="uniform">Uniform</option>
                    <option value="triangular">Triangular</option>
                  </select>
                </div>
              </div>
              <div className="text-xs text-gray-600">
                Range: {(parameter.baseValue * (1 - paramConfig.variationRange / 100)).toFixed(2)} - {(parameter.baseValue * (1 + paramConfig.variationRange / 100)).toFixed(2)}{parameter.unit}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-xl font-semibold ${textColors.primary} flex items-center`}>
            <Settings className="h-5 w-5 mr-2" />
            Sensitivity Analysis Configuration
          </h2>
          <p className={`text-sm ${textColors.muted} mt-1`}>
            Configure parameters and scenarios for Monte Carlo simulation
          </p>
        </div>
        <Button
          onClick={handleRunSimulation}
          disabled={disabled || isRunning || validationErrors.length > 0}
          className="flex items-center space-x-2"
        >
          {isRunning ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          <span>{isRunning ? 'Running...' : 'Run Simulation'}</span>
        </Button>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Enabled Parameters
                </p>
                <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                  {enabledParametersCount}
                </p>
              </div>
              <Target className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Scenarios
                </p>
                <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                  {configuration.scenarioCount.toLocaleString()}
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
                  Correlation Strength
                </p>
                <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                  {(configuration.correlationStrength * 100).toFixed(0)}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${textColors.muted}`}>
                  Impact Score
                </p>
                <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                  {totalVariationImpact.toFixed(0)}
                </p>
              </div>
              <Zap className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-start space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-medium text-red-900 mb-2">Configuration Issues</h3>
                <ul className="text-sm text-red-800 space-y-1">
                  {validationErrors.map((error, index) => (
                    <li key={index}>• {error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Configuration Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="parameters">Parameters</TabsTrigger>
          <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
          <TabsTrigger value="correlations">Correlations</TabsTrigger>
        </TabsList>

        {/* Parameters Tab */}
        <TabsContent value="parameters" className="space-y-6 mt-6">
          {/* Market Parameters */}
          <div>
            <h3 className={`text-lg font-semibold ${textColors.primary} mb-4 flex items-center`}>
              <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
              Market Parameters
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {getParametersByCategory('market').map(parameter => (
                <ParameterControl key={parameter.name} parameter={parameter} />
              ))}
            </div>
          </div>

          {/* Property Parameters */}
          <div>
            <h3 className={`text-lg font-semibold ${textColors.primary} mb-4 flex items-center`}>
              <Target className="h-5 w-5 mr-2 text-green-600" />
              Property Parameters
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {getParametersByCategory('property').map(parameter => (
                <ParameterControl key={parameter.name} parameter={parameter} />
              ))}
            </div>
          </div>

          {/* Financing Parameters */}
          <div>
            <h3 className={`text-lg font-semibold ${textColors.primary} mb-4 flex items-center`}>
              <BarChart3 className="h-5 w-5 mr-2 text-amber-600" />
              Financing Parameters
            </h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {getParametersByCategory('financing').map(parameter => (
                <ParameterControl key={parameter.name} parameter={parameter} />
              ))}
            </div>
          </div>
        </TabsContent>

        {/* Scenarios Tab */}
        <TabsContent value="scenarios" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Simulation Settings</CardTitle>
              <CardDescription>
                Configure the number of scenarios and simulation parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="scenario-count" className="text-sm font-medium">
                    Number of Scenarios
                  </Label>
                  <Input
                    id="scenario-count"
                    type="number"
                    min="10"
                    max="10000"
                    step="50"
                    value={configuration.scenarioCount}
                    onChange={(e) => updateGlobalSetting('scenarioCount', Number(e.target.value))}
                    disabled={disabled}
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Recommended: 500-1000 for balanced accuracy and performance
                  </p>
                </div>
                <div>
                  <Label htmlFor="correlation-strength" className="text-sm font-medium">
                    Correlation Strength (0-1)
                  </Label>
                  <Input
                    id="correlation-strength"
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={configuration.correlationStrength}
                    onChange={(e) => updateGlobalSetting('correlationStrength', Number(e.target.value))}
                    disabled={disabled}
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Higher values increase parameter correlation effects
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Correlations Tab */}
        <TabsContent value="correlations" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <Info className="h-5 w-5 mr-2 text-blue-600" />
                Parameter Correlations
              </CardTitle>
              <CardDescription>
                Understanding how parameters interact in the simulation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Positive Correlations</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Interest Rate ↔ Cap Rate (credit market conditions)</li>
                    <li>• Rent Growth ↔ Property Appreciation (market demand)</li>
                    <li>• Expense Growth ↔ Inflation (operating cost pressure)</li>
                  </ul>
                </div>
                <div className="p-4 bg-amber-50 rounded-lg">
                  <h4 className="font-medium text-amber-900 mb-2">Negative Correlations</h4>
                  <ul className="text-sm text-amber-800 space-y-1">
                    <li>• Interest Rate ↔ Property Value (financing cost impact)</li>
                    <li>• Vacancy Rate ↔ Rent Growth (supply/demand balance)</li>
                    <li>• Cap Rate ↔ Property Appreciation (yield compression)</li>
                  </ul>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">
                    <strong>Note:</strong> The correlation strength setting (0-1) controls how strongly these 
                    relationships influence the simulation. Higher values create more realistic but potentially 
                    more extreme scenarios.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}