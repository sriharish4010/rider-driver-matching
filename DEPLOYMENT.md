# 🚀 Deployment Guide - Rider-Driver Matching System

This guide covers deploying your Rider-Driver Matching System to various cloud platforms.

---

## 📋 Prerequisites

- GitHub repository: `https://github.com/sriharish4010/rider-driver-matching`
- Project uses:
  - **Frontend**: HTML/CSS/JavaScript (static files)
  - **Backend**: Flask + PySpark (Python)

---

## 🌐 Deployment Options

### **Option 1: Frontend Only (GitHub Pages)** ⭐ Easiest & Free

Perfect for the standalone frontend without backend API.

#### Steps:
1. Go to your GitHub repository settings
2. Navigate to **Pages** section
3. Under "Source", select branch: `main` and folder: `/ (root)`
4. Click **Save**
5. Your site will be live at: `https://sriharish4010.github.io/rider-driver-matching/`

**Note**: This deploys only the frontend. The matching algorithm runs in the browser using `dashboard.js`.

---

### **Option 2: Full Stack on Render** ⭐ Recommended for Backend

[Render](https://render.com) offers free tier and supports Python apps with PySpark.

#### Backend Deployment:

1. **Sign up** at [render.com](https://render.com)

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `rider-driver-matching-api`
     - **Environment**: `Python 3`
     - **Build Command**: `cd backend && pip install -r requirements.txt`
     - **Start Command**: `cd backend && python app.py`
     - **Instance Type**: Free

3. **Environment Variables** (Optional):
   - Add `PORT` (Render auto-provides this)
   - Add any other config from `backend/config.ini`

4. **Deploy**: Click "Create Web Service"
   - Your API will be at: `https://rider-driver-matching-api.onrender.com`

#### Frontend Deployment:

1. **Create Static Site** on Render:
   - Click "New +" → "Static Site"
   - Connect same GitHub repository
   - Configure:
     - **Name**: `rider-driver-matching`
     - **Build Command**: Leave empty (static HTML)
     - **Publish Directory**: `.` (root)

2. **Update Frontend** to use API:
   - Edit `assets/dashboard.js` and `assets/upload.js`
   - Replace `http://localhost:5000` with your Render API URL

---

### **Option 3: Railway** 🚂

[Railway](https://railway.app) - Simple deployment with free tier.

#### Steps:

1. **Sign up** at [railway.app](https://railway.app)

2. **Create New Project**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Configure**:
   - Railway auto-detects Python
   - Set **Root Directory**: `backend`
   - Add environment variables if needed

4. **Deploy**: Railway auto-deploys on push

---

### **Option 4: Heroku** 💜

Classic platform, easy deployment (paid after Nov 2022).

#### Steps:

1. **Install Heroku CLI**:
   ```bash
   # Already configured with Procfile and runtime.txt
   ```

2. **Login & Create App**:
   ```bash
   heroku login
   heroku create rider-driver-matching-api
   ```

3. **Deploy**:
   ```bash
   git push heroku main
   ```

4. **Open**:
   ```bash
   heroku open
   ```

---

### **Option 5: AWS/Azure/GCP** ☁️ Enterprise

For production deployments with high traffic:

#### AWS Elastic Beanstalk:
- Package backend as zip
- Upload to Elastic Beanstalk console
- Configure Python 3.11 environment

#### Azure App Service:
- Create App Service (Python 3.11)
- Deploy via GitHub Actions or CLI
- Configure startup command

#### Google Cloud Run:
- Create Dockerfile for backend
- Push to Container Registry
- Deploy to Cloud Run

---

## 🔧 Post-Deployment Configuration

### Update Frontend API Endpoints:

If deploying backend separately, update these files:

**assets/upload.js** (line ~50):
```javascript
const API_URL = 'https://your-api-url.com'; // Update this
```

**assets/dashboard.js** (line ~30):
```javascript
const API_URL = 'https://your-api-url.com'; // Update this
```

---

## ✅ Quick Start Recommendations

### For Demo/Testing:
- **Frontend**: GitHub Pages (free, instant)
- **Backend**: Not needed (use standalone mode)

### For Full Features:
- **Frontend**: Render Static Site or GitHub Pages
- **Backend**: Render Web Service (free tier)

### For Production:
- **Frontend**: Vercel/Netlify (CDN)
- **Backend**: AWS/Azure with autoscaling

---

## 🧪 Testing Your Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-api-url.com/health

# Upload test data
curl -X POST https://your-api-url.com/api/upload \
  -H "Content-Type: application/json" \
  -d '{"drivers": [...], "riders": [...]}'

# Get matches
curl https://your-api-url.com/api/match
```

---

## 📝 Environment Variables Needed

For backend deployment:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 5000 |
| `FLASK_ENV` | Environment | production |
| `SPARK_HOME` | Spark installation | Auto-detected |

---

## 🐛 Troubleshooting

### PySpark memory issues:
Add to environment variables:
```
PYSPARK_DRIVER_MEMORY=2g
PYSPARK_EXECUTOR_MEMORY=2g
```

### CORS errors:
Ensure `flask-cors` is installed and configured in `app.py`

### Build failures:
Check Python version matches `runtime.txt` (3.11.5)

---

## 📞 Need Help?

- Check logs: `heroku logs --tail` or platform-specific logs
- Verify requirements.txt has all dependencies
- Ensure PORT environment variable is used

---

**Your project is now deployment-ready! Choose the option that best fits your needs.** 🚀
