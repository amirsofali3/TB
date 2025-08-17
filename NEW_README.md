# AI Trading Bot

## 🎯 Complete AI-Powered Cryptocurrency Trading System

This is a sophisticated AI trading bot that automatically trades cryptocurrencies using machine learning, 196+ technical indicators, and advanced position management strategies.

## ✨ Key Features

### 🧠 AI & Machine Learning
- **Advanced ML Model**: Uses simplified rule-based model with feature selection
- **196+ Technical Indicators**: Complete set from technical_indicators_only.csv
- **RFE Feature Selection**: Automatically selects 30-50 best indicators
- **70%+ Confidence Threshold**: Only acts on high-confidence signals
- **Real-time Training**: Continuously learns from market data

### 💹 Trading Features
- **4-Hour Timeframe**: Operates on 4-hour candles for stability
- **Tiered TP/SL System**: TP1=3%, TP2=5%, TP3=8% with trailing stops
- **Demo Mode**: Start with $100 virtual balance for testing
- **Multi-Symbol Support**: BTCUSDT, ETHUSDT, SOLUSDT, DOGEUSDT
- **Emergency Exit**: Closes positions on opposite high-confidence signals

### 🌐 Web Dashboard
- **Real-time Monitoring**: Live updates every 10 seconds
- **System Status**: Balance, positions, signals overview
- **Signal History**: Recent trading signals with confidence levels
- **Position Management**: Active positions with P&L tracking
- **Model Metrics**: Training accuracy and feature selection info

### 📊 Database & Data
- **SQLite Database**: Local database with all trading data
- **Historical Data**: Stores candles, signals, positions, training runs
- **Comprehensive Logging**: Detailed system logs for debugging

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- No external dependencies required for basic operation

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/amirsofali3/TB.git
   cd TB
   ```

2. **Start the trading system:**
   ```bash
   ./start_trading.sh
   # or
   python complete_system.py
   ```

3. **Start the web dashboard (in another terminal):**
   ```bash
   ./start_dashboard.sh
   # or
   python dashboard_server.py
   ```

4. **Open dashboard in browser:**
   ```
   http://localhost:8000
   ```

## 📋 System Components

### Core Files
- `complete_system.py` - Main trading system with AI model and trading logic
- `dashboard_server.py` - Web dashboard for monitoring and control
- `minimal_startup.py` - Minimal system initialization for testing
- `technical_indicators_only.csv` - 196+ technical indicator definitions

### Database
- `database/sqlite_connection.py` - SQLite database connection and table management
- `data/trading_bot.db` - Local SQLite database (created automatically)

### AI/ML Components
- `ml/simple_model.py` - Simplified ML model with RFE feature selection
- `indicators/simple_calculator.py` - Technical indicators calculator

### Configuration
- `.env` - Environment configuration (database, API keys, settings)
- `requirements.txt` - Python package dependencies

## 🔧 System Architecture

### Trading Flow
1. **Data Collection**: Loads historical OHLCV data from database
2. **Feature Engineering**: Calculates 196+ technical indicators
3. **Model Training**: Uses RFE to select best 30-50 features
4. **Signal Generation**: Creates BUY/SELL signals with confidence scores
5. **Position Management**: Opens positions with tiered TP/SL levels
6. **Risk Management**: Monitors positions and exits on adverse conditions

### Database Schema
```sql
-- Trading signals
CREATE TABLE trading_signals (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR(20),
    signal_type VARCHAR(10),    -- BUY/SELL
    confidence REAL,            -- 0.0 to 1.0
    price REAL,
    model_version VARCHAR(50),
    created_at TIMESTAMP
);

-- Trading positions
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    symbol VARCHAR(20),
    side VARCHAR(10),           -- LONG/SHORT
    entry_price REAL,
    quantity REAL,
    tp1_price REAL,             -- Take Profit levels
    tp2_price REAL,
    tp3_price REAL,
    current_sl REAL,            -- Current Stop Loss
    status VARCHAR(20),         -- OPEN/CLOSED
    pnl REAL
);
```

## 🎛️ Configuration

### Environment Variables (.env)
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=TB
DB_USER=root
DB_PASSWORD=your_password

# Trading Configuration
DEMO_ACCOUNT_BALANCE=100
SIGNAL_CONFIDENCE_THRESHOLD=70
SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT,DOGEUSDT

# Take Profit / Stop Loss Settings
TP1_PERCENT=3.0
TP2_PERCENT=5.0
TP3_PERCENT=8.0

# Web Dashboard
WEB_PORT=8000
WEB_HOST=0.0.0.0
```

## 📊 Dashboard Features

### Real-time Monitoring
- **System Status**: Current balance, active positions, recent signals
- **AI Model Info**: Training accuracy, selected features, confidence threshold
- **Trading Signals**: Recent BUY/SELL signals with confidence levels
- **Position Management**: Active positions with P&L tracking

### API Endpoints
- `GET /api/status` - System status and metrics
- `GET /api/signals` - Recent trading signals
- `GET /api/positions` - Active and recent positions
- `GET /api/training` - ML model training information

## 🔬 Technical Indicators

The system implements 196+ technical indicators including:

### Trend Indicators
- Moving Averages (SMA, EMA, WMA)
- MACD, MACD Signal, MACD Histogram
- Bollinger Bands (Upper, Lower, Middle, Width, %B)
- Ichimoku Cloud (Tenkan, Kijun, Senkou A/B, Chikou)

### Momentum Indicators
- RSI (multiple periods)
- Stochastic %K and %D
- Williams %R
- Rate of Change (ROC)
- Momentum oscillators

### Volume Indicators
- Volume SMA
- Volume ratios
- Money Flow Index (MFI)
- Volume Weighted Average Price (VWAP)

### Volatility Indicators
- Average True Range (ATR)
- Bollinger Band Width
- Standard Deviation

## 🎯 Trading Strategy

### Signal Generation
- Uses ensemble of technical indicators
- ML model evaluates current market conditions
- Only acts on signals with >70% confidence
- Considers multiple timeframes for confirmation

### Position Management
- **Entry**: Opens position on high-confidence signal
- **TP1 (3%)**: Partial profit taking, move SL to breakeven
- **TP2 (5%)**: Additional profit taking, move SL to TP1
- **TP3 (8%)**: Final profit taking, move SL to TP2
- **Emergency Exit**: Close on opposite signal >70% confidence

### Risk Management
- Maximum 2% risk per trade
- Position sizing based on account balance
- Multiple position limit per symbol
- Stop loss always active

## 📈 Performance Monitoring

### Key Metrics
- **Training Accuracy**: ML model prediction accuracy
- **Signal Confidence**: Average confidence of generated signals
- **Win Rate**: Percentage of profitable trades
- **Average P&L**: Average profit/loss per trade
- **Maximum Drawdown**: Largest peak-to-trough decline

### Logging
- All trading actions logged with timestamps
- Signal generation details recorded
- Position entry/exit reasons documented
- System errors and warnings tracked

## 🛠️ Development & Customization

### Adding New Indicators
1. Add indicator definition to `technical_indicators_only.csv`
2. Implement calculation in `indicators/simple_calculator.py`
3. System automatically includes in feature selection

### Model Customization
- Adjust confidence threshold in `.env`
- Modify feature selection criteria in `ml/simple_model.py`
- Add new model types by extending base model class

### Exchange Integration
- Current system uses demo data
- Extend with real exchange API for live trading
- Implement order management for actual trading

## ⚠️ Important Notes

### Demo Mode
- System starts in demo mode with $100 virtual balance
- Uses simulated market data for testing
- No real money or API connections required

### Risk Disclaimer
This trading bot is for educational and research purposes. Cryptocurrency trading involves significant risk. Always test thoroughly in demo mode before considering live trading. The authors are not responsible for any financial losses.

### Future Enhancements
- Real exchange API integration
- Advanced ML models (neural networks, ensemble methods)
- Additional technical indicators
- Portfolio optimization
- Backtesting framework
- Mobile app dashboard

## 📞 Support

For issues and questions:
- Create GitHub issues for bugs and feature requests
- Check system logs for detailed error information
- Use the web dashboard for real-time debugging
- Review database tables for historical data analysis

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for the cryptocurrency trading community**

*Created by AI Assistant for amirsofali3/TB repository*