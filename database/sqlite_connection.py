import sqlite3
import logging
import os
from typing import Optional

class DatabaseConnection:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'trading_bot.db')
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def init_engine(self):
        """Initialize SQLite database"""
        try:
            # For now, use simple SQLite connection
            self.logger.info(f"Initializing SQLite database at: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            self._create_tables(conn)
            conn.close()
            self.logger.info("Database engine initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize database engine: {e}")
            return False
    
    def _create_tables(self, conn):
        """Create necessary tables if they don't exist"""
        cursor = conn.cursor()
        
        # Candles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol VARCHAR(20) NOT NULL,
                timestamp INTEGER NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        # System logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level VARCHAR(10) NOT NULL,
                component VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # Training runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'RUNNING',
                model_version VARCHAR(50),
                accuracy REAL,
                selected_features TEXT,
                hyperparameters TEXT,
                metrics TEXT
            )
        ''')
        
        # Trading signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol VARCHAR(20) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                signal_type VARCHAR(10) NOT NULL,
                confidence REAL NOT NULL,
                price REAL NOT NULL,
                model_version VARCHAR(50),
                indicators_used TEXT,
                executed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                entry_price REAL NOT NULL,
                quantity REAL NOT NULL,
                current_price REAL,
                initial_sl REAL,
                current_sl REAL,
                tp1_price REAL,
                tp2_price REAL,
                tp3_price REAL,
                tp1_hit BOOLEAN DEFAULT FALSE,
                tp2_hit BOOLEAN DEFAULT FALSE,
                tp3_hit BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'OPEN',
                pnl REAL DEFAULT 0.0,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                close_reason VARCHAR(50)
            )
        ''')
        
        conn.commit()
        self.logger.info("Database tables created/verified successfully")
    
    def get_session(self):
        """Get a database connection (SQLite doesn't use sessions like SQLAlchemy)"""
        return sqlite3.connect(self.db_path)
    
    def test_connection(self):
        """Test database connection"""
        try:
            conn = self.get_session()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False
    
    def add_candle_data(self, symbol: str, timestamp: int, open_price: float, 
                       high: float, low: float, close: float, volume: float):
        """Add candle data to the database"""
        try:
            conn = self.get_session()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO candles 
                (symbol, timestamp, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, timestamp, open_price, high, low, close, volume))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error adding candle data: {e}")
            return False
    
    def get_candle_data(self, symbol: str, limit: Optional[int] = None):
        """Get candle data for a symbol"""
        try:
            conn = self.get_session()
            cursor = conn.cursor()
            query = "SELECT * FROM candles WHERE symbol = ? ORDER BY timestamp DESC"
            if limit:
                query += f" LIMIT {limit}"
            cursor.execute(query, (symbol,))
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            self.logger.error(f"Error getting candle data: {e}")
            return []

# Global database connection instance
db_connection = DatabaseConnection()