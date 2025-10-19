import sqlite3
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager


DATABASE_PATH = Path(__file__).parent / "traffic_data.db"


class TrafficDatabase:
    """SQLite database for traffic sensor data"""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Get database connection context"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sensor readings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    uid TEXT NOT NULL,
                    gas INTEGER NOT NULL,
                    count INTEGER NOT NULL,
                    headway_ms INTEGER NOT NULL,
                    flag TEXT,
                    received_at TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_reading_id INTEGER NOT NULL,
                    congestion_level INTEGER NOT NULL,
                    congestion_status TEXT NOT NULL,
                    confidence INTEGER NOT NULL,
                    next_minute_prediction INTEGER,
                    next_minute_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sensor_reading_id) REFERENCES sensor_readings(id)
                )
            ''')
            
            # Statistics table (for aggregated data)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    avg_gas REAL,
                    max_gas INTEGER,
                    min_gas INTEGER,
                    avg_headway REAL,
                    total_vehicles INTEGER,
                    peak_congestion INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            ''')
            
            # Create indices for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_readings(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_uid ON sensor_readings(uid)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_congestion_status ON predictions(congestion_status)')
            
            conn.commit()
            print(f"✓ Database initialized at {self.db_path}")
    
    def insert_reading(self, timestamp, uid, gas, count, headway_ms, flag, received_at):
        """Insert a sensor reading"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sensor_readings 
                (timestamp, uid, gas, count, headway_ms, flag, received_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, uid, gas, count, headway_ms, flag, received_at))
            return cursor.lastrowid
    
    def insert_prediction(self, sensor_reading_id, congestion_level, congestion_status, 
                         confidence, next_minute_prediction, next_minute_status):
        """Insert a prediction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (sensor_reading_id, congestion_level, congestion_status, confidence, 
                 next_minute_prediction, next_minute_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sensor_reading_id, congestion_level, congestion_status, confidence,
                  next_minute_prediction, next_minute_status))
            return cursor.lastrowid
    
    def get_readings(self, limit=100, offset=0):
        """Get sensor readings with limit and offset"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM sensor_readings 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_readings_by_date(self, date):
        """Get readings for a specific date"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM sensor_readings 
                WHERE DATE(timestamp) = ? 
                ORDER BY timestamp DESC
            ''', (date,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_predictions(self, limit=100, offset=0):
        """Get predictions with sensor data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, r.gas, r.count, r.headway_ms, r.timestamp
                FROM predictions p
                JOIN sensor_readings r ON p.sensor_reading_id = r.id
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_congestion_summary(self, hours=24):
        """Get congestion summary for last N hours"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    congestion_status,
                    COUNT(*) as count,
                    AVG(congestion_level) as avg_level,
                    MAX(congestion_level) as max_level,
                    MIN(congestion_level) as min_level
                FROM predictions
                WHERE created_at >= datetime('now', '-' || ? || ' hours')
                GROUP BY congestion_status
            ''', (hours,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_statistics(self, date=None):
        """Get daily statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT * FROM statistics WHERE date = ?
            ''', (date,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_statistics(self):
        """Calculate and update daily statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate statistics
            cursor.execute('''
                SELECT 
                    AVG(gas) as avg_gas,
                    MAX(gas) as max_gas,
                    MIN(gas) as min_gas,
                    AVG(headway_ms) as avg_headway,
                    MAX(count) as total_vehicles
                FROM sensor_readings
                WHERE DATE(timestamp) = ?
            ''', (today,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute('''
                    SELECT MAX(congestion_level) as peak_congestion
                    FROM predictions
                    WHERE DATE(created_at) = ?
                ''', (today,))
                pred_row = cursor.fetchone()
                peak = pred_row['peak_congestion'] if pred_row else 0
                
                cursor.execute('''
                    INSERT OR REPLACE INTO statistics 
                    (date, avg_gas, max_gas, min_gas, avg_headway, total_vehicles, peak_congestion)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (today, row['avg_gas'], row['max_gas'], row['min_gas'], 
                      row['avg_headway'], row['total_vehicles'], peak))
                conn.commit()
    
    def get_total_count(self):
        """Get total number of readings"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM sensor_readings')
            return cursor.fetchone()['count']
    
    def clear_old_data(self, days=30):
        """Delete readings older than N days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM sensor_readings 
                WHERE DATE(timestamp) < DATE('now', '-' || ? || ' days')
            ''', (days,))
            cursor.execute('''
                DELETE FROM predictions 
                WHERE DATE(created_at) < DATE('now', '-' || ? || ' days')
            ''', (days,))
            deleted = cursor.rowcount
            conn.commit()
            return deleted


# Create global database instance
db = TrafficDatabase()
