/**
 * Property Template Selector Component
 * Allows users to choose from predefined property templates
 */

'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, ArrowRight } from 'lucide-react';
import { PROPERTY_TEMPLATES, PropertyTemplate } from '@/types/propertyTemplates';

interface PropertyTemplateSelectorProps {
  selectedTemplate: PropertyTemplate | null;
  onTemplateSelect: (template: PropertyTemplate) => void;
  onContinue: () => void;
}

export function PropertyTemplateSelector({
  selectedTemplate,
  onTemplateSelect,
  onContinue
}: PropertyTemplateSelectorProps) {
  const [hoveredTemplate, setHoveredTemplate] = useState<string | null>(null);

  const getCategoryColor = (category: PropertyTemplate['category']) => {
    switch (category) {
      case 'residential':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'mixed-use':
        return 'bg-purple-50 border-purple-200 text-purple-800';
      case 'single-family':
        return 'bg-green-50 border-green-200 text-green-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">Choose Property Type</h2>
        <p className="text-gray-600 mt-2">
          Select a template to get started with optimized default values for your property type
        </p>
      </div>

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {PROPERTY_TEMPLATES.map((template) => {
          const isSelected = selectedTemplate?.id === template.id;
          const isHovered = hoveredTemplate === template.id;

          return (
            <Card
              key={template.id}
              className={`cursor-pointer transition-all duration-200 ${
                isSelected
                  ? 'ring-2 ring-blue-500 border-blue-300 shadow-lg'
                  : isHovered
                  ? 'border-gray-300 shadow-md transform scale-[1.02]'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => onTemplateSelect(template)}
              onMouseEnter={() => setHoveredTemplate(template.id)}
              onMouseLeave={() => setHoveredTemplate(null)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-3xl">{template.icon}</div>
                    <div>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <Badge 
                        variant="outline" 
                        className={`mt-1 ${getCategoryColor(template.category)}`}
                      >
                        {template.category.replace('-', ' ')}
                      </Badge>
                    </div>
                  </div>
                  {isSelected && (
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-sm mb-4">
                  {template.description}
                </CardDescription>

                {/* Template Preview */}
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Renovation Period:</span>
                    <span className="font-medium">
                      {template.defaultConfig.renovation_info.anticipated_duration_months} months
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Renovation Budget:</span>
                    <span className="font-medium">
                      ${template.defaultConfig.renovation_info.estimated_cost.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Equity Percentage:</span>
                    <span className="font-medium">
                      {template.defaultConfig.equity_structure.investor_equity_share_pct}%
                    </span>
                  </div>
                  
                  {template.defaultConfig.residential_units && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Avg. Rent/Unit:</span>
                      <span className="font-medium">
                        ${template.defaultConfig.residential_units.average_rent_per_unit.toLocaleString()}
                      </span>
                    </div>
                  )}
                  
                  {template.defaultConfig.commercial_units && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Avg. Rent/Unit:</span>
                      <span className="font-medium">
                        ${template.defaultConfig.commercial_units.average_rent_per_unit.toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Continue Button */}
      {selectedTemplate && (
        <div className="flex justify-center pt-6">
          <Button
            onClick={onContinue}
            size="lg"
            className="flex items-center space-x-2"
          >
            <span>Continue with {selectedTemplate.name}</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      )}

      {/* Custom Template Option */}
      <div className="text-center pt-4 border-t border-gray-200">
        <p className="text-sm text-gray-500 mb-3">
          Don&apos;t see your property type?
        </p>
        <Button 
          variant="outline" 
          onClick={() => {
            // For now, select the first template as a fallback
            onTemplateSelect(PROPERTY_TEMPLATES[0]);
          }}
        >
          Start with Custom Template
        </Button>
      </div>
    </div>
  );
}