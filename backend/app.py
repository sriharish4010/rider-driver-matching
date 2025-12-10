"""
Flask REST API Server for PySpark Ride Matching System
Provides endpoints to match the frontend's existing functionality
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from spark_matcher import SparkRideMatcher
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize Spark matcher (singleton)
matcher = None

def get_matcher():
    """Get or create Spark matcher instance"""
    global matcher
    if matcher is None:
        matcher = SparkRideMatcher()
    return matcher

# In-memory storage for current session (can be replaced with database)
current_data = {
    "drivers": None,
    "riders": None,
    "drivers_df": None,
    "riders_df": None,
    "matches_df": None
}


@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        "service": "Ride-Sharing Matchmaking System - PySpark Backend",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "/api/upload": "POST - Upload drivers and riders data",
            "/api/match": "GET - Get driver-rider matches",
            "/api/analytics": "GET - Get analytics dashboard data",
            "/api/export": "GET - Export matches as JSON",
            "/health": "GET - Health check"
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "spark_active": matcher is not None
    })


@app.route('/api/upload', methods=['POST'])
def upload_data():
    """
    Upload drivers and riders data
    
    Expects JSON:
    {
        "drivers": [...],
        "riders": [...]
    }
    
    Returns validation results and analytics
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        drivers_data = data.get('drivers', [])
        riders_data = data.get('riders', [])
        
        # Validate data
        if not isinstance(drivers_data, list) or len(drivers_data) == 0:
            return jsonify({"error": "Drivers data must be a non-empty array"}), 400
        
        if not isinstance(riders_data, list) or len(riders_data) == 0:
            return jsonify({"error": "Riders data must be a non-empty array"}), 400
        
        # Validate driver fields
        for i, driver in enumerate(drivers_data):
            if 'driver_id' not in driver:
                return jsonify({"error": f"Driver at index {i} missing driver_id"}), 400
            if 'location' not in driver or not isinstance(driver['location'], list) or len(driver['location']) != 2:
                return jsonify({"error": f"Driver {driver.get('driver_id', i)} has invalid location"}), 400
            if 'vehicle_type' not in driver:
                return jsonify({"error": f"Driver {driver['driver_id']} missing vehicle_type"}), 400
        
        # Validate rider fields
        for i, rider in enumerate(riders_data):
            if 'rider_id' not in rider:
                return jsonify({"error": f"Rider at index {i} missing rider_id"}), 400
            if 'location' not in rider or not isinstance(rider['location'], list) or len(rider['location']) != 2:
                return jsonify({"error": f"Rider {rider.get('rider_id', i)} has invalid location"}), 400
        
        # Store data
        current_data["drivers"] = drivers_data
        current_data["riders"] = riders_data
        
        # Load into Spark
        spark_matcher = get_matcher()
        current_data["drivers_df"] = spark_matcher.load_drivers(drivers_data)
        current_data["riders_df"] = spark_matcher.load_riders(riders_data)
        
        # Calculate matches
        current_data["matches_df"] = spark_matcher.calculate_matches(
            current_data["drivers_df"],
            current_data["riders_df"],
            top_n=3
        )
        
        # Get analytics
        analytics = spark_matcher.get_analytics(
            current_data["drivers_df"],
            current_data["riders_df"],
            current_data["matches_df"]
        )
        
        return jsonify({
            "success": True,
            "message": f"Successfully processed {len(drivers_data)} drivers and {len(riders_data)} riders",
            "analytics": analytics
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/match', methods=['GET'])
def get_matches():
    """
    Get driver-rider matches
    
    Returns matches grouped by rider (same format as frontend JavaScript)
    """
    try:
        if current_data["matches_df"] is None:
            return jsonify({"error": "No data uploaded. Please upload drivers and riders first."}), 400
        
        spark_matcher = get_matcher()
        matches = spark_matcher.get_matches_by_rider(current_data["matches_df"])
        
        return jsonify({
            "success": True,
            "matches": matches
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Get analytics dashboard data (same as frontend dashboard)
    
    Returns:
    - driver_count
    - rider_count
    - avg_rating
    - match_count
    - vehicle_distribution
    """
    try:
        if current_data["drivers_df"] is None or current_data["riders_df"] is None:
            return jsonify({"error": "No data uploaded. Please upload drivers and riders first."}), 400
        
        spark_matcher = get_matcher()
        analytics = spark_matcher.get_analytics(
            current_data["drivers_df"],
            current_data["riders_df"],
            current_data["matches_df"]
        )
        
        return jsonify({
            "success": True,
            "analytics": analytics
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/export', methods=['GET'])
def export_results():
    """
    Export matches in the same format as frontend export
    
    Returns JSON with metadata and all matches
    """
    try:
        if current_data["matches_df"] is None:
            return jsonify({"error": "No data uploaded. Please upload drivers and riders first."}), 400
        
        spark_matcher = get_matcher()
        matches = spark_matcher.get_matches_by_rider(current_data["matches_df"])
        analytics = spark_matcher.get_analytics(
            current_data["drivers_df"],
            current_data["riders_df"],
            current_data["matches_df"]
        )
        
        export_data = {
            "metadata": {
                "exportDate": datetime.now().isoformat(),
                "totalDrivers": analytics["driver_count"],
                "totalRiders": analytics["rider_count"],
                "totalMatches": analytics["match_count"],
                "backend": "PySpark"
            },
            "matches": matches
        }
        
        return jsonify(export_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/match-single', methods=['POST'])
def match_single_rider():
    """
    Match a single rider with drivers
    
    Expects JSON:
    {
        "rider": {
            "rider_id": 999,
            "location": [12.97, 77.59],
            "preferred_vehicle": "Sedan",
            "urgency": "high"
        }
    }
    
    Returns top 3 matches for the rider
    """
    try:
        if current_data["drivers_df"] is None:
            return jsonify({"error": "No drivers uploaded. Please upload drivers first."}), 400
        
        data = request.get_json()
        if not data or 'rider' not in data:
            return jsonify({"error": "No rider data provided"}), 400
        
        rider_data = data['rider']
        
        # Validate rider
        if 'rider_id' not in rider_data:
            return jsonify({"error": "Rider missing rider_id"}), 400
        if 'location' not in rider_data or not isinstance(rider_data['location'], list):
            return jsonify({"error": "Rider has invalid location"}), 400
        
        # Create temporary rider DataFrame
        spark_matcher = get_matcher()
        temp_rider_df = spark_matcher.load_riders([rider_data])
        
        # Calculate matches
        matches_df = spark_matcher.calculate_matches(
            current_data["drivers_df"],
            temp_rider_df,
            top_n=3
        )
        
        # Get matches
        matches = spark_matcher.get_matches_by_rider(matches_df)
        
        return jsonify({
            "success": True,
            "rider_id": rider_data['rider_id'],
            "matches": matches[0] if len(matches) > 0 else {"top_matches": []}
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    """Get all drivers data"""
    try:
        if current_data["drivers"] is None:
            return jsonify({"error": "No drivers uploaded"}), 400
        
        return jsonify({
            "success": True,
            "drivers": current_data["drivers"]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/riders', methods=['GET'])
def get_riders():
    """Get all riders data"""
    try:
        if current_data["riders"] is None:
            return jsonify({"error": "No riders uploaded"}), 400
        
        return jsonify({
            "success": True,
            "riders": current_data["riders"]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/",
            "/health",
            "/api/upload",
            "/api/match",
            "/api/analytics",
            "/api/export",
            "/api/match-single",
            "/api/drivers",
            "/api/riders"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error", "details": str(e)}), 500


if __name__ == '__main__':
    # Load default data if available
    drivers_path = os.path.join('..', 'drivers.json')
    riders_path = os.path.join('..', 'riders.json')
    
    if os.path.exists(drivers_path) and os.path.exists(riders_path):
        print("Loading default data from drivers.json and riders.json...")
        try:
            with open(drivers_path, 'r') as f:
                drivers_data = json.load(f)
            with open(riders_path, 'r') as f:
                riders_data = json.load(f)
            
            current_data["drivers"] = drivers_data
            current_data["riders"] = riders_data
            
            spark_matcher = get_matcher()
            current_data["drivers_df"] = spark_matcher.load_drivers(drivers_data)
            current_data["riders_df"] = spark_matcher.load_riders(riders_data)
            current_data["matches_df"] = spark_matcher.calculate_matches(
                current_data["drivers_df"],
                current_data["riders_df"],
                top_n=3
            )
            
            print(f"✓ Loaded {len(drivers_data)} drivers and {len(riders_data)} riders")
        except Exception as e:
            print(f"Warning: Could not load default data: {e}")
    
    print("\n" + "="*70)
    print("🚀 PySpark Ride-Sharing Matchmaking Backend Starting...")
    print("="*70)
    print(f"Server running on: http://localhost:5000")
    print(f"API Documentation: http://localhost:5000/")
    print(f"Health Check: http://localhost:5000/health")
    print("="*70 + "\n")
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
