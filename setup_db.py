#!/usr/bin/env python3
"""
Setup script to create telemetry table and insert sample rover data into Pukki DBaaS
Run this ONCE to initialize your database
"""

import psycopg2
from datetime import datetime, timedelta
import random

# ============================================================================
# UPDATE THESE WITH YOUR PUKKI DATABASE CREDENTIALS
# ============================================================================

DB_HOST = "195.148.30.93"
DB_PORT = 5432
DB_NAME = "database1"  # Change if different
DB_USER = "Nihar"   # Change if different
DB_PASSWORD = "Nihar@1341"  # CHANGE THIS!

# ============================================================================

def create_connection():
    """Create connection to Pukki database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("✓ Connected to Pukki DBaaS")
        return conn
    except psycopg2.Error as e:
        print(f"✗ Connection failed: {e}")
        return None

def create_telemetry_table(conn):
    """Create telemetry table"""
    cursor = conn.cursor()
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS telemetry (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        latitude FLOAT NOT NULL,
        longitude FLOAT NOT NULL,
        speed FLOAT,
        battery_level INT,
        temperature FLOAT,
        sensor_reading FLOAT
    );
    """
    
    try:
        cursor.execute(create_table_sql)
        conn.commit()
        print("✓ Telemetry table created (or already exists)")
        cursor.close()
        return True
    except psycopg2.Error as e:
        print(f"✗ Table creation failed: {e}")
        conn.rollback()
        return False

def generate_telemetry_data(num_records=25):
    """Generate realistic simulated rover telemetry data"""
    data = []
    base_time = datetime.now() - timedelta(hours=1)
    
    # Simulate a rover moving in Helsinki area
    start_lat = 60.1699
    start_lon = 24.9384
    
    for i in range(num_records):
        timestamp = base_time + timedelta(minutes=i*2.4)
        latitude = start_lat + random.uniform(-0.01, 0.01)
        longitude = start_lon + random.uniform(-0.015, 0.015)
        speed = random.uniform(0.5, 8.5)
        battery_level = max(0, 100 - (i * 3) + random.randint(-5, 5))
        temperature = random.uniform(15.0, 28.5)
        sensor_reading = random.uniform(20.0, 150.0)
        
        data.append({
            'timestamp': timestamp,
            'latitude': round(latitude, 6),
            'longitude': round(longitude, 6),
            'speed': round(speed, 2),
            'battery_level': battery_level,
            'temperature': round(temperature, 2),
            'sensor_reading': round(sensor_reading, 2)
        })
    
    return data

def insert_telemetry_data(conn, data):
    """Insert telemetry data into database"""
    cursor = conn.cursor()
    
    insert_sql = """
    INSERT INTO telemetry 
    (timestamp, latitude, longitude, speed, battery_level, temperature, sensor_reading)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        for record in data:
            cursor.execute(insert_sql, (
                record['timestamp'],
                record['latitude'],
                record['longitude'],
                record['speed'],
                record['battery_level'],
                record['temperature'],
                record['sensor_reading']
            ))
        
        conn.commit()
        print(f"✓ Inserted {len(data)} telemetry records")
        cursor.close()
        return True
    except psycopg2.Error as e:
        print(f"✗ Data insertion failed: {e}")
        conn.rollback()
        return False

def verify_data(conn):
    """Verify data was inserted"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM telemetry;")
        count = cursor.fetchone()[0]
        print(f"✓ Total records in telemetry table: {count}")
        
        # Show sample
        cursor.execute("""
            SELECT id, timestamp, latitude, longitude, speed, battery_level
            FROM telemetry
            ORDER BY timestamp DESC
            LIMIT 3
        """)
        
        print("\nLatest 3 records:")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Time: {row[1]}, Lat: {row[2]}, Lon: {row[3]}, Speed: {row[4]} m/s, Battery: {row[5]}%")
        
        cursor.close()
        return True
    except psycopg2.Error as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    print("=" * 70)
    print("Pukki DBaaS Telemetry Data Setup")
    print("=" * 70)
    
    conn = create_connection()
    if not conn:
        return
    
    print("\n[1/4] Creating telemetry table...")
    if not create_telemetry_table(conn):
        conn.close()
        return
    
    print("\n[2/4] Generating simulated telemetry data...")
    data = generate_telemetry_data(num_records=25)
    print(f"  Generated {len(data)} records")
    
    print("\n[3/4] Inserting data into database...")
    if not insert_telemetry_data(conn, data):
        conn.close()
        return
    
    print("\n[4/4] Verifying data...")
    verify_data(conn)
    
    conn.close()
    print("\n" + "=" * 70)
    print("✓ Setup complete! Your Streamlit app can now query this data.")
    print("=" * 70)

if __name__ == "__main__":
    main()