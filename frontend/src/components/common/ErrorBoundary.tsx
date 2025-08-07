/**
 * Enhanced Error Boundary Component
 * Provides comprehensive error handling with fallbacks and recovery options
 */

'use client';

import React, { Component, ReactNode, ErrorInfo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertTriangle,
  RefreshCw,
  Bug,
  ArrowLeft,
  Copy,
  ExternalLink,
} from 'lucide-react';
import { textColors } from '@/lib/utils';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showDetails?: boolean;
  enableReset?: boolean;
  resetKeys?: Array<string | number>;
  resetOnPropsChange?: boolean;
  context?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  eventId: string | null;
  resetCount: number;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
      resetCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      eventId: Math.random().toString(36).substr(2, 9),
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to an error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Call the onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In a real application, you might want to log to an error monitoring service
    // Example: Sentry.captureException(error, { contexts: { errorBoundary: errorInfo } });
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetKeys, resetOnPropsChange } = this.props;
    const { hasError, resetCount } = this.state;

    // Reset error state if resetKeys changed
    if (hasError && resetKeys && prevProps.resetKeys) {
      const hasResetKeyChanged = resetKeys.some(
        (key, index) => key !== prevProps.resetKeys![index]
      );
      
      if (hasResetKeyChanged) {
        this.resetError();
      }
    }

    // Reset error state if props changed and resetOnPropsChange is true
    if (hasError && resetOnPropsChange && prevProps !== this.props) {
      this.resetError();
    }

    // Auto-reset after multiple attempts
    if (hasError && resetCount > 2) {
      this.autoReset();
    }
  }

  componentWillUnmount() {
    if (this.resetTimeoutId) {
      window.clearTimeout(this.resetTimeoutId);
    }
  }

  resetError = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      eventId: null,
      resetCount: prevState.resetCount + 1,
    }));
  };

  autoReset = () => {
    if (this.resetTimeoutId) return;

    this.resetTimeoutId = window.setTimeout(() => {
      this.resetError();
      this.resetTimeoutId = null;
    }, 5000);
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoBack = () => {
    window.history.back();
  };

  handleCopyError = () => {
    const { error, errorInfo, eventId } = this.state;
    const errorText = `
Error ID: ${eventId}
Component: ${this.props.context || 'Unknown'}
Error: ${error?.message}
Stack: ${error?.stack}
Component Stack: ${errorInfo?.componentStack}
    `.trim();

    navigator.clipboard.writeText(errorText).then(() => {
      console.log('Error details copied to clipboard');
    });
  };

  handleReportIssue = () => {
    const { error, eventId } = this.state;
    const title = encodeURIComponent(`Error: ${error?.message || 'Unknown error'}`);
    const body = encodeURIComponent(`
Error ID: ${eventId}
Context: ${this.props.context || 'Unknown'}
Browser: ${navigator.userAgent}
URL: ${window.location.href}

Error Details:
${error?.stack || 'No stack trace available'}
    `);

    const issueUrl = `https://github.com/your-repo/issues/new?title=${title}&body=${body}`;
    window.open(issueUrl, '_blank');
  };

  render() {
    const { hasError, error, errorInfo, eventId, resetCount } = this.state;
    const { children, fallback, showDetails = true, enableReset = true, context } = this.props;

    if (hasError) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
          <Card className="w-full max-w-2xl">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 bg-red-100 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                </div>
                <div>
                  <CardTitle className="text-xl text-red-600">
                    Something went wrong
                  </CardTitle>
                  <CardDescription>
                    {context ? `Error in ${context}` : 'An unexpected error occurred'}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Error Summary */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-medium ${textColors.secondary}`}>
                    Error Message
                  </span>
                  <Badge variant="outline" className="text-xs font-mono">
                    ID: {eventId}
                  </Badge>
                </div>
                <div className="bg-red-50 p-3 rounded-lg border border-red-200">
                  <p className="text-red-800 text-sm font-mono break-words">
                    {error?.message || 'Unknown error occurred'}
                  </p>
                </div>
              </div>

              {/* Retry Information */}
              {resetCount > 0 && (
                <div className="bg-amber-50 p-3 rounded-lg border border-amber-200">
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="h-4 w-4 text-amber-600" />
                    <span className="text-amber-800 text-sm">
                      Retry attempts: {resetCount}
                      {resetCount > 2 && ' (Auto-reset in progress...)'}
                    </span>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3">
                {enableReset && (
                  <Button
                    onClick={this.resetError}
                    className="flex items-center space-x-2"
                    variant={resetCount > 2 ? "secondary" : "default"}
                  >
                    <RefreshCw className="h-4 w-4" />
                    <span>Try Again</span>
                  </Button>
                )}

                <Button
                  variant="outline"
                  onClick={this.handleReload}
                  className="flex items-center space-x-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Reload Page</span>
                </Button>

                <Button
                  variant="outline"
                  onClick={this.handleGoBack}
                  className="flex items-center space-x-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span>Go Back</span>
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={this.handleCopyError}
                  className="flex items-center space-x-2"
                >
                  <Copy className="h-4 w-4" />
                  <span>Copy Error</span>
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={this.handleReportIssue}
                  className="flex items-center space-x-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span>Report Issue</span>
                </Button>
              </div>

              {/* Detailed Error Information */}
              {showDetails && error?.stack && (
                <details className="space-y-3">
                  <summary className={`cursor-pointer text-sm font-medium ${textColors.secondary} flex items-center space-x-2`}>
                    <Bug className="h-4 w-4" />
                    <span>Technical Details</span>
                  </summary>
                  <div className="bg-gray-50 p-3 rounded-lg border">
                    <pre className="text-xs font-mono whitespace-pre-wrap break-words text-gray-700 max-h-40 overflow-y-auto">
                      {error.stack}
                    </pre>
                  </div>
                  
                  {errorInfo?.componentStack && (
                    <div className="bg-gray-50 p-3 rounded-lg border">
                      <p className="text-xs font-medium text-gray-700 mb-2">Component Stack:</p>
                      <pre className="text-xs font-mono whitespace-pre-wrap break-words text-gray-600 max-h-32 overflow-y-auto">
                        {errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </details>
              )}

              {/* Help Text */}
              <div className="text-xs text-gray-500 space-y-1">
                <p>If this error persists, please:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Try refreshing the page or reloading the application</li>
                  <li>Check your internet connection</li>
                  <li>Clear your browser cache and cookies</li>
                  <li>Report the issue using the button above</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return children;
  }
}

// HOC wrapper for functional components
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => {
    return (
      <ErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}

// Hook for triggering error boundary from functional components
export function useErrorHandler() {
  return (error: Error, errorInfo?: any) => {
    // Re-throw the error to be caught by the nearest error boundary
    throw error;
  };
}