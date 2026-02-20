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
            # Default to data/skyscraper.db relative to repository root
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.db_path = os.path.join(base_dir, "data", "skyscraper.db")
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
            logger.info(f"NEW FLIGHT: {flight_data.get('airline')} {flight_data.get('departure_time')} - No previous record found.")
            return True
            
        last_price = row[0]
        
        if last_price is None:
            # Previously seen but no numeric price stored -> Treat as new/update -> Send
            logger.info("UPDATE FLIGHT: Previous record had no price.")
            return True
            
        if current_price is None:
            # Can't parse current price
            logger.info("SKIP FLIGHT: Current price could not be parsed.")
            return False

        if current_price < last_price:
            # Price dropped! -> Send
            logger.info(f"PRICE DROP: {current_price} < {last_price}")
            return True
        elif current_price > last_price:
            # Price increased -> Don't send
            logger.info(f"PRICE INCREASE: {current_price} > {last_price} - Suppressing.")
            return False
            
        # Price is same -> Don't send
        logger.info(f"SAME FLIGHT: Price {current_price} is unchanged.")
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
