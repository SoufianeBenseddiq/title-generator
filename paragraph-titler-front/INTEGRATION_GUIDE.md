# 🔗 Frontend-Backend Integration Guide

## ✅ What's Been Updated

All frontend API calls have been updated to match the backend endpoints:

### Authentication
- ✅ **Register**: `POST /register` (was `/auth/register`)
- ✅ **Login**: `POST /login` (was `/auth/login`, now uses `username` instead of `email`)
- ✅ **Get Profile**: `GET /me` (was `/auth/profile`)

### Paragraph Title Generation
- ✅ **Generate Title**: `POST /generate-title` (was `/paragraphs/generate`)
- ✅ **Get History**: `GET /saved-results` (was `/paragraphs/history`)
- ✅ **Delete Result**: `DELETE /saved-results/{result_id}` (new)

### Response Format Updates
- ✅ Updated to handle backend response format: `{ success, data, message }`
- ✅ Updated authentication to use `access_token` instead of `token`
- ✅ Updated user data structure to match backend

## 🚀 How to Test

### 1. Start the Backend
```powershell
cd ai_paragraph_titler_project
.\venv\Scripts\Activate.ps1
python main.py
```

Backend should be running at: **http://localhost:8000**

### 2. Start the Frontend
```powershell
cd paragraph-titler-front
npm install  # if you haven't already
npm run dev
```

Frontend should be running at: **http://localhost:3000** (or check the terminal output)

### 3. Test the Integration

1. **Register a new user:**
   - Go to http://localhost:3000/register
   - Fill in username, email, and password
   - Click "Sign Up"
   - You should be redirected to the dashboard

2. **Login:**
   - Go to http://localhost:3000/login
   - Use your **username** (not email) and password
   - Click "Sign In"
   - You should be redirected to the dashboard

3. **Generate a Title:**
   - On the dashboard, paste a paragraph
   - Click "Generate Title"
   - You should see the generated title appear

4. **View History:**
   - Click on "History" in the navigation
   - You should see all your previously generated titles

5. **View Profile:**
   - Click on "Profile" in the navigation
   - You should see your user information

## 🔧 Configuration

The frontend is configured to use `http://localhost:8000` as the default API URL.

If you need to change it, create a `.env` file in `paragraph-titler-front/`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### CORS Errors
- Make sure the backend is running
- Check that CORS in `main.py` allows `http://localhost:3000`
- The backend already has CORS configured for ports 3000 and 5173

### Authentication Errors
- Make sure you're using **username** (not email) for login
- Check that the token is being stored in localStorage
- Check browser console for detailed error messages

### API Connection Errors
- Verify backend is running at http://localhost:8000
- Check browser Network tab to see the actual API calls
- Verify the API endpoints match the backend

## 📝 API Endpoints Reference

### Backend Endpoints
- `POST /register` - Register new user
- `POST /login` - Login (username + password)
- `GET /me` - Get current user info
- `POST /generate-title` - Generate title for paragraph
- `GET /saved-results` - Get user's saved results
- `DELETE /saved-results/{id}` - Delete a saved result

### Frontend Routes
- `/` - Landing page
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Main title generation page
- `/history` - View saved titles
- `/profile` - User profile page

## ✅ Integration Checklist

- [x] API endpoints updated
- [x] Authentication flow updated
- [x] Response format handling updated
- [x] Login uses username instead of email
- [x] CORS configured in backend
- [x] Token storage and retrieval working
- [x] Error handling updated

## 🎉 You're All Set!

The frontend and backend are now fully integrated. Start both servers and test the application!

