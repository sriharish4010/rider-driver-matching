"""
Simplified PySpark Ride-Sharing Matchmaking System
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, expr
from pyspark.sql.types import DoubleType
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number
import math

# Initialize Spark
spark = SparkSession.builder \
    .appName("Ride-Matching-System") \
    .config("spark.ui.port", "4040") \
    .config("spark.driver.memory", "1g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("\n" + "="*60)
print("🚀 SPARK RIDE-SHARING MATCHMAKING SYSTEM")
print("="*60)
print(f"✅ Spark UI: {spark.sparkContext.uiWebUrl}")
print("="*60 + "\n")

# UDFs
@udf(returnType=DoubleType())
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@udf(returnType=DoubleType())
def traffic_weight(zone):
    if not zone: return 0.9
    z = zone.lower()
    if 'low' in z: return 1.0
    if 'high' in z: return 0.75
    return 0.9

@udf(returnType=DoubleType())
def urgency_weight(urg):
    if not urg: return 1.0
    u = urg.lower()
    if 'high' in u: return 1.3
    if 'low' in u: return 0.8
    return 1.0

# Load data
print("📂 Loading datasets...")
drivers = spark.read.json("drivers.json").filter(col("status") == "available")
riders = spark.read.json("riders.json")

driver_count = drivers.count()
rider_count = riders.count()

print(f"✅ {driver_count} available drivers")
print(f"✅ {rider_count} riders\n")

# Show samples
print("Sample Drivers:")
drivers.select("driver_id", "name", "vehicle_type", "rating").show(3, False)

print("Sample Riders:")
riders.select("rider_id", "preferred_vehicle", "urgency").show(3, False)

# Rename columns to avoid ambiguity
drivers_renamed = drivers.selectExpr(
    "driver_id",
    "name as driver_name",
    "location[0] as driver_lat",
    "location[1] as driver_lon",
    "vehicle_type",
    "rating",
    "traffic_zone"
)

riders_renamed = riders.selectExpr(
    "rider_id",
    "location[0] as rider_lat",
    "location[1] as rider_lon",
    "preferred_vehicle",
    "urgency"
)

# Cross join
print("🔄 Creating matches (cross join)...")
matches = riders_renamed.crossJoin(drivers_renamed)
total_combinations = matches.count()
print(f"📊 Total combinations: {total_combinations}\n")

# Calculate distance
print("📏 Calculating distances...")
matches = matches.withColumn(
    "distance_km",
    haversine(
        col("rider_lat"), col("rider_lon"),
        col("driver_lat"), col("driver_lon")
    )
)

# Filter by distance (<= 50km)
matches = matches.filter(col("distance_km") <= 50)
print(f"✅ Matches within 50km: {matches.count()}\n")

# Calculate score
print("🎯 Calculating match scores...")

# Distance score (0-50 points)
matches = matches.withColumn(
    "distance_score",
    expr("GREATEST(0, 50 - (distance_km / 50.0 * 50))")
)

# Vehicle match (0-30 points)
matches = matches.withColumn(
    "vehicle_score",
    expr("CASE WHEN LOWER(preferred_vehicle) = LOWER(vehicle_type) THEN 30 ELSE 0 END")
)

# Rating score (0-20 points)
matches = matches.withColumn(
    "rating_score",
    expr("(rating / 5.0) * 20")
)

# Apply weights
matches = matches.withColumn("traffic_w", traffic_weight(col("traffic_zone")))
matches = matches.withColumn("urgency_w", urgency_weight(col("urgency")))

# Final score
matches = matches.withColumn(
    "match_score",
    expr("(distance_score + vehicle_score + rating_score) * traffic_w * urgency_w")
)

# Rank matches per rider
print("🏆 Ranking matches...")
window_spec = Window.partitionBy("rider_id").orderBy(col("match_score").desc())
matches = matches.withColumn("rank", row_number().over(window_spec))

# Get top 3 per rider
top3 = matches.filter(col("rank") <= 3)
top3_count = top3.count()
print(f"✅ Top 3 matches per rider: {top3_count} matches\n")

# Show results
print("="*60)
print("📋 TOP MATCHES")
print("="*60)
top3.select(
    "rider_id", "rank", "driver_id", "driver_name",
    "vehicle_type", "rating", "distance_km", "match_score"
).orderBy("rider_id", "rank").show(30, truncate=False)

# Analytics
print("\n" + "="*60)
print("📊 ANALYTICS")
print("="*60 + "\n")

print("1️⃣ Average Match Score:")
top3.agg({"match_score": "avg"}).show()

print("2️⃣ Average Distance:")
top3.agg({"distance_km": "avg"}).show()

print("3️⃣ Matches by Vehicle Type:")
top3.groupBy("vehicle_type").count().orderBy(col("count").desc()).show()

print("4️⃣ Matches by Traffic Zone:")
top3.groupBy("traffic_zone").count().orderBy(col("count").desc()).show()

print("5️⃣ Top Drivers (Most Matches):")
top3.groupBy("driver_id", "driver_name", "rating") \
    .count() \
    .orderBy(col("count").desc(), col("rating").desc()) \
    .show(10)

# Save results
print("\n💾 Saving results to 'spark_output/'...")
top3.select(
    "rider_id", "rank", "driver_id", "driver_name",
    "vehicle_type", "rating", "distance_km", "match_score", "traffic_zone"
).coalesce(1).write.mode("overwrite").csv("spark_output/matches", header=True)

print("✅ Results saved!\n")

print("="*60)
print("✅ SPARK JOB COMPLETED SUCCESSFULLY!")
print(f"🌐 View Spark UI: {spark.sparkContext.uiWebUrl}")
print("="*60 + "\n")

input("⏸️  Press Enter to stop Spark and close UI...")

spark.stop()
print("✅ Spark stopped")
