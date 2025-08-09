/**
 * Accessible Input Component
 * Enhanced input with WCAG AA compliance, validation, and screen reader support
 */

'use client';

import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { focusRing, aria, validationMessages, accessibleColors } from '@/lib/accessibility';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

const accessibleInputVariants = cva(
  `flex w-full rounded-md border px-3 py-2 text-sm placeholder:text-gray-400 
   disabled:cursor-not-allowed disabled:opacity-50 transition-colors ${focusRing.input}`,
  {
    variants: {
      variant: {
        default: 'border-gray-300 bg-white hover:border-gray-400',
        error: 'border-red-500 bg-red-50 text-red-900 placeholder:text-red-400',
        success: 'border-green-500 bg-green-50 text-green-900',
        warning: 'border-amber-500 bg-amber-50 text-amber-900',
      },
      inputSize: {
        default: 'h-10',
        sm: 'h-9 px-2 text-xs',
        lg: 'h-12 px-4',
      },
    },
    defaultVariants: {
      variant: 'default',
      inputSize: 'default',
    },
  }
);

export interface AccessibleInputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof accessibleInputVariants> {
  label?: string;
  error?: string;
  success?: string;
  warning?: string;
  hint?: string;
  required?: boolean;
  showValidation?: boolean;
  validationRules?: {
    required?: boolean;
    min?: number;
    max?: number;
    pattern?: RegExp;
    minLength?: number;
    maxLength?: number;
    custom?: (value: string) => string | null;
  };
  onValidation?: (isValid: boolean, message?: string) => void;
}

const AccessibleInput = React.forwardRef<HTMLInputElement, AccessibleInputProps>(
  (
    {
      className,
      variant,
      inputSize,
      label,
      error,
      success,
      warning,
      hint,
      required = false,
      showValidation = true,
      validationRules,
      onValidation,
      id,
      value,
      onChange,
      onBlur,
      ...props
    },
    ref
  ) => {
    const [internalError, setInternalError] = React.useState<string>('');
    const [touched, setTouched] = React.useState(false);
    
    // Generate unique IDs
    const inputId = id || React.useMemo(() => `input-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`, []);
    const errorId = `${inputId}-error`;
    const hintId = `${inputId}-hint`;
    const labelId = `${inputId}-label`;

    // Validation function
    const validateValue = React.useCallback((val: string) => {
      if (!validationRules) return null;

      if (validationRules.required && !val.trim()) {
        return validationMessages.required(label || 'This field');
      }

      if (validationRules.minLength && val.length < validationRules.minLength) {
        return validationMessages.invalid(label || 'This field', `at least ${validationRules.minLength} characters`);
      }

      if (validationRules.maxLength && val.length > validationRules.maxLength) {
        return validationMessages.invalid(label || 'This field', `no more than ${validationRules.maxLength} characters`);
      }

      if (validationRules.pattern && !validationRules.pattern.test(val)) {
        return validationMessages.format(label || 'This field', 'the correct format');
      }

      if (validationRules.min !== undefined && props.type === 'number') {
        const numVal = parseFloat(val);
        if (!isNaN(numVal) && numVal < validationRules.min) {
          return validationMessages.range(label || 'This field', validationRules.min);
        }
      }

      if (validationRules.max !== undefined && props.type === 'number') {
        const numVal = parseFloat(val);
        if (!isNaN(numVal) && numVal > validationRules.max) {
          return validationMessages.range(label || 'This field', undefined, validationRules.max);
        }
      }

      if (validationRules.custom) {
        return validationRules.custom(val);
      }

      return null;
    }, [validationRules, label, props.type]);

    // Handle validation
    React.useEffect(() => {
      if (!showValidation || !touched || !value) return;
      
      const errorMessage = validateValue(value as string);
      setInternalError(errorMessage || '');
      onValidation?.(errorMessage === null, errorMessage || undefined);
    }, [value, validateValue, showValidation, touched, onValidation]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e);
      if (touched) {
        const errorMessage = validateValue(e.target.value);
        setInternalError(errorMessage || '');
        onValidation?.(errorMessage === null, errorMessage || undefined);
      }
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setTouched(true);
      onBlur?.(e);
      
      if (showValidation) {
        const errorMessage = validateValue(e.target.value);
        setInternalError(errorMessage || '');
        onValidation?.(errorMessage === null, errorMessage || undefined);
      }
    };

    // Determine current status
    const currentError = error || internalError;
    const currentVariant = currentError ? 'error' : success ? 'success' : warning ? 'warning' : variant;

    // ARIA attributes
    const ariaDescribedBy = [
      currentError ? errorId : null,
      success && !currentError ? `${inputId}-success` : null,
      warning && !currentError && !success ? `${inputId}-warning` : null,
      hint ? hintId : null,
    ].filter(Boolean).join(' ') || undefined;

    const StatusIcon = currentError ? AlertCircle : success ? CheckCircle : warning ? Info : null;

    return (
      <div className=\"space-y-2\">
        {/* Label */}
        {label && (
          <label 
            id={labelId}
            htmlFor={inputId}
            className={`block text-sm font-medium ${
              currentError ? 'text-red-700' : success ? 'text-green-700' : 'text-gray-700'
            }`}
          >
            {label}
            {required && (
              <span className=\"text-red-500 ml-1\" aria-label=\"required\">
                *
              </span>
            )}
          </label>
        )}

        {/* Input container */}
        <div className=\"relative\">
          <input
            ref={ref}
            id={inputId}
            className={cn(accessibleInputVariants({ variant: currentVariant, inputSize }), className)}
            {...aria.validation.required(required)}
            {...aria.validation.invalid(!!currentError)}
            aria-describedby={ariaDescribedBy}
            aria-labelledby={label ? labelId : undefined}
            value={value}
            onChange={handleChange}
            onBlur={handleBlur}
            {...props}
          />

          {/* Status icon */}
          {StatusIcon && (
            <div className=\"absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none\">
              <StatusIcon 
                className={`h-4 w-4 ${
                  currentError ? 'text-red-500' : 
                  success ? 'text-green-500' : 
                  'text-amber-500'
                }`}
                aria-hidden=\"true\"
              />
            </div>
          )}
        </div>

        {/* Messages */}
        <div className=\"space-y-1\">
          {/* Error message */}
          {currentError && (
            <p 
              id={errorId} 
              className=\"text-sm text-red-700 flex items-start gap-2\" 
              role=\"alert\"
              aria-live=\"polite\"
            >
              <AlertCircle className=\"h-4 w-4 mt-0.5 flex-shrink-0\" aria-hidden=\"true\" />
              {currentError}
            </p>
          )}

          {/* Success message */}
          {success && !currentError && (
            <p 
              id={`${inputId}-success`} 
              className=\"text-sm text-green-700 flex items-start gap-2\"
              role=\"status\"
            >
              <CheckCircle className=\"h-4 w-4 mt-0.5 flex-shrink-0\" aria-hidden=\"true\" />
              {success}
            </p>
          )}

          {/* Warning message */}
          {warning && !currentError && !success && (
            <p 
              id={`${inputId}-warning`} 
              className=\"text-sm text-amber-700 flex items-start gap-2\"
              role=\"alert\"
            >
              <Info className=\"h-4 w-4 mt-0.5 flex-shrink-0\" aria-hidden=\"true\" />
              {warning}
            </p>
          )}

          {/* Hint text */}
          {hint && !currentError && !success && !warning && (
            <p 
              id={hintId} 
              className=\"text-sm text-gray-500\"
            >
              {hint}
            </p>
          )}
        </div>
      </div>
    );
  }
);

AccessibleInput.displayName = 'AccessibleInput';

export { AccessibleInput, accessibleInputVariants };