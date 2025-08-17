import logging
import threading
import time
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime

from ml.model import TradingModel
from ml.trainer import ModelTrainer
from trading.position_manager import PositionManager
from trading.coinex_api import CoinExAPI
from data.fetcher import DataFetcher
from database.connection import db_connection
from database.models import TradingSignal, Position, TradingMetrics
from config.settings import TRADING_CONFIG, ML_CONFIG

class TradingEngine:
    """
    Main trading engine that coordinates all components
    """
    
    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.api = CoinExAPI()
        self.position_manager = PositionManager(self.api)
        self.data_fetcher = DataFetcher(self.api)
        self.model = None
        self.trainer = ModelTrainer()
        
        # Trading state
        self.is_running = False
        self.trading_thread = None
        self.model_trained = False
        self.demo_balance = TRADING_CONFIG['demo_balance']
        self.used_balance = 0.0
        
        # Configuration
        self.symbols = TRADING_CONFIG['symbols']
        self.confidence_threshold = TRADING_CONFIG['confidence_threshold']
        self.timeframe = TRADING_CONFIG['timeframe']
        
        # Thread management
        self.stop_trading = False
        
        self.logger.info(f"Trading engine initialized (Demo: {demo_mode})")
    
    def start_system(self):
        """Start the complete trading system"""
        try:
            self.logger.info("Starting trading system...")
            
            # 1. Test connections
            if not self._test_connections():
                raise Exception("Connection tests failed")
            
            # 2. Initialize data fetching
            self.data_fetcher.start_real_time_updates()
            
            # 3. Train model if needed
            if not self.model_trained:
                self.logger.info("Training AI model...")
                self.train_model()
            
            # 4. Start trading
            self.start_trading()
            
            self.logger.info("Trading system started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start trading system: {e}")
            raise
    
    def stop_system(self):
        """Stop the complete trading system"""
        try:
            self.logger.info("Stopping trading system...")
            
            # Stop trading
            self.stop_trading_flag = True
            if self.trading_thread and self.trading_thread.is_alive():
                self.trading_thread.join(timeout=10)
            
            # Stop position monitoring
            self.position_manager.stop_position_monitoring()
            
            # Stop data fetching
            self.data_fetcher.stop_real_time_updates()
            
            self.is_running = False
            self.logger.info("Trading system stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping trading system: {e}")
    
    def train_model(self, retrain: bool = False) -> Dict[str, Any]:
        """Train or retrain the AI model"""
        try:
            self.logger.info(f"{'Retraining' if retrain else 'Training'} AI model...")
            
            # Train model with RFE
            training_result = self.trainer.train_with_rfe(retrain=retrain)
            
            # Load trained model
            self.model = self.trainer.model
            self.model_trained = True
            
            self.logger.info(f"Model training completed: {training_result['model_version']}")
            
            return training_result
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            raise
    
    def start_trading(self):
        """Start the trading loop"""
        if self.is_running:
            self.logger.warning("Trading is already running")
            return
        
        if not self.model_trained or not self.model:
            raise ValueError("Model must be trained before starting trading")
        
        self.is_running = True
        self.stop_trading = False
        
        # Start position monitoring
        self.position_manager.start_position_monitoring()
        
        # Start trading thread
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
        
        self.logger.info("Trading started")
    
    def stop_trading(self):
        """Stop trading"""
        self.stop_trading = True
        self.is_running = False
        
        if self.trading_thread and self.trading_thread.is_alive():
            self.trading_thread.join(timeout=10)
        
        self.logger.info("Trading stopped")
    
    def _trading_loop(self):
        """Main trading loop"""
        while not self.stop_trading:
            try:
                # Process each symbol
                for symbol in self.symbols:
                    try:
                        self._process_symbol(symbol)
                    except Exception as e:
                        self.logger.error(f"Error processing {symbol}: {e}")
                
                # Update trading metrics
                self._update_trading_metrics()
                
                # Sleep for next iteration (4-hour timeframe)
                time.sleep(60)  # Check every minute but signal on timeframe completion
                
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                time.sleep(60)
    
    def _process_symbol(self, symbol: str):
        """Process trading signals for a specific symbol"""
        try:
            # Get latest market data with indicators
            latest_data = self.data_fetcher.get_latest_data_with_indicators(symbol)
            
            if latest_data is None or latest_data.empty:
                self.logger.warning(f"No data available for {symbol}")
                return
            
            # Check if we're at a new timeframe boundary (4h)
            if not self._is_new_timeframe(symbol):
                return
            
            # Generate prediction
            prediction_result = self._generate_signal(latest_data, symbol)
            
            if prediction_result and prediction_result['meets_threshold']:
                signal = prediction_result['signal']
                confidence = prediction_result['confidence']
                
                self.logger.info(f"Signal generated for {symbol}: {signal} (confidence: {confidence:.3f})")
                
                # Record signal in database
                self._record_signal(symbol, signal, confidence, latest_data['close'].iloc[-1])
                
                # Process signal
                if signal == 'BUY':
                    self._process_buy_signal(symbol, confidence, latest_data['close'].iloc[-1])
                elif signal == 'SELL':
                    self._process_sell_signal(symbol, confidence, latest_data['close'].iloc[-1])
            
        except Exception as e:
            self.logger.error(f"Error processing symbol {symbol}: {e}")
    
    def _generate_signal(self, data: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate trading signal using AI model"""
        try:
            # Get features from the latest row
            feature_columns = self.model.feature_names
            latest_features = {}
            
            for feature in feature_columns:
                if feature in data.columns:
                    latest_features[feature] = data[feature].iloc[-1]
                else:
                    self.logger.warning(f"Feature {feature} not found for {symbol}")
                    latest_features[feature] = 0.0
            
            # Generate prediction
            prediction_result = self.model.predict_single(latest_features)
            
            return prediction_result
            
        except Exception as e:
            self.logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    def _process_buy_signal(self, symbol: str, confidence: float, current_price: float):
        """Process BUY signal"""
        try:
            # Check if we already have a position for this symbol
            existing_position = self._get_open_position(symbol)
            if existing_position:
                self.logger.info(f"Already have open position for {symbol}, skipping BUY signal")
                return
            
            # Calculate position size
            position_size = self._calculate_position_size(symbol, current_price)
            
            if position_size <= 0:
                self.logger.warning(f"Insufficient balance for {symbol} position")
                return
            
            if self.demo_mode:
                # Demo trading
                position_id = self.position_manager.open_position(
                    symbol, 'LONG', position_size, current_price, confidence
                )
                
                if position_id:
                    # Update used balance
                    position_value = position_size * current_price
                    self.used_balance += position_value
                    self.logger.info(f"Demo BUY order placed for {symbol}: {position_size} @ {current_price}")
            else:
                # Live trading
                try:
                    # Place market buy order
                    order_result = self.api.place_order(
                        symbol, 'buy', position_size, order_type='market'
                    )
                    
                    if order_result:
                        position_id = self.position_manager.open_position(
                            symbol, 'LONG', position_size, current_price, confidence
                        )
                        self.logger.info(f"Live BUY order placed for {symbol}: {position_size} @ {current_price}")
                
                except Exception as e:
                    self.logger.error(f"Failed to place live BUY order for {symbol}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error processing BUY signal for {symbol}: {e}")
    
    def _process_sell_signal(self, symbol: str, confidence: float, current_price: float):
        """Process SELL signal"""
        try:
            # Check for existing position
            existing_position = self._get_open_position(symbol)
            
            if existing_position:
                # Emergency close if high confidence opposite signal
                if confidence >= self.confidence_threshold:
                    self.position_manager.emergency_close_position(existing_position['id'], confidence)
                    self.logger.info(f"Emergency close triggered for {symbol} position")
            else:
                # No existing position for SELL signal - just log
                self.logger.info(f"SELL signal for {symbol} but no open position - waiting for BUY signal")
            
        except Exception as e:
            self.logger.error(f"Error processing SELL signal for {symbol}: {e}")
    
    def _calculate_position_size(self, symbol: str, price: float) -> float:
        """Calculate position size based on risk management"""
        try:
            available_balance = self.demo_balance - self.used_balance if self.demo_mode else self._get_real_balance()
            
            # Use percentage of available balance
            risk_amount = available_balance * TRADING_CONFIG['risk_per_trade']
            position_size = risk_amount / price
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0.0
    
    def _get_real_balance(self) -> float:
        """Get real account balance"""
        try:
            balance_info = self.api.get_balance()
            # Extract USDT balance
            return float(balance_info.get('USDT', {}).get('available', 0.0))
        except Exception as e:
            self.logger.error(f"Error getting real balance: {e}")
            return 0.0
    
    def _get_open_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get open position for symbol"""
        try:
            session = db_connection.get_session()
            position = session.query(Position).filter(
                Position.symbol == symbol,
                Position.status == 'OPEN'
            ).first()
            session.close()
            
            if position:
                return {
                    'id': position.id,
                    'symbol': position.symbol,
                    'side': position.side,
                    'entry_price': position.entry_price,
                    'quantity': position.quantity
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting open position for {symbol}: {e}")
            return None
    
    def _record_signal(self, symbol: str, signal: str, confidence: float, price: float):
        """Record trading signal in database"""
        try:
            session = db_connection.get_session()
            
            trading_signal = TradingSignal(
                symbol=symbol,
                signal_type=signal,
                confidence=confidence,
                price=price,
                model_version=self.model.model_version if self.model else 'unknown'
            )
            
            session.add(trading_signal)
            session.commit()
            session.close()
            
        except Exception as e:
            self.logger.error(f"Error recording signal: {e}")
    
    def _is_new_timeframe(self, symbol: str) -> bool:
        """Check if we're at a new 4-hour timeframe boundary"""
        # For 4-hour timeframe, check if current hour is divisible by 4
        current_hour = datetime.now().hour
        return current_hour % 4 == 0
    
    def _update_trading_metrics(self):
        """Update daily trading metrics"""
        try:
            # Get today's metrics
            today = datetime.now().date()
            
            session = db_connection.get_session()
            
            # Get existing or create new metric record
            metric = session.query(TradingMetrics).filter(
                TradingMetrics.date == today
            ).first()
            
            if not metric:
                metric = TradingMetrics(
                    date=today,
                    portfolio_value=self.demo_balance if self.demo_mode else self._get_real_balance(),
                    available_balance=self.demo_balance - self.used_balance if self.demo_mode else self._get_real_balance()
                )
                session.add(metric)
            
            # Update with current data
            positions = self.position_manager.get_active_positions()
            total_pnl = sum(pos['pnl'] for pos in positions)
            
            metric.daily_pnl = total_pnl
            metric.daily_pnl_percentage = (total_pnl / self.demo_balance) * 100 if self.demo_balance > 0 else 0
            
            session.commit()
            session.close()
            
        except Exception as e:
            self.logger.error(f"Error updating trading metrics: {e}")
    
    def _test_connections(self) -> bool:
        """Test all system connections"""
        try:
            # Test database
            if not db_connection.test_connection():
                return False
            
            # Test API if not demo mode
            if not self.demo_mode:
                if not self.api.test_connection():
                    return False
            
            self.logger.info("All connection tests passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'is_running': self.is_running,
            'demo_mode': self.demo_mode,
            'model_trained': self.model_trained,
            'model_version': self.model.model_version if self.model else None,
            'demo_balance': self.demo_balance,
            'used_balance': self.used_balance,
            'available_balance': self.demo_balance - self.used_balance,
            'active_positions': len(self.position_manager.get_active_positions()),
            'symbols': self.symbols,
            'timeframe': self.timeframe,
            'confidence_threshold': self.confidence_threshold
        }
    
    def get_trading_summary(self) -> Dict[str, Any]:
        """Get trading performance summary"""
        try:
            positions = self.position_manager.get_active_positions()
            total_pnl = sum(pos['pnl'] for pos in positions)
            
            return {
                'total_positions': len(positions),
                'total_unrealized_pnl': total_pnl,
                'portfolio_value': self.demo_balance + total_pnl,
                'positions': positions
            }
            
        except Exception as e:
            self.logger.error(f"Error getting trading summary: {e}")
            return {}