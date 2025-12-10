"""
PySpark Backend - Keeps Spark UI Running
This script processes ride-sharing matches and keeps the Spark UI alive
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, row_number
from pyspark.sql.window import Window
import time
import signal
import sys

# Global variable to control the loop
keep_running = True

def signal_handler(sig, frame):
    global keep_running
    print('\n\n🛑 Stopping Spark...')
    keep_running = False

signal.signal(signal.SIGINT, signal_handler)

def main():
    print("\n" + "="*70)
    print("🚀 SPARK RIDE-SHARING MATCHMAKING BACKEND")
    print("="*70)
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("RideMatchmaking") \
        .config("spark.ui.port", "4040") \
        .config("spark.driver.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    print(f"\n✅ Spark Session Started")
    print(f"🌐 Spark UI: http://localhost:4040")
    print(f"📊 Processing ride-sharing matchmaking data...\n")
    
    try:
        # Load datasets
        print("Loading datasets...")
        drivers = spark.read.option("multiline", "true").json("drivers.json")
        riders = spark.read.option("multiline", "true").json("riders.json")
        
        # Filter available drivers
        drivers_available = drivers.filter(col("status") == "available")
        
        # Prepare data with renamed columns
        drivers_prep = drivers_available.select(
            col("driver_id"),
            col("name").alias("driver_name"),
            col("location").getItem(0).alias("d_lat"),
            col("location").getItem(1).alias("d_lon"),
            col("vehicle_type"),
            col("rating"),
            col("traffic_zone")
        )
        
        riders_prep = riders.select(
            col("rider_id"),
            col("location").getItem(0).alias("r_lat"),
            col("location").getItem(1).alias("r_lon"),
            col("preferred_vehicle"),
            col("urgency")
        )
        
        # Cross join - SPARK JOB #1
        print("✓ Cross joining riders and drivers...")
        combinations = riders_prep.crossJoin(drivers_prep)
        
        # Calculate Haversine distance - SPARK JOB #2
        print("✓ Calculating distances...")
        with_distance = combinations.withColumn(
            "distance_km",
            expr("""
                6371 * 2 * ASIN(SQRT(
                    POW(SIN((RADIANS(d_lat) - RADIANS(r_lat)) / 2), 2) +
                    COS(RADIANS(r_lat)) * COS(RADIANS(d_lat)) *
                    POW(SIN((RADIANS(d_lon) - RADIANS(r_lon)) / 2), 2)
                ))
            """)
        )
        
        # Filter by distance
        in_range = with_distance.filter(col("distance_km") <= 50)
        
        # Calculate match scores - SPARK JOB #3
        print("✓ Computing match scores...")
        scored = in_range \
            .withColumn("dist_score", expr("GREATEST(0, 50 - (distance_km / 50.0 * 50))")) \
            .withColumn("veh_score", expr("CASE WHEN LOWER(preferred_vehicle) = LOWER(vehicle_type) THEN 30 ELSE 0 END")) \
            .withColumn("rating_score", expr("(rating / 5.0) * 20")) \
            .withColumn("traffic_w", expr("CASE WHEN LOWER(traffic_zone) = 'low' THEN 1.0 WHEN LOWER(traffic_zone) = 'high' THEN 0.75 ELSE 0.9 END")) \
            .withColumn("urgency_w", expr("CASE WHEN LOWER(urgency) = 'high' THEN 1.3 WHEN LOWER(urgency) = 'low' THEN 0.8 ELSE 1.0 END")) \
            .withColumn("match_score", expr("(dist_score + veh_score + rating_score) * traffic_w * urgency_w"))
        
        # Rank matches per rider - SPARK JOB #4
        print("✓ Ranking matches...")
        window_spec = Window.partitionBy("rider_id").orderBy(col("match_score").desc())
        ranked = scored.withColumn("rank", row_number().over(window_spec))
        
        # Get top 3 matches per rider
        top3 = ranked.filter(col("rank") <= 3)
        
        # Force computation and caching - SPARK JOB #5
        print("✓ Caching results...")
        top3.cache()
        total_matches = top3.count()
        
        print(f"\n{'='*70}")
        print(f"📊 RESULTS SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Total Top Matches: {total_matches}")
        
        # Compute analytics - More Spark jobs
        print("\n✓ Computing analytics...")
        
        # Average score - SPARK JOB #6
        avg_score_row = top3.agg({"match_score": "avg"}).collect()[0]
        avg_score = avg_score_row[0]
        print(f"   Average Match Score: {avg_score:.2f}")
        
        # Vehicle distribution - SPARK JOB #7
        vehicle_counts = top3.groupBy("vehicle_type").count().collect()
        print(f"   Vehicle Types: {len(vehicle_counts)} categories")
        
        # Traffic zones - SPARK JOB #8
        zone_counts = top3.groupBy("traffic_zone").count().collect()
        print(f"   Traffic Zones: {len(zone_counts)} zones")
        
        # Save results - SPARK JOB #9
        print("\n✓ Saving results to spark_output/...")
        output_path = "spark_output/matches"
        top3.select(
            "rider_id", "rank", "driver_id", "driver_name",
            "vehicle_type", "rating", "distance_km", "match_score", "traffic_zone"
        ).coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)
        
        print(f"\n{'='*70}")
        print(f"✅ ALL SPARK JOBS COMPLETED SUCCESSFULLY!")
        print(f"{'='*70}")
        print(f"\n🌐 Spark UI is running at: http://localhost:4040")
        print(f"📁 Results saved to: {output_path}/")
        print(f"\nYou can now:")
        print(f"  • Open Spark UI to see Jobs, Stages, and DAG visualization")
        print(f"  • Click Jobs tab to see all 9+ completed jobs")
        print(f"  • Click SQL tab to see DataFrame operations")
        print(f"  • View execution plans and performance metrics")
        print(f"\n⏸️  Keeping Spark UI alive... Press Ctrl+C to stop")
        print(f"{'='*70}\n")
        
        # Keep the process alive so Spark UI remains accessible
        global keep_running
        while keep_running:
            time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Received stop signal")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔄 Cleaning up...")
        spark.stop()
        print("✅ Spark stopped cleanly\n")

if __name__ == "__main__":
    main()
