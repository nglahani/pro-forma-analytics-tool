/**
 * Property Input Page
 * Template selection and multi-step property input form
 */

'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PropertyTemplateSelector } from '@/components/property/PropertyTemplateSelector';
import { PropertyInputForm } from '@/components/property/PropertyInputForm';
import { PropertyTemplate } from '@/types/propertyTemplates';
import { SimplifiedPropertyInput } from '@/types/property';
import { useDCFAnalysis } from '@/hooks/useAPI';
import { apiService } from '@/lib/api/service';

type PageState = 'template-selection' | 'property-form' | 'success';

export default function PropertyInputPage() {
  const [pageState, setPageState] = useState<PageState>('template-selection');
  const [selectedTemplate, setSelectedTemplate] = useState<PropertyTemplate | null>(null);
  const [submittedProperty, setSubmittedProperty] = useState<SimplifiedPropertyInput | null>(null);
  const dcfAnalysis = useDCFAnalysis();

  const handleTemplateSelect = (template: PropertyTemplate) => {
    setSelectedTemplate(template);
  };

  const handleTemplateContinue = () => {
    if (selectedTemplate) {
      setPageState('property-form');
    }
  };

  const handleFormBack = () => {
    setPageState('template-selection');
  };

  const handleFormSubmit = async (propertyData: SimplifiedPropertyInput) => {
    // Auto-derive MSA code if city and state are provided
    const city = propertyData.address?.city;
    const state = propertyData.address?.state;
    if (city && state && !propertyData.address?.msa_code) {
      const msaCode = apiService.getMSAFromCity(city, state);
      if (msaCode && propertyData.address) {
        propertyData.address.msa_code = msaCode;
      }
    }

    setSubmittedProperty(propertyData);
    setPageState('success');
    console.log('Property submitted:', propertyData);
    
    // Optionally run DCF analysis immediately
    // This will be available for the user to trigger manually from the success screen
  };

  const handleStartOver = () => {
    setSelectedTemplate(null);
    setSubmittedProperty(null);
    dcfAnalysis.reset();
    setPageState('template-selection');
  };

  const handleRunAnalysis = async () => {
    if (submittedProperty) {
      await dcfAnalysis.execute(submittedProperty);
    }
  };

  const renderPageContent = () => {
    switch (pageState) {
      case 'template-selection':
        return (
          <PropertyTemplateSelector
            selectedTemplate={selectedTemplate}
            onTemplateSelect={handleTemplateSelect}
            onContinue={handleTemplateContinue}
          />
        );

      case 'property-form':
        return selectedTemplate ? (
          <PropertyInputForm
            template={selectedTemplate}
            onBack={handleFormBack}
            onSubmit={handleFormSubmit}
          />
        ) : null;

      case 'success':
        return (
          <div className="max-w-2xl mx-auto text-center space-y-6">
            <div className="text-6xl">🎉</div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Property Successfully Submitted!
              </h2>
              <p className="text-gray-600">
                Your property &quot;{submittedProperty?.property_name}&quot; has been saved and is ready for analysis.
              </p>
            </div>

            <Card>
              <CardContent className="p-6">
                <div className="text-left space-y-3">
                  <h3 className="font-semibold text-gray-900">What&apos;s Next?</h3>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-center">
                      <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs flex items-center justify-center mr-3">1</span>
                      Run DCF Analysis to get NPV and IRR calculations
                    </li>
                    <li className="flex items-center">
                      <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs flex items-center justify-center mr-3">2</span>
                      Execute Monte Carlo simulation for risk assessment
                    </li>
                    <li className="flex items-center">
                      <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs flex items-center justify-center mr-3">3</span>
                      View market data and forecasts for your property location
                    </li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* DCF Analysis Results */}
            {dcfAnalysis.data && (
              <Card className="border-green-200 bg-green-50">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-green-900 mb-4">
                    DCF Analysis Results
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-green-600 font-medium">NPV</p>
                      <p className="text-green-900 text-lg font-bold">
                        ${dcfAnalysis.data.npv.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-green-600 font-medium">IRR</p>
                      <p className="text-green-900 text-lg font-bold">
                        {(dcfAnalysis.data.irr * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-green-600 font-medium">Equity Multiple</p>
                      <p className="text-green-900 text-lg font-bold">
                        {dcfAnalysis.data.equity_multiple.toFixed(2)}x
                      </p>
                    </div>
                    <div>
                      <p className="text-green-600 font-medium">Recommendation</p>
                      <p className="text-green-900 text-lg font-bold">
                        {dcfAnalysis.data.investment_recommendation.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Analysis Error */}
            {dcfAnalysis.error && (
              <Card className="border-red-200 bg-red-50">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-red-900 mb-2">
                    Analysis Error
                  </h3>
                  <p className="text-red-700 text-sm">
                    {dcfAnalysis.error}
                  </p>
                </CardContent>
              </Card>
            )}

            <div className="flex space-x-4 justify-center">
              <Button variant="outline" onClick={handleStartOver}>
                Add Another Property
              </Button>
              <Button
                onClick={handleRunAnalysis}
                disabled={dcfAnalysis.loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {dcfAnalysis.loading ? 'Analyzing...' : 'Run DCF Analysis'}
              </Button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header - only show on template selection */}
        {pageState === 'template-selection' && (
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Add New Property</h1>
            <p className="text-gray-600 mt-2">
              Start by selecting a property template, then enter your property details for analysis
            </p>
          </div>
        )}

        {/* Page Content */}
        {renderPageContent()}
      </div>
    </div>
  );
}