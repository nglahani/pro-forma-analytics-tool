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

- **Next.js 15** with App Router and TypeScript
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
   # Edit .env.local with your FastAPI backend URL
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

## License

This project is part of the Pro Forma Analytics tool suite.
