from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql
from config.settings import DATABASE_CONFIG
import logging

# Install PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Initialize SQLAlchemy
db = SQLAlchemy()

class DatabaseConnection:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.connection_string = self._build_connection_string()
        
    def _build_connection_string(self):
        """Build MySQL connection string"""
        return (f"mysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
                f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}"
                f"/{DATABASE_CONFIG['database']}?charset={DATABASE_CONFIG['charset']}")
    
    def init_engine(self):
        """Initialize database engine"""
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_size=20,
                max_overflow=0,
                pool_pre_ping=True,
                echo=False
            )
            self.Session = sessionmaker(bind=self.engine)
            logging.info("Database engine initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize database engine: {e}")
            return False
    
    def get_session(self):
        """Get a new database session"""
        if not self.Session:
            self.init_engine()
        return self.Session()
    
    def test_connection(self):
        """Test database connection"""
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            logging.error(f"Database connection test failed: {e}")
            return False

# Global database connection instance
db_connection = DatabaseConnection()