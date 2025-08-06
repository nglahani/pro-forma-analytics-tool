/**
 * Address Input Component with Validation
 * Provides real-time address validation and MSA auto-detection
 */

'use client';

import { useEffect, useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle, AlertCircle, Loader2, MapPin } from 'lucide-react';
import { PropertyAddress } from '@/types/property';
import { useAddressValidation } from '@/hooks/useAddressValidation';
import { textColors } from '@/lib/utils';

interface AddressInputProps {
  address: Partial<PropertyAddress>;
  onChange: (address: Partial<PropertyAddress>) => void;
  onMSADetected?: (msaCode: string, msaInfo: any) => void;
  errors?: {
    street?: string;
    city?: string;
    state?: string;
    zip_code?: string;
  };
}

export function AddressInput({ 
  address, 
  onChange, 
  onMSADetected,
  errors = {} 
}: AddressInputProps) {
  const { isValidating, result, error, validateAddress, clearValidation } = useAddressValidation();
  const [hasTriggeredValidation, setHasTriggeredValidation] = useState(false);

  // Trigger validation when address changes
  useEffect(() => {
    if (address.street || address.city || address.state) {
      setHasTriggeredValidation(true);
      validateAddress(address);
    } else {
      clearValidation();
      setHasTriggeredValidation(false);
    }
  }, [address.street, address.city, address.state, address.zip_code, validateAddress, clearValidation]);

  // Notify parent when MSA is detected
  useEffect(() => {
    if (result?.msa_info && onMSADetected) {
      onMSADetected(result.msa_info.msa_code, result.msa_info);
    }
  }, [result?.msa_info, onMSADetected]);

  const handleFieldChange = (field: keyof PropertyAddress, value: string) => {
    onChange({
      ...address,
      [field]: value,
    });
  };

  const handleSuggestionSelect = (suggestion: PropertyAddress) => {
    onChange(suggestion);
    if (suggestion.msa_code && onMSADetected) {
      onMSADetected(suggestion.msa_code, result?.msa_info);
    }
  };

  const getValidationStatus = () => {
    if (!hasTriggeredValidation) return null;
    if (isValidating) return 'validating';
    if (error) return 'error';
    if (result?.isValid) return 'valid';
    if (result?.suggestions && result.suggestions.length > 0) return 'suggestions';
    return 'invalid';
  };

  const validationStatus = getValidationStatus();

  return (
    <div className="space-y-4">
      {/* Address Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2 space-y-2">
          <Label htmlFor="street" className={textColors.secondary}>
            Street Address *
          </Label>
          <div className="relative">
            <Input
              id="street"
              value={address.street || ''}
              onChange={(e) => handleFieldChange('street', e.target.value)}
              placeholder="123 Main Street"
              className={errors.street ? 'border-red-500 focus:ring-red-500' : ''}
            />
            {validationStatus === 'validating' && (
              <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 animate-spin text-gray-400" />
            )}
          </div>
          {errors.street && (
            <p className="text-sm text-red-600">{errors.street}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="city" className={textColors.secondary}>
            City *
          </Label>
          <Input
            id="city"
            value={address.city || ''}
            onChange={(e) => handleFieldChange('city', e.target.value)}
            placeholder="New York"
            className={errors.city ? 'border-red-500 focus:ring-red-500' : ''}
          />
          {errors.city && (
            <p className="text-sm text-red-600">{errors.city}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="state" className={textColors.secondary}>
            State *
          </Label>
          <Input
            id="state"
            value={address.state || ''}
            onChange={(e) => handleFieldChange('state', e.target.value.toUpperCase())}
            placeholder="NY"
            maxLength={2}
            className={errors.state ? 'border-red-500 focus:ring-red-500' : ''}
          />
          {errors.state && (
            <p className="text-sm text-red-600">{errors.state}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="zip_code" className={textColors.secondary}>
            ZIP Code
          </Label>
          <Input
            id="zip_code"
            value={address.zip_code || ''}
            onChange={(e) => handleFieldChange('zip_code', e.target.value)}
            placeholder="10001"
            maxLength={5}
            className={errors.zip_code ? 'border-red-500 focus:ring-red-500' : ''}
          />
          {errors.zip_code && (
            <p className="text-sm text-red-600">{errors.zip_code}</p>
          )}
        </div>
      </div>

      {/* Validation Status */}
      {hasTriggeredValidation && (
        <div className="space-y-3">
          {validationStatus === 'validating' && (
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Validating address...</span>
            </div>
          )}

          {validationStatus === 'valid' && result?.msa_info && (
            <div className="flex items-start space-x-2 p-3 bg-green-50 border border-green-200 rounded-md">
              <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-green-900">Address Validated</p>
                <div className="flex items-center space-x-2 mt-1">
                  <MapPin className="h-3 w-3 text-green-600" />
                  <span className="text-xs text-green-800">
                    {result.msa_info.name} (MSA: {result.msa_info.msa_code})
                  </span>
                </div>
              </div>
            </div>
          )}

          {validationStatus === 'suggestions' && result?.suggestions && (
            <Card className="border-amber-200 bg-amber-50">
              <CardContent className="p-4">
                <div className="flex items-start space-x-2 mb-3">
                  <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-amber-900">
                      Address suggestions available
                    </p>
                    <p className="text-xs text-amber-800">
                      Click a suggestion to use it
                    </p>
                  </div>
                </div>
                <div className="space-y-2">
                  {result.suggestions.slice(0, 3).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionSelect(suggestion)}
                      className="w-full text-left p-2 text-sm bg-white border border-amber-200 rounded hover:bg-amber-50 transition-colors"
                    >
                      <div className="font-medium text-gray-900">
                        {suggestion.street}
                      </div>
                      <div className="text-gray-600">
                        {suggestion.city}, {suggestion.state} {suggestion.zip_code}
                      </div>
                      {suggestion.msa_code && (
                        <Badge variant="secondary" className="mt-1 text-xs">
                          MSA: {suggestion.msa_code}
                        </Badge>
                      )}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {validationStatus === 'error' && (
            <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-md">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-900">Validation Error</p>
                <p className="text-xs text-red-800">
                  {error || 'Unable to validate address'}
                </p>
              </div>
            </div>
          )}

          {validationStatus === 'invalid' && (
            <div className="flex items-center space-x-2 p-3 bg-gray-50 border border-gray-200 rounded-md">
              <AlertCircle className="h-4 w-4 text-gray-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Address Not Found</p>
                <p className="text-xs text-gray-600">
                  Please check the address details
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}