/**
 * Tests for DashboardLayout Component
 * 
 * Tests the main dashboard layout including sidebar navigation
 * and header functionality.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { DashboardLayout } from '../DashboardLayout';

// Mock child components
jest.mock('../Sidebar', () => ({
  Sidebar: ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => (
    <div data-testid="sidebar" data-open={isOpen}>
      <button onClick={onClose} data-testid="sidebar-close">
        Close Sidebar
      </button>
      Sidebar Content
    </div>
  ),
}));

jest.mock('../Header', () => ({
  Header: ({ onMenuClick }: { onMenuClick: () => void }) => (
    <div data-testid="header">
      <button onClick={onMenuClick} data-testid="menu-button">
        Open Menu
      </button>
      Header Content
    </div>
  ),
}));

describe('DashboardLayout', () => {
  it('renders all layout components', () => {
    render(
      <DashboardLayout>
        <div data-testid="main-content">Main Content</div>
      </DashboardLayout>
    );

    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('main-content')).toBeInTheDocument();
  });

  it('renders children content correctly', () => {
    const testContent = 'Test dashboard content';
    render(
      <DashboardLayout>
        <div>{testContent}</div>
      </DashboardLayout>
    );

    expect(screen.getByText(testContent)).toBeInTheDocument();
  });

  it('sidebar starts closed by default', () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const sidebar = screen.getByTestId('sidebar');
    expect(sidebar).toHaveAttribute('data-open', 'false');
  });

  it('opens sidebar when menu button is clicked', () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const menuButton = screen.getByTestId('menu-button');
    const sidebar = screen.getByTestId('sidebar');

    // Initially closed
    expect(sidebar).toHaveAttribute('data-open', 'false');

    // Click menu button to open
    fireEvent.click(menuButton);
    expect(sidebar).toHaveAttribute('data-open', 'true');
  });

  it('closes sidebar when close button is clicked', () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const menuButton = screen.getByTestId('menu-button');
    const closeButton = screen.getByTestId('sidebar-close');
    const sidebar = screen.getByTestId('sidebar');

    // Open sidebar first
    fireEvent.click(menuButton);
    expect(sidebar).toHaveAttribute('data-open', 'true');

    // Close sidebar
    fireEvent.click(closeButton);
    expect(sidebar).toHaveAttribute('data-open', 'false');
  });

  it('applies correct CSS classes for layout structure', () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    // Check main container has flex layout
    const container = screen.getByTestId('sidebar').parentElement;
    expect(container).toHaveClass('flex', 'h-screen', 'bg-gray-50');
  });

  it('maintains sidebar state through multiple interactions', () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const menuButton = screen.getByTestId('menu-button');
    const closeButton = screen.getByTestId('sidebar-close');
    const sidebar = screen.getByTestId('sidebar');

    // Multiple open/close cycles
    fireEvent.click(menuButton); // Open
    expect(sidebar).toHaveAttribute('data-open', 'true');

    fireEvent.click(closeButton); // Close
    expect(sidebar).toHaveAttribute('data-open', 'false');

    fireEvent.click(menuButton); // Open again
    expect(sidebar).toHaveAttribute('data-open', 'true');

    fireEvent.click(closeButton); // Close again
    expect(sidebar).toHaveAttribute('data-open', 'false');
  });

  it('renders with complex children content', () => {
    render(
      <DashboardLayout>
        <div data-testid="complex-content">
          <h1>Dashboard Title</h1>
          <div>
            <p>Some paragraph content</p>
            <button>Action Button</button>
          </div>
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
          </ul>
        </div>
      </DashboardLayout>
    );

    expect(screen.getByTestId('complex-content')).toBeInTheDocument();
    expect(screen.getByText('Dashboard Title')).toBeInTheDocument();
    expect(screen.getByText('Some paragraph content')).toBeInTheDocument();
    expect(screen.getByText('Action Button')).toBeInTheDocument();
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
  });

  it('handles empty children gracefully', () => {
    render(
      <DashboardLayout>
        {null}
      </DashboardLayout>
    );

    // Should still render layout components
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });

  it('provides proper accessibility structure', () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    // Main content should be within a main element
    const mainElement = screen.getByRole('main');
    expect(mainElement).toBeInTheDocument();
  });
});