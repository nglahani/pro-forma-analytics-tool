/**
 * Batch Property Upload Component
 * CSV upload with validation, preview, and batch processing capabilities
 */

'use client';

import { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  X,
  Download,
  Play,
  Pause,
  RotateCcw,
  Eye,
  FileSpreadsheet,
  AlertTriangle,
  Info,
} from 'lucide-react';
import { SimplifiedPropertyInput } from '@/types/property';
import { textColors } from '@/lib/utils';

export interface BatchUploadError {
  row: number;
  field: string;
  value: any;
  message: string;
  severity: 'error' | 'warning';
}

export interface BatchValidationResult {
  isValid: boolean;
  totalRows: number;
  validRows: number;
  errors: BatchUploadError[];
  warnings: BatchUploadError[];
  properties: SimplifiedPropertyInput[];
}

export interface BatchUploadProgress {
  total: number;
  completed: number;
  current?: string;
  phase: 'uploading' | 'validating' | 'processing' | 'complete' | 'error';
  startTime?: Date;
  estimatedCompletion?: Date;
}

interface BatchUploaderProps {
  onUpload: (properties: SimplifiedPropertyInput[]) => void;
  onValidationComplete?: (result: BatchValidationResult) => void;
  maxFileSize?: number; // in MB
  maxProperties?: number;
  isProcessing?: boolean;
  progress?: BatchUploadProgress;
  className?: string;
}

// Sample CSV template data
const csvTemplate = `property_name,address,city,state,zip_code,purchase_price,down_payment_percentage,loan_terms_years,loan_terms_rate,residential_units,commercial_units,monthly_rent_per_unit,renovation_months,equity_share_percentage,cash_percentage
"Sample Property 1","123 Main St","New York","NY","10001",2500000,25,30,6.5,24,0,4200,6,75,25
"Sample Property 2","456 Oak Ave","Los Angeles","CA","90210",1800000,30,25,6.8,18,2,3800,4,80,20
"Sample Property 3","789 Pine Rd","Chicago","IL","60601",1200000,20,30,6.2,12,0,2800,3,70,30`;

const requiredFields = [
  'property_name',
  'address', 
  'city',
  'state',
  'purchase_price',
  'down_payment_percentage',
  'residential_units',
  'monthly_rent_per_unit'
];

const fieldValidations = {
  purchase_price: { min: 50000, max: 50000000, type: 'currency' },
  down_payment_percentage: { min: 5, max: 50, type: 'percentage' },
  loan_terms_years: { min: 5, max: 40, type: 'integer' },
  loan_terms_rate: { min: 1, max: 15, type: 'percentage' },
  residential_units: { min: 1, max: 1000, type: 'integer' },
  commercial_units: { min: 0, max: 100, type: 'integer' },
  monthly_rent_per_unit: { min: 500, max: 20000, type: 'currency' },
  renovation_months: { min: 0, max: 36, type: 'integer' },
  equity_share_percentage: { min: 50, max: 100, type: 'percentage' },
  cash_percentage: { min: 0, max: 100, type: 'percentage' },
};

export function BatchUploader({
  onUpload,
  onValidationComplete,
  maxFileSize = 10,
  maxProperties = 100,
  isProcessing = false,
  progress,
  className = '',
}: BatchUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [csvData, setCsvData] = useState<any[]>([]);
  const [validationResult, setValidationResult] = useState<BatchValidationResult | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'preview' | 'validation'>('upload');
  const [showAllRows, setShowAllRows] = useState(false);

  // Parse CSV content
  const parseCSV = useCallback((content: string): any[] => {
    const lines = content.trim().split('\n');
    if (lines.length === 0) return [];

    const headers = lines[0].split(',').map(h => h.replace(/['"]/g, '').trim());
    const rows = lines.slice(1).map((line, index) => {
      const values = line.split(',').map(v => v.replace(/['"]/g, '').trim());
      const row: any = { _rowIndex: index + 2 }; // +2 for header and 1-based indexing
      
      headers.forEach((header, i) => {
        row[header] = values[i] || '';
      });
      
      return row;
    });

    return rows;
  }, []);

  // Validate property data
  const validateProperty = useCallback((property: any, rowIndex: number): BatchUploadError[] => {
    const errors: BatchUploadError[] = [];

    // Check required fields
    requiredFields.forEach(field => {
      if (!property[field] || property[field].toString().trim() === '') {
        errors.push({
          row: rowIndex,
          field,
          value: property[field],
          message: `${field} is required`,
          severity: 'error',
        });
      }
    });

    // Validate field formats and ranges
    Object.entries(fieldValidations).forEach(([field, validation]) => {
      const value = property[field];
      if (value === undefined || value === '') return;

      const numValue = parseFloat(value);
      
      if (isNaN(numValue)) {
        errors.push({
          row: rowIndex,
          field,
          value,
          message: `${field} must be a valid number`,
          severity: 'error',
        });
        return;
      }

      if (validation.type === 'integer' && !Number.isInteger(numValue)) {
        errors.push({
          row: rowIndex,
          field,
          value,
          message: `${field} must be a whole number`,
          severity: 'error',
        });
      }

      if (numValue < validation.min) {
        errors.push({
          row: rowIndex,
          field,
          value,
          message: `${field} must be at least ${validation.min}`,
          severity: 'error',
        });
      }

      if (numValue > validation.max) {
        errors.push({
          row: rowIndex,
          field,
          value,
          message: `${field} must not exceed ${validation.max}`,
          severity: 'error',
        });
      }
    });

    // Business logic validations
    const purchasePrice = parseFloat(property.purchase_price || 0);
    const downPayment = parseFloat(property.down_payment_percentage || 0);
    const monthlyRent = parseFloat(property.monthly_rent_per_unit || 0);
    const units = parseInt(property.residential_units || 0);

    // Rent roll validation
    const totalMonthlyRent = monthlyRent * units;
    const annualRent = totalMonthlyRent * 12;
    const rentMultiple = purchasePrice / annualRent;

    if (rentMultiple > 25) {
      errors.push({
        row: rowIndex,
        field: 'monthly_rent_per_unit',
        value: monthlyRent,
        message: `Rent seems low for purchase price (${rentMultiple.toFixed(1)}x rent multiple)`,
        severity: 'warning',
      });
    }

    if (rentMultiple < 8) {
      errors.push({
        row: rowIndex,
        field: 'monthly_rent_per_unit',
        value: monthlyRent,
        message: `Rent seems high for purchase price (${rentMultiple.toFixed(1)}x rent multiple)`,
        severity: 'warning',
      });
    }

    return errors;
  }, []);

  // Validate all uploaded data
  const validateData = useCallback((data: any[]): BatchValidationResult => {
    const allErrors: BatchUploadError[] = [];
    const validProperties: SimplifiedPropertyInput[] = [];

    data.forEach((row, index) => {
      const rowErrors = validateProperty(row, row._rowIndex || index + 2);
      allErrors.push(...rowErrors);

      // If no errors, convert to SimplifiedPropertyInput
      const hasErrors = rowErrors.some(e => e.severity === 'error');
      if (!hasErrors) {
        validProperties.push({
          property_name: row.property_name,
          address: {
            street: row.address,
            city: row.city,
            state: row.state,
            zip_code: row.zip_code,
          },
          purchase_price: parseFloat(row.purchase_price),
          down_payment_percentage: parseFloat(row.down_payment_percentage),
          loan_terms: {
            years: parseInt(row.loan_terms_years || 30),
            rate: parseFloat(row.loan_terms_rate || 6.5),
          },
          residential_units: parseInt(row.residential_units),
          commercial_units: parseInt(row.commercial_units || 0),
          monthly_rent_per_unit: parseFloat(row.monthly_rent_per_unit),
          renovation_months: parseInt(row.renovation_months || 0),
          equity_share_percentage: parseFloat(row.equity_share_percentage || 75),
          cash_percentage: parseFloat(row.cash_percentage || 25),
        });
      }
    });

    const errors = allErrors.filter(e => e.severity === 'error');
    const warnings = allErrors.filter(e => e.severity === 'warning');

    return {
      isValid: errors.length === 0,
      totalRows: data.length,
      validRows: validProperties.length,
      errors,
      warnings,
      properties: validProperties,
    };
  }, [validateProperty]);

  // Handle file upload
  const handleFileUpload = useCallback(async (file: File) => {
    if (file.size > maxFileSize * 1024 * 1024) {
      alert(`File size must be less than ${maxFileSize}MB`);
      return;
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      alert('Please upload a CSV file');
      return;
    }

    try {
      const content = await file.text();
      const parsed = parseCSV(content);
      
      if (parsed.length === 0) {
        alert('CSV file appears to be empty');
        return;
      }

      if (parsed.length > maxProperties) {
        alert(`Maximum ${maxProperties} properties allowed`);
        return;
      }

      setUploadedFile(file);
      setCsvData(parsed);
      
      // Validate immediately
      const result = validateData(parsed);
      setValidationResult(result);
      onValidationComplete?.(result);
      
      setActiveTab('preview');
    } catch (error) {
      console.error('Error parsing CSV:', error);
      alert('Error parsing CSV file. Please check the format.');
    }
  }, [maxFileSize, maxProperties, parseCSV, validateData, onValidationComplete]);

  // Handle drag and drop
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  }, [handleFileUpload]);

  // Handle file input change
  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  }, [handleFileUpload]);

  // Download CSV template
  const downloadTemplate = useCallback(() => {
    const blob = new Blob([csvTemplate], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'property_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  // Start batch processing
  const handleStartProcessing = useCallback(() => {
    if (validationResult && validationResult.isValid && validationResult.properties.length > 0) {
      onUpload(validationResult.properties);
    }
  }, [validationResult, onUpload]);

  // Preview data (limited rows)
  const previewData = useMemo(() => {
    return showAllRows ? csvData : csvData.slice(0, 10);
  }, [csvData, showAllRows]);

  const getErrorsForRow = useCallback((rowIndex: number) => {
    if (!validationResult) return [];
    return validationResult.errors.filter(e => e.row === rowIndex);
  }, [validationResult]);

  const getWarningsForRow = useCallback((rowIndex: number) => {
    if (!validationResult) return [];
    return validationResult.warnings.filter(e => e.row === rowIndex);
  }, [validationResult]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-xl font-semibold ${textColors.primary} flex items-center`}>
            <Upload className="h-5 w-5 mr-2" />
            Batch Property Upload
          </h2>
          <p className={`text-sm ${textColors.muted} mt-1`}>
            Upload multiple properties for batch DCF analysis
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={downloadTemplate}
            className="flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Download Template</span>
          </Button>
        </div>
      </div>

      {/* Progress Indicator */}
      {isProcessing && progress && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Activity className="h-4 w-4 text-blue-600 animate-pulse" />
                <span className="font-medium text-blue-900">
                  {progress.phase === 'processing' ? 'Processing Properties' : 'Uploading'}
                </span>
              </div>
              <span className="text-sm text-blue-700">
                {progress.completed} of {progress.total}
              </span>
            </div>
            
            <Progress 
              value={(progress.completed / progress.total) * 100} 
              className="mb-2"
            />
            
            {progress.current && (
              <p className="text-sm text-blue-700">
                Currently processing: {progress.current}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="upload">Upload</TabsTrigger>
          <TabsTrigger value="preview" disabled={!uploadedFile}>Preview</TabsTrigger>
          <TabsTrigger value="validation" disabled={!validationResult}>Validation</TabsTrigger>
        </TabsList>

        {/* Upload Tab */}
        <TabsContent value="upload" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Upload CSV File</CardTitle>
              <CardDescription>
                Select a CSV file containing property data for batch analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <FileSpreadsheet className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Drop your CSV file here
                </h3>
                <p className="text-gray-600 mb-4">
                  Or click to browse and select a file
                </p>
                
                <div className="space-y-4">
                  <Label htmlFor="file-upload">
                    <Button variant="outline" className="cursor-pointer">
                      <Upload className="h-4 w-4 mr-2" />
                      Select File
                    </Button>
                  </Label>
                  <Input
                    id="file-upload"
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  
                  <div className="text-sm text-gray-500">
                    <p>Maximum file size: {maxFileSize}MB</p>
                    <p>Maximum properties: {maxProperties}</p>
                    <p>Supported format: CSV</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Template Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <Info className="h-5 w-5 mr-2 text-blue-600" />
                CSV Format Requirements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Required Fields</h4>
                  <ul className="text-sm space-y-1">
                    {requiredFields.map(field => (
                      <li key={field} className="flex items-center space-x-2">
                        <CheckCircle className="h-3 w-3 text-green-600" />
                        <span>{field}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-medium mb-3">Optional Fields</h4>
                  <ul className="text-sm space-y-1">
                    <li className="flex items-center space-x-2">
                      <span className="w-3 h-3 rounded-full bg-gray-300" />
                      <span>zip_code</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-3 h-3 rounded-full bg-gray-300" />
                      <span>loan_terms_years</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-3 h-3 rounded-full bg-gray-300" />
                      <span>loan_terms_rate</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-3 h-3 rounded-full bg-gray-300" />
                      <span>commercial_units</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <span className="w-3 h-3 rounded-full bg-gray-300" />
                      <span>renovation_months</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preview Tab */}
        <TabsContent value="preview" className="space-y-6 mt-6">
          {uploadedFile && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg">Data Preview</CardTitle>
                    <CardDescription>
                      {uploadedFile.name} • {csvData.length} properties
                    </CardDescription>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {csvData.length > 10 && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowAllRows(!showAllRows)}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        {showAllRows ? 'Show Less' : 'Show All'}
                      </Button>
                    )}
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setUploadedFile(null);
                        setCsvData([]);
                        setValidationResult(null);
                        setActiveTab('upload');
                      }}
                    >
                      <X className="h-4 w-4 mr-1" />
                      Remove
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Row</TableHead>
                        <TableHead>Property Name</TableHead>
                        <TableHead>Address</TableHead>
                        <TableHead>Purchase Price</TableHead>
                        <TableHead>Units</TableHead>
                        <TableHead>Monthly Rent</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {previewData.map((row, index) => {
                        const rowIndex = row._rowIndex || index + 2;
                        const errors = getErrorsForRow(rowIndex);
                        const warnings = getWarningsForRow(rowIndex);
                        const hasErrors = errors.length > 0;
                        const hasWarnings = warnings.length > 0;
                        
                        return (
                          <TableRow key={index} className={hasErrors ? 'bg-red-50' : hasWarnings ? 'bg-amber-50' : ''}>
                            <TableCell className="font-mono text-xs">{rowIndex}</TableCell>
                            <TableCell className="font-medium">{row.property_name || '-'}</TableCell>
                            <TableCell className="text-sm">
                              {row.address && row.city ? `${row.address}, ${row.city}` : '-'}
                            </TableCell>
                            <TableCell className="font-mono">
                              {row.purchase_price ? `$${parseInt(row.purchase_price).toLocaleString()}` : '-'}
                            </TableCell>
                            <TableCell>{row.residential_units || '-'}</TableCell>
                            <TableCell className="font-mono">
                              {row.monthly_rent_per_unit ? `$${parseInt(row.monthly_rent_per_unit).toLocaleString()}` : '-'}
                            </TableCell>
                            <TableCell>
                              {hasErrors ? (
                                <Badge variant="destructive" className="text-xs">
                                  <AlertCircle className="h-3 w-3 mr-1" />
                                  Error
                                </Badge>
                              ) : hasWarnings ? (
                                <Badge variant="outline" className="text-amber-600 border-amber-300 text-xs">
                                  <AlertTriangle className="h-3 w-3 mr-1" />
                                  Warning
                                </Badge>
                              ) : (
                                <Badge variant="outline" className="text-green-600 border-green-300 text-xs">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  Valid
                                </Badge>
                              )}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
                
                {csvData.length > 10 && !showAllRows && (
                  <div className="text-center mt-4">
                    <p className="text-sm text-gray-600">
                      Showing first 10 of {csvData.length} properties
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Validation Tab */}
        <TabsContent value="validation" className="space-y-6 mt-6">
          {validationResult && (
            <>
              {/* Validation Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`text-sm font-medium ${textColors.muted}`}>
                          Total Properties
                        </p>
                        <p className={`text-2xl font-bold ${textColors.primary} mt-1`}>
                          {validationResult.totalRows}
                        </p>
                      </div>
                      <FileText className="h-8 w-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`text-sm font-medium ${textColors.muted}`}>
                          Valid Properties
                        </p>
                        <p className={`text-2xl font-bold text-green-600 mt-1`}>
                          {validationResult.validRows}
                        </p>
                      </div>
                      <CheckCircle className="h-8 w-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`text-sm font-medium ${textColors.muted}`}>
                          Errors
                        </p>
                        <p className={`text-2xl font-bold text-red-600 mt-1`}>
                          {validationResult.errors.length}
                        </p>
                      </div>
                      <AlertCircle className="h-8 w-8 text-red-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Validation Status */}
              <Card className={`border-2 ${validationResult.isValid ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {validationResult.isValid ? (
                        <CheckCircle className="h-6 w-6 text-green-600" />
                      ) : (
                        <AlertCircle className="h-6 w-6 text-red-600" />
                      )}
                      <div>
                        <h3 className={`font-medium ${validationResult.isValid ? 'text-green-900' : 'text-red-900'}`}>
                          {validationResult.isValid ? 'Ready for Processing' : 'Validation Failed'}
                        </h3>
                        <p className={`text-sm ${validationResult.isValid ? 'text-green-700' : 'text-red-700'}`}>
                          {validationResult.isValid 
                            ? `${validationResult.validRows} properties are ready for batch analysis`
                            : `${validationResult.errors.length} errors must be fixed before processing`
                          }
                        </p>
                      </div>
                    </div>

                    {validationResult.isValid && validationResult.validRows > 0 && (
                      <Button
                        onClick={handleStartProcessing}
                        disabled={isProcessing}
                        className="flex items-center space-x-2"
                      >
                        {isProcessing ? (
                          <Pause className="h-4 w-4" />
                        ) : (
                          <Play className="h-4 w-4" />
                        )}
                        <span>{isProcessing ? 'Processing...' : 'Start Analysis'}</span>
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Error Details */}
              {validationResult.errors.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg text-red-700">
                      Validation Errors ({validationResult.errors.length})
                    </CardTitle>
                    <CardDescription>
                      These errors must be fixed before processing
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {validationResult.errors.map((error, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                          <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <p className="text-sm font-medium text-red-900">
                              Row {error.row}, Field: {error.field}
                            </p>
                            <p className="text-sm text-red-700">{error.message}</p>
                            {error.value && (
                              <p className="text-xs text-red-600 font-mono mt-1">
                                Current value: "{error.value}"
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Warning Details */}
              {validationResult.warnings.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg text-amber-700">
                      Warnings ({validationResult.warnings.length})
                    </CardTitle>
                    <CardDescription>
                      These warnings should be reviewed but won't prevent processing
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {validationResult.warnings.map((warning, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-amber-50 rounded-lg">
                          <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <p className="text-sm font-medium text-amber-900">
                              Row {warning.row}, Field: {warning.field}
                            </p>
                            <p className="text-sm text-amber-700">{warning.message}</p>
                            {warning.value && (
                              <p className="text-xs text-amber-600 font-mono mt-1">
                                Current value: "{warning.value}"
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}