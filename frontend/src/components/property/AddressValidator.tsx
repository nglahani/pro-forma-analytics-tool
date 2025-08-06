/**
 * AddressValidator Component
 * 
 * Provides real-time address validation and MSA auto-detection
 * for property input forms with smart suggestions and error handling.
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { 
  MapPin, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  Search,
  X
} from 'lucide-react';
import { apiService } from '@/lib/api/service';
import { debounce } from '@/lib/utils';

interface AddressData {
  street: string;
  city: string;
  state: string;
  zip_code: string;
}

interface AddressValidationResult {
  is_valid: boolean;
  formatted_address?: string;
  msa_code?: string;
  msa_name?: string;
  suggestions?: string[];
  error_message?: string;
}

interface AddressValidatorProps {
  initialAddress?: Partial<AddressData>;
  onAddressChange: (address: AddressData & { msa_code?: string; msa_name?: string }) => void;
  onValidationChange: (isValid: boolean) => void;
  className?: string;
}

export function AddressValidator({
  initialAddress,
  onAddressChange,
  onValidationChange,
  className = ''
}: AddressValidatorProps) {
  const [address, setAddress] = useState<AddressData>({
    street: initialAddress?.street || '',
    city: initialAddress?.city || '',
    state: initialAddress?.state || '',
    zip_code: initialAddress?.zip_code || '',
  });

  const [validation, setValidation] = useState<AddressValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [hasUserInput, setHasUserInput] = useState(false);

  // MSA mapping for supported markets
  const supportedMSAs = apiService.getSupportedMSAs();
  
  const validateAddress = useCallback(
    debounce(async (addressData: AddressData) => {
      if (!addressData.street.trim() || !addressData.city.trim() || !addressData.state.trim()) {
        setValidation(null);
        onValidationChange(false);
        return;
      }

      setIsValidating(true);
      
      try {
        // First try API validation if available
        const result = await apiService.validateAddress(addressData);
        
        if (result.success && result.data) {
          const validationResult: AddressValidationResult = {
            is_valid: result.data.is_valid,
            formatted_address: result.data.formatted_address,
            msa_code: result.data.msa_code,
            msa_name: result.data.msa_name,
            suggestions: result.data.suggestions,
          };
          
          setValidation(validationResult);
          onValidationChange(validationResult.is_valid);
          
          if (validationResult.is_valid) {
            onAddressChange({
              ...addressData,
              msa_code: validationResult.msa_code,
              msa_name: validationResult.msa_name,
            });
          }
        } else {
          // Fallback to client-side MSA detection
          performClientSideValidation(addressData);
        }
      } catch (error) {
        // Fallback to client-side MSA detection
        performClientSideValidation(addressData);
      } finally {
        setIsValidating(false);
      }
    }, 500),
    [onAddressChange, onValidationChange]
  );

  const performClientSideValidation = (addressData: AddressData) => {
    const msaCode = apiService.getMSAFromCity(addressData.city, addressData.state);
    const msa = supportedMSAs.find(m => m.code === msaCode);
    
    if (msa) {
      const validationResult: AddressValidationResult = {
        is_valid: true,
        formatted_address: `${addressData.street}, ${addressData.city}, ${addressData.state} ${addressData.zip_code}`,
        msa_code: msa.code,
        msa_name: msa.name,
      };
      
      setValidation(validationResult);
      onValidationChange(true);
      onAddressChange({
        ...addressData,
        msa_code: msa.code,
        msa_name: msa.name,
      });
    } else {
      // Check for similar cities in supported MSAs
      const suggestions = supportedMSAs
        .filter(msa => 
          msa.city.toLowerCase().includes(addressData.city.toLowerCase()) ||
          addressData.city.toLowerCase().includes(msa.city.toLowerCase())
        )
        .map(msa => `${msa.city}, ${msa.state}`)
        .slice(0, 3);

      const validationResult: AddressValidationResult = {
        is_valid: false,
        error_message: suggestions.length > 0 
          ? `City not in supported markets. Did you mean one of these?`
          : `City not in supported markets: ${supportedMSAs.map(m => `${m.city}, ${m.state}`).join(', ')}`,
        suggestions,
      };
      
      setValidation(validationResult);
      onValidationChange(false);
      setShowSuggestions(suggestions.length > 0);
    }
  };

  const handleAddressFieldChange = (field: keyof AddressData, value: string) => {
    const newAddress = { ...address, [field]: value };
    setAddress(newAddress);
    setHasUserInput(true);
    
    // Clear previous validation state
    if (validation && !validation.is_valid) {
      setValidation(null);
      setShowSuggestions(false);
    }
    
    // Trigger validation
    validateAddress(newAddress);
  };

  const applySuggestion = (suggestion: string) => {
    const [city, state] = suggestion.split(', ');
    const newAddress = { ...address, city: city.trim(), state: state.trim() };
    setAddress(newAddress);
    setShowSuggestions(false);
    validateAddress(newAddress);
  };

  const getValidationStatus = () => {
    if (isValidating) return 'validating';
    if (!hasUserInput || !validation) return 'neutral';
    return validation.is_valid ? 'valid' : 'invalid';
  };

  const getStatusIcon = () => {
    const status = getValidationStatus();
    switch (status) {
      case 'validating':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'valid':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'invalid':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <MapPin className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    const status = getValidationStatus();
    switch (status) {
      case 'validating':
        return 'border-blue-300 bg-blue-50';
      case 'valid':
        return 'border-green-300 bg-green-50';
      case 'invalid':
        return 'border-red-300 bg-red-50';
      default:
        return 'border-gray-200';
    }
  };

  useEffect(() => {
    if (initialAddress) {
      const initialAddr = {
        street: initialAddress.street || '',
        city: initialAddress.city || '',
        state: initialAddress.state || '',
        zip_code: initialAddress.zip_code || '',
      };
      setAddress(initialAddr);
      if (initialAddr.city && initialAddr.state) {
        validateAddress(initialAddr);
      }
    }
  }, [initialAddress, validateAddress]);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Address Input Fields */}
      <Card className={`${getStatusColor()} transition-colors duration-200`}>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-4">
            {getStatusIcon()}
            <Label className="text-sm font-medium">Property Address</Label>
            {validation?.is_valid && validation.msa_name && (
              <Badge variant="secondary" className="text-xs">
                {validation.msa_name}
              </Badge>
            )}
          </div>

          <div className="grid grid-cols-1 gap-4">
            {/* Street Address */}
            <div>
              <Label htmlFor="street" className="text-sm text-gray-600">
                Street Address
              </Label>
              <Input
                id="street"
                value={address.street}
                onChange={(e) => handleAddressFieldChange('street', e.target.value)}
                placeholder="123 Main Street"
                className="mt-1"
              />
            </div>

            {/* City, State, ZIP in a row */}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label htmlFor="city" className="text-sm text-gray-600">
                  City
                </Label>
                <Input
                  id="city"
                  value={address.city}
                  onChange={(e) => handleAddressFieldChange('city', e.target.value)}
                  placeholder="New York"
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="state" className="text-sm text-gray-600">
                  State
                </Label>
                <Input
                  id="state"
                  value={address.state}
                  onChange={(e) => handleAddressFieldChange('state', e.target.value.toUpperCase())}
                  placeholder="NY"
                  maxLength={2}
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="zip" className="text-sm text-gray-600">
                  ZIP Code
                </Label>
                <Input
                  id="zip"
                  value={address.zip_code}
                  onChange={(e) => handleAddressFieldChange('zip_code', e.target.value)}
                  placeholder="10001"
                  className="mt-1"
                />
              </div>
            </div>
          </div>

          {/* Validation Messages */}
          {validation && (
            <div className="mt-3 text-sm">
              {validation.is_valid ? (
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-4 w-4" />
                  <span>
                    Address validated • Market: {validation.msa_name}
                  </span>
                </div>
              ) : (
                <div className="text-red-700">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" />
                    <span>{validation.error_message}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Address Suggestions */}
      {showSuggestions && validation?.suggestions && validation.suggestions.length > 0 && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Search className="h-4 w-4 text-blue-600" />
                <Label className="text-sm font-medium text-blue-800">
                  Suggested Locations
                </Label>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSuggestions(false)}
                className="h-6 w-6 p-0 text-blue-600 hover:text-blue-800"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="space-y-2">
              {validation.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => applySuggestion(suggestion)}
                  className="w-full justify-start text-left border-blue-200 hover:bg-blue-100"
                >
                  <MapPin className="h-3 w-3 mr-2" />
                  {suggestion}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Supported Markets Reference */}
      {!validation?.is_valid && hasUserInput && (
        <Card className="border-gray-200">
          <CardContent className="p-4">
            <Label className="text-sm font-medium text-gray-700 mb-2 block">
              Supported Markets
            </Label>
            <div className="flex flex-wrap gap-2">
              {supportedMSAs.map((msa) => (
                <Badge 
                  key={msa.code} 
                  variant="outline" 
                  className="text-xs cursor-pointer hover:bg-gray-100"
                  onClick={() => {
                    setAddress(prev => ({ ...prev, city: msa.city, state: msa.state }));
                    validateAddress({ ...address, city: msa.city, state: msa.state });
                  }}
                >
                  {msa.city}, {msa.state}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}