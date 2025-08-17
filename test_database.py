#!/usr/bin/env python3
"""
Simple test script to verify database functionality
"""

import os
import sys
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_basics():
    """Test basic database functionality"""
    
    logger.info("=" * 50)
    logger.info("AI TRADING BOT - DATABASE TEST")
    logger.info("=" * 50)
    
    try:
        # Test configuration loading
        logger.info("Step 1: Testing configuration loading...")
        from config.settings import DATABASE_CONFIG
        logger.info(f"Database config: {DATABASE_CONFIG}")
        
        # Test database connection
        logger.info("Step 2: Testing database connection...")
        from database.connection import db_connection
        
        result = db_connection.init_engine()
        logger.info(f"Database engine initialization: {result}")
        
        if not result:
            raise Exception("Database engine initialization failed")
            
        # Test connection
        result = db_connection.test_connection()
        logger.info(f"Database connection test: {result}")
        
        if not result:
            raise Exception("Database connection test failed")
        
        # Test models
        logger.info("Step 3: Testing database models...")
        from database.models import Base, SystemLog
        
        # Create tables
        Base.metadata.create_all(db_connection.engine)
        logger.info("Database tables created successfully")
        
        # Test inserting and querying data
        logger.info("Step 4: Testing database operations...")
        session = db_connection.get_session()
        
        try:
            # Insert a test log
            test_log = SystemLog(
                level='INFO',
                module='test',
                message='Database test successful',
                details='Testing basic database functionality'
            )
            session.add(test_log)
            session.commit()
            
            # Query it back
            logs = session.query(SystemLog).filter(SystemLog.module == 'test').all()
            logger.info(f"Found {len(logs)} test log entries")
            
            logger.info("=" * 50)
            logger.info("✅ DATABASE TEST PASSED!")
            logger.info("All database operations are working correctly.")
            logger.info("The bot should now be able to start successfully.")
            logger.info("=" * 50)
            
        finally:
            session.close()
            
        return True
        
    except Exception as e:
        logger.error(f"❌ DATABASE TEST FAILED: {e}")
        logger.info("=" * 50)
        return False

if __name__ == "__main__":
    success = test_database_basics()
    sys.exit(0 if success else 1)