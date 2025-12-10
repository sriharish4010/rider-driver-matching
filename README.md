# 🔹 Ride-Sharing Matchmaking System

**Real-Time Driver & Rider Matching with Neon Cyber Theme + PySpark Backend**

A futuristic web application demonstrating intelligent ride-sharing matchmaking algorithms similar to Uber/Ola platforms. Features beautiful neon blue & purple glowing UI with glassmorphism effects, now powered by **Apache Spark (PySpark)** backend for scalable, enterprise-grade processing.

---

## 🌟 Features

- **Smart Matchmaking Algorithm** - Uses Haversine distance, traffic zones, urgency weights, and vehicle preferences
- **🔥 PySpark Backend** - Enterprise-grade distributed data processing with Apache Spark
- **Dual Architecture** - Frontend works standalone OR with backend API
- **Real-time Analytics Dashboard** - Interactive charts showing driver/rider counts and vehicle distribution
- **Neon Cyber UI** - Stunning glowing effects, smooth animations, and glassmorphism design
- **RESTful API** - 9 endpoints for all matchmaking operations
- **Data Export** - Download matched results as JSON
- **Fully Responsive** - Works seamlessly on desktop, tablet, and mobile devices
- **100% Algorithm Parity** - Backend implements identical matching logic

---

## 📁 Project Structure

```
RDM/
├── index.html              # Landing page with hero section
├── upload.html             # Dataset upload interface
├── dashboard.html          # Analytics dashboard with charts
├── assets/
│   ├── styles.css          # Neon/glass styling with animations
│   ├── upload.js           # File validation & session storage
│   └── dashboard.js        # Matching logic & Chart.js visualizations
├── backend/                # 🔥 NEW: PySpark Backend
│   ├── app.py              # Flask REST API server
│   ├── spark_matcher.py    # PySpark matching engine (core logic)
│   ├── requirements.txt    # Python dependencies
│   ├── config.ini          # Configuration settings
│   ├── start.bat           # Windows startup script
│   ├── start.sh            # Unix/Linux/macOS startup script
│   ├── test_matcher.py     # Test suite
│   ├── README.md           # Backend documentation
│   └── QUICKSTART.md       # Backend quick start
├── drivers.json            # Sample driver dataset (15 drivers)
├── riders.json             # Sample rider dataset (8 riders)
└── README.md               # This file
```

---

## 🚀 Quick Start

### Frontend Only (Original)

#### Method 1: Direct Open (Simplest)

1. Open `index.html` in your web browser
2. Click **"📤 Upload Dataset"**
3. Upload `drivers.json` and `riders.json`
4. View the dashboard with charts and matches

#### Method 2: Local Server (Recommended)

From the project folder in PowerShell:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

Alternative with Node.js:
```powershell
npx serve
```

### 🔥 NEW: PySpark Backend

#### Quick Start (1 Minute)

**Windows:**
```powershell
cd backend
.\start.bat
```

**Unix/Linux/macOS:**
```bash
cd backend
chmod +x start.sh
./start.sh
```

Backend API starts at **http://localhost:5000**

#### Test Backend
```bash
cd backend
python test_matcher.py
```

#### API Usage
```bash
# Get API info
curl http://localhost:5000/

# Upload data and get matches
curl -X POST http://localhost:5000/api/upload \
  -H "Content-Type: application/json" \
  -d @sample_data.json

# Get matches
curl http://localhost:5000/api/match

# Get analytics
curl http://localhost:5000/api/analytics
```

**See `backend/README.md` for complete API documentation**

---

## 📊 How It Works

### 1. Upload Page
- Validates JSON files for correct structure
- Checks required fields (driver_id, rider_id, location, etc.)
- Stores data in browser `sessionStorage`
- Provides helpful error messages for invalid data

### 2. Matching Algorithm

The system scores each driver for each rider based on:

**Distance Score** (0-100 points)
- Calculated using Haversine formula
- Closer drivers get higher scores
- Normalized over 50km window

**Vehicle Preference Match** (+30 points)
- Bonus if driver's vehicle matches rider's preference

**Driver Rating Bonus** (0-25 points)
- Higher-rated drivers score better
- Scaled from 0-5 star rating

**Traffic Zone Weight** (×0.75 to ×1.0)
- `low` traffic: 1.0× multiplier
- `medium` traffic: 0.9× multiplier
- `high` traffic: 0.75× multiplier

**Urgency Weight** (×0.8 to ×1.3)
- `high` urgency: 1.3× multiplier
- `medium` urgency: 1.0× multiplier
- `low` urgency: 0.8× multiplier

**Final Score** = (Distance + Vehicle Bonus + Rating Bonus) × Traffic Weight × Urgency Weight

### 3. Dashboard

Displays:
- **Metric Cards** - Total drivers, riders, matches, avg rating
- **Bar Chart** - Driver vs Rider count comparison
- **Pie Chart** - Vehicle type distribution
- **Match List** - Top 3 driver recommendations per rider with scores

---

## 📥 Input Format

### drivers.json
```json
[
  {
    "driver_id": 1,
    "location": [12.9716, 77.5946],
    "vehicle_type": "Sedan",
    "rating": 4.8,
    "status": "available",
    "traffic_zone": "medium"
  }
]
```

**Required Fields:**
- `driver_id` (number/string) - Unique driver identifier
- `location` (array) - [latitude, longitude] as numbers
- `vehicle_type` (string) - Sedan, SUV, Hatchback, Luxury, etc.

**Optional Fields:**
- `rating` (number) - 0-5 star rating
- `status` (string) - "available" or "busy"
- `traffic_zone` (string) - "low", "medium", or "high"

### riders.json
```json
[
  {
    "rider_id": 101,
    "location": [12.9700, 77.6000],
    "preferred_vehicle": "Sedan",
    "urgency": "high"
  }
]
```

**Required Fields:**
- `rider_id` (number/string) - Unique rider identifier
- `location` (array) - [latitude, longitude] as numbers

**Optional Fields:**
- `preferred_vehicle` (string) - Sedan, SUV, Hatchback, etc.
- `urgency` (string) - "low", "medium", or "high"

---

## 🎨 Technologies Used

### Frontend
- **HTML5** - Semantic structure
- **CSS3** - Neon effects, animations, glassmorphism, gradients
- **JavaScript (ES6+)** - FileReader API, sessionStorage, algorithms
- **Chart.js** - Interactive bar & pie charts (via CDN)

### 🔥 Backend (NEW)
- **PySpark 3.5.0** - Apache Spark for distributed data processing
- **Flask 3.0.0** - RESTful API framework
- **Python 3.8+** - Backend programming
- **Pandas** - Data manipulation
- **NumPy** - Numerical operations

---

## ✨ Key Algorithms

### Haversine Distance Formula
```javascript
function haversine([lat1, lon1], [lat2, lon2]) {
  const toRad = v => v * Math.PI / 180;
  const R = 6371; // Earth radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat/2)**2 + 
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * 
            Math.sin(dLon/2)**2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}
```

---

## 🎯 Use Cases

Perfect for:
- **Mini/Major Projects** - Academic assignments
- **Viva Presentations** - Live demonstration
- **Lab Exams** - Quick setup and demo
- **Portfolio/Resume** - GitHub showcase
- **Learning** - Study real-world algorithms

---

## 🔧 Customization

### Adjust Scoring Weights

Edit `assets/dashboard.js`:
```javascript
// Change distance window
const maxDist = 50; // km

// Modify bonuses
const vehicleBonus = 30;  // vehicle match bonus
const ratingBonus = 25;   // max rating bonus

// Adjust traffic weights
function trafficWeight(zone) {
  if(zone === 'low') return 1.0;
  if(zone === 'medium') return 0.9;
  if(zone === 'high') return 0.75;
}
```

---

## 🔧 Customization

### Frontend Scoring Weights

Edit `assets/dashboard.js`:
```javascript
// Change distance window
const maxDist = 50; // km

// Modify bonuses
const vehicleBonus = 30;  // vehicle match bonus
const ratingBonus = 25;   // max rating bonus

// Adjust traffic weights
function trafficWeight(zone) {
  if(zone === 'low') return 1.0;
  if(zone === 'medium') return 0.9;
  if(zone === 'high') return 0.75;
}
```

### Backend Configuration

Edit `backend/config.ini`:
```ini
[matching]
max_distance = 50
top_matches = 3
vehicle_match_bonus = 30
max_rating_bonus = 25

[traffic_weights]
low = 1.0
medium = 0.9
high = 0.75
```

### Change Color Scheme

Edit `assets/styles.css`:
```css
:root {
  --neon-blue: #00e5ff;     /* Primary color */
  --neon-purple: #b23cff;   /* Accent color */
}
```

---

## 📤 Export Feature

Click **"💾 Export Results"** on the dashboard to download a JSON file containing:
- Metadata (export date, totals)
- All matches with scores and details
- Ready for further processing or reporting

---

## 🐛 Troubleshooting

### Frontend Issues

**Problem:** Charts not displaying
- **Solution:** Ensure internet connection (Chart.js loads from CDN)

**Problem:** "No datasets found" error
- **Solution:** Upload files again from the Upload page

**Problem:** Invalid JSON error
- **Solution:** Validate JSON format using jsonlint.com

**Problem:** No matches found
- **Solution:** Ensure drivers have `status: "available"`

### Backend Issues

**Problem:** Java not found (PySpark)
- **Solution:** Install Java 8/11 and set JAVA_HOME environment variable

**Problem:** Port 5000 already in use
- **Solution:** Change port in `backend/app.py` to 5001 or other available port

**Problem:** Spark memory error
- **Solution:** Reduce memory settings in `backend/spark_matcher.py`

**Problem:** Module not found
- **Solution:** Run `pip install -r backend/requirements.txt`

---
- **Solution:** Upload files again from the Upload page

**Problem:** Invalid JSON error
- **Solution:** Validate JSON format using jsonlint.com

**Problem:** No matches found
- **Solution:** Ensure drivers have `status: "available"`

---

## 🎓 Academic Context

This project demonstrates:

### Frontend
- ✅ **Data Structures** - Arrays, objects, maps
- ✅ **Algorithms** - Haversine, scoring, sorting
- ✅ **File I/O** - FileReader API
- ✅ **Data Visualization** - Chart.js integration
- ✅ **Web Storage** - sessionStorage API
- ✅ **Responsive Design** - Mobile-first CSS

### 🔥 Backend (NEW)
- ✅ **Apache Spark** - Distributed data processing
- ✅ **PySpark DataFrames** - Structured data operations
- ✅ **RESTful APIs** - Professional web services
- ✅ **UDFs (User Defined Functions)** - Custom Spark functions
- ✅ **Window Functions** - Advanced analytics
- ✅ **Big Data Architecture** - Scalable system design
- ✅ **Geospatial Computing** - Distance calculations at scale

Perfect for:
- Mini/Major Projects with **Big Data** component
- Spark/PySpark coursework
- Backend development learning
- Academic presentations requiring scalability demos

Inspired by real-world ride-sharing platforms, now **fully implemented with Apache Spark backend**.

---

## 🚀 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Original)                   │
│  HTML + CSS + JavaScript + Chart.js                     │
│  • Works standalone (no backend needed)                 │
│  • Client-side matching algorithm                       │
│  • SessionStorage data                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Optional
                     │ REST API
                     │
┌────────────────────▼────────────────────────────────────┐
│              BACKEND (NEW - PySpark)                     │
│  Flask REST API + PySpark Engine                        │
│  • Server-side distributed processing                   │
│  • Identical matching algorithm                         │
│  • Scalable to millions of records                      │
│  • 9 API endpoints                                      │
└─────────────────────────────────────────────────────────┘
```

**Key Point:** Both work independently! Frontend doesn't require backend.

---

## 📝 License

Free to use for educational purposes. Feel free to modify and extend!

---

## 🤝 Contributing

Suggestions for improvement:

### Frontend
- [ ] Add real-time driver movement simulation
- [ ] Implement Hungarian algorithm for optimal 1-to-1 matching
- [ ] Add map visualization with markers
- [ ] Create driver acceptance/rejection simulation
- [ ] Implement surge pricing logic

### Backend
- [x] ✅ PySpark backend implementation
- [ ] Add database persistence (PostgreSQL/MongoDB)
- [ ] Implement caching with Redis
- [ ] Add authentication (JWT)
- [ ] Real-time updates via WebSockets
- [ ] Docker containerization
- [ ] Machine learning-based scoring
- [ ] Kubernetes deployment configs

---

## 📞 Support

### Frontend Issues
1. Check this README thoroughly
2. Validate your JSON files at jsonlint.com
3. Open browser console (F12) for error messages
4. Ensure all files are in correct directory structure

### Backend Issues
1. Check `backend/README.md` for detailed documentation
2. Run `python backend/test_matcher.py` to verify installation
3. Check Flask logs in terminal
4. Verify Java installation for PySpark
5. Review Spark logs for detailed errors

---

**Made with ❤️ using HTML, CSS, JavaScript, Chart.js, PySpark & Flask**

🌟 **Dual Architecture: Simple frontend + Enterprise backend!**

---

## 📋 Summary

✅ **Frontend** - Beautiful UI, works standalone, client-side matching  
✅ **🔥 Backend** - PySpark distributed processing, RESTful API, enterprise-scale  
✅ **Algorithm Parity** - 100% identical matching logic in both  
✅ **Optional Integration** - Use backend API or keep frontend-only  
✅ **Production Ready** - Complete with tests, docs, and deployment scripts  
✅ **Educational** - Perfect for academic projects demonstrating full-stack + big data  

**No existing code was removed - all frontend logic preserved!**

---

For questions or issues:
1. Check this README thoroughly
2. Validate your JSON files
3. Open browser console (F12) for error messages
4. Ensure all files are in correct directory structure

---

**Made with ❤️ using HTML, CSS, JavaScript & Chart.js**

🌟 Star this project if you find it useful!
