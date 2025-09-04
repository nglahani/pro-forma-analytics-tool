/**
 * Dashboard Sidebar Component
 * Navigation sidebar with professional styling
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Calculator, 
  Building, 
  TrendingUp, 
  BarChart3,
  Plus,
  X 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  badge?: string;
}

const navigation: NavigationItem[] = [
  {
    name: 'Home',
    href: '/',
    icon: Home,
    description: 'Overview and quick actions'
  },
  {
    name: 'Properties',
    href: '/properties',
    icon: Building,
    description: 'Manage your property portfolio'
  },
  {
    name: 'Add Property',
    href: '/property-input',
    icon: Plus,
    description: 'Add new property for analysis',
    badge: 'New'
  },
  {
    name: 'Financial Forecasts',
    href: '/analysis',
    icon: Calculator,
    description: 'DCF analysis and financial modeling'
  },
  {
    name: 'Risk Analysis',
    href: '/monte-carlo',
    icon: BarChart3,
    description: 'Monte Carlo simulations and risk modeling'
  },
  {
    name: 'Market Insights',
    href: '/market-data',
    icon: TrendingUp,
    description: 'Market trends and forecasts'
  }
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200 pt-4 pb-4 overflow-y-auto">
          {/* Logo area */}
          <div className="flex items-center flex-shrink-0 px-4 mb-8">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Calculator className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  Pro Forma
                </h1>
                <p className="text-xs text-gray-500">Analytics</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors',
                    isActive
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                      : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                  )}
                >
                  <Icon
                    className={cn(
                      'flex-shrink-0 -ml-1 mr-3 h-5 w-5',
                      isActive
                        ? 'text-blue-600'
                        : 'text-gray-400 group-hover:text-gray-500'
                    )}
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span>{item.name}</span>
                      {item.badge && (
                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </p>
                  </div>
                </Link>
              );
            })}
          </nav>

          {/* Bottom section */}
          <div className="flex-shrink-0 px-3 py-4 border-t border-gray-200">
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-blue-900">
                    FastAPI Ready
                  </p>
                  <p className="text-xs text-blue-700">
                    Backend integration active
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile sidebar */}
      <div
        className={cn(
          'lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white transform transition-transform duration-300 ease-in-out',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Mobile header */}
          <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Calculator className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  Pro Forma
                </h1>
                <p className="text-xs text-gray-500">Analytics</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Mobile navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    'group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors',
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                  )}
                >
                  <Icon
                    className={cn(
                      'flex-shrink-0 -ml-1 mr-3 h-5 w-5',
                      isActive
                        ? 'text-blue-600'
                        : 'text-gray-400 group-hover:text-gray-500'
                    )}
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span>{item.name}</span>
                      {item.badge && (
                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </p>
                  </div>
                </Link>
              );
            })}
          </nav>

          {/* Mobile bottom section */}
          <div className="flex-shrink-0 px-3 py-4 border-t border-gray-200">
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-blue-900">
                    FastAPI Ready
                  </p>
                  <p className="text-xs text-blue-700">
                    Backend integration active
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}