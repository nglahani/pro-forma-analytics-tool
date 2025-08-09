/**
 * Accessible Card Component
 * Enhanced card with proper ARIA semantics and keyboard navigation
 */

'use client';

import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { focusRing, aria, keyboard } from '@/lib/accessibility';
import { cn } from '@/lib/utils';

const accessibleCardVariants = cva(
  'rounded-lg border bg-white text-gray-950 shadow-sm transition-colors',
  {
    variants: {
      variant: {
        default: 'border-gray-200',
        elevated: 'border-gray-200 shadow-md',
        interactive: `border-gray-200 hover:shadow-md hover:border-gray-300 cursor-pointer ${focusRing.default}`,
        success: 'border-green-200 bg-green-50',
        warning: 'border-amber-200 bg-amber-50',
        error: 'border-red-200 bg-red-50',
        info: 'border-blue-200 bg-blue-50',
      },
      size: {
        default: 'p-6',
        sm: 'p-4',
        lg: 'p-8',
        none: 'p-0',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface AccessibleCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof accessibleCardVariants> {
  as?: React.ElementType;
  interactive?: boolean;
  heading?: string;
  description?: string;
  onAction?: () => void;
  actionLabel?: string;
}

const AccessibleCard = React.forwardRef<HTMLDivElement, AccessibleCardProps>(
  (
    {
      className,
      variant,
      size,
      as: Component = 'div',
      interactive = false,
      heading,
      description,
      onAction,
      actionLabel,
      children,
      onClick,
      onKeyDown,
      role,
      tabIndex,
      ...props
    },
    ref
  ) => {
    // Generate unique IDs
    const cardId = React.useMemo(
      () => `card-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      []
    );
    const headingId = `${cardId}-heading`;
    const descId = `${cardId}-desc`;

    // Determine if card should be interactive
    const isInteractive = interactive || !!onClick || !!onAction;
    const finalVariant = isInteractive && variant === 'default' ? 'interactive' : variant;

    // Handle keyboard interactions
    const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
      if (isInteractive && (event.key === keyboard.keys.ENTER || event.key === keyboard.keys.SPACE)) {
        event.preventDefault();
        if (onAction) {
          onAction();
        } else if (onClick) {
          onClick(event as any);
        }
      }
      onKeyDown?.(event);
    };

    // Handle clicks
    const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
      if (onAction) {
        onAction();
      } else {
        onClick?.(event);
      }
    };

    // ARIA attributes
    const ariaProps = {
      role: role || (isInteractive ? 'button' : 'article'),
      tabIndex: tabIndex !== undefined ? tabIndex : (isInteractive ? 0 : undefined),
      'aria-labelledby': heading ? headingId : undefined,
      'aria-describedby': description ? descId : undefined,
      'aria-label': actionLabel && !heading ? actionLabel : undefined,
    };

    return (
      <Component
        ref={ref}
        id={cardId}
        className={cn(accessibleCardVariants({ variant: finalVariant, size }), className)}
        onClick={isInteractive ? handleClick : onClick}
        onKeyDown={isInteractive ? handleKeyDown : onKeyDown}
        {...ariaProps}
        {...props}
      >
        {heading && (
          <div className=\"mb-4\">
            <h3 
              id={headingId}
              className=\"text-lg font-semibold leading-tight\"
            >
              {heading}
            </h3>
            {description && (
              <p 
                id={descId}
                className=\"text-sm text-gray-600 mt-1\"
              >
                {description}
              </p>
            )}
          </div>
        )}
        {children}
      </Component>
    );
  }
);

AccessibleCard.displayName = 'AccessibleCard';

// Card Header Component
const AccessibleCardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
));

AccessibleCardHeader.displayName = 'AccessibleCardHeader';

// Card Title Component
export interface AccessibleCardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  level?: 1 | 2 | 3 | 4 | 5 | 6;
}

const AccessibleCardTitle = React.forwardRef<
  HTMLParagraphElement,
  AccessibleCardTitleProps
>(({ className, level = 3, ...props }, ref) => {
  const Heading = `h${level}` as keyof JSX.IntrinsicElements;
  
  return (
    <Heading
      ref={ref}
      className={cn('text-lg font-semibold leading-none tracking-tight', className)}
      {...props}
    />
  );
});

AccessibleCardTitle.displayName = 'AccessibleCardTitle';

// Card Description Component  
const AccessibleCardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-gray-600', className)}
    {...props}
  />
));

AccessibleCardDescription.displayName = 'AccessibleCardDescription';

// Card Content Component
const AccessibleCardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div 
    ref={ref} 
    className={cn('p-6 pt-0', className)} 
    {...props} 
  />
));

AccessibleCardContent.displayName = 'AccessibleCardContent';

// Card Footer Component
const AccessibleCardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
));

AccessibleCardFooter.displayName = 'AccessibleCardFooter';

export {
  AccessibleCard,
  AccessibleCardHeader,
  AccessibleCardTitle,
  AccessibleCardDescription,
  AccessibleCardContent,
  AccessibleCardFooter,
  accessibleCardVariants,
};