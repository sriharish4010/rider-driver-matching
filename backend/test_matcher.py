"""
Test script for PySpark Ride Matcher
Run this to verify the matching algorithm works correctly
"""

import json
import sys
from spark_matcher import SparkRideMatcher

def test_basic_matching():
    """Test basic matching functionality"""
    print("\n" + "="*70)
    print("Testing PySpark Ride Matcher")
    print("="*70 + "\n")
    
    # Sample test data
    test_drivers = [
        {
            "driver_id": 1,
            "location": [12.9716, 77.5946],
            "vehicle_type": "Sedan",
            "rating": 4.8,
            "status": "available",
            "traffic_zone": "medium"
        },
        {
            "driver_id": 2,
            "location": [12.9750, 77.5900],
            "vehicle_type": "SUV",
            "rating": 4.5,
            "status": "available",
            "traffic_zone": "low"
        },
        {
            "driver_id": 3,
            "location": [12.9600, 77.6100],
            "vehicle_type": "Sedan",
            "rating": 4.9,
            "status": "busy",
            "traffic_zone": "high"
        }
    ]
    
    test_riders = [
        {
            "rider_id": 101,
            "location": [12.9700, 77.6000],
            "preferred_vehicle": "Sedan",
            "urgency": "high"
        }
    ]
    
    try:
        # Initialize matcher
        print("1. Initializing Spark Matcher...")
        matcher = SparkRideMatcher()
        print("   ✓ Spark session created successfully\n")
        
        # Load data
        print("2. Loading test data...")
        drivers_df = matcher.load_drivers(test_drivers)
        riders_df = matcher.load_riders(test_riders)
        print(f"   ✓ Loaded {len(test_drivers)} drivers")
        print(f"   ✓ Loaded {len(test_riders)} riders\n")
        
        # Calculate matches
        print("3. Calculating matches...")
        matches_df = matcher.calculate_matches(drivers_df, riders_df, top_n=3)
        matches_count = matches_df.count()
        print(f"   ✓ Generated {matches_count} matches\n")
        
        # Display matches
        print("4. Match Results:")
        print("-" * 70)
        matches_df.show(truncate=False)
        
        # Get analytics
        print("\n5. Analytics:")
        print("-" * 70)
        analytics = matcher.get_analytics(drivers_df, riders_df, matches_df)
        for key, value in analytics.items():
            print(f"   {key}: {value}")
        
        # Get matches by rider
        print("\n6. Matches by Rider:")
        print("-" * 70)
        matches_by_rider = matcher.get_matches_by_rider(matches_df)
        print(json.dumps(matches_by_rider, indent=2))
        
        # Stop Spark
        print("\n7. Cleaning up...")
        matcher.stop()
        print("   ✓ Spark session stopped\n")
        
        print("="*70)
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def test_with_actual_data():
    """Test with actual drivers.json and riders.json"""
    print("\n" + "="*70)
    print("Testing with Actual Data Files")
    print("="*70 + "\n")
    
    try:
        # Load actual data
        print("1. Loading actual data files...")
        with open('../drivers.json', 'r') as f:
            drivers_data = json.load(f)
        with open('../riders.json', 'r') as f:
            riders_data = json.load(f)
        
        print(f"   ✓ Loaded {len(drivers_data)} drivers from drivers.json")
        print(f"   ✓ Loaded {len(riders_data)} riders from riders.json\n")
        
        # Initialize matcher
        print("2. Initializing Spark Matcher...")
        matcher = SparkRideMatcher()
        print("   ✓ Spark session created\n")
        
        # Load into Spark
        print("3. Loading data into Spark DataFrames...")
        drivers_df = matcher.load_drivers(drivers_data)
        riders_df = matcher.load_riders(riders_data)
        print("   ✓ Data loaded successfully\n")
        
        # Calculate matches
        print("4. Calculating matches (this may take a moment)...")
        matches_df = matcher.calculate_matches(drivers_df, riders_df, top_n=3)
        print(f"   ✓ Matches calculated\n")
        
        # Get analytics
        print("5. Analytics Summary:")
        print("-" * 70)
        analytics = matcher.get_analytics(drivers_df, riders_df, matches_df)
        print(f"   Total Drivers: {analytics['driver_count']}")
        print(f"   Total Riders: {analytics['rider_count']}")
        print(f"   Average Rating: {analytics['avg_rating']}")
        print(f"   Total Matches: {analytics['match_count']}")
        print(f"   Vehicle Distribution:")
        for vehicle, count in analytics['vehicle_distribution'].items():
            print(f"      - {vehicle}: {count}")
        
        # Sample matches
        print("\n6. Sample Matches (first rider):")
        print("-" * 70)
        matches_by_rider = matcher.get_matches_by_rider(matches_df)
        if len(matches_by_rider) > 0:
            sample = matches_by_rider[0]
            print(f"   Rider ID: {sample['rider_id']}")
            print(f"   Preferred Vehicle: {sample['preferred_vehicle']}")
            print(f"   Urgency: {sample['urgency']}")
            print(f"\n   Top Matches:")
            for i, match in enumerate(sample['top_matches'], 1):
                print(f"      {i}. Driver {match['driver_id']} - {match['vehicle_type']}")
                print(f"         Distance: {match['distance_km']} km")
                print(f"         Rating: {match['rating']}")
                print(f"         Match Score: {match['match_score']}")
                print()
        
        # Stop Spark
        print("7. Cleaning up...")
        matcher.stop()
        print("   ✓ Spark session stopped\n")
        
        print("="*70)
        print("✓ ACTUAL DATA TEST PASSED!")
        print("="*70 + "\n")
        
        return True
        
    except FileNotFoundError:
        print("   ✗ Could not find drivers.json or riders.json")
        print("   Make sure to run this from the backend/ directory\n")
        return False
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PySpark Ride Matcher Test Suite")
    print("="*70)
    
    # Run basic test
    basic_passed = test_basic_matching()
    
    # Run actual data test
    actual_passed = test_with_actual_data()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Basic Matching Test: {'✓ PASSED' if basic_passed else '✗ FAILED'}")
    print(f"Actual Data Test: {'✓ PASSED' if actual_passed else '✗ FAILED'}")
    print("="*70 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if (basic_passed and actual_passed) else 1)
