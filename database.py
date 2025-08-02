import sqlite3
import json
from datetime import datetime
from typing import Dict, Any

class QueryLogger:
    def __init__(self, db_path: str = "queries.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the required table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='query_logs'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                # Create new table with all columns
                cursor.execute('''
                    CREATE TABLE query_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        state TEXT,
                        district TEXT,
                        court_complex TEXT,
                        case_type TEXT,
                        case_number TEXT,
                        case_year TEXT,
                        captcha_value TEXT,
                        request_data TEXT,
                        response_data TEXT,
                        raw_json_response TEXT,
                        success BOOLEAN,
                        error_message TEXT
                    )
                ''')
            else:
                # Check if raw_json_response column exists
                cursor.execute("PRAGMA table_info(query_logs)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'raw_json_response' not in columns:
                    # Add the new column to existing table
                    cursor.execute('ALTER TABLE query_logs ADD COLUMN raw_json_response TEXT')
            
            conn.commit()
    
    def log_query(self, 
                  state: str = None,
                  district: str = None,
                  court_complex: str = None,
                  case_type: str = None,
                  case_number: str = None,
                  case_year: str = None,
                  captcha_value: str = None,
                  request_data: Dict[str, Any] = None,
                  response_data: Dict[str, Any] = None,
                  raw_json_response: Dict[str, Any] = None,
                  success: bool = True,
                  error_message: str = None):
        """Log a query with all its details"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO query_logs 
                (state, district, court_complex, case_type, case_number, case_year, 
                 captcha_value, request_data, response_data, raw_json_response, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                state, district, court_complex, case_type, case_number, case_year,
                captcha_value, 
                json.dumps(request_data) if request_data else None,
                json.dumps(response_data) if response_data else None,
                json.dumps(raw_json_response) if raw_json_response else None,
                success,
                error_message
            ))
            conn.commit()
    
    def get_recent_queries(self, limit: int = 50):
        """Get recent queries for viewing"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM query_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
    
    def get_query_stats(self):
        """Get basic statistics about queries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total queries
            cursor.execute('SELECT COUNT(*) FROM query_logs')
            total_queries = cursor.fetchone()[0]
            
            # Successful queries
            cursor.execute('SELECT COUNT(*) FROM query_logs WHERE success = 1')
            successful_queries = cursor.fetchone()[0]
            
            # Failed queries
            cursor.execute('SELECT COUNT(*) FROM query_logs WHERE success = 0')
            failed_queries = cursor.fetchone()[0]
            
            # Most common states
            cursor.execute('''
                SELECT state, COUNT(*) as count 
                FROM query_logs 
                WHERE state IS NOT NULL 
                GROUP BY state 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            top_states = cursor.fetchall()
            
            return {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'failed_queries': failed_queries,
                'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                'top_states': top_states
            } 