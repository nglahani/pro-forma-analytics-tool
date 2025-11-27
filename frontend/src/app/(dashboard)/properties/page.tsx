/**
 * Properties Page - Simplified Storage List
 * Reference list of analyzed properties
 */

'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Building2, Search, ExternalLink, RefreshCw, Plus } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAnalysisHistory } from '@/hooks/useAPI';
import { formatCurrency, formatPercentage, formatTimestamp } from '@/lib/utils/formatters';

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
  const router = useRouter();
  const [properties, setProperties] = useState(mockProperties);
  const [searchQuery, setSearchQuery] = useState('');
  const analysisHistory = useAnalysisHistory();

  // Load properties from localStorage and API
  useEffect(() => {
    const loadProperties = async () => {
      // First, load from localStorage
      try {
        const savedProperties = JSON.parse(localStorage.getItem('savedProperties') || '[]');

        if (savedProperties.length > 0) {
          const localData = savedProperties
            .filter((prop: any) => prop.status === 'analyzed') // Only show analyzed properties
            .map((prop: any, index: number) => ({
              id: prop.property_id || `local_${index}`,
              address: prop.property_address || prop.property_name || 'Unknown Property',
              type: prop.commercial_units?.total_units > 0 ? 'Mixed-Use' : 'Residential',
              units: (prop.residential_units?.total_units || 0) + (prop.commercial_units?.total_units || 0),
              analyzedDate: prop.analyzedAt || prop.savedAt || new Date().toISOString(),
              npv: prop.npv || 0,
              irr: prop.irr || 0,
              equity_multiple: prop.equity_multiple || 0,
              recommendation: prop.recommendation || 'HOLD',
              status: 'Completed',
              rawData: prop, // Store raw data for viewing details
            }));

          setProperties(localData);
        } else {
          setProperties([]);
        }
      } catch (error) {
        console.error('Failed to load from localStorage:', error);
        setProperties([]);
      }

      // Then, try to fetch from API
      try {
        await analysisHistory.execute(20);
      } catch (error) {
        console.warn('Failed to fetch from API, using localStorage only:', error);
      }
    };

    loadProperties();
  }, []);

  // Merge API data with localStorage when API fetch completes
  useEffect(() => {
    if (analysisHistory.data && Array.isArray(analysisHistory.data) && analysisHistory.data.length > 0) {
      console.log('API analysis history received:', analysisHistory.data.length, 'analyses');

      const apiData = analysisHistory.data.map((analysis: any) => ({
        id: analysis.request_id || analysis.property_id,
        address: analysis.property_address || `Property ${analysis.property_id}`,
        type: 'Multifamily',
        units: 0,
        analyzedDate: analysis.analysis_date || analysis.analysis_timestamp,
        npv: analysis.financial_metrics?.npv || 0,
        irr: analysis.financial_metrics?.irr || 0,
        equity_multiple: analysis.financial_metrics?.equity_multiple || 0,
        recommendation: analysis.investment_recommendation || 'HOLD',
        status: 'Completed',
        rawData: analysis,
      }));

      // Merge API data with existing localStorage data, avoiding duplicates
      setProperties(prevProps => {
        const combined = [...prevProps];
        apiData.forEach(apiProp => {
          if (!combined.find(p => p.id === apiProp.id)) {
            combined.push(apiProp);
          }
        });
        return combined;
      });
    }
  }, [analysisHistory.data]);

  // Filter properties based on search query
  const filteredProperties = properties.filter(prop =>
    prop.address.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleRefresh = async () => {
    await analysisHistory.execute(20);
  };

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Properties
            </h1>
            <p className="text-gray-600 mt-1">
              Reference list of previously analyzed properties
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={analysisHistory.loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${analysisHistory.loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button onClick={() => router.push('/property-input')}>
              <Plus className="h-4 w-4 mr-2" />
              Add Property
            </Button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search by address..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Properties List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Analyzed Properties ({filteredProperties.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analysisHistory.loading && properties.length === 0 ? (
              <div className="text-center py-12">
                <Building2 className="mx-auto h-12 w-12 text-gray-400 animate-pulse" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">
                  Loading properties...
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Fetching your analysis history
                </p>
              </div>
            ) : filteredProperties.length === 0 && properties.length === 0 ? (
              <div className="text-center py-12">
                <Building2 className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">
                  No properties analyzed yet
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Properties will appear here after running DCF analysis
                </p>
                <Button
                  className="mt-4"
                  onClick={() => router.push('/property-input')}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Analyze Your First Property
                </Button>
              </div>
            ) : filteredProperties.length === 0 ? (
              <div className="text-center py-12">
                <Search className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-sm font-medium text-gray-900">
                  No properties match your search
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  Try a different search term
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredProperties.map((property) => (
                  <div
                    key={property.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                    onClick={() => console.log('View property:', property.id)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium text-gray-900">
                          {property.address}
                        </h3>
                        <Badge variant="outline">{property.type}</Badge>
                        {property.units > 0 && (
                          <Badge variant="outline">{property.units} units</Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>{formatTimestamp(property.analyzedDate, 'short')}</span>
                        <span>NPV: {formatCurrency(property.npv)}</span>
                        <span>IRR: {formatPercentage(property.irr)}</span>
                        {property.equity_multiple > 0 && (
                          <span>Equity: {property.equity_multiple.toFixed(2)}x</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={property.status === 'Completed' ? 'default' : 'secondary'}
                      >
                        {property.status}
                      </Badge>
                      <Button variant="outline" size="sm" onClick={(e) => {
                        e.stopPropagation();
                        window.open('/analysis', '_blank');
                      }}>
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