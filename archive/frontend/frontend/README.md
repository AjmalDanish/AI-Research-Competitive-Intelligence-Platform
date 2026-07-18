# Competitive Intelligence Platform - Frontend

Modern React-based frontend for the AI Research Competitive Intelligence Platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Material-UI** - Component library
- **React Router** - Client-side routing
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Vite** - Build tool

## Features

- 🎨 Modern, responsive UI with Material-UI
- 📊 Interactive dashboards and charts
- 🔐 Authentication with JWT tokens
- 📈 Real-time market intelligence
- 🏢 Competitor tracking and analysis
- 🚨 Alert management system
- 📄 Report generation
- ⚙️ User settings management

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

### Build for Production

```bash
npm run build
```

### Run Tests

```bash
npm test
```

## Project Structure

```
src/
├── components/
│   └── layout/
│       ├── Navbar.tsx
│       └── Sidebar.tsx
├── contexts/
│   └── AuthContext.tsx
├── pages/
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   ├── Competitors.tsx
│   ├── MarketIntelligence.tsx
│   ├── Analytics.tsx
│   ├── Alerts.tsx
│   ├── Reports.tsx
│   └── Settings.tsx
├── services/
│   └── api.ts
├── App.tsx
├── main.tsx
└── vite-env.d.ts
```

## Pages Overview

### Dashboard
- Overview metrics and KPIs
- Market trends visualization
- Recent activity feed
- Key insights panel

### Competitors
- Competitor list (grid/table views)
- Add/Edit/Delete competitors
- Competitor details and metrics
- Status tracking

### Market Intelligence
- Market trends and forecasts
- News sentiment analysis
- Market share tracking
- Opportunity detection

### Analytics
- SWOT analysis
- Competitor comparison
- Performance metrics
- AI-powered insights

### Alerts
- Create custom alerts
- Filter by type and severity
- Mark as read/unread
- Real-time notifications

### Reports
- Generate reports
- Download in multiple formats
- Report templates
- Report history

### Settings
- Profile management
- Notification preferences
- API configuration
- Display settings

## API Integration

The frontend connects to the backend REST API using Axios:

```typescript
import { competitorsAPI } from '../services/api';

// Get all competitors
const response = await competitorsAPI.list();

// Create a competitor
await competitorsAPI.create({ name, website, industry });
```

## Styling

The project uses Material-UI's theming system:

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
});
```

## Development Tips

1. **Hot Reload**: Vite provides fast hot module replacement
2. **Type Checking**: TypeScript ensures type safety
3. **Component Reusability**: Build reusable components for consistency
4. **State Management**: Use React Context for global state

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

MIT