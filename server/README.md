# Email Bot API Server

A FastAPI-based backend for the Email Bot application with MongoDB Atlas integration and JWT authentication.

## 🚀 Features

- **MongoDB Atlas Integration**: Cloud-hosted NoSQL database
- **JWT Authentication**: Secure login and registration
- **Password Hashing**: bcrypt encryption for security
- **Email Service**: SMTP integration for sending emails
- **RESTful API**: Clean, documented endpoints
- **CORS Support**: Frontend integration ready

## 📋 Prerequisites

- Python 3.8+
- MongoDB Atlas account (free tier available)
- Gmail account for SMTP

## 🛠 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. MongoDB Atlas Setup

1. **Create MongoDB Atlas Account**:

   - Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Sign up for a free account
   - Create a new cluster (M0 Free tier)

2. **Configure Database**:

   - Create a database user with read/write permissions
   - Whitelist your IP address (or use 0.0.0.0/0 for development)
   - Get your connection string

3. **Run Setup Script**:
   ```bash
   python setup_mongodb.py
   ```
   - Enter your MongoDB Atlas credentials
   - This will create a `.env` file automatically

### 3. Environment Configuration

The setup script creates a `.env` file with:

```env
MONGODB_URL=mongodb+srv://emailbotuser:<password>@email-bot-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=email_bot
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
CORS_ORIGINS=["http://localhost:3000"]
```

### 4. Start the Server

```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication Endpoints

### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

### Login User

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <your-jwt-token>
```

### Logout

```http
POST /api/auth/logout
Authorization: Bearer <your-jwt-token>
```

## 🗄 Database Schema

### Users Collection

```javascript
{
  "_id": ObjectId,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "hashed_password": "bcrypt_hash",
  "created_at": ISODate,
  "last_login": ISODate,
  "is_active": true,
  "settings": {}
}
```

### Customers Collection

```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "name": "Customer Name",
  "email": "customer@example.com",
  "company": "Company Name",
  "phone": "+1234567890",
  "email_time": "09:00",
  "status": "active",
  "tags": ["vip", "corporate"],
  "created_at": ISODate,
  "last_email_sent": ISODate,
  "email_count": 5
}
```

## 🔧 Development

### Project Structure

```
server/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   └── security.py        # JWT and password utilities
│   ├── db/
│   │   └── mongodb.py         # Database connection
│   ├── models/
│   │   └── user.py           # Pydantic models
│   ├── routes/
│   │   └── auth.py           # Authentication endpoints
│   ├── services/
│   │   └── auth_service.py   # Business logic
│   └── main.py               # FastAPI application
├── requirements.txt          # Python dependencies
├── setup_mongodb.py         # Setup script
└── README.md                # This file
```

### Testing the API

1. **Health Check**:

   ```bash
   curl http://localhost:8000/health
   ```

2. **Register a User**:

   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
   ```

3. **Login**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

## 🚨 Security Notes

- Change the `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting for production
- Regular security updates

## 🐛 Troubleshooting

### MongoDB Connection Issues

1. Check your IP is whitelisted in MongoDB Atlas
2. Verify connection string format
3. Ensure database user has correct permissions

### JWT Token Issues

1. Check `SECRET_KEY` is set correctly
2. Verify token expiration time
3. Ensure proper Authorization header format

### Email Service Issues

1. Verify Gmail app password is correct
2. Check SMTP settings
3. Ensure 2FA is enabled on Gmail account

## 📞 Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review the logs for error messages
3. Verify your configuration in `.env` file

## 🔄 Next Steps

After setting up authentication:

1. Implement customer management endpoints
2. Add email campaign functionality
3. Create email templates system
4. Add reporting and analytics
5. Implement user roles and permissions
