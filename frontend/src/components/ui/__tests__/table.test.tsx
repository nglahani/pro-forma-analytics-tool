/**
 * Tests for Table components
 * Comprehensive coverage for all table-related components
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
} from '../table';

describe('Table Components', () => {
  describe('Table', () => {
    it('renders with default styling', () => {
      render(
        <Table data-testid="table">
          <TableBody>
            <TableRow>
              <TableCell>Content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      
      const table = screen.getByTestId('table');
      expect(table).toBeInTheDocument();
      expect(table).toHaveClass('w-full', 'caption-bottom', 'text-sm');
    });

    it('applies custom className', () => {
      render(<Table className="custom-table" data-testid="table" />);
      
      const table = screen.getByTestId('table');
      expect(table).toHaveClass('custom-table');
    });

    it('forwards ref correctly', () => {
      const ref = React.createRef<HTMLTableElement>();
      render(<Table ref={ref} />);
      
      expect(ref.current).toBeInstanceOf(HTMLTableElement);
    });

    it('has scrollable container wrapper', () => {
      const { container } = render(<Table data-testid="table" />);
      const wrapper = container.firstChild as HTMLElement;
      
      expect(wrapper).toHaveClass('relative', 'w-full', 'overflow-auto');
    });
  });

  describe('TableHeader', () => {
    it('renders with default styling', () => {
      render(
        <Table>
          <TableHeader data-testid="table-header">
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      
      const header = screen.getByTestId('table-header');
      expect(header).toBeInTheDocument();
      expect(header).toHaveClass('[&_tr]:border-b');
    });

    it('applies custom className', () => {
      render(
        <Table>
          <TableHeader className="custom-header" data-testid="table-header" />
        </Table>
      );
      
      const header = screen.getByTestId('table-header');
      expect(header).toHaveClass('custom-header');
    });
  });

  describe('TableBody', () => {
    it('renders with default styling', () => {
      render(
        <Table>
          <TableBody data-testid="table-body">
            <TableRow>
              <TableCell>Body content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      
      const body = screen.getByTestId('table-body');
      expect(body).toBeInTheDocument();
      expect(body).toHaveClass('[&_tr:last-child]:border-0');
    });

    it('applies custom className', () => {
      render(
        <Table>
          <TableBody className="custom-body" data-testid="table-body" />
        </Table>
      );
      
      const body = screen.getByTestId('table-body');
      expect(body).toHaveClass('custom-body');
    });
  });

  describe('TableFooter', () => {
    it('renders with default styling', () => {
      render(
        <Table>
          <TableFooter data-testid="table-footer">
            <TableRow>
              <TableCell>Footer content</TableCell>
            </TableRow>
          </TableFooter>
        </Table>
      );
      
      const footer = screen.getByTestId('table-footer');
      expect(footer).toBeInTheDocument();
      expect(footer).toHaveClass('border-t', 'bg-muted/50', 'font-medium');
    });

    it('applies custom className', () => {
      render(
        <Table>
          <TableFooter className="custom-footer" data-testid="table-footer" />
        </Table>
      );
      
      const footer = screen.getByTestId('table-footer');
      expect(footer).toHaveClass('custom-footer');
    });
  });

  describe('TableRow', () => {
    it('renders with default styling', () => {
      render(
        <Table>
          <TableBody>
            <TableRow data-testid="table-row">
              <TableCell>Row content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      
      const row = screen.getByTestId('table-row');
      expect(row).toBeInTheDocument();
      expect(row).toHaveClass('border-b', 'transition-colors', 'hover:bg-muted/50');
    });

    it('applies custom className', () => {
      render(
        <Table>
          <TableBody>
            <TableRow className="custom-row" data-testid="table-row">
              <TableCell>Content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      
      const row = screen.getByTestId('table-row');
      expect(row).toHaveClass('custom-row');
    });

    it('supports data-state attributes', () => {
      render(
        <Table>
          <TableBody>
            <TableRow data-state="selected" data-testid="table-row">
              <TableCell>Selected row</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      
      const row = screen.getByTestId('table-row');
      expect(row).toHaveAttribute('data-state', 'selected');
      expect(row).toHaveClass('data-[state=selected]:bg-muted');
    });
  });

  describe('TableHead', () => {
    it('renders with default styling', () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead data-testid="table-head">Header Cell</TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      
      const head = screen.getByTestId('table-head');
      expect(head).toBeInTheDocument();
      expect(head).toHaveClass('h-12', 'px-4', 'text-left', 'align-middle', 'font-medium');
    });

    it('applies custom className', () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="custom-head" data-testid="table-head">
                Header
              </TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      
      const head = screen.getByTestId('table-head');
      expect(head).toHaveClass('custom-head');
    });

    it('supports role attributes', () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead scope="col" data-testid="table-head">
                Sortable Header
              </TableHead>
            </TableRow>
          </TableHeader>
        </Table>
      );
      
      const head = screen.getByTestId('table-head');
      expect(head).toHaveAttribute('scope', 'col');
    });
  });

  describe('TableCell', () => {
    it('renders with default styling', () => {
      render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell data-testid="table-cell">Cell content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      
      const cell = screen.getByTestId('table-cell');
      expect(cell).toBeInTheDocument();
      expect(cell).toHaveClass('p-4', 'align-middle');
    });

    it('applies custom className', () => {
      render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell className="custom-cell" data-testid="table-cell">
                Content
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      
      const cell = screen.getByTestId('table-cell');
      expect(cell).toHaveClass('custom-cell');
    });

    it('supports colspan and rowspan', () => {
      render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell colSpan={2} rowSpan={1} data-testid="table-cell">
                Spanning cell
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );
      
      const cell = screen.getByTestId('table-cell');
      expect(cell).toHaveAttribute('colSpan', '2');
      expect(cell).toHaveAttribute('rowSpan', '1');
    });
  });

  describe('TableCaption', () => {
    it('renders with default styling', () => {
      render(
        <Table>
          <TableCaption data-testid="table-caption">
            Table description
          </TableCaption>
        </Table>
      );
      
      const caption = screen.getByTestId('table-caption');
      expect(caption).toBeInTheDocument();
      expect(caption).toHaveClass('mt-4', 'text-sm', 'text-muted-foreground');
    });

    it('applies custom className', () => {
      render(
        <Table>
          <TableCaption className="custom-caption" data-testid="table-caption">
            Custom caption
          </TableCaption>
        </Table>
      );
      
      const caption = screen.getByTestId('table-caption');
      expect(caption).toHaveClass('custom-caption');
    });
  });

  describe('Complete Table Structure', () => {
    it('renders full table with all components', () => {
      render(
        <Table data-testid="complete-table">
          <TableCaption>Financial Data Table</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Metric</TableHead>
              <TableHead>Value</TableHead>
              <TableHead>Change</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Revenue</TableCell>
              <TableCell>$100,000</TableCell>
              <TableCell>+5%</TableCell>
            </TableRow>
            <TableRow data-state="selected">
              <TableCell>Expenses</TableCell>
              <TableCell>$75,000</TableCell>
              <TableCell>-2%</TableCell>
            </TableRow>
          </TableBody>
          <TableFooter>
            <TableRow>
              <TableCell>Total</TableCell>
              <TableCell>$25,000</TableCell>
              <TableCell>+3%</TableCell>
            </TableRow>
          </TableFooter>
        </Table>
      );

      expect(screen.getByTestId('complete-table')).toBeInTheDocument();
      expect(screen.getByText('Financial Data Table')).toBeInTheDocument();
      expect(screen.getByText('Metric')).toBeInTheDocument();
      expect(screen.getByText('Revenue')).toBeInTheDocument();
      expect(screen.getByText('$100,000')).toBeInTheDocument();
      expect(screen.getByText('Total')).toBeInTheDocument();
    });

    it('maintains proper table semantics', () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>John Doe</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );

      const table = screen.getByRole('table');
      const headers = screen.getAllByRole('columnheader');
      const cells = screen.getAllByRole('cell');

      expect(table).toBeInTheDocument();
      expect(headers).toHaveLength(1);
      expect(cells).toHaveLength(1);
    });
  });

  describe('Accessibility', () => {
    it('supports ARIA attributes', () => {
      render(
        <Table aria-label="Data table" aria-describedby="table-description" data-testid="table">
          <TableBody>
            <TableRow>
              <TableCell>Data</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );

      const table = screen.getByTestId('table');
      expect(table).toHaveAttribute('aria-label', 'Data table');
      expect(table).toHaveAttribute('aria-describedby', 'table-description');
    });

    it('handles checkbox styling', () => {
      render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead data-testid="checkbox-header">
                <input type="checkbox" role="checkbox" />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell data-testid="checkbox-cell">
                <input type="checkbox" role="checkbox" />
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      );

      const header = screen.getByTestId('checkbox-header');
      const cell = screen.getByTestId('checkbox-cell');
      
      expect(header).toHaveClass('[&:has([role=checkbox])]:pr-0');
      expect(cell).toHaveClass('[&:has([role=checkbox])]:pr-0');
    });
  });
});