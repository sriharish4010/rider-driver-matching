"""
Simple PySpark Script to Launch Spark UI
Minimal script to start Spark and keep UI running
"""

import os
import time
import sys

def main():
    print("\n" + "="*70)
    print("🚀 STARTING SPARK UI")
    print("="*70 + "\n")
    
    # Set environment variables for better compatibility
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, count, avg
        
        print("✅ PySpark imported successfully")
        
        # Create Spark session with basic configuration
        spark = SparkSession.builder \
            .appName("SimpleSparkUI") \
            .config("spark.ui.port", "4040") \
            .config("spark.driver.memory", "512m") \
            .config("spark.executor.memory", "512m") \
            .config("spark.sql.shuffle.partitions", "2") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
        
        print(f"✅ Spark Session Started")
        print(f"🌐 Spark UI available at: http://localhost:4040")
        print(f"📊 Loading sample data...\n")
        
        # Load the JSON data
        try:
            drivers_df = spark.read.option("multiline", "true").json("drivers.json")
            riders_df = spark.read.option("multiline", "true").json("riders.json")
            
            print(f"✅ Data loaded successfully")
            print(f"   - Drivers: {drivers_df.count()} records")
            print(f"   - Riders: {riders_df.count()} records")
            
            # Show sample data to create Spark jobs
            print("\n📋 Sample Driver Data:")
            drivers_df.show(5)
            
            print("📋 Sample Rider Data:")
            riders_df.show(5)
            
            # Perform some basic analytics to generate Spark jobs
            print("\n📊 Analytics (Creating Spark Jobs):")
            
            # Job 1: Count by vehicle type
            print("1. Vehicle type distribution:")
            drivers_df.groupBy("vehicle_type").count().orderBy(col("count").desc()).show()
            
            # Job 2: Average rating by vehicle type
            print("2. Average ratings by vehicle type:")
            drivers_df.groupBy("vehicle_type").agg(avg("rating").alias("avg_rating")).show()
            
            # Job 3: Available drivers by traffic zone
            print("3. Available drivers by traffic zone:")
            drivers_df.filter(col("status") == "available") \
                     .groupBy("traffic_zone").count().show()
            
            # Job 4: Rider urgency distribution
            print("4. Rider urgency levels:")
            riders_df.groupBy("urgency").count().show()
            
            # Simple matching demonstration
            print("\n🔄 Simple matching demonstration:")
            available_drivers = drivers_df.filter(col("status") == "available")
            print(f"   Available drivers: {available_drivers.count()}")
            
            # Create a simple cross join for demonstration
            simple_matches = riders_df.crossJoin(available_drivers.limit(5))
            match_count = simple_matches.count()
            print(f"   Sample matches generated: {match_count}")
            
            print(f"\n" + "="*70)
            print("✅ SPARK JOBS COMPLETED!")
            print("="*70)
            print(f"🌐 Spark UI: http://localhost:4040")
            print("📊 You can now view:")
            print("   • Jobs tab - See completed Spark jobs")
            print("   • Stages tab - View execution stages")
            print("   • SQL tab - See DataFrame operations")
            print("   • Environment tab - See Spark configuration")
            print("="*70)
            
            # Keep Spark UI alive
            print(f"\n⏸️  Keeping Spark UI running...")
            print("💡 Open http://localhost:4040 in your browser")
            print("🛑 Press Ctrl+C to stop\n")
            
            try:
                while True:
                    time.sleep(10)
                    print(".", end="", flush=True)
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping Spark UI...")
                
        except Exception as data_error:
            print(f"❌ Error loading data: {data_error}")
            print("💡 Make sure drivers.json and riders.json exist in the current directory")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Try: pip install pyspark")
        return
    except Exception as e:
        print(f"❌ Spark Error: {e}")
        return
    finally:
        try:
            spark.stop()
            print("✅ Spark stopped cleanly")
        except:
            print("⚠️  Spark cleanup completed")

if __name__ == "__main__":
    main()