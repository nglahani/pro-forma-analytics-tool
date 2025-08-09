/**
 * Tests for DropdownMenu components
 * Comprehensive coverage for Radix UI DropdownMenu functionality
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuRadioGroup,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
} from '../dropdown-menu';

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Check: () => <div data-testid="check-icon" />,
  ChevronRight: () => <div data-testid="chevron-right-icon" />,
  Circle: () => <div data-testid="circle-icon" />,
}));

describe('DropdownMenu Components', () => {
  describe('Basic DropdownMenu', () => {
    it('renders dropdown menu trigger', () => {
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open Menu</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem>Item 1</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      expect(screen.getByRole('button', { name: 'Open Menu' })).toBeInTheDocument();
    });

    it('opens menu content when trigger is clicked', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open Menu</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem>Item 1</DropdownMenuItem>
            <DropdownMenuItem>Item 2</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      const trigger = screen.getByRole('button', { name: 'Open Menu' });
      await user.click(trigger);

      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
    });
  });

  describe('DropdownMenuContent', () => {
    it('renders with default styling', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent data-testid="dropdown-content">
            <DropdownMenuItem>Content</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      const content = screen.getByTestId('dropdown-content');
      expect(content).toHaveClass('z-50', 'min-w-[8rem]', 'overflow-hidden', 'rounded-md', 'border');
    });

    it('applies custom className', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="custom-content" data-testid="dropdown-content">
            <DropdownMenuItem>Content</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByTestId('dropdown-content')).toHaveClass('custom-content');
    });

    it('supports custom sideOffset', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent sideOffset={10} data-testid="dropdown-content">
            <DropdownMenuItem>Content</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      // sideOffset is passed to the underlying Radix component
      expect(screen.getByTestId('dropdown-content')).toBeInTheDocument();
    });
  });

  describe('DropdownMenuItem', () => {
    it('renders with default styling', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem data-testid="menu-item">Test Item</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      const item = screen.getByTestId('menu-item');
      expect(item).toHaveClass('relative', 'flex', 'cursor-default', 'select-none');
    });

    it('applies inset styling', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem inset data-testid="inset-item">Inset Item</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByTestId('inset-item')).toHaveClass('pl-8');
    });

    it('handles disabled state', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem disabled data-testid="disabled-item">
              Disabled Item
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      const disabledItem = screen.getByTestId('disabled-item');
      expect(disabledItem).toHaveClass('data-[disabled]:pointer-events-none', 'data-[disabled]:opacity-50');
    });
  });

  describe('DropdownMenuCheckboxItem', () => {
    it('renders checkbox item with check indicator', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuCheckboxItem checked>
              Checked Item
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByText('Checked Item')).toBeInTheDocument();
      expect(screen.getByTestId('check-icon')).toBeInTheDocument();
    });

    it('handles checked state changes', async () => {
      const user = userEvent.setup();
      const handleCheckedChange = jest.fn();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuCheckboxItem 
              checked={false} 
              onCheckedChange={handleCheckedChange}
            >
              Toggle Item
            </DropdownMenuCheckboxItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      await user.click(screen.getByText('Toggle Item'));
      
      expect(handleCheckedChange).toHaveBeenCalledWith(true);
    });
  });

  describe('DropdownMenuRadioGroup and DropdownMenuRadioItem', () => {
    it('renders radio group with items', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuRadioGroup value="option1">
              <DropdownMenuRadioItem value="option1">Option 1</DropdownMenuRadioItem>
              <DropdownMenuRadioItem value="option2">Option 2</DropdownMenuRadioItem>
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByText('Option 1')).toBeInTheDocument();
      expect(screen.getByText('Option 2')).toBeInTheDocument();
      expect(screen.getByTestId('circle-icon')).toBeInTheDocument();
    });

    it('handles radio value changes', async () => {
      const user = userEvent.setup();
      const handleValueChange = jest.fn();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuRadioGroup value="option1" onValueChange={handleValueChange}>
              <DropdownMenuRadioItem value="option1">Option 1</DropdownMenuRadioItem>
              <DropdownMenuRadioItem value="option2">Option 2</DropdownMenuRadioItem>
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      await user.click(screen.getByText('Option 2'));
      
      expect(handleValueChange).toHaveBeenCalledWith('option2');
    });
  });

  describe('DropdownMenuLabel and DropdownMenuSeparator', () => {
    it('renders label and separator', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuLabel>Menu Section</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Item 1</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByText('Menu Section')).toBeInTheDocument();
      // Separator creates a visual break
    });

    it('applies inset styling to label', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuLabel inset data-testid="inset-label">
              Inset Label
            </DropdownMenuLabel>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByTestId('inset-label')).toHaveClass('pl-8');
    });
  });

  describe('DropdownMenuShortcut', () => {
    it('renders shortcut text', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem>
              Save File
              <DropdownMenuShortcut>⌘S</DropdownMenuShortcut>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByText('⌘S')).toBeInTheDocument();
    });
  });

  describe('DropdownMenuSub', () => {
    it('renders submenu with trigger', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>More Options</DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                <DropdownMenuItem>Sub Item 1</DropdownMenuItem>
                <DropdownMenuItem>Sub Item 2</DropdownMenuItem>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      const subTrigger = screen.getByText('More Options');
      expect(subTrigger).toBeInTheDocument();
      expect(screen.getByTestId('chevron-right-icon')).toBeInTheDocument();
    });

    it('applies inset styling to sub trigger', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger inset data-testid="inset-trigger">
                Inset Trigger
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                <DropdownMenuItem>Sub Item</DropdownMenuItem>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByTestId('inset-trigger')).toHaveClass('pl-8');
    });
  });

  describe('DropdownMenuGroup', () => {
    it('groups menu items', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Open</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuGroup>
              <DropdownMenuItem>Group Item 1</DropdownMenuItem>
              <DropdownMenuItem>Group Item 2</DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Regular Item</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button'));
      
      expect(screen.getByText('Group Item 1')).toBeInTheDocument();
      expect(screen.getByText('Group Item 2')).toBeInTheDocument();
      expect(screen.getByText('Regular Item')).toBeInTheDocument();
    });
  });

  describe('Complete DropdownMenu Structure', () => {
    it('renders complex menu with all components', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Complex Menu</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem>
                Profile
                <DropdownMenuShortcut>⌘P</DropdownMenuShortcut>
              </DropdownMenuItem>
              <DropdownMenuItem>
                Settings
                <DropdownMenuShortcut>⌘S</DropdownMenuShortcut>
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuCheckboxItem checked>
              Show Status Bar
            </DropdownMenuCheckboxItem>
            <DropdownMenuRadioGroup value="light">
              <DropdownMenuRadioItem value="light">Light</DropdownMenuRadioItem>
              <DropdownMenuRadioItem value="dark">Dark</DropdownMenuRadioItem>
            </DropdownMenuRadioGroup>
            <DropdownMenuSeparator />
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>More Tools</DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                <DropdownMenuItem>Developer Tools</DropdownMenuItem>
                <DropdownMenuItem>Extensions</DropdownMenuItem>
              </DropdownMenuSubContent>
            </DropdownMenuSub>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      await user.click(screen.getByRole('button', { name: 'Complex Menu' }));
      
      expect(screen.getByText('Actions')).toBeInTheDocument();
      expect(screen.getByText('Profile')).toBeInTheDocument();
      expect(screen.getByText('⌘P')).toBeInTheDocument();
      expect(screen.getByText('Show Status Bar')).toBeInTheDocument();
      expect(screen.getByText('Light')).toBeInTheDocument();
      expect(screen.getByText('More Tools')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button>Keyboard Menu</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem>Item 1</DropdownMenuItem>
            <DropdownMenuItem>Item 2</DropdownMenuItem>
            <DropdownMenuItem>Item 3</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      const trigger = screen.getByRole('button', { name: 'Keyboard Menu' });
      
      // Open with Enter
      trigger.focus();
      await user.keyboard('{Enter}');
      
      expect(screen.getByText('Item 1')).toBeInTheDocument();
    });

    it('supports ARIA attributes', async () => {
      const user = userEvent.setup();
      
      render(
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button aria-label="Menu options">Menu</button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem>Option 1</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );

      const trigger = screen.getByLabelText('Menu options');
      expect(trigger).toBeInTheDocument();
    });
  });
});