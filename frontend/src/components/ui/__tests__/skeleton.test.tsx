/**
 * Tests for Skeleton component
 * Comprehensive coverage for skeleton loading states
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { Skeleton } from '../skeleton';

describe('Skeleton', () => {
  it('renders with default styling', () => {
    render(<Skeleton data-testid="skeleton" />);
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toBeInTheDocument();
    expect(skeleton).toHaveClass('animate-pulse', 'rounded-md', 'bg-muted');
  });

  it('applies custom className', () => {
    render(<Skeleton className="custom-skeleton" data-testid="skeleton" />);
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toHaveClass('custom-skeleton');
    expect(skeleton).toHaveClass('animate-pulse', 'rounded-md', 'bg-muted');
  });

  it('supports custom attributes', () => {
    render(
      <Skeleton 
        id="skeleton-id"
        role="progressbar"
        aria-label="Loading content"
        data-testid="skeleton"
      />
    );
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toHaveAttribute('id', 'skeleton-id');
    expect(skeleton).toHaveAttribute('role', 'progressbar');
    expect(skeleton).toHaveAttribute('aria-label', 'Loading content');
  });

  it('renders with custom dimensions', () => {
    render(
      <Skeleton 
        className="h-4 w-full"
        style={{ height: '16px', width: '100%' }}
        data-testid="skeleton"
      />
    );
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toHaveClass('h-4', 'w-full');
    expect(skeleton).toHaveStyle('height: 16px; width: 100%');
  });

  it('can contain content', () => {
    render(
      <Skeleton data-testid="skeleton">
        <span>Loading text</span>
      </Skeleton>
    );
    
    expect(screen.getByText('Loading text')).toBeInTheDocument();
  });

  it('handles multiple skeleton patterns', () => {
    render(
      <div>
        <Skeleton className="h-4 w-[250px]" data-testid="skeleton-1" />
        <Skeleton className="h-4 w-[200px]" data-testid="skeleton-2" />
        <Skeleton className="h-4 w-[150px]" data-testid="skeleton-3" />
      </div>
    );
    
    expect(screen.getByTestId('skeleton-1')).toHaveClass('h-4', 'w-[250px]');
    expect(screen.getByTestId('skeleton-2')).toHaveClass('h-4', 'w-[200px]');
    expect(screen.getByTestId('skeleton-3')).toHaveClass('h-4', 'w-[150px]');
  });

  it('renders circular skeleton', () => {
    render(
      <Skeleton className="rounded-full h-12 w-12" data-testid="skeleton" />
    );
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toHaveClass('rounded-full', 'h-12', 'w-12');
  });

  it('supports card-like skeleton layout', () => {
    render(
      <div className="space-y-2" data-testid="card-skeleton">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-3/5" />
      </div>
    );
    
    const container = screen.getByTestId('card-skeleton');
    expect(container).toBeInTheDocument();
    
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons).toHaveLength(3);
  });

  it('maintains accessibility for loading states', () => {
    render(
      <Skeleton 
        role="status"
        aria-label="Content is loading"
        data-testid="skeleton"
      />
    );
    
    const skeleton = screen.getByTestId('skeleton');
    expect(skeleton).toHaveAttribute('role', 'status');
    expect(skeleton).toHaveAttribute('aria-label', 'Content is loading');
  });

  it('handles onClick events', () => {
    const handleClick = jest.fn();
    render(<Skeleton onClick={handleClick} data-testid="skeleton" />);
    
    const skeleton = screen.getByTestId('skeleton');
    skeleton.click();
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});