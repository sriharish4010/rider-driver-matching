"""
PySpark-based Ride-Sharing Matchmaking System
Real matching algorithm using Apache Spark
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, lit, explode, array, struct
from pyspark.sql.types import DoubleType, ArrayType, StructType, StructField, StringType, IntegerType
import math
import json
import sys

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Ride-Sharing-Matchmaking") \
    .config("spark.ui.port", "4040") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.debug.maxToStringFields", "100") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("✅ Spark Session Started")
spark_ui_port = spark.sparkContext.uiWebUrl
print(f"🌐 Spark UI: {spark_ui_port}")

# Define schemas explicitly
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, ArrayType

driver_schema = StructType([
    StructField("driver_id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("location", ArrayType(DoubleType()), True),
    StructField("vehicle_type", StringType(), True),
    StructField("rating", DoubleType(), True),
    StructField("status", StringType(), True),
    StructField("traffic_zone", StringType(), True)
])

rider_schema = StructType([
    StructField("rider_id", IntegerType(), True),
    StructField("location", ArrayType(DoubleType()), True),
    StructField("preferred_vehicle", StringType(), True),
    StructField("urgency", StringType(), True)
])

# Haversine Distance UDF
def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates in kilometers"""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

haversine_udf = udf(haversine, DoubleType())

# Traffic Weight UDF
def traffic_weight(zone):
    """Apply traffic zone weight"""
    if zone is None:
        return 0.9
    zone_lower = zone.lower()
    if 'low' in zone_lower:
        return 1.0
    elif 'medium' in zone_lower:
        return 0.9
    elif 'high' in zone_lower:
        return 0.75
    return 0.9

traffic_weight_udf = udf(traffic_weight, DoubleType())

# Urgency Weight UDF
def urgency_weight(urgency):
    """Apply urgency weight"""
    if urgency is None:
        return 1.0
    urgency_lower = urgency.lower()
    if 'high' in urgency_lower:
        return 1.3
    elif 'medium' in urgency_lower:
        return 1.0
    elif 'low' in urgency_lower:
        return 0.8
    return 1.0

urgency_weight_udf = udf(urgency_weight, DoubleType())

# Load Datasets
try:
    print("\n📂 Loading datasets...")
    
    # Read drivers with schema
    drivers_df = spark.read.schema(driver_schema).json("drivers.json")
    driver_count = drivers_df.count()
    print(f"✅ Loaded {driver_count} drivers")
    drivers_df.show(5, truncate=False)
    
    # Read riders with schema
    riders_df = spark.read.schema(rider_schema).json("riders.json")
    rider_count = riders_df.count()
    print(f"✅ Loaded {rider_count} riders")
    riders_df.show(5, truncate=False)
    
except Exception as e:
    print(f"❌ Error loading datasets: {e}")
    spark.stop()
    sys.exit(1)

# Filter available drivers
available_drivers = drivers_df.filter(col("status") == "available")
print(f"\n🚗 Available drivers: {available_drivers.count()}")

# Cross join riders with drivers for matching
print("\n🔄 Performing cross join...")
matches = riders_df.crossJoin(available_drivers)
print(f"📊 Total combinations: {matches.count()}")

# Calculate distances
print("\n📏 Calculating distances...")
matches = matches.withColumn(
    "distance",
    haversine_udf(
        col("location")[0],  # rider lat
        col("location")[1],  # rider lon
        col("location")[0],  # driver lat (note: after crossJoin, need to handle column names)
        col("location")[1]   # driver lon
    )
)

# Add column aliases to distinguish rider and driver columns
riders_aliased = riders_df.selectExpr(
    "rider_id",
    "location as rider_location",
    "preferred_vehicle",
    "urgency"
)

drivers_aliased = available_drivers.selectExpr(
    "driver_id",
    "name as driver_name",
    "location as driver_location",
    "vehicle_type",
    "rating",
    "traffic_zone"
)

# Proper cross join with aliases
matches = riders_aliased.crossJoin(drivers_aliased)

# Calculate distance
matches = matches.withColumn(
    "distance",
    haversine_udf(
        col("rider_location")[0],
        col("rider_location")[1],
        col("driver_location")[0],
        col("driver_location")[1]
    )
)

# Calculate match score
print("\n🎯 Calculating match scores...")

# Distance score (0-50 points)
matches = matches.withColumn(
    "distance_score",
    50 - (col("distance") / 50.0 * 50)
)

# Vehicle match bonus (0-30 points)
matches = matches.withColumn(
    "vehicle_bonus",
    udf(lambda pref, vtype: 30.0 if pref and vtype and pref.lower() == vtype.lower() else 0.0, DoubleType())(
        col("preferred_vehicle"),
        col("vehicle_type")
    )
)

# Rating bonus (0-20 points)
matches = matches.withColumn(
    "rating_bonus",
    (col("rating") / 5.0 * 20)
)

# Apply traffic and urgency weights
matches = matches.withColumn("traffic_weight", traffic_weight_udf(col("traffic_zone")))
matches = matches.withColumn("urgency_weight", urgency_weight_udf(col("urgency")))

# Final score calculation
matches = matches.withColumn(
    "match_score",
    (col("distance_score") + col("vehicle_bonus") + col("rating_bonus")) * 
    col("traffic_weight") * col("urgency_weight")
)

# Filter matches within 50km
matches = matches.filter(col("distance") <= 50)

print(f"✅ Matches within 50km: {matches.count()}")

# Show sample matches
print("\n📋 Sample matches:")
matches.select(
    "rider_id", "driver_id", "driver_name", "distance", 
    "match_score", "vehicle_type", "rating"
).orderBy(col("match_score").desc()).show(10)

# Get top 3 matches per rider
from pyspark.sql.window import Window

windowSpec = Window.partitionBy("rider_id").orderBy(col("match_score").desc())

top_matches = matches.withColumn("rank", udf(lambda: 1, IntegerType())())

# Use window function to rank
from pyspark.sql.functions import row_number

windowSpec = Window.partitionBy("rider_id").orderBy(col("match_score").desc())
ranked_matches = matches.withColumn("rank", row_number().over(windowSpec))
top3_matches = ranked_matches.filter(col("rank") <= 3)

print(f"\n🎯 Top 3 matches per rider: {top3_matches.count()} total matches")
top3_matches.select(
    "rider_id", "rank", "driver_id", "driver_name", 
    "distance", "match_score", "vehicle_type"
).show(20)

# Save results
print("\n💾 Saving results...")
output_path = "spark_output"

# Save as JSON
top3_matches.select(
    "rider_id", "driver_id", "driver_name", "vehicle_type", 
    "rating", "distance", "match_score", "traffic_zone", "rank"
).coalesce(1).write.mode("overwrite").json(f"{output_path}/matches_json")

# Save as CSV
top3_matches.select(
    "rider_id", "driver_id", "driver_name", "vehicle_type", 
    "rating", "distance", "match_score", "traffic_zone", "rank"
).coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{output_path}/matches_csv")

print(f"✅ Results saved to {output_path}/")

# Analytics
print("\n📊 ANALYTICS SUMMARY")
print("=" * 50)

# Total matches
total_matches = top3_matches.count()
print(f"Total Matches: {total_matches}")

# Average match score
avg_score = top3_matches.agg({"match_score": "avg"}).collect()[0][0]
print(f"Average Match Score: {avg_score:.2f}")

# Average distance
avg_distance = top3_matches.agg({"distance": "avg"}).collect()[0][0]
print(f"Average Distance: {avg_distance:.2f} km")

# Matches by vehicle type
print("\nMatches by Vehicle Type:")
top3_matches.groupBy("vehicle_type").count().orderBy(col("count").desc()).show()

# Matches by traffic zone
print("\nMatches by Traffic Zone:")
top3_matches.groupBy("traffic_zone").count().orderBy(col("count").desc()).show()

# Top rated drivers in matches
print("\nTop Rated Drivers:")
top3_matches.groupBy("driver_id", "driver_name", "rating") \
    .count() \
    .orderBy(col("count").desc(), col("rating").desc()) \
    .show(10)

print("\n" + "=" * 50)
print("✅ Spark Job Completed Successfully!")
print(f"🌐 View details at: http://localhost:4040")
print("=" * 50)

# Keep Spark UI running
input("\n⏸️  Press Enter to stop Spark and close UI...")

# Stop Spark
spark.stop()
print("✅ Spark Session Stopped")
