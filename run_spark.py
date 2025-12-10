"""
PySpark Ride-Sharing Matchmaking - Production Ready
Run this to see Spark Jobs and DAG graphs in the UI
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, row_number
from pyspark.sql.window import Window
from pyspark.sql.types import DoubleType
import math

def create_spark_session():
    """Initialize Spark with proper configuration"""
    return SparkSession.builder \
        .appName("RideSharingMatchmaking") \
        .config("spark.ui.port", "4040") \
        .config("spark.driver.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

def haversine_distance(df, lat1_col, lon1_col, lat2_col, lon2_col, result_col="distance_km"):
    """Calculate haversine distance between two GPS points"""
    return df.withColumn(
        result_col,
        expr(f"""
            6371 * 2 * ASIN(SQRT(
                POW(SIN((RADIANS({lat2_col}) - RADIANS({lat1_col})) / 2), 2) +
                COS(RADIANS({lat1_col})) * COS(RADIANS({lat2_col})) *
                POW(SIN((RADIANS({lon2_col}) - RADIANS({lon1_col})) / 2), 2)
            ))
        """)
    )

def main():
    print("\n" + "="*70)
    print("🚀 SPARK RIDE-SHARING MATCHMAKING SYSTEM")
    print("="*70 + "\n")
    
    # Initialize Spark
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    ui_url = spark.sparkContext.uiWebUrl
    print(f"✅ Spark Session Created")
    print(f"🌐 Spark UI: {ui_url}")
    print(f"📊 Open in browser to see Jobs and DAG visualization\n")
    
    try:
        # Load datasets
        print("📂 Loading datasets...")
        drivers_raw = spark.read.option("multiline", "true").json("drivers.json")
        riders_raw = spark.read.option("multiline", "true").json("riders.json")
        
        print(f"   • Drivers: {drivers_raw.count()}")
        print(f"   • Riders: {riders_raw.count()}\n")
        
        # Filter available drivers
        drivers = drivers_raw.filter(col("status") == "available")
        riders = riders_raw
        
        # Prepare data with unique column names
        print("🔄 Preparing data for matching...")
        drivers_prep = drivers.selectExpr(
            "driver_id",
            "name as driver_name",
            "location[0] as driver_lat",
            "location[1] as driver_lon",
            "vehicle_type",
            "rating",
            "traffic_zone"
        ).cache()
        
        riders_prep = riders.selectExpr(
            "rider_id",
            "location[0] as rider_lat",
            "location[1] as rider_lon",
            "preferred_vehicle",
            "urgency"
        ).cache()
        
        # Cross join - this creates a Spark job
        print("🔀 Performing cross join (Spark Job #1)...")
        matches = riders_prep.crossJoin(drivers_prep)
        total_combinations = matches.count()
        print(f"   ✅ Created {total_combinations} combinations\n")
        
        # Calculate distances - Spark job #2
        print("📏 Calculating distances (Spark Job #2)...")
        matches_with_dist = haversine_distance(
            matches,
            "rider_lat", "rider_lon",
            "driver_lat", "driver_lon"
        )
        
        # Filter by distance
        matches_filtered = matches_with_dist.filter(col("distance_km") <= 50)
        within_range = matches_filtered.count()
        print(f"   ✅ {within_range} matches within 50km\n")
        
        # Calculate scores - Spark job #3
        print("🎯 Computing match scores (Spark Job #3)...")
        
        # Distance score (0-50 points)
        matches_scored = matches_filtered.withColumn(
            "distance_score",
            expr("GREATEST(0, 50 - (distance_km / 50.0 * 50))")
        )
        
        # Vehicle match (0-30 points)
        matches_scored = matches_scored.withColumn(
            "vehicle_score",
            expr("CASE WHEN LOWER(COALESCE(preferred_vehicle, '')) = LOWER(vehicle_type) THEN 30 ELSE 0 END")
        )
        
        # Rating score (0-20 points)
        matches_scored = matches_scored.withColumn(
            "rating_score",
            expr("(COALESCE(rating, 0) / 5.0) * 20")
        )
        
        # Traffic weight
        matches_scored = matches_scored.withColumn(
            "traffic_w",
            expr("""
                CASE 
                    WHEN LOWER(traffic_zone) LIKE '%low%' THEN 1.0
                    WHEN LOWER(traffic_zone) LIKE '%high%' THEN 0.75
                    ELSE 0.9
                END
            """)
        )
        
        # Urgency weight
        matches_scored = matches_scored.withColumn(
            "urgency_w",
            expr("""
                CASE 
                    WHEN LOWER(urgency) LIKE '%high%' THEN 1.3
                    WHEN LOWER(urgency) LIKE '%low%' THEN 0.8
                    ELSE 1.0
                END
            """)
        )
        
        # Final score
        matches_scored = matches_scored.withColumn(
            "match_score",
            expr("(distance_score + vehicle_score + rating_score) * traffic_w * urgency_w")
        )
        
        # Rank matches per rider - Spark job #4
        print("🏆 Ranking matches (Spark Job #4)...")
        window_spec = Window.partitionBy("rider_id").orderBy(col("match_score").desc())
        ranked = matches_scored.withColumn("rank", row_number().over(window_spec))
        
        # Get top 3 per rider
        top3 = ranked.filter(col("rank") <= 3).cache()
        top3_count = top3.count()
        print(f"   ✅ Selected top 3 matches per rider ({top3_count} total)\n")
        
        # Show results
        print("="*70)
        print("📋 SAMPLE RESULTS")
        print("="*70)
        top3.select(
            "rider_id", "rank", "driver_name", "vehicle_type",
            "rating", "distance_km", "match_score"
        ).orderBy("rider_id", "rank").show(15, truncate=False)
        
        # Analytics - More Spark jobs
        print("\n" + "="*70)
        print("📊 ANALYTICS (Additional Spark Jobs)")
        print("="*70 + "\n")
        
        print("1. Average Match Score:")
        top3.agg({"match_score": "avg"}).show()
        
        print("2. Average Distance:")
        top3.agg({"distance_km": "avg"}).show()
        
        print("3. Matches by Vehicle Type:")
        top3.groupBy("vehicle_type").count().orderBy(col("count").desc()).show()
        
        print("4. Matches by Traffic Zone:")
        top3.groupBy("traffic_zone").count().orderBy(col("count").desc()).show()
        
        print("5. Top Drivers:")
        top3.groupBy("driver_id", "driver_name", "rating") \
            .count() \
            .orderBy(col("count").desc(), col("rating").desc()) \
            .show(10)
        
        # Save results
        print("\n💾 Saving results...")
        output_path = "spark_output/final_matches"
        top3.select(
            "rider_id", "rank", "driver_id", "driver_name",
            "vehicle_type", "rating", "distance_km", "match_score", "traffic_zone"
        ).coalesce(1).write.mode("overwrite").csv(output_path, header=True)
        
        print(f"   ✅ Saved to {output_path}/\n")
        
        print("="*70)
        print("✅ ALL SPARK JOBS COMPLETED!")
        print(f"🌐 Check Spark UI: {ui_url}")
        print("   • Jobs tab - See all completed jobs")
        print("   • Stages tab - See execution stages")
        print("   • SQL tab - See DataFrame operations")
        print("   • DAG visualization - See query execution plan")
        print("="*70 + "\n")
        
        input("⏸️  Press ENTER to stop Spark and close UI...")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        spark.stop()
        print("\n✅ Spark Session Stopped")

if __name__ == "__main__":
    main()
