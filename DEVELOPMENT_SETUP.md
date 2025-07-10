# Development Setup Guide

## 🚀 Quick Start for Localhost Development

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### 1. Backend Setup (FastAPI)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
cd server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will be available at:** http://localhost:8000

### 2. Frontend Setup (React)

```bash
# Install Node.js dependencies
cd client
npm install

# Start the development server
npm start
```

**Frontend will be available at:** http://localhost:3000

### 3. Environment Variables

The backend uses default values for development, but you can set these environment variables:

```bash
# Optional: Set environment variables for development
export MONGODB_URL="mongodb+srv://emailbotuser:Xa5EekvEr1cMEGUq@cluster0.wdvicn9.mongodb.net/emailbot?retryWrites=true&w=majority&appName=Cluster0"
export DATABASE_NAME="emailbot"
export SECRET_KEY="your-secret-key-change-this-in-production"
```

## 🔧 API Endpoints for Development

### Authentication Endpoints

| Endpoint             | Method | Description       | Request Body                                                                         |
| -------------------- | ------ | ----------------- | ------------------------------------------------------------------------------------ |
| `/api/auth/register` | POST   | Register new user | `{"email": "user@example.com", "password": "password123", "full_name": "User Name"}` |
| `/api/auth/login`    | POST   | Login user        | `{"email": "user@example.com", "password": "password123"}`                           |
| `/api/auth/me`       | GET    | Get current user  | Requires Authorization header                                                        |

### Health Check Endpoints

| Endpoint  | Method | Description          |
| --------- | ------ | -------------------- |
| `/health` | GET    | Server health check  |
| `/test`   | GET    | Simple test endpoint |

## 🧪 Testing the Registration Flow

### Manual Testing

1. **Backend Health Check:**

   ```bash
   curl http://localhost:8000/health
   ```

2. **Register a User:**

   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'
   ```

3. **Login with User:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123"}'
   ```

### Automated Testing

Run the test script to verify the complete flow:

```bash
node test_registration_flow.js
```

## 📁 Project Structure

```
Email_Bot-email_dev/
├── server/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── client/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Login.js     # Registration/Login component
│   │   ├── services/
│   │   │   └── authService.js # Authentication service
│   │   └── config.js        # API configuration
│   └── package.json         # Node.js dependencies
├── requirements.txt         # Backend dependencies
└── test_registration_flow.js # Test script
```

## 🔍 Troubleshooting

### Common Issues

1. **Backend not starting:**

   - Check if port 8000 is available
   - Verify Python dependencies are installed
   - Check MongoDB connection

2. **Frontend not starting:**

   - Check if port 3000 is available
   - Verify Node.js dependencies are installed
   - Check for any build errors

3. **Registration fails:**

   - Verify backend is running on http://localhost:8000
   - Check MongoDB connection
   - Ensure email is unique

4. **CORS issues:**
   - Backend is configured to allow all origins in development
   - Check browser console for CORS errors

### Debug Commands

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend is running
curl http://localhost:3000

# Check MongoDB connection
curl http://localhost:8000/health | grep database

# Test registration endpoint
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"debug@example.com","password":"debug123","full_name":"Debug User"}'
```

## 🎯 Development Workflow

1. **Start both servers:**

   ```bash
   # Terminal 1: Backend
   cd server && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   # Terminal 2: Frontend
   cd client && npm start
   ```

2. **Test the flow:**

   - Open http://localhost:3000
   - Navigate to registration page
   - Create a new account
   - Verify automatic login and redirect

3. **Monitor logs:**
   - Backend logs will show in the uvicorn terminal
   - Frontend logs will show in the browser console

## ✅ Verification Checklist

- [ ] Backend server running on http://localhost:8000
- [ ] Frontend server running on http://localhost:3000
- [ ] MongoDB connection working
- [ ] Registration endpoint responding
- [ ] Login endpoint responding
- [ ] Frontend can register new users
- [ ] Frontend can login with existing users
- [ ] JWT tokens are generated and stored
- [ ] User data is saved to database

## 🚀 Next Steps

After successful local development setup:

1. **Test all features** in the browser
2. **Check API documentation** at http://localhost:8000/docs
3. **Run the test script** to verify everything works
4. **Start developing** new features!

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check server logs for error messages
4. Run the test script to isolate issues
