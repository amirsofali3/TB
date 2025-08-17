# AI Trading Bot - Quick Setup Guide

## ⚡ Quick Start (1 Minute Setup)

If you're experiencing startup issues, run the automated setup:

```bash
python3 easy_setup.py
```

Then start the bot:
```bash
./start_bot.sh
# OR
python3 main.py
```

## 🔧 Manual Setup (If Needed)

### 1. Install Dependencies
```bash
pip install sqlalchemy flask flask-cors pandas numpy scikit-learn python-dotenv PyMySQL requests
```

### 2. Database Setup
The bot now supports **automatic fallback to SQLite** if MySQL is not available:

- **MySQL (Recommended for production)**: Configure in `.env` file
- **SQLite (Automatic fallback)**: No setup needed - works out of the box

### 3. Configuration
Edit `.env` file (optional):
```bash
# Database (optional - SQLite fallback available)  
DB_HOST=localhost
DB_PORT=3306
DB_NAME=TB
DB_USER=root
DB_PASSWORD=your_password

# CoinEx API (optional - demo mode available)
COINEX_API_KEY=your_api_key
COINEX_SECRET_KEY=your_secret_key
```

## 🛠️ What Was Fixed

The following issues have been resolved:

### ✅ Database Connection Issues
- **Fixed**: `Table 'tb.system_logs' doesn't exist` error
- **Fixed**: SQLAlchemy 2.0 syntax compatibility (`text()` wrapper added)
- **Added**: SQLite fallback when MySQL is unavailable
- **Added**: Automatic table creation

### ✅ Dependency Issues  
- **Fixed**: `ModuleNotFoundError: No module named 'dotenv'`
- **Added**: Manual .env file parsing fallback
- **Fixed**: Flask-SQLAlchemy integration conflicts
- **Updated**: Compatible with both SQLAlchemy 1.4 and 2.0

### ✅ Startup Process
- **Improved**: Better error messages with troubleshooting tips
- **Added**: Graceful fallback mechanisms
- **Added**: Database initialization validation
- **Fixed**: Component initialization order

## 📊 System Status

After the fixes, you should see:
- ✅ Database connection working (MySQL or SQLite)
- ✅ Web dashboard accessible at http://localhost:5000  
- ✅ No "table doesn't exist" errors
- ✅ Proper logging system working
- ⚠️ Network errors only (normal in restricted environments)

## 🚨 Troubleshooting

### Database Issues
```bash
# Test database connection
python3 test_database.py

# Setup database manually
python3 setup_database.py
```

### Missing Packages
```bash
# Install specific package
pip install --user package_name

# Or run full setup
python3 easy_setup.py
```

### Permission Issues
```bash
# Use --user flag
pip install --user package_name

# Or create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🎯 Demo Mode

The bot runs in **DEMO MODE** by default:
- No real money at risk
- Virtual $100 balance  
- All trading logic functional
- Safe for testing and learning

## 📈 Production Setup

For live trading:
1. Set up MySQL database
2. Configure CoinEx API credentials
3. Set `DEMO_ACCOUNT_BALANCE=0` in config
4. Run with proper monitoring

## 🔍 Logs and Monitoring

- **Application logs**: `logs/trading_bot.log`
- **Database file**: `trading_bot.db` (if using SQLite)
- **Web dashboard**: http://localhost:5000
- **System status**: Check `/api/system/status` endpoint