"""
PySpark Backend Server - Keeps Spark UI alive
Runs matching algorithm and keeps UI accessible at http://localhost:4040
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, row_number
from pyspark.sql.window import Window
import time
import signal
import sys

# Global spark session
spark = None
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running, spark
    print("\n\n🛑 Shutting down Spark...")
    running = False
    if spark:
        try:
            spark.stop()
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def run_matching():
    """Run the matching algorithm - triggers Spark jobs"""
    global spark
    
    print("\n" + "="*70)
    print("🚀 SPARK RIDE-SHARING MATCHMAKING SYSTEM")
    print("="*70)
    
    # Initialize Spark
    spark = SparkSession.builder \
        .appName("RideMatchmaking") \
        .config("spark.ui.port", "4040") \
        .config("spark.driver.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.ui.enabled", "true") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    print(f"\n✅ Spark Session Created")
    print(f"🌐 Spark UI: http://localhost:4040")
    print(f"📊 Jobs and DAG visualizations will appear as operations run\n")
    
    try:
        # Load data
        print("📂 Loading datasets...")
        drivers = spark.read.option("multiline", "true").json("drivers.json")
        riders = spark.read.option("multiline", "true").json("riders.json")
        print(f"   ✅ Loaded {drivers.count()} drivers, {riders.count()} riders\n")
        
        # Prepare data
        print("🔄 Preparing data (Spark Job #1)...")
        drivers_prep = drivers \
            .filter(col("status") == "available") \
            .select(
                col("driver_id"),
                col("name").alias("driver_name"),
                col("location").getItem(0).alias("d_lat"),
                col("location").getItem(1).alias("d_lon"),
                col("vehicle_type"),
                col("rating"),
                col("traffic_zone")
            ).cache()
        
        riders_prep = riders \
            .select(
                col("rider_id"),
                col("location").getItem(0).alias("r_lat"),
                col("location").getItem(1).alias("r_lon"),
                col("preferred_vehicle"),
                col("urgency")
            ).cache()
        
        print(f"   ✅ {drivers_prep.count()} available drivers\n")
        
        # Cross join (Spark Job #2)
        print("🔀 Cross joining riders × drivers (Spark Job #2)...")
        matches = riders_prep.crossJoin(drivers_prep)
        total = matches.count()
        print(f"   ✅ Created {total} combinations\n")
        
        # Calculate distances (Spark Job #3)
        print("📏 Calculating Haversine distances (Spark Job #3)...")
        with_dist = matches.withColumn(
            "distance_km",
            expr("""
                6371 * 2 * ASIN(SQRT(
                    POW(SIN((RADIANS(d_lat) - RADIANS(r_lat)) / 2), 2) +
                    COS(RADIANS(r_lat)) * COS(RADIANS(d_lat)) *
                    POW(SIN((RADIANS(d_lon) - RADIANS(r_lon)) / 2), 2)
                ))
            """)
        ).filter(col("distance_km") <= 50).cache()
        
        within_range = with_dist.count()
        print(f"   ✅ {within_range} matches within 50km\n")
        
        # Compute scores (Spark Job #4)
        print("🎯 Computing match scores (Spark Job #4)...")
        scored = with_dist \
            .withColumn("dist_score", expr("GREATEST(0, 50 - (distance_km / 50.0 * 50))")) \
            .withColumn("veh_score", expr("CASE WHEN LOWER(preferred_vehicle) = LOWER(vehicle_type) THEN 30 ELSE 0 END")) \
            .withColumn("rating_score", expr("(rating / 5.0) * 20")) \
            .withColumn("traffic_w", expr("CASE WHEN LOWER(traffic_zone) = 'low' THEN 1.0 WHEN LOWER(traffic_zone) = 'high' THEN 0.75 ELSE 0.9 END")) \
            .withColumn("urgency_w", expr("CASE WHEN LOWER(urgency) = 'high' THEN 1.3 WHEN LOWER(urgency) = 'low' THEN 0.8 ELSE 1.0 END")) \
            .withColumn("match_score", expr("(dist_score + veh_score + rating_score) * traffic_w * urgency_w")) \
            .cache()
        
        avg_score = scored.agg({"match_score": "avg"}).collect()[0][0]
        print(f"   ✅ Average match score: {avg_score:.2f}\n")
        
        # Rank (Spark Job #5)
        print("🏆 Ranking top 3 matches per rider (Spark Job #5)...")
        window = Window.partitionBy("rider_id").orderBy(col("match_score").desc())
        ranked = scored.withColumn("rank", row_number().over(window))
        top3 = ranked.filter(col("rank") <= 3).cache()
        
        final_count = top3.count()
        print(f"   ✅ {final_count} top matches selected\n")
        
        # Analytics (Spark Jobs #6-8)
        print("📊 Computing analytics (Spark Jobs #6-8)...")
        
        vehicle_dist = top3.groupBy("vehicle_type").count().collect()
        print("   Vehicle distribution:")
        for row in vehicle_dist:
            print(f"      • {row['vehicle_type']}: {row['count']} matches")
        
        zone_dist = top3.groupBy("traffic_zone").count().collect()
        print("\n   Zone distribution:")
        for row in zone_dist:
            print(f"      • {row['traffic_zone']}: {row['count']} matches")
        
        # Save results (Spark Job #9)
        print("\n💾 Saving results (Spark Job #9)...")
        top3.select(
            "rider_id", "rank", "driver_id", "driver_name",
            "vehicle_type", "rating", "distance_km", "match_score", "traffic_zone"
        ).coalesce(1).write.mode("overwrite").csv("spark_output", header=True)
        print("   ✅ Saved to spark_output/\n")
        
        print("="*70)
        print("✅ ALL SPARK JOBS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n🌐 Spark UI: http://localhost:4040")
        print("   • Jobs tab - See 9 completed jobs")
        print("   • Stages tab - See execution stages with task details")
        print("   • SQL tab - See DataFrame query plans")
        print("   • DAG visualization - See query execution graphs")
        print("\n⏸️  Server running... Press Ctrl+C to stop\n")
        
    except Exception as e:
        print(f"\n❌ Error during matching: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main server loop"""
    global running, spark
    
    try:
        # Run matching algorithm
        run_matching()
        
        # Keep alive for UI access
        print("⏳ Keeping Spark UI alive...")
        while running:
            time.sleep(5)
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        print("\n🛑 Stopping Spark session...")
        if spark:
            try:
                spark.stop()
            except:
                pass
        print("✅ Stopped\n")

if __name__ == "__main__":
    main()
