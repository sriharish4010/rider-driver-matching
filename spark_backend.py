"""
Simplified PySpark Backend for Ride-Sharing Matchmaking
Runs Spark jobs that populate the UI with DAG visualizations
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, row_number, lit
from pyspark.sql.window import Window
import sys

def main():
    # Initialize Spark with configuration
    spark = SparkSession.builder \
        .appName("RideMatchmaking") \
        .config("spark.ui.port", "4040") \
        .config("spark.driver.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")
    
    print("\n" + "="*60)
    print("🚀 SPARK RIDE MATCHMAKING STARTED")
    print(f"🌐 Spark UI: http://localhost:4040")
    print("="*60 + "\n")
    
    # Load data
    print("Loading data...")
    drivers = spark.read.option("multiline", "true").json("drivers.json")
    riders = spark.read.option("multiline", "true").json("riders.json")
    
    # Prepare for cross join
    print("Preparing datasets...")
    drivers_clean = drivers \
        .filter(col("status") == "available") \
        .select(
            col("driver_id"),
            col("name").alias("driver_name"),
            col("location").getItem(0).alias("d_lat"),
            col("location").getItem(1).alias("d_lon"),
            col("vehicle_type"),
            col("rating"),
            col("traffic_zone")
        )
    
    riders_clean = riders \
        .select(
            col("rider_id"),
            col("location").getItem(0).alias("r_lat"),
            col("location").getItem(1).alias("r_lon"),
            col("preferred_vehicle"),
            col("urgency")
        )
    
    # Cross join - SPARK JOB #1
    print("Cross joining riders and drivers...")
    combinations = riders_clean.crossJoin(drivers_clean)
    
    # Calculate distance - SPARK JOB #2
    print("Calculating distances...")
    with_distance = combinations.withColumn(
        "distance_km",
        expr("""
            6371 * 2 * ASIN(SQRT(
                POW(SIN((RADIANS(d_lat) - RADIANS(r_lat)) / 2), 2) +
                COS(RADIANS(r_lat)) * COS(RADIANS(d_lat)) *
                POW(SIN((RADIANS(d_lon) - RADIANS(r_lon)) / 2), 2)
            ))
        """)
    ).filter(col("distance_km") <= 50)
    
    # Score calculation - SPARK JOB #3
    print("Computing match scores...")
    scored = with_distance \
        .withColumn("dist_score", expr("GREATEST(0, 50 - (distance_km / 50.0 * 50))")) \
        .withColumn("veh_score", expr("CASE WHEN LOWER(preferred_vehicle) = LOWER(vehicle_type) THEN 30 ELSE 0 END")) \
        .withColumn("rating_score", expr("(rating / 5.0) * 20")) \
        .withColumn("traffic_w", expr("CASE WHEN LOWER(traffic_zone) = 'low' THEN 1.0 WHEN LOWER(traffic_zone) = 'high' THEN 0.75 ELSE 0.9 END")) \
        .withColumn("urgency_w", expr("CASE WHEN LOWER(urgency) = 'high' THEN 1.3 WHEN LOWER(urgency) = 'low' THEN 0.8 ELSE 1.0 END")) \
        .withColumn("final_score", expr("(dist_score + veh_score + rating_score) * traffic_w * urgency_w"))
    
    # Rank - SPARK JOB #4
    print("Ranking matches...")
    window = Window.partitionBy("rider_id").orderBy(col("final_score").desc())
    ranked = scored.withColumn("rank", row_number().over(window))
    top_matches = ranked.filter(col("rank") <= 3)
    
    # Analytics - SPARK JOBS #5-8
    print("Computing analytics...")
    
    print("\n📊 RESULTS:")
    print(f"Total matches: {top_matches.count()}")
    
    print("\nTop 10 Matches:")
    top_matches.select("rider_id", "rank", "driver_name", "vehicle_type", "distance_km", "final_score") \
        .orderBy("rider_id", "rank") \
        .show(10, truncate=False)
    
    print("\nAverage Score:")
    top_matches.agg({"final_score": "avg"}).show()
    
    print("\nMatches by Vehicle:")
    top_matches.groupBy("vehicle_type").count().orderBy(col("count").desc()).show()
    
    # Save output
    print("\nSaving results...")
    top_matches.select(
        "rider_id", "rank", "driver_id", "driver_name",
        "vehicle_type", "rating", "distance_km", "final_score"
    ).coalesce(1).write.mode("overwrite").csv("spark_output", header=True)
    
    print("\n✅ SUCCESS!")
    print("="*60)
    print("🌐 Check Spark UI: http://localhost:4040")
    print("   • Jobs tab - 8+ completed jobs")
    print("   • Stages tab - Execution stages")
    print("   • SQL tab - DataFrame operations")
    print("="*60)
    print("\nPress Ctrl+C to stop...")
    
    # Keep alive for UI access
    import time
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping Spark...")
    
    spark.stop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
