"""
Python script to test the PySpark Backend API
Run this after starting the backend server
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health():
    """Test health endpoint"""
    print_section("1. Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload():
    """Test upload endpoint"""
    print_section("2. Testing Upload Data")
    
    # Load sample data
    try:
        with open('../drivers.json', 'r') as f:
            drivers = json.load(f)
        with open('../riders.json', 'r') as f:
            riders = json.load(f)
    except FileNotFoundError:
        print("❌ Error: drivers.json or riders.json not found")
        return False
    
    data = {
        "drivers": drivers,
        "riders": riders
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/upload",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_analytics():
    """Test analytics endpoint"""
    print_section("3. Testing Analytics")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        if result.get('success'):
            analytics = result['analytics']
            print(f"\n📊 Analytics Summary:")
            print(f"   Total Drivers: {analytics['driver_count']}")
            print(f"   Total Riders: {analytics['rider_count']}")
            print(f"   Average Rating: {analytics['avg_rating']}")
            print(f"   Total Matches: {analytics['match_count']}")
            print(f"   Vehicle Distribution:")
            for vehicle, count in analytics['vehicle_distribution'].items():
                print(f"      - {vehicle}: {count}")
        else:
            print(json.dumps(result, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_matches():
    """Test matches endpoint"""
    print_section("4. Testing Get Matches")
    try:
        response = requests.get(f"{BASE_URL}/api/match")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        if result.get('success'):
            matches = result['matches']
            print(f"\n🎯 Found {len(matches)} riders with matches")
            if len(matches) > 0:
                sample = matches[0]
                print(f"\nSample Match (Rider {sample['rider_id']}):")
                print(f"   Preferred Vehicle: {sample['preferred_vehicle']}")
                print(f"   Urgency: {sample['urgency']}")
                print(f"   Top Matches: {len(sample['top_matches'])}")
                for i, match in enumerate(sample['top_matches'][:3], 1):
                    print(f"\n   Match {i}:")
                    print(f"      Driver ID: {match['driver_id']}")
                    print(f"      Vehicle: {match['vehicle_type']}")
                    print(f"      Distance: {match['distance_km']} km")
                    print(f"      Rating: {match['rating']}")
                    print(f"      Score: {match['match_score']}")
        else:
            print(json.dumps(result, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_single_match():
    """Test single rider match"""
    print_section("5. Testing Single Rider Match")
    
    new_rider = {
        "rider": {
            "rider_id": 999,
            "location": [12.9750, 77.5950],
            "preferred_vehicle": "SUV",
            "urgency": "high"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/match-single",
            json=new_rider,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        result = response.json()
        if result.get('success'):
            print(f"\n✅ Matched Rider {result['rider_id']}")
            matches = result['matches']['top_matches']
            print(f"   Found {len(matches)} matches:")
            for i, match in enumerate(matches, 1):
                print(f"\n   {i}. Driver {match['driver_id']}")
                print(f"      Vehicle: {match['vehicle_type']}")
                print(f"      Distance: {match['distance_km']} km")
                print(f"      Score: {match['match_score']}")
        else:
            print(json.dumps(result, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_export():
    """Test export endpoint"""
    print_section("6. Testing Export")
    try:
        response = requests.get(f"{BASE_URL}/api/export")
        print(f"Status Code: {response.status_code}")
        result = response.json()
        if 'metadata' in result:
            print(f"\n📦 Export Metadata:")
            for key, value in result['metadata'].items():
                print(f"   {key}: {value}")
            print(f"\n✅ Export contains {len(result.get('matches', []))} rider matches")
        else:
            print(json.dumps(result, indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("  🔥 PySpark Backend API Test Suite")
    print("="*70)
    print(f"\nTesting API at: {BASE_URL}")
    print("Make sure the backend server is running!")
    print("Start with: python app.py")
    
    results = {
        "Health Check": test_health(),
        "Upload Data": test_upload(),
        "Analytics": test_analytics(),
        "Get Matches": test_matches(),
        "Single Match": test_single_match(),
        "Export": test_export()
    }
    
    # Summary
    print_section("TEST SUMMARY")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
