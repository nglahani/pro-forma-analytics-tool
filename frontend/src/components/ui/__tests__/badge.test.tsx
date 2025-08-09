/**
 * Tests for Badge component
 * Comprehensive coverage for badge variants and styling
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { Badge } from '../badge';

describe('Badge', () => {
  it('renders with default variant', () => {
    render(<Badge>Default badge</Badge>);
    
    const badge = screen.getByText('Default badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-primary');
  });

  it('renders with different variants', () => {
    const variants = ['default', 'secondary', 'destructive', 'outline', 'success', 'warning'] as const;
    
    variants.forEach((variant) => {
      const { unmount } = render(<Badge variant={variant}>{variant} badge</Badge>);
      const badge = screen.getByText(`${variant} badge`);
      expect(badge).toBeInTheDocument();
      unmount();
    });
  });

  it('applies custom className', () => {
    render(<Badge className="custom-badge">Custom badge</Badge>);
    
    const badge = screen.getByText('Custom badge');
    expect(badge).toHaveClass('custom-badge');
  });

  it('renders with custom attributes', () => {
    render(
      <Badge data-testid="badge" role="status" aria-label="Status badge">
        Status
      </Badge>
    );
    
    const badge = screen.getByTestId('badge');
    expect(badge).toHaveAttribute('role', 'status');
    expect(badge).toHaveAttribute('aria-label', 'Status badge');
  });

  it('renders with different content types', () => {
    render(
      <Badge>
        <span>Icon</span>
        Text content
      </Badge>
    );
    
    expect(screen.getByText('Icon')).toBeInTheDocument();
    expect(screen.getByText('Text content')).toBeInTheDocument();
  });
});