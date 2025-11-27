# Pro Forma Analytics - Frontend

A modern React/Next.js dashboard for real estate financial analysis, providing an intuitive interface for the Pro Forma Analytics DCF engine.

## Features

- **Property Input Forms**: Multi-step wizard with property templates
- **DCF Analysis**: Real-time financial analysis with NPV, IRR, and investment recommendations
- **Monte Carlo Simulation**: Interactive scatter plots with 500+ scenarios
- **Market Data Integration**: Current market conditions and forecasts
- **Responsive Design**: NYT/Claude Artifacts inspired aesthetic
- **Real-time Updates**: Live analysis progress and results

## Tech Stack

- **Next.js 16** with App Router and TypeScript
- **Tailwind CSS** for styling with custom design system
- **Radix UI** components for accessibility
- **Recharts** for financial data visualization
- **TanStack Query** for server state management
- **Zustand** for client state management
- **Zod** for runtime validation

## Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- FastAPI backend running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration (see Environment Variables below)
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Development

### Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (dashboard)/        # Dashboard route group
│   ├── auth/              # Authentication pages
│   └── api/               # API proxy routes
├── components/            # React components
│   ├── ui/                # Base UI components (shadcn/ui)
│   ├── forms/             # Property input forms
│   ├── charts/            # Financial visualizations
│   └── layout/            # Layout components
├── lib/                   # Utilities and configuration
│   ├── api/               # FastAPI client integration
│   ├── auth/              # Authentication service
│   └── utils.ts           # Common utilities
├── hooks/                 # Custom React hooks
└── types/                 # TypeScript definitions
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

### API Integration

The frontend integrates with the FastAPI backend through:

- **DCF Analysis**: `/api/v1/analysis/dcf`
- **Monte Carlo**: `/api/v1/simulation/monte-carlo`
- **Market Data**: `/api/v1/data/markets/{msa_code}`
- **Batch Analysis**: `/api/v1/analysis/batch`

See `src/types/api.ts` for complete API interface definitions.

## Environment Variables

The frontend uses environment variables prefixed with `NEXT_PUBLIC_` to expose them to the browser. Configure these in `.env.local` (not committed to Git).

### Required Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `NEXT_PUBLIC_API_URL` | FastAPI backend base URL | `http://localhost:8000` | `https://api.example.com` |
| `NEXT_PUBLIC_DEV_API_KEY` | Development API key | `dev_test_key_12345678901234567890123` | See backend for key generation |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `NEXT_PUBLIC_WS_URL` | WebSocket URL for real-time updates | `ws://localhost:8000` | `wss://api.example.com` |
| `NEXT_PUBLIC_ENV` | Environment name | `development` | `production`, `staging` |
| `NEXT_PUBLIC_APP_NAME` | Application display name | `Pro Forma Analytics` | Custom branding |
| `NEXT_PUBLIC_APP_VERSION` | Application version | `1.0.0` | Semantic version |
| `NEXT_PUBLIC_ENABLE_MONTE_CARLO` | Enable Monte Carlo features | `true` | `false` to disable |
| `NEXT_PUBLIC_ENABLE_BATCH_ANALYSIS` | Enable batch analysis | `false` | `true` to enable |
| `NEXT_PUBLIC_ENABLE_MARKET_DATA` | Enable market data features | `true` | `false` to disable |

### Development Notes

- **API Key**: In development mode, the frontend automatically uses the dev API key. In production, implement proper authentication.
- **API URL**: When deploying, update `NEXT_PUBLIC_API_URL` to your production backend URL.
- **Feature Flags**: Use the `ENABLE_*` flags to control feature availability during development.

### Example `.env.local`

```bash
# Backend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Environment
NEXT_PUBLIC_ENV=development

# Application Settings
NEXT_PUBLIC_APP_NAME="Pro Forma Analytics"
NEXT_PUBLIC_APP_VERSION=1.0.0

# Feature Flags
NEXT_PUBLIC_ENABLE_MONTE_CARLO=true
NEXT_PUBLIC_ENABLE_BATCH_ANALYSIS=false
NEXT_PUBLIC_ENABLE_MARKET_DATA=true

# Development API Key (DO NOT use in production)
NEXT_PUBLIC_DEV_API_KEY=dev_test_key_12345678901234567890123
```

## Testing

### Run Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Type Checking

```bash
# Check TypeScript types without building
npm run type-check
```

Current test coverage: 30%+ with comprehensive component testing.

## License

This project is part of the Pro Forma Analytics tool suite.
