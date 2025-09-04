/**
 * Properties Page - Simplified Storage List
 * Reference list of analyzed properties
 */

'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Building2, Search, ExternalLink } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useEffect, useState } from 'react';
import { apiService } from '@/lib/api/service';

// Mock data for demonstration - replace with actual API call
const mockProperties = [
  {
    id: 1,
    address: '123 Main St, New York, NY 10001',
    type: 'Multifamily',
    units: 24,
    analyzedDate: '2024-01-15',
    npv: 1250000,
    irr: 12.5,
    status: 'Completed'
  },
  {
    id: 2,
    address: '456 Oak Ave, Los Angeles, CA 90210',
    type: 'Commercial', 
    units: 8,
    analyzedDate: '2024-01-10',
    npv: 875000,
    irr: 11.2,
    status: 'Completed'
  },
  {
    id: 3,
    address: '789 Pine Rd, Chicago, IL 60601',
    type: 'Mixed-Use',
    units: 16,
    analyzedDate: '2024-01-08',
    npv: 950000,
    irr: 13.8,
    status: 'Completed'
  }
];

export default function PropertiesPage() {
  const [properties, setProperties] = useState(mockProperties);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch analysis history on component mount
  useEffect(() => {
    const fetchAnalysisHistory = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // First try to get data from local storage
        const savedProperties = JSON.parse(localStorage.getItem('savedProperties') || '[]');
        
        if (savedProperties.length > 0) {
          const localData = savedProperties.map((prop: any, index: number) => ({
            id: prop.property_id || `local_${index}`,
            address: prop.property_address || prop.property_name || 'Unknown Property',
            type: prop.commercial_units ? 'Mixed-Use' : 'Residential',
            units: (prop.residential_units?.total_units || 0) + (prop.commercial_units?.total_units || 0),
            analyzedDate: prop.savedAt ? new Date(prop.savedAt).toLocaleDateString() : new Date().toLocaleDateString(),
            npv: 0, // Will be populated after analysis
            irr: 0.0, // Will be populated after analysis
            status: prop.status === 'analyzed' ? 'Completed' : 'Saved'
          }));
          setProperties([...localData, ...mockProperties]);
        } else {
          console.log('No saved properties in local storage');
        }

        // Also try to fetch from API
        const response = await apiService.getAnalysisHistory(20);
        if (response.success && response.data && response.data.length > 0) {
          const transformedData = response.data.map((analysis: any) => ({
            id: analysis.analysis_id || analysis.property_id,
            address: analysis.property_address || `Property ${analysis.property_id}`,
            type: analysis.property_type || 'Multifamily',
            units: analysis.total_units || 0,
            analyzedDate: analysis.analysis_date ? new Date(analysis.analysis_date).toLocaleDateString() : 'Unknown',
            npv: Math.round(analysis.npv || 0),
            irr: analysis.irr ? parseFloat((analysis.irr * 100).toFixed(1)) : 0.0,
            status: 'Completed'
          }));
          
          // Merge with local storage data, avoiding duplicates
          setProperties(prevProps => {
            const combined = [...prevProps];
            transformedData.forEach(apiProp => {
              if (!combined.find(p => p.id === apiProp.id)) {
                combined.push(apiProp);
              }
            });
            return combined;
          });
        }
      } catch (err) {
        console.log('Error fetching analysis history, using available data:', err);
        // Don't overwrite existing properties on error
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysisHistory();
  }, []);

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">
            Properties
          </h1>
          <p className="text-gray-600 mt-1">
            Reference list of previously analyzed properties
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search by address..."
              className="pl-10"
            />
          </div>
        </div>

        {/* Properties List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Analyzed Properties ({properties.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-12">
                <Building2 className="mx-auto h-12 w-12 text-gray-400 animate-pulse" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">
                  Loading properties...
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Fetching your analysis history
                </p>
              </div>
            ) : properties.length === 0 ? (
              <div className="text-center py-12">
                <Building2 className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">
                  No properties analyzed yet
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Properties will appear here after running DCF analysis
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {properties.map((property) => (
                  <div
                    key={property.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium text-gray-900">
                          {property.address}
                        </h3>
                        <Badge variant="outline">{property.type}</Badge>
                        <Badge variant="outline">{property.units} units</Badge>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>Analyzed: {property.analyzedDate}</span>
                        <span>NPV: ${property.npv.toLocaleString()}</span>
                        <span>IRR: {property.irr}%</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant={property.status === 'Completed' ? 'success' : 'warning'}
                      >
                        {property.status}
                      </Badge>
                      <Button variant="outline" size="sm">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}