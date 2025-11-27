import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Keep standard .next directory but disable OneDrive features that cause conflicts
  distDir: '.next-safe',
  
  // OneDrive compatibility settings
  outputFileTracingExcludes: {
    '*': ['**/.next/**', '**/node_modules/@swc/core-win32-x64-msvc/**'],
  },
  
  experimental: {
    optimizePackageImports: ['recharts', '@radix-ui/react-dialog', 'lucide-react'],
  },

  // Acknowledge turbopack but use webpack for OneDrive compatibility
  turbopack: {},
  
  // Configure webpack for OneDrive compatibility
  webpack: (config, { dev, isServer }) => {
    // OneDrive-safe file watching with polling
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
      ignored: ['**/.next-safe/**', '**/node_modules/**', '**/.git/**'],
    };
    
    // Reduce file system operations in development
    if (dev) {
      // Use memory cache to avoid OneDrive conflicts
      config.cache = {
        type: 'memory',
      };
      config.snapshot = {
        managedPaths: [],
        immutablePaths: [],
      };
    }
    
    // Configure resolve for external build directory
    config.resolve.symlinks = false;
    config.resolve.cacheWithContext = false;
    
    // Standard module resolution
    config.resolve.modules = config.resolve.modules || [];
    config.resolve.modules.unshift('node_modules');
    
    return config;
  },
  // Note: eslint configuration moved to .eslintrc for Next.js 16 compatibility
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production'
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1/:path*'
      }
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-Frame-Options', 
            value: 'DENY'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          }
        ]
      }
    ];
  }
};

export default nextConfig;
