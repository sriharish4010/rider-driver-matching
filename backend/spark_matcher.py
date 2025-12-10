"""
PySpark-based Ride Matching Engine
Implements the exact same matching logic as the frontend JavaScript version
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, lit, udf, struct, array, explode, when, 
    sum as spark_sum, avg as spark_avg, count, collect_list
)
from pyspark.sql.types import DoubleType, StructType, StructField, StringType, IntegerType, ArrayType
import math


class SparkRideMatcher:
    """
    PySpark implementation of the ride-sharing matchmaking algorithm.
    Preserves all logic from the original JavaScript implementation.
    """
    
    def __init__(self, app_name="RideMatchingSystem"):
        """Initialize Spark session"""
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Register UDFs
        self._register_udfs()
    
    def _register_udfs(self):
        """Register User Defined Functions for Spark"""
        
        # Haversine distance calculation (exact same as JavaScript)
        @udf(DoubleType())
        def haversine_udf(lat1, lon1, lat2, lon2):
            """Calculate distance between two points in km using Haversine formula"""
            if None in [lat1, lon1, lat2, lon2]:
                return None
            
            def to_rad(v):
                return v * math.pi / 180
            
            R = 6371  # Earth radius in km
            dLat = to_rad(lat2 - lat1)
            dLon = to_rad(lon2 - lon1)
            
            a = (math.sin(dLat/2)**2 + 
                 math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * 
                 math.sin(dLon/2)**2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            return R * c
        
        # Traffic zone weight (exact same logic as JavaScript)
        @udf(DoubleType())
        def traffic_weight_udf(zone):
            """Calculate traffic weight multiplier"""
            if not zone:
                return 0.9
            
            zone_lower = str(zone).lower()
            if 'low' in zone_lower:
                return 1.0
            elif 'medium' in zone_lower:
                return 0.9
            elif 'high' in zone_lower:
                return 0.75
            return 0.9
        
        # Urgency weight (exact same logic as JavaScript)
        @udf(DoubleType())
        def urgency_weight_udf(urgency):
            """Calculate urgency weight multiplier"""
            if not urgency:
                return 1.0
            
            urgency_lower = str(urgency).lower()
            if 'high' in urgency_lower:
                return 1.3
            elif 'medium' in urgency_lower:
                return 1.0
            elif 'low' in urgency_lower:
                return 0.8
            return 1.0
        
        # Vehicle match bonus (exact same logic as JavaScript)
        @udf(DoubleType())
        def vehicle_bonus_udf(driver_vehicle, rider_preference):
            """Calculate vehicle preference match bonus"""
            if not driver_vehicle or not rider_preference:
                return 0.0
            
            if str(driver_vehicle).lower() == str(rider_preference).lower():
                return 30.0
            return 0.0
        
        # Rating bonus (exact same logic as JavaScript)
        @udf(DoubleType())
        def rating_bonus_udf(rating):
            """Calculate rating bonus"""
            if not rating or rating == 0:
                return 10.0
            return (float(rating) / 5.0) * 25.0
        
        # Store UDFs as instance variables
        self.haversine_udf = haversine_udf
        self.traffic_weight_udf = traffic_weight_udf
        self.urgency_weight_udf = urgency_weight_udf
        self.vehicle_bonus_udf = vehicle_bonus_udf
        self.rating_bonus_udf = rating_bonus_udf
    
    def load_drivers(self, drivers_data):
        """
        Load drivers data into Spark DataFrame
        
        Args:
            drivers_data: List of driver dictionaries
        
        Returns:
            Spark DataFrame with drivers
        """
        df = self.spark.createDataFrame(drivers_data)
        
        # Ensure location is extracted as separate columns
        df = df.withColumn("lat", col("location")[0]) \
               .withColumn("lon", col("location")[1])
        
        # Set defaults for optional fields
        df = df.withColumn("status", 
                          when(col("status").isNull(), lit("available"))
                          .otherwise(col("status")))
        df = df.withColumn("rating", 
                          when(col("rating").isNull(), lit(0.0))
                          .otherwise(col("rating")))
        df = df.withColumn("traffic_zone", 
                          when(col("traffic_zone").isNull(), lit("medium"))
                          .otherwise(col("traffic_zone")))
        
        return df
    
    def load_riders(self, riders_data):
        """
        Load riders data into Spark DataFrame
        
        Args:
            riders_data: List of rider dictionaries
        
        Returns:
            Spark DataFrame with riders
        """
        df = self.spark.createDataFrame(riders_data)
        
        # Extract location coordinates
        df = df.withColumn("lat", col("location")[0]) \
               .withColumn("lon", col("location")[1])
        
        # Set defaults for optional fields
        df = df.withColumn("preferred_vehicle", 
                          when(col("preferred_vehicle").isNull(), lit("Any"))
                          .otherwise(col("preferred_vehicle")))
        df = df.withColumn("urgency", 
                          when(col("urgency").isNull(), lit("medium"))
                          .otherwise(col("urgency")))
        
        return df
    
    def calculate_matches(self, drivers_df, riders_df, top_n=3):
        """
        Calculate driver-rider matches using the exact same algorithm as JavaScript
        
        Args:
            drivers_df: Spark DataFrame with drivers
            riders_df: Spark DataFrame with riders
            top_n: Number of top matches per rider (default: 3)
        
        Returns:
            Spark DataFrame with matches
        """
        MAX_DIST = 50  # km window (same as JavaScript)
        
        # Filter only available drivers (exact same logic as JavaScript)
        available_drivers = drivers_df.filter(
            col("status").isNull() | (col("status").cast("string").lower() == "available")
        )
        
        # Cross join riders and drivers to create all possible pairs
        matches = riders_df.alias("r").crossJoin(available_drivers.alias("d"))
        
        # Calculate distance using Haversine (exact same as JavaScript)
        matches = matches.withColumn(
            "distance_km",
            self.haversine_udf(
                col("r.lat"), col("r.lon"),
                col("d.lat"), col("d.lon")
            )
        )
        
        # Round distance to 2 decimal places (same as JavaScript)
        matches = matches.withColumn(
            "distance_km",
            (col("distance_km") * 100).cast("bigint") / 100.0
        )
        
        # Normalize distance for scoring (exact same logic as JavaScript)
        matches = matches.withColumn(
            "dist_norm",
            when(col("distance_km") < MAX_DIST, col("distance_km"))
            .otherwise(lit(MAX_DIST))
        )
        
        # Calculate distance score: closer = higher (0-100 points)
        # Exact same formula as JavaScript: Math.max(0, 100 - (distNorm / maxDist) * 100)
        matches = matches.withColumn(
            "distance_score",
            when(
                (lit(100) - (col("dist_norm") / lit(MAX_DIST)) * 100) > 0,
                lit(100) - (col("dist_norm") / lit(MAX_DIST)) * 100
            ).otherwise(lit(0))
        )
        
        # Calculate vehicle preference bonus (exact same as JavaScript)
        matches = matches.withColumn(
            "vehicle_bonus",
            self.vehicle_bonus_udf(col("d.vehicle_type"), col("r.preferred_vehicle"))
        )
        
        # Calculate rating bonus (exact same as JavaScript)
        matches = matches.withColumn(
            "rating_bonus",
            self.rating_bonus_udf(col("d.rating"))
        )
        
        # Calculate traffic weight (exact same as JavaScript)
        matches = matches.withColumn(
            "traffic_weight",
            self.traffic_weight_udf(col("d.traffic_zone"))
        )
        
        # Calculate urgency weight (exact same as JavaScript)
        matches = matches.withColumn(
            "urgency_weight",
            self.urgency_weight_udf(col("r.urgency"))
        )
        
        # Calculate final score (exact same formula as JavaScript)
        # Score = (distanceScore + vehicleBonus + ratingBonus) * trafficWeight * urgencyWeight
        matches = matches.withColumn(
            "raw_score",
            (col("distance_score") + col("vehicle_bonus") + col("rating_bonus")) * 
            col("traffic_weight") * col("urgency_weight")
        )
        
        # Round to 2 decimal places (same as JavaScript)
        matches = matches.withColumn(
            "match_score",
            (col("raw_score") * 100).cast("bigint") / 100.0
        )
        
        # Select relevant columns for output
        result = matches.select(
            col("r.rider_id").alias("rider_id"),
            col("r.location").alias("rider_location"),
            col("r.lat").alias("rider_lat"),
            col("r.lon").alias("rider_lon"),
            col("r.preferred_vehicle").alias("preferred_vehicle"),
            col("r.urgency").alias("urgency"),
            col("d.driver_id").alias("driver_id"),
            col("d.location").alias("driver_location"),
            col("d.lat").alias("driver_lat"),
            col("d.lon").alias("driver_lon"),
            col("d.vehicle_type").alias("vehicle_type"),
            col("d.rating").alias("rating"),
            col("d.traffic_zone").alias("traffic_zone"),
            col("distance_km"),
            col("match_score")
        )
        
        # Get top N matches per rider (same as JavaScript)
        from pyspark.sql.window import Window
        from pyspark.sql.functions import row_number
        
        window_spec = Window.partitionBy("rider_id").orderBy(col("match_score").desc())
        
        result = result.withColumn("rank", row_number().over(window_spec))
        result = result.filter(col("rank") <= top_n)
        
        return result.orderBy("rider_id", "rank")
    
    def get_analytics(self, drivers_df, riders_df, matches_df):
        """
        Calculate analytics metrics (same as JavaScript dashboard)
        
        Returns:
            Dictionary with analytics data
        """
        # Driver count
        driver_count = drivers_df.count()
        
        # Rider count
        rider_count = riders_df.count()
        
        # Average rating
        avg_rating = drivers_df.agg(spark_avg("rating").alias("avg_rating")).collect()[0]["avg_rating"]
        avg_rating = round(avg_rating, 1) if avg_rating else 0.0
        
        # Total matches
        match_count = matches_df.count()
        
        # Vehicle distribution
        vehicle_dist = drivers_df.groupBy("vehicle_type") \
            .agg(count("*").alias("count")) \
            .orderBy(col("count").desc()) \
            .collect()
        
        vehicle_distribution = {
            row["vehicle_type"]: row["count"] 
            for row in vehicle_dist
        }
        
        return {
            "driver_count": driver_count,
            "rider_count": rider_count,
            "avg_rating": avg_rating,
            "match_count": match_count,
            "vehicle_distribution": vehicle_distribution
        }
    
    def get_matches_by_rider(self, matches_df):
        """
        Group matches by rider (same structure as JavaScript output)
        
        Returns:
            List of dictionaries with rider and their top matches
        """
        # Group by rider
        grouped = matches_df.groupBy("rider_id", "rider_location", "preferred_vehicle", "urgency") \
            .agg(
                collect_list(
                    struct(
                        col("driver_id"),
                        col("vehicle_type"),
                        col("rating"),
                        col("distance_km"),
                        col("match_score"),
                        col("traffic_zone"),
                        col("rank")
                    )
                ).alias("matches")
            )
        
        # Convert to list of dictionaries (same format as JavaScript)
        result = []
        for row in grouped.collect():
            matches_list = sorted(row["matches"], key=lambda x: x["rank"])
            
            result.append({
                "rider_id": row["rider_id"],
                "rider_location": row["rider_location"],
                "preferred_vehicle": row["preferred_vehicle"],
                "urgency": row["urgency"],
                "top_matches": [
                    {
                        "driver_id": m["driver_id"],
                        "vehicle_type": m["vehicle_type"],
                        "rating": float(m["rating"]) if m["rating"] else 0.0,
                        "distance_km": float(m["distance_km"]),
                        "match_score": float(m["match_score"]),
                        "traffic_zone": m["traffic_zone"]
                    }
                    for m in matches_list
                ]
            })
        
        return result
    
    def stop(self):
        """Stop Spark session"""
        self.spark.stop()


# Example usage
if __name__ == "__main__":
    # Test with sample data
    import json
    
    # Load sample data
    with open('../drivers.json', 'r') as f:
        drivers_data = json.load(f)
    
    with open('../riders.json', 'r') as f:
        riders_data = json.load(f)
    
    # Initialize matcher
    matcher = SparkRideMatcher()
    
    # Load data
    drivers_df = matcher.load_drivers(drivers_data)
    riders_df = matcher.load_riders(riders_data)
    
    # Calculate matches
    matches_df = matcher.calculate_matches(drivers_df, riders_df, top_n=3)
    
    # Get analytics
    analytics = matcher.get_analytics(drivers_df, riders_df, matches_df)
    print("\n=== Analytics ===")
    print(f"Drivers: {analytics['driver_count']}")
    print(f"Riders: {analytics['rider_count']}")
    print(f"Average Rating: {analytics['avg_rating']}")
    print(f"Total Matches: {analytics['match_count']}")
    print(f"Vehicle Distribution: {analytics['vehicle_distribution']}")
    
    # Get matches by rider
    matches_by_rider = matcher.get_matches_by_rider(matches_df)
    print("\n=== Matches by Rider ===")
    print(json.dumps(matches_by_rider, indent=2))
    
    # Stop Spark
    matcher.stop()
