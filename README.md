# Hotel Management System - Frontend

A modern React application for hotel booking and management, built with Vite and React Router.

## Features

- 🏨 **Landing Page** - Beautiful homepage showcasing hotel amenities and rooms
- 🔐 **Authentication** - User signup, login, and session management
- 📋 **Booking System** - Create and manage hotel bookings
- 👤 **Guest Dashboard** - View profile and bookings
- 🔧 **Admin Dashboard** - Manage bookings, view statistics, and update booking statuses
- 🎨 **Modern UI** - Responsive design with gradient themes

## Tech Stack

- **React 18** - UI library
- **React Router v6** - Routing
- **Axios** - HTTP client
- **Vite** - Build tool and dev server

## Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:5000
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ProtectedRoute.jsx    # Route protection for authenticated users
│   │   └── AdminRoute.jsx        # Route protection for admin users
│   ├── context/
│   │   └── AuthContext.jsx       # Authentication state management
│   ├── pages/
│   │   ├── Home.jsx              # Landing page
│   │   ├── Login.jsx             # Login page
│   │   ├── Signup.jsx            # Signup page
│   │   ├── Booking.jsx           # Booking form
│   │   ├── Dashboard.jsx         # Guest dashboard
│   │   └── AdminDashboard.jsx    # Admin dashboard
│   ├── services/
│   │   └── api.js                # API service with axios
│   ├── App.jsx                   # Main app component with routing
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── package.json
├── vite.config.js
└── index.html
```

## Available Routes

- `/` - Landing page (Home)
- `/login` - User login
- `/signup` - User registration
- `/booking` - Create booking (Protected)
- `/dashboard` - Guest dashboard (Protected)
- `/admin/dashboard` - Admin dashboard (Admin only)

## API Integration

The frontend communicates with the Flask backend API. Make sure the backend is running on `http://localhost:5000` (or update `VITE_API_URL` in `.env`).

### Key API Endpoints Used:

- `POST /signup` - User registration
- `POST /login` - User login
- `GET /me` - Get current user
- `POST /logout` - Logout user
- `POST /hotel_booking` - Create booking
- `GET /admin/dashboard/stats` - Get dashboard statistics
- `GET /admin/bookings` - Get all bookings
- `PUT /admin/bookings/:id/status` - Update booking status

## Building for Production

```bash
npm run build
```

The build output will be in the `dist` directory.

## Development

- The app uses Vite's hot module replacement for fast development
- API requests are automatically proxied from `/api` to the backend
- Cookies are handled automatically for authentication

## Notes

- The application uses cookie-based authentication
- Protected routes require authentication
- Admin routes require admin role
- All API calls include credentials (cookies) automatically

