# 🚀 IIT BHU Placement Dashboard - Deployment Guide

## 📋 Prerequisites

- Python 3.9+
- Docker & Docker Compose (optional)
- Git

## 🔐 Environment Setup

1. **Copy environment template:**
   ```bash
   cp env_template.txt .env
   ```

2. **Edit `.env` file with your session IDs:**
   ```bash
   # Get these from your browser's developer tools when logged into placement portal
   PPO_SESSION_ID=your_actual_ppo_session_id
   INTERNSHIP_SESSION_ID=your_actual_internship_session_id
   ```

## 🐳 Docker Deployment (Recommended)

### Quick Start
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker
```bash
# Build image
docker build -t placement-dashboard .

# Run container
docker run -d \
  --name placement-dashboard \
  -p 5000:5000 \
  --env-file .env \
  placement-dashboard
```

## 🐍 Python Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python app.py
```

### Production Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

## ☁️ Cloud Deployment

### Heroku
1. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables:**
   ```bash
   heroku config:set PPO_SESSION_ID=your_session_id
   heroku config:set INTERNSHIP_SESSION_ID=your_session_id
   heroku config:set FLASK_ENV=production
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

### Railway
1. **Connect GitHub repository**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push**

### Render
1. **Connect GitHub repository**
2. **Set environment variables**
3. **Deploy automatically**

## 🔄 Updating Session IDs

When session expires:

1. **Get new session ID** from placement portal
2. **Update environment variable:**
   ```bash
   # For Docker
   docker-compose down
   # Edit .env file
   docker-compose up -d
   
   # For Heroku
   heroku config:set PPO_SESSION_ID=new_session_id
   heroku config:set INTERNSHIP_SESSION_ID=new_session_id
   ```

## 📊 Monitoring

- **Health Check:** `http://your-domain/health`
- **Dashboard:** `http://your-domain/`
- **API:** `http://your-domain/api/run-scrapers`

## 🛡️ Security Notes

- ✅ Session IDs are in environment variables
- ✅ `.env` file is in `.gitignore`
- ✅ Production mode disables debug
- ✅ Non-root Docker user
- ❌ Don't commit session IDs to Git
- ❌ Don't share `.env` file

## 🚨 Troubleshooting

### Common Issues

1. **Session expired:**
   - Update environment variables
   - Restart application

2. **Port already in use:**
   ```bash
   # Change port in .env
   PORT=5001
   ```

3. **Docker build fails:**
   ```bash
   # Clean build
   docker system prune -a
   docker build --no-cache .
   ```

### Logs
```bash
# Docker logs
docker-compose logs -f

# Python logs
tail -f app.log
```
