/**
 * Tests for Tabs components
 * Comprehensive coverage for Radix UI Tabs functionality
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../tabs';

describe('Tabs Components', () => {
  describe('TabsList', () => {
    it('renders with default styling', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList data-testid="tabs-list">
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
        </Tabs>
      );
      
      const list = screen.getByTestId('tabs-list');
      expect(list).toBeInTheDocument();
      expect(list).toHaveClass('inline-flex', 'h-10', 'items-center', 'justify-center', 'rounded-md', 'bg-muted');
    });

    it('applies custom className', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList className="custom-tabs-list" data-testid="tabs-list">
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
        </Tabs>
      );
      
      const list = screen.getByTestId('tabs-list');
      expect(list).toHaveClass('custom-tabs-list');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(
        <Tabs defaultValue="tab1">
          <TabsList ref={ref}>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
        </Tabs>
      );
      
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });
  });

  describe('TabsTrigger', () => {
    it('renders with default styling', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1" data-testid="tabs-trigger">Tab 1</TabsTrigger>
          </TabsList>
        </Tabs>
      );
      
      const trigger = screen.getByTestId('tabs-trigger');
      expect(trigger).toBeInTheDocument();
      expect(trigger).toHaveClass('inline-flex', 'items-center', 'justify-center', 'whitespace-nowrap');
    });

    it('applies custom className', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1" className="custom-trigger" data-testid="tabs-trigger">
              Tab 1
            </TabsTrigger>
          </TabsList>
        </Tabs>
      );
      
      const trigger = screen.getByTestId('tabs-trigger');
      expect(trigger).toHaveClass('custom-trigger');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLButtonElement>();
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1" ref={ref}>Tab 1</TabsTrigger>
          </TabsList>
        </Tabs>
      );
      
      expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    });

    it('shows active state styling', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1" data-testid="active-trigger">Active Tab</TabsTrigger>
            <TabsTrigger value="tab2" data-testid="inactive-trigger">Inactive Tab</TabsTrigger>
          </TabsList>
        </Tabs>
      );
      
      const activeTrigger = screen.getByTestId('active-trigger');
      const inactiveTrigger = screen.getByTestId('inactive-trigger');
      
      expect(activeTrigger).toHaveClass('data-[state=active]:bg-background');
      expect(inactiveTrigger).toHaveClass('data-[state=active]:bg-background');
      expect(activeTrigger).toHaveAttribute('data-state', 'active');
      expect(inactiveTrigger).toHaveAttribute('data-state', 'inactive');
    });

    it('handles disabled state', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1" disabled data-testid="disabled-trigger">
              Disabled Tab
            </TabsTrigger>
          </TabsList>
        </Tabs>
      );
      
      const trigger = screen.getByTestId('disabled-trigger');
      expect(trigger).toBeDisabled();
      expect(trigger).toHaveClass('disabled:pointer-events-none', 'disabled:opacity-50');
    });
  });

  describe('TabsContent', () => {
    it('renders with default styling', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" data-testid="tabs-content">
            Tab 1 content
          </TabsContent>
        </Tabs>
      );
      
      const content = screen.getByTestId('tabs-content');
      expect(content).toBeInTheDocument();
      expect(content).toHaveClass('mt-2', 'ring-offset-background');
    });

    it('applies custom className', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" className="custom-content" data-testid="tabs-content">
            Content
          </TabsContent>
        </Tabs>
      );
      
      const content = screen.getByTestId('tabs-content');
      expect(content).toHaveClass('custom-content');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>();
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" ref={ref}>
            Content
          </TabsContent>
        </Tabs>
      );
      
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });

    it('shows only active content', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Tab 1 content</TabsContent>
          <TabsContent value="tab2">Tab 2 content</TabsContent>
        </Tabs>
      );
      
      expect(screen.getByText('Tab 1 content')).toBeInTheDocument();
      expect(screen.queryByText('Tab 2 content')).not.toBeInTheDocument();
    });
  });

  describe('Complete Tabs Structure', () => {
    it('renders full tabs with all components', () => {
      render(
        <Tabs defaultValue="overview" data-testid="complete-tabs">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>
          <TabsContent value="overview">
            <h3>Overview Content</h3>
            <p>This is the overview tab content.</p>
          </TabsContent>
          <TabsContent value="analytics">
            <h3>Analytics Content</h3>
            <p>This is the analytics tab content.</p>
          </TabsContent>
          <TabsContent value="reports">
            <h3>Reports Content</h3>
            <p>This is the reports tab content.</p>
          </TabsContent>
        </Tabs>
      );

      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('Reports')).toBeInTheDocument();
      expect(screen.getByText('Overview Content')).toBeInTheDocument();
    });

    it('handles tab switching interactions', async () => {
      const user = userEvent.setup();
      
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Tab 1 content</TabsContent>
          <TabsContent value="tab2">Tab 2 content</TabsContent>
        </Tabs>
      );

      // Initially tab 1 should be active
      expect(screen.getByText('Tab 1 content')).toBeInTheDocument();
      expect(screen.queryByText('Tab 2 content')).not.toBeInTheDocument();

      // Click tab 2
      await user.click(screen.getByText('Tab 2'));

      // Now tab 2 should be active
      expect(screen.queryByText('Tab 1 content')).not.toBeInTheDocument();
      expect(screen.getByText('Tab 2 content')).toBeInTheDocument();
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
            <TabsTrigger value="tab3">Tab 3</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Tab 1 content</TabsContent>
          <TabsContent value="tab2">Tab 2 content</TabsContent>
          <TabsContent value="tab3">Tab 3 content</TabsContent>
        </Tabs>
      );

      const tab1 = screen.getByText('Tab 1');
      await user.click(tab1);
      expect(tab1).toHaveFocus();

      // Use arrow keys to navigate
      await user.keyboard('{ArrowRight}');
      expect(screen.getByText('Tab 2')).toHaveFocus();

      await user.keyboard('{ArrowRight}');
      expect(screen.getByText('Tab 3')).toHaveFocus();

      await user.keyboard('{ArrowLeft}');
      expect(screen.getByText('Tab 2')).toHaveFocus();
    });

    it('maintains proper ARIA attributes', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabsList>
            <TabsTrigger value="tab1">Tab 1</TabsTrigger>
            <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          </TabsList>
          <TabsContent value="tab1">Tab 1 content</TabsContent>
          <TabsContent value="tab2">Tab 2 content</TabsContent>
        </Tabs>
      );

      const tabList = screen.getByRole('tablist');
      const tabs = screen.getAllByRole('tab');
      const tabPanels = screen.getAllByRole('tabpanel', { hidden: true });

      expect(tabList).toBeInTheDocument();
      expect(tabs).toHaveLength(2);
      expect(tabPanels).toHaveLength(2); // All panels are in DOM, inactive ones are hidden
    });
  });

  describe('Accessibility', () => {
    it('supports custom ARIA attributes', () => {
      render(
        <Tabs defaultValue="tab1" aria-label="Settings tabs">
          <TabsList aria-labelledby="settings-heading">
            <TabsTrigger value="tab1" aria-describedby="tab1-description">
              General
            </TabsTrigger>
          </TabsList>
          <TabsContent value="tab1" aria-labelledby="tab1-heading">
            General settings content
          </TabsContent>
        </Tabs>
      );

      const tabs = screen.getByRole('tablist');
      const tab = screen.getByRole('tab');
      const panel = screen.getByRole('tabpanel');

      expect(tabs).toHaveAttribute('aria-labelledby', 'settings-heading');
      expect(tab).toHaveAttribute('aria-describedby', 'tab1-description');
      expect(panel).toHaveAttribute('aria-labelledby', 'tab1-heading');
    });

    it('handles controlled state', () => {
      const ControlledTabs = () => {
        const [value, setValue] = React.useState('tab1');
        return (
          <Tabs value={value} onValueChange={setValue}>
            <TabsList>
              <TabsTrigger value="tab1">Tab 1</TabsTrigger>
              <TabsTrigger value="tab2">Tab 2</TabsTrigger>
            </TabsList>
            <TabsContent value="tab1">Tab 1 content</TabsContent>
            <TabsContent value="tab2">Tab 2 content</TabsContent>
          </Tabs>
        );
      };

      render(<ControlledTabs />);
      expect(screen.getByText('Tab 1 content')).toBeInTheDocument();
    });
  });
});