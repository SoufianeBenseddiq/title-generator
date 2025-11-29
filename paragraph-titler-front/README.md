# Paragraph Titler - Frontend

A beautiful, responsive React.js frontend for the Paragraph Titler AI-powered title generation platform.

## Features

- 🎨 **Beautiful UI** - Modern, responsive design with smooth animations
- 🔐 **Authentication** - Secure login and registration system
- 📝 **Title Generation** - Generate AI-powered titles from paragraphs
- 📚 **History Tracking** - View all your generated titles and paragraphs
- 👤 **Profile Management** - View and edit your profile information
- 🎯 **Protected Routes** - Secure access to authenticated pages
- ⚡ **Fast & Responsive** - Optimized for all device sizes

## Tech Stack

- **React 18** - UI library
- **React Router** - Navigation and routing
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling and responsive design
- **Axios** - HTTP client for API calls
- **Context API** - State management for authentication

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend API running (see backend configuration)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```

Update the URL to match your backend API endpoint.

3. Start the development server:
```bash
npm run dev
```

The application will open at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The production build will be in the `dist` directory.

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── Navbar.jsx      # Navigation bar
│   └── ProtectedRoute.jsx  # Route protection
├── context/            # React Context
│   └── AuthContext.jsx # Authentication state
├── pages/              # Page components
│   ├── Landing.jsx     # Landing page
│   ├── Login.jsx       # Login page
│   ├── Register.jsx    # Registration page
│   ├── Dashboard.jsx   # Main title generation page
│   ├── History.jsx     # History page
│   └── Profile.jsx     # Profile page
├── services/           # API services
│   └── api.js         # API configuration and endpoints
├── App.jsx            # Main app component
├── main.jsx           # Entry point
└── index.css          # Global styles
```

## API Endpoints

The frontend expects the following backend endpoints:

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile

### Paragraphs
- `POST /paragraphs/generate` - Generate title from paragraph
- `GET /paragraphs/history` - Get user's paragraph history

### Expected Response Formats

**Register/Login:**
```json
{
  "status": "success",
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

**Generate Title:**
```json
{
  "status": "success",
  "message": "Title generated successfully",
  "object": {
    "title": "Generated Title",
    "paragraph": "Original paragraph text"
  }
}
```

**History:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Title",
      "paragraph": "Paragraph text",
      "user_id": 1,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## Features in Detail

### Landing Page
- Beautiful hero section with gradient text
- Feature highlights
- Call-to-action buttons
- Responsive design

### Authentication
- Secure login and registration
- Form validation
- Error handling
- Automatic token management

### Dashboard
- Paragraph input with character count
- Real-time title generation
- Success/error feedback
- Tips for best results

### History
- Grid layout of all generated titles
- Date formatting
- Empty state handling
- Responsive cards

### Profile
- View profile information
- Edit profile functionality
- Avatar with user initial
- Form validation

## Customization

### Styling
The app uses Tailwind CSS. Customize colors, animations, and styles in:
- `tailwind.config.js` - Tailwind configuration
- `src/index.css` - Global styles and utility classes

### API Configuration
Update the API base URL in:
- `.env` file for environment variables
- `src/services/api.js` for API configuration

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT

