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

    // Transform frontend data format to backend-compatible format
    const backendCompatibleData = {
      property_id: propertyData.property_id || `prop_${Date.now()}`,
      property_name: propertyData.property_name || 'Unnamed Property',
      analysis_date: propertyData.analysis_date || new Date().toISOString().split('T')[0],
      
      // Ensure residential_units has required fields
      residential_units: {
        total_units: propertyData.residential_units?.total_units || 1,
        average_rent_per_unit: propertyData.residential_units?.average_rent_per_unit || 0,
        average_square_feet_per_unit: propertyData.residential_units?.average_square_feet_per_unit || 1000
      },
      
      // Handle commercial_units (optional)
      commercial_units: propertyData.commercial_units ? {
        total_units: propertyData.commercial_units.total_units || 0,
        average_rent_per_unit: propertyData.commercial_units.average_rent_per_unit || 0,
        average_square_feet_per_unit: propertyData.commercial_units.average_square_feet_per_unit || 1000
      } : undefined,
      
      // Ensure renovation_info has required fields
      renovation_info: {
        status: propertyData.renovation_info?.status || 'planned',
        anticipated_duration_months: propertyData.renovation_info?.anticipated_duration_months || 6,
        estimated_cost: propertyData.renovation_info?.estimated_cost || 0
      },
      
      // Ensure equity_structure has required fields  
      equity_structure: {
        investor_equity_share_pct: propertyData.equity_structure?.investor_equity_share_pct || 25,
        self_cash_percentage: propertyData.equity_structure?.self_cash_percentage || 75
      },
      
      // Extract fields from address for backend compatibility
      city: propertyData.address?.city || 'New York',
      state: propertyData.address?.state || 'NY', 
      msa_code: propertyData.address?.msa_code || '35620', // Default to NYC
      property_address: propertyData.address ? 
        `${propertyData.address.street || '123 Main St'}, ${propertyData.address.city || 'New York'}, ${propertyData.address.state || 'NY'} ${propertyData.address.zip_code || '10001'}` : 
        '123 Main St, New York, NY 10001',
      purchase_price: propertyData.financials?.purchase_price || 500000,
      notes: propertyData.notes || ''
    };

    // Store the property data
    setSubmittedProperty(backendCompatibleData as any);
    
    // Save to local storage as a backup
    try {
      const savedProperties = JSON.parse(localStorage.getItem('savedProperties') || '[]');
      savedProperties.push({
        ...backendCompatibleData,
        savedAt: new Date().toISOString(),
        status: 'submitted'
      });
      localStorage.setItem('savedProperties', JSON.stringify(savedProperties));
      console.log('Property saved to local storage');
    } catch (error) {
      console.warn('Could not save to local storage:', error);
    }
    
    setPageState('success');
    console.log('Property submitted (transformed):', backendCompatibleData);
  };

  const handleStartOver = () => {
    setSelectedTemplate(null);
    setSubmittedProperty(null);
    dcfAnalysis.reset();
    setPageState('template-selection');
  };

  const handleRunAnalysis = async () => {
    if (submittedProperty) {
      console.log('Starting DCF Analysis with data:', JSON.stringify(submittedProperty, null, 2));
      console.log('DCF Analysis hook state before execution:', {
        loading: dcfAnalysis.loading,
        error: dcfAnalysis.error,
        data: dcfAnalysis.data
      });
      
      try {
        await dcfAnalysis.execute(submittedProperty);
        console.log('DCF Analysis completed:', {
          loading: dcfAnalysis.loading,
          error: dcfAnalysis.error,
          data: dcfAnalysis.data
        });
        
        // Update local storage with analysis results
        if (dcfAnalysis.data && dcfAnalysis.data.success && dcfAnalysis.data.data) {
          try {
            const savedProperties = JSON.parse(localStorage.getItem('savedProperties') || '[]');
            const propertyIndex = savedProperties.findIndex((p: any) => p.property_id === submittedProperty.property_id);
            if (propertyIndex >= 0) {
              savedProperties[propertyIndex].status = 'analyzed';
              savedProperties[propertyIndex].analysis_results = dcfAnalysis.data.data;
              savedProperties[propertyIndex].analyzedAt = new Date().toISOString();
              localStorage.setItem('savedProperties', JSON.stringify(savedProperties));
              console.log('Analysis results saved to local storage');
            }
          } catch (error) {
            console.warn('Could not save analysis results to local storage:', error);
          }
        }
      } catch (error) {
        console.error('DCF Analysis failed with error:', error);
      }
    } else {
      console.error('No submitted property data available for DCF analysis');
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

            {/* Success State */}
            {dcfAnalysis.data && dcfAnalysis.data.success && (
              <Card className="border-green-200 bg-green-50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="text-green-600">✅</div>
                      <div>
                        <p className="text-green-800 font-medium">DCF Analysis Complete!</p>
                        <p className="text-green-700 text-sm">
                          NPV: ${dcfAnalysis.data.data?.financial_metrics?.npv?.toLocaleString()} | 
                          IRR: {((dcfAnalysis.data.data?.financial_metrics?.irr || 0) * 100).toFixed(1)}% |
                          Recommendation: {dcfAnalysis.data.data?.investment_recommendation}
                        </p>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => window.open('/analysis', '_blank')}
                    >
                      View Details
                    </Button>
                  </div>
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
                {dcfAnalysis.loading ? 'Analyzing Property...' : 'Run DCF Analysis'}
              </Button>
            </div>

            {/* Real-time status messages */}
            {dcfAnalysis.loading && (
              <Card className="border-blue-200 bg-blue-50">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <p className="text-blue-800 text-sm">
                      Running comprehensive DCF analysis with Monte Carlo simulation...
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
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