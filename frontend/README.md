# Trucking Driver Portal - Frontend

A modern Next.js application for trucking company drivers to manage their trips, documents, and payroll.

## Features

- **Multiple Authentication Methods**
  - Username/Password with JWT
  - Email OTP (One-time password)
  - 2FA Support (when enabled on backend)

- **Driver Dashboard**
  - View current active trip
  - Track all trips (past and present)
  - Access documents (licenses, payslips, etc.)
  - View payroll history
  - Real-time trip status updates

- **Trip Management**
  - Start trips
  - Mark trips as delivered
  - View trip details and history
  - Track mileage and earnings

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Form Handling**: React Hook Form
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Date Formatting**: date-fns

## Setup Instructions

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Running Django backend API

### Installation

1. **Install dependencies**
\`\`\`bash
npm install
# or
yarn install
\`\`\`

2. **Configure environment variables**

Create a \`.env.local\` file:
\`\`\`
NEXT_PUBLIC_API_URL=http://localhost:8000/api
\`\`\`

3. **Run development server**
\`\`\`bash
npm run dev
# or
yarn dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000)

### Build for Production

\`\`\`bash
npm run build
npm start
\`\`\`

## Project Structure

\`\`\`
├── app/
│   ├── dashboard/
│   │   └── page.tsx          # Driver dashboard
│   ├── login/
│   │   └── page.tsx          # Login page with auth options
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Home/redirect page
│   └── globals.css           # Global styles
├── components/
│   └── TripCard.tsx          # Reusable trip card component
├── lib/
│   ├── api.ts                # API client and endpoints
│   ├── store.ts              # Zustand state management
│   └── types.ts              # TypeScript interfaces
├── middleware.ts             # Route protection
└── tailwind.config.ts        # Tailwind configuration
\`\`\`

## Key Features Explained

### Authentication Flow

1. User selects authentication method (password or email OTP)
2. For password: Direct login with credentials
3. For email OTP: Request OTP → Verify OTP → Login
4. JWT tokens stored in localStorage
5. Automatic token refresh on expiry
6. Protected routes via middleware

### Dashboard Components

- **Stats Cards**: Quick overview of miles, truck, pay rate, trips
- **Current Trip Alert**: Prominent display of active trip with action buttons
- **Tabs**: Organized view of overview, trips, documents, payroll
- **Trip Cards**: Detailed trip information with status updates

### API Integration

All API calls are centralized in \`lib/api.ts\`:
- Automatic token injection
- Token refresh on 401 errors
- Centralized error handling
- Type-safe API functions

### State Management

Using Zustand for lightweight, simple state:
- User authentication state
- Driver profile data
- Persistent across page reloads

## Customization

### Styling

Tailwind utilities are in \`globals.css\`:
- \`.btn-primary\`: Primary action buttons
- \`.btn-secondary\`: Secondary buttons
- \`.input\`: Form inputs
- \`.card\`: Content cards

### API Configuration

Update API base URL in \`.env.local\`:
\`\`\`
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
\`\`\`

### Adding New Features

1. Add API functions to \`lib/api.ts\`
2. Create types in \`lib/types.ts\`
3. Build components in \`components/\`
4. Add routes in \`app/\`

## Authentication Methods

### Username/Password
\`\`\`typescript
const response = await authApi.login(username, password);
\`\`\`

### Email OTP
\`\`\`typescript
// Request OTP
await authApi.requestEmailOTP(email);

// Verify OTP
const response = await authApi.verifyEmailOTP(email, otpCode);
\`\`\`

### 2FA (if enabled)
\`\`\`typescript
// If user has 2FA enabled
const response = await authApi.login(username, password);
// Returns: { requires_otp: true, temp_token: "..." }

// Then verify
await authApi.verifyOTP(tempToken, otpCode);
\`\`\`

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Docker

\`\`\`dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
\`\`\`

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

Proprietary - All rights reserved
\`\`\`

This frontend application provides a clean, modern interface for drivers to interact with the trucking management system!