# 🔥 PySpark Backend - Ride-Sharing Matchmaking System

**Enterprise-Grade Backend using Apache Spark for Distributed Data Processing**

This backend implements the **exact same matching algorithm** as the frontend JavaScript version, but using **Apache Spark (PySpark)** for scalable, distributed data processing. All matching logic, scoring formulas, and business rules are preserved identically.

---

## 🌟 Features

- **100% Algorithm Parity** - Identical matching logic to frontend JavaScript
- **PySpark Processing** - Distributed data processing with Apache Spark
- **RESTful API** - Flask endpoints for all frontend operations
- **Scalable Architecture** - Handle thousands of drivers and riders
- **Real-time Matching** - Fast Haversine distance calculations
- **Complete Analytics** - Same dashboard metrics as frontend

---

## 📁 Backend Structure

```
backend/
├── app.py                  # Flask REST API server
├── spark_matcher.py        # PySpark matching engine (core logic)
├── requirements.txt        # Python dependencies
├── config.ini              # Configuration settings
├── start.bat               # Windows startup script
├── start.sh                # Unix/Linux/macOS startup script
├── test_matcher.py         # Test suite
└── .gitignore              # Git ignore patterns
```

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **Java 8/11** (for PySpark) - [Download Java](https://www.oracle.com/java/technologies/downloads/)

### Installation

#### Windows (PowerShell)

```powershell
cd backend
.\start.bat
```

#### Unix/Linux/macOS

```bash
cd backend
chmod +x start.sh
./start.sh
```

#### Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

The server will start at **http://localhost:5000**

---

## 🔌 API Endpoints

### 1. **Home / API Info**
```
GET /
```
Returns API documentation and available endpoints.

**Response:**
```json
{
  "service": "Ride-Sharing Matchmaking System - PySpark Backend",
  "version": "1.0",
  "status": "running",
  "endpoints": {...}
}
```

---

### 2. **Health Check**
```
GET /health
```
Check if the backend is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T10:30:00",
  "spark_active": true
}
```

---

### 3. **Upload Data**
```
POST /api/upload
Content-Type: application/json
```

Upload drivers and riders data for processing.

**Request Body:**
```json
{
  "drivers": [
    {
      "driver_id": 1,
      "location": [12.9716, 77.5946],
      "vehicle_type": "Sedan",
      "rating": 4.8,
      "status": "available",
      "traffic_zone": "medium"
    }
  ],
  "riders": [
    {
      "rider_id": 101,
      "location": [12.9700, 77.6000],
      "preferred_vehicle": "Sedan",
      "urgency": "high"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 15 drivers and 8 riders",
  "analytics": {
    "driver_count": 15,
    "rider_count": 8,
    "avg_rating": 4.6,
    "match_count": 24,
    "vehicle_distribution": {
      "Sedan": 5,
      "SUV": 4,
      "Hatchback": 4,
      "Luxury": 2
    }
  }
}
```

---

### 4. **Get Matches**
```
GET /api/match
```

Get all driver-rider matches (top 3 per rider).

**Response:**
```json
{
  "success": true,
  "matches": [
    {
      "rider_id": 101,
      "rider_location": [12.9700, 77.6000],
      "preferred_vehicle": "Sedan",
      "urgency": "high",
      "top_matches": [
        {
          "driver_id": 1,
          "vehicle_type": "Sedan",
          "rating": 4.8,
          "distance_km": 0.65,
          "match_score": 142.35,
          "traffic_zone": "medium"
        }
      ]
    }
  ]
}
```

---

### 5. **Get Analytics**
```
GET /api/analytics
```

Get dashboard analytics (same as frontend).

**Response:**
```json
{
  "success": true,
  "analytics": {
    "driver_count": 15,
    "rider_count": 8,
    "avg_rating": 4.6,
    "match_count": 24,
    "vehicle_distribution": {
      "Sedan": 5,
      "SUV": 4,
      "Hatchback": 4,
      "Luxury": 2
    }
  }
}
```

---

### 6. **Export Results**
```
GET /api/export
```

Export matches in JSON format (same as frontend export).

**Response:**
```json
{
  "metadata": {
    "exportDate": "2025-11-24T10:30:00",
    "totalDrivers": 15,
    "totalRiders": 8,
    "totalMatches": 24,
    "backend": "PySpark"
  },
  "matches": [...]
}
```

---

### 7. **Match Single Rider**
```
POST /api/match-single
Content-Type: application/json
```

Match a single rider against existing drivers.

**Request Body:**
```json
{
  "rider": {
    "rider_id": 999,
    "location": [12.97, 77.59],
    "preferred_vehicle": "Sedan",
    "urgency": "high"
  }
}
```

**Response:**
```json
{
  "success": true,
  "rider_id": 999,
  "matches": {
    "top_matches": [...]
  }
}
```

---

### 8. **Get Drivers**
```
GET /api/drivers
```

Retrieve all uploaded drivers.

---

### 9. **Get Riders**
```
GET /api/riders
```

Retrieve all uploaded riders.

---

## 🧮 PySpark Matching Algorithm

### Exact Implementation Details

The PySpark backend implements **100% identical logic** to the JavaScript frontend:

#### 1. **Haversine Distance** (same formula)
```python
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dLat = to_rad(lat2 - lat1)
    dLon = to_rad(lon2 - lon1)
    a = sin(dLat/2)^2 + cos(lat1) * cos(lat2) * sin(dLon/2)^2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c
```

#### 2. **Traffic Zone Weights** (same values)
- `low`: 1.0×
- `medium`: 0.9×
- `high`: 0.75×

#### 3. **Urgency Weights** (same values)
- `low`: 0.8×
- `medium`: 1.0×
- `high`: 1.3×

#### 4. **Scoring Components** (same bonuses)
- **Distance Score**: 0-100 points (closer = higher)
- **Vehicle Match Bonus**: +30 points
- **Rating Bonus**: 0-25 points (scaled from 0-5 stars)

#### 5. **Final Score Formula** (identical)
```
Score = (Distance Score + Vehicle Bonus + Rating Bonus) × Traffic Weight × Urgency Weight
```

#### 6. **Filtering** (same logic)
- Only `available` drivers are matched
- Top 3 drivers per rider
- Sorted by score (descending)

---

## 🧪 Testing

Run the test suite to verify the PySpark implementation:

```bash
python test_matcher.py
```

**Tests Include:**
1. Basic matching with sample data
2. Full test with actual `drivers.json` and `riders.json`
3. Analytics calculation
4. Data validation

**Expected Output:**
```
======================================
✓ ALL TESTS PASSED SUCCESSFULLY!
======================================
```

---

## 📊 PySpark Architecture

### Data Flow

```
1. Load JSON → Spark DataFrame
2. Extract lat/lon coordinates
3. Cross join riders × drivers
4. Calculate Haversine distances (UDF)
5. Apply traffic/urgency weights (UDFs)
6. Calculate vehicle match bonus (UDF)
7. Calculate rating bonus (UDF)
8. Compute final scores
9. Rank by score (Window function)
10. Return top N matches per rider
```

### Why PySpark?

- **Scalability**: Handle 100K+ drivers/riders
- **Performance**: Distributed computing
- **Analytics**: Built-in aggregation functions
- **Real-world**: Industry-standard for big data
- **Production-ready**: Enterprise architecture

---

## 🔧 Configuration

Edit `config.ini` to customize settings:

```ini
[spark]
driver_memory = 2g
executor_memory = 2g

[matching]
max_distance = 50        # km
top_matches = 3          # per rider
vehicle_match_bonus = 30
max_rating_bonus = 25

[traffic_weights]
low = 1.0
medium = 0.9
high = 0.75

[urgency_weights]
low = 0.8
medium = 1.0
high = 1.3
```

---

## 🐍 Code Structure

### `spark_matcher.py` - Core Engine

```python
class SparkRideMatcher:
    - __init__(): Initialize Spark session
    - _register_udfs(): Register custom functions
    - load_drivers(): Load driver data
    - load_riders(): Load rider data
    - calculate_matches(): Run matching algorithm
    - get_analytics(): Calculate metrics
    - get_matches_by_rider(): Group results
```

### `app.py` - Flask API

```python
Routes:
    / - API documentation
    /health - Health check
    /api/upload - Upload data
    /api/match - Get matches
    /api/analytics - Get analytics
    /api/export - Export results
    /api/match-single - Match one rider
    /api/drivers - Get drivers
    /api/riders - Get riders
```

---

## 🌐 Frontend Integration

### Option 1: Modify Frontend to Use Backend API

Update `assets/upload.js`:

```javascript
// Send data to backend instead of sessionStorage
const response = await fetch('http://localhost:5000/api/upload', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({drivers, riders})
});
```

### Option 2: Keep Both (Recommended)

- Frontend: Continues to work standalone
- Backend: Available as optional API service
- Best of both worlds!

---

## 📦 Dependencies

### Core
- **Flask 3.0.0** - Web framework
- **flask-cors 4.0.0** - CORS support
- **PySpark 3.5.0** - Spark engine

### Data Processing
- **numpy 1.24.3** - Numerical operations
- **pandas 2.0.3** - Data manipulation
- **pyarrow 14.0.1** - Performance optimization

### Development
- **pytest 7.4.3** - Testing
- **requests 2.31.0** - HTTP client

---

## 🔍 Troubleshooting

### Issue: Java not found

**Error:** `JAVA_HOME is not set`

**Solution:**
1. Install Java 8 or 11
2. Set environment variable:
   ```bash
   # Windows
   set JAVA_HOME=C:\Program Files\Java\jdk-11.0.12
   
   # Unix/Linux/macOS
   export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
   ```

### Issue: Port 5000 already in use

**Solution:** Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Spark memory error

**Solution:** Reduce memory in `spark_matcher.py`:
```python
.config("spark.driver.memory", "1g")
.config("spark.executor.memory", "1g")
```

---

## 📚 API Testing with cURL

```bash
# Upload data
curl -X POST http://localhost:5000/api/upload \
  -H "Content-Type: application/json" \
  -d @test_data.json

# Get matches
curl http://localhost:5000/api/match

# Get analytics
curl http://localhost:5000/api/analytics

# Export results
curl http://localhost:5000/api/export > results.json
```

---

## 📚 API Testing with Python

```python
import requests

# Upload data
with open('../drivers.json') as f:
    drivers = json.load(f)
with open('../riders.json') as f:
    riders = json.load(f)

response = requests.post('http://localhost:5000/api/upload', 
    json={'drivers': drivers, 'riders': riders})
print(response.json())

# Get matches
matches = requests.get('http://localhost:5000/api/match')
print(matches.json())
```

---

## 🎓 Educational Value

This backend demonstrates:

✅ **Apache Spark** - Industry-standard big data processing  
✅ **Distributed Computing** - Scalable algorithms  
✅ **RESTful APIs** - Professional web services  
✅ **UDFs** - Custom Spark functions  
✅ **DataFrames** - Spark SQL operations  
✅ **Window Functions** - Advanced analytics  
✅ **Geospatial Calculations** - Haversine distance  

Perfect for:
- Big Data coursework
- Spark/PySpark learning
- Backend development
- API design
- Academic projects

---

## 🚀 Production Deployment

### Docker (Future Enhancement)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Cloud Deployment Options

- **AWS**: Deploy on EC2 with EMR for Spark
- **Azure**: Use Azure Databricks + App Service
- **GCP**: Deploy on Compute Engine with Dataproc
- **Heroku**: Simple deployment with buildpacks

---

## 📝 Comparison: Frontend vs Backend

| Feature | Frontend (JS) | Backend (PySpark) |
|---------|--------------|-------------------|
| Algorithm | ✅ Identical | ✅ Identical |
| Distance Calc | Haversine | Haversine |
| Scoring | Same formula | Same formula |
| Weights | Same values | Same values |
| Top N | 3 per rider | 3 per rider |
| Processing | Client-side | Server-side |
| Scalability | Limited | Unlimited |
| Distribution | Browser | Spark cluster |
| Data Size | Small datasets | Big data ready |

---

## 🤝 Contributing

Enhancements welcome:
- [ ] Add database persistence (PostgreSQL/MongoDB)
- [ ] Implement caching (Redis)
- [ ] Add authentication (JWT)
- [ ] Real-time updates (WebSockets)
- [ ] Dockerize backend
- [ ] Add machine learning scoring
- [ ] Implement surge pricing

---

## 📄 License

Free to use for educational purposes.

---

## 📞 Support

**Issues?**
1. Check `test_matcher.py` output
2. Verify Java installation
3. Check Flask logs
4. Review Spark logs in console

---

**Built with 💙 using PySpark, Flask, and Python**

🌟 **Perfect blend of frontend simplicity + backend scalability!**

---

## 🎯 Summary

✅ **PySpark backend fully implemented**  
✅ **100% algorithm parity with frontend**  
✅ **RESTful API with 9 endpoints**  
✅ **Complete test suite**  
✅ **Production-ready architecture**  
✅ **Scalable to big data**  
✅ **Easy to deploy and run**  

**No frontend code was changed or removed - everything still works!**
