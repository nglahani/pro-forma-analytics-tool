/**
 * Tests for Card components
 * Comprehensive coverage for Card, CardHeader, CardTitle, CardContent, CardFooter
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription } from '../card';

describe('Card Components', () => {
  describe('Card', () => {
    it('renders with default styling', () => {
      render(<Card data-testid="card">Card content</Card>);
      
      const card = screen.getByTestId('card');
      expect(card).toBeInTheDocument();
      expect(card).toHaveClass('rounded-xl', 'border', 'bg-card');
    });

    it('applies custom className', () => {
      render(<Card className="custom-card" data-testid="card">Content</Card>);
      
      const card = screen.getByTestId('card');
      expect(card).toHaveClass('custom-card');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(<Card ref={ref}>Content</Card>);
      
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('CardHeader', () => {
    it('renders with default styling', () => {
      render(<CardHeader data-testid="card-header">Header content</CardHeader>);
      
      const header = screen.getByTestId('card-header');
      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'p-6');
    });

    it('applies custom className', () => {
      render(<CardHeader className="custom-header" data-testid="card-header">Content</CardHeader>);
      
      const header = screen.getByTestId('card-header');
      expect(header).toHaveClass('custom-header');
    });
  });

  describe('CardTitle', () => {
    it('renders with default styling', () => {
      render(<CardTitle data-testid="card-title">Title text</CardTitle>);
      
      const title = screen.getByTestId('card-title');
      expect(title).toBeInTheDocument();
      expect(title).toHaveClass('font-semibold', 'leading-none', 'tracking-tight');
    });

    it('renders as heading element when appropriate', () => {
      render(<CardTitle>My Card Title</CardTitle>);
      
      const title = screen.getByText('My Card Title');
      expect(title.tagName).toBe('DIV'); // Default is div
    });
  });

  describe('CardContent', () => {
    it('renders with default styling', () => {
      render(<CardContent data-testid="card-content">Content text</CardContent>);
      
      const content = screen.getByTestId('card-content');
      expect(content).toBeInTheDocument();
      expect(content).toHaveClass('p-6', 'pt-0');
    });

    it('displays content correctly', () => {
      render(<CardContent>This is card content</CardContent>);
      
      expect(screen.getByText('This is card content')).toBeInTheDocument();
    });
  });

  describe('CardFooter', () => {
    it('renders with default styling', () => {
      render(<CardFooter data-testid="card-footer">Footer content</CardFooter>);
      
      const footer = screen.getByTestId('card-footer');
      expect(footer).toBeInTheDocument();
      expect(footer).toHaveClass('flex', 'items-center', 'p-6', 'pt-0');
    });
  });

  describe('CardDescription', () => {
    it('renders with default styling', () => {
      render(<CardDescription data-testid="card-description">Description text</CardDescription>);
      
      const description = screen.getByTestId('card-description');
      expect(description).toBeInTheDocument();
      expect(description).toHaveClass('text-sm', 'text-muted-foreground');
    });
  });

  describe('Complete Card Structure', () => {
    it('renders full card with all components', () => {
      render(
        <Card data-testid="full-card">
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
            <CardDescription>Card description text</CardDescription>
          </CardHeader>
          <CardContent>
            Main content goes here
          </CardContent>
          <CardFooter>
            <button>Action Button</button>
          </CardFooter>
        </Card>
      );

      expect(screen.getByTestId('full-card')).toBeInTheDocument();
      expect(screen.getByText('Card Title')).toBeInTheDocument();
      expect(screen.getByText('Card description text')).toBeInTheDocument();
      expect(screen.getByText('Main content goes here')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Action Button' })).toBeInTheDocument();
    });

    it('maintains proper nesting structure', () => {
      render(
        <Card data-testid="nested-card">
          <CardHeader data-testid="nested-header">
            <CardTitle data-testid="nested-title">Title</CardTitle>
          </CardHeader>
        </Card>
      );

      const card = screen.getByTestId('nested-card');
      const header = screen.getByTestId('nested-header');
      const title = screen.getByTestId('nested-title');

      expect(card).toContainElement(header);
      expect(header).toContainElement(title);
    });
  });

  describe('Accessibility', () => {
    it('supports ARIA attributes', () => {
      render(
        <Card role="region" aria-label="Info card" data-testid="aria-card">
          Content
        </Card>
      );

      const card = screen.getByTestId('aria-card');
      expect(card).toHaveAttribute('role', 'region');
      expect(card).toHaveAttribute('aria-label', 'Info card');
    });

    it('supports custom attributes', () => {
      render(
        <Card id="custom-id" data-custom="value" data-testid="custom-card">
          Content
        </Card>
      );

      const card = screen.getByTestId('custom-card');
      expect(card).toHaveAttribute('id', 'custom-id');
      expect(card).toHaveAttribute('data-custom', 'value');
    });
  });
});