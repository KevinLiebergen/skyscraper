import os
import sqlite3
import logging
from datetime import datetime

import logging
import sys
import os
# Add src to path to allow importing utils if not already in path
# But usually this is run from main.py which sets the path.
# We will use a try-except import or just assume path is set.
try:
    from utils.parsing import parse_price
except ImportError:
    # Fallback if running standalone or path not set correctly
    def parse_price(x): return None

logger = logging.getLogger("skyscraper.database")

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to data/skyscraper.db relative to CWD
            self.db_path = os.path.join("data", "skyscraper.db")
        else:
            self.db_path = db_path
            
        # Ensure directory exists
        dirname = os.path.dirname(self.db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
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
                price REAL,
                seen_at TIMESTAMP
            )
        """)
        
        # Migration: Add price column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE flights ADD COLUMN price REAL")
        except sqlite3.OperationalError:
            pass # Column likely already exists
        # Index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_flight_lookup 
            ON flights (origin, destination, date, airline, departure_time, price_text)
        """)
        conn.commit()
        conn.close()

    def is_flight_new(self, flight_data: dict, origin, destination, date, return_date) -> bool:
        """
        Checks if the flight is "interesting" (New or Price Drop).
        Returns True if we should notify, False otherwise.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Check for the LATEST seen price for this specific flight leg
        query = """
            SELECT price FROM flights 
            WHERE origin=? 
            AND destination=? 
            AND date=? 
            AND (return_date=? OR (return_date IS NULL AND ? IS NULL))
            AND airline=? 
            AND departure_time=? 
            AND arrival_time=? 
            ORDER BY seen_at DESC LIMIT 1
        """
        
        params = (
            origin, 
            destination, 
            date, 
            return_date, return_date, 
            flight_data.get('airline', 'Unknown'),
            flight_data.get('departure_time', 'N/A'),
            flight_data.get('arrival_time', 'N/A')
        )
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        current_price = parse_price(flight_data.get('price'))
        
        if not row:
            # Flight not seen before -> Send
            return True
            
        last_price = row[0]
        
        if last_price is None:
            # Previously seen but no numeric price stored -> Treat as new/update -> Send
            return True
            
        if current_price is None:
            # Can't parse current price -> Default to generic deduplication (if text matches)
            # But here we assume if we can't parse, we might as well send if it's not exact match?
            # Let's fallback to False to be safe (no spam) or True?
            # User said: "if results are duplicated... do not send".
            # If we can't parse price, we rely on exact flight details match which we just found.
            # Let's return False to avoid spamming "N/A" prices if they persist.
            return False

        if current_price < last_price:
            # Price dropped! -> Send
            return True
        elif current_price > last_price:
            # Price increased -> Don't send (User requirement implied)
            return False
            
        # Price is same -> Don't send
        return False

    def save_flight(self, flight_data: dict, origin, destination, date, return_date):
        """
        Saves a flight offer to the database.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO flights (
                origin, destination, date, return_date, 
                airline, departure_time, arrival_time, price_text, price, seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            parse_price(flight_data.get('price')),
            datetime.now()
        )
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
