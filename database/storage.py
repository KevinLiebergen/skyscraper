import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger("skyscraper.database")

class DatabaseManager:
    def __init__(self, db_path="skyscraper.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT,
                destination TEXT,
                date TEXT,
                return_date TEXT,
                airline TEXT,
                departure_time TEXT,
                arrival_time TEXT,
                price_text TEXT,
                seen_at TIMESTAMP
            )
        """)
        # Index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flight_lookup 
            ON flights (origin, destination, date, airline, departure_time, price_text)
        """)
        conn.commit()
        conn.close()

    def is_flight_new(self, flight_data: dict, origin, destination, date, return_date) -> bool:
        """
        Checks if this specific flight offer (including price) has been seen before.
        Returns True if it's new (or price changed), False if it's a duplicate.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # We define "same offer" as: same route, dates, airline, flight times, AND PRICE.
        # If price changes, it counts as "new" (so we notify).
        
        query = """
            SELECT 1 FROM flights 
            WHERE origin=? 
            AND destination=? 
            AND date=? 
            AND (return_date=? OR (return_date IS NULL AND ? IS NULL))
            AND airline=? 
            AND departure_time=? 
            AND arrival_time=? 
            AND price_text=?
        """
        
        params = (
            origin, 
            destination, 
            date, 
            return_date, return_date, # Handle NULL comparison logic in python or SQL
            flight_data.get('airline', 'Unknown'),
            flight_data.get('departure_time', 'N/A'),
            flight_data.get('arrival_time', 'N/A'),
            flight_data.get('price', 'N/A')
        )
        
        cursor.execute(query, params)
        exists = cursor.fetchone()
        conn.close()
        
        return not exists

    def save_flight(self, flight_data: dict, origin, destination, date, return_date):
        """
        Saves a flight offer to the database.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO flights (
                origin, destination, date, return_date, 
                airline, departure_time, arrival_time, price_text, seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            origin, 
            destination, 
            date, 
            return_date,
            flight_data.get('airline', 'Unknown'),
            flight_data.get('departure_time', 'N/A'),
            flight_data.get('arrival_time', 'N/A'),
            flight_data.get('price', 'N/A'),
            datetime.now()
        )
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
