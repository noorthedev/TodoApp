# Phase 2 Todo Frontend

Next.js frontend for the Phase 2 Todo application with JWT authentication.

## Prerequisites

- Node.js 18.0 or higher
- npm or yarn

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your actual values
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   - http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   │   ├── auth/        # Authentication components
│   │   ├── tasks/       # Task management components
│   │   └── ui/          # Reusable UI components
│   ├── lib/             # Utility libraries
│   │   ├── api.ts       # API client (Axios)
│   │   ├── auth.ts      # Auth context
│   │   └── types.ts     # TypeScript types
│   └── hooks/           # Custom React hooks
└── tests/               # Test files
```

## Pages

- `/` - Home page with links to login/register
- `/login` - User login
- `/register` - User registration
- `/dashboard` - Task management dashboard (protected)

## Environment Variables

See `.env.local.example` for required configuration.

## Development

- Run dev server: `npm run dev`
- Build for production: `npm run build`
- Start production server: `npm start`
- Run linter: `npm run lint`

## Authentication

The application uses JWT tokens stored in localStorage. Tokens are automatically included in API requests via Axios interceptors.

## Theme Architecture

### Current Implementation
- **Theme System**: CSS Variables defined in `src/app/globals.css`
- **Color Management**: Centralized color definitions in `:root` selector
- **Dark Mode**: Being implemented (Feature 001-theme-contrast-fix)

### Color Variables
```css
:root {
  --primary: #3b82f6;
  --primary-hover: #2563eb;
  --success: #10b981;
  --bg-site: #f8fafc;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --card-bg: #ffffff;
}
```

### Accessibility Standards
- **Target**: WCAG 2.1 Level AA compliance
- **Contrast Ratios**:
  - Normal text: 4.5:1 minimum
  - Large text: 3:1 minimum
- **Current Status**: Light mode meets all WCAG 2.1 AA standards

### Known Issues
- Button component uses inline styles instead of CSS variables (being refactored)
- Dark mode not yet implemented (in progress)
