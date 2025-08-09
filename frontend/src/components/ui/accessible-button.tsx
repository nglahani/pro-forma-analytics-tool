/**
 * Accessible Button Component
 * Enhanced button with WCAG AA compliance and keyboard navigation
 */

'use client';

import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { focusRing, accessibleColors, keyboard } from '@/lib/accessibility';
import { cn } from '@/lib/utils';

const accessibleButtonVariants = cva(
  `inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors 
   disabled:pointer-events-none disabled:opacity-50 ${focusRing.button}`,
  {
    variants: {
      variant: {
        default: `bg-gray-900 text-gray-50 hover:bg-gray-800 active:bg-gray-700 
                 shadow-sm border border-gray-900`,
        destructive: `bg-red-600 text-white hover:bg-red-700 active:bg-red-800 
                     shadow-sm border border-red-600`,
        outline: `border border-gray-300 bg-white text-gray-900 hover:bg-gray-50 
                  active:bg-gray-100 shadow-sm`,
        secondary: `bg-gray-100 text-gray-900 hover:bg-gray-200 active:bg-gray-300 
                    border border-gray-200`,
        ghost: `text-gray-900 hover:bg-gray-100 active:bg-gray-200`,
        link: `text-blue-600 underline-offset-4 hover:underline active:text-blue-800`,
        success: `bg-green-600 text-white hover:bg-green-700 active:bg-green-800 
                  shadow-sm border border-green-600`,
        warning: `bg-amber-600 text-white hover:bg-amber-700 active:bg-amber-800 
                  shadow-sm border border-amber-600`,
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface AccessibleButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof accessibleButtonVariants> {
  asChild?: boolean;
  loading?: boolean;
  loadingText?: string;
  description?: string;
  shortcut?: string;
}

const AccessibleButton = React.forwardRef<HTMLButtonElement, AccessibleButtonProps>(
  (
    { 
      className, 
      variant, 
      size, 
      asChild = false, 
      loading = false,
      loadingText = 'Loading...',
      description,
      shortcut,
      children,
      disabled,
      ...props 
    }, 
    ref
  ) => {
    const Comp = asChild ? Slot : 'button';
    
    // Generate unique ID for aria-describedby if needed
    const descriptionId = React.useMemo(
      () => description ? `btn-desc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}` : undefined,
      [description]
    );

    const isDisabled = disabled || loading;

    const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
      // Handle keyboard shortcuts
      if (shortcut && event.key === shortcut && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        if (!isDisabled) {
          (event.currentTarget as HTMLButtonElement).click();
        }
      }
      
      // Call original onKeyDown if provided
      props.onKeyDown?.(event);
    };

    return (
      <div className=\"relative inline-flex\">
        <Comp
          className={cn(accessibleButtonVariants({ variant, size, className }))}
          ref={ref}
          disabled={isDisabled}
          aria-disabled={isDisabled}
          aria-describedby={descriptionId}
          aria-busy={loading}
          {...props}
          onKeyDown={handleKeyDown}
        >
          {loading && (
            <svg 
              className=\"animate-spin -ml-1 mr-2 h-4 w-4\" 
              xmlns=\"http://www.w3.org/2000/svg\" 
              fill=\"none\" 
              viewBox=\"0 0 24 24\"
              aria-hidden=\"true\"
            >
              <circle 
                className=\"opacity-25\" 
                cx=\"12\" 
                cy=\"12\" 
                r=\"10\" 
                stroke=\"currentColor\" 
                strokeWidth=\"4\"
              />
              <path 
                className=\"opacity-75\" 
                fill=\"currentColor\" 
                d=\"M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z\"
              />
            </svg>
          )}
          
          <span className={loading ? 'sr-only sm:not-sr-only' : ''}>
            {loading ? loadingText : children}
          </span>
          
          {loading && (
            <span className=\"sr-only\" aria-live=\"polite\">
              {loadingText}
            </span>
          )}
          
          {shortcut && !loading && (
            <span className=\"sr-only\">
              Keyboard shortcut: {shortcut}
            </span>
          )}
        </Comp>
        
        {/* Description tooltip */}
        {description && (
          <div 
            id={descriptionId} 
            className=\"sr-only\"
            role=\"tooltip\"
          >
            {description}
          </div>
        )}
        
        {/* Keyboard shortcut indicator */}
        {shortcut && !loading && (
          <span 
            className=\"absolute -top-2 -right-2 bg-gray-800 text-white text-xs px-1 py-0.5 rounded opacity-0 group-focus:opacity-100 transition-opacity\"
            aria-hidden=\"true\"
          >
            {shortcut}
          </span>
        )}
      </div>
    );
  }
);

AccessibleButton.displayName = 'AccessibleButton';

export { AccessibleButton, accessibleButtonVariants };