import requests
import hashlib
import hmac
import time
import json
import logging
from typing import Dict, List, Any, Optional
from config.settings import COINEX_CONFIG

class CoinExAPI:
    """
    CoinEx API client for cryptocurrency trading
    """
    
    def __init__(self):
        self.api_key = COINEX_CONFIG['api_key']
        self.secret_key = COINEX_CONFIG['secret_key']
        self.sandbox_mode = COINEX_CONFIG['sandbox_mode']
        self.base_url = COINEX_CONFIG['sandbox_url'] if self.sandbox_mode else COINEX_CONFIG['base_url']
        self.logger = logging.getLogger(__name__)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TradingBot/1.0'
        })
    
    def _generate_signature(self, params: Dict[str, Any], secret_key: str) -> str:
        """Generate signature for API authentication"""
        sorted_params = sorted(params.items())
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        return hmac.new(
            secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.md5
        ).hexdigest().upper()
    
    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None,
                     auth_required: bool = True) -> Dict[str, Any]:
        """Make authenticated request to CoinEx API"""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        # Add timestamp for authenticated requests
        if auth_required:
            params['access_id'] = self.api_key
            params['tonce'] = int(time.time() * 1000)
            
            # Generate signature
            signature = self._generate_signature(params, self.secret_key)
            
            headers = {
                'authorization': signature,
            }
        else:
            headers = {}
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('code') == 0:
                return result.get('data', {})
            else:
                self.logger.error(f"API error: {result}")
                raise Exception(f"CoinEx API error: {result.get('message', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker information for a symbol"""
        try:
            endpoint = f"market/ticker?market={symbol}"
            return self._make_request('GET', endpoint, auth_required=False)
        except Exception as e:
            self.logger.error(f"Error getting ticker for {symbol}: {e}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        try:
            endpoint = "balance/info"
            return self._make_request('GET', endpoint)
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            raise
    
    def place_order(self, symbol: str, side: str, amount: float, price: float = None,
                   order_type: str = 'limit') -> Dict[str, Any]:
        """
        Place a trading order
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'buy' or 'sell'
            amount: Order amount
            price: Order price (for limit orders)
            order_type: 'limit' or 'market'
        """
        try:
            params = {
                'market': symbol,
                'type': side,
                'amount': str(amount),
            }
            
            if order_type == 'limit':
                if price is None:
                    raise ValueError("Price required for limit orders")
                params['price'] = str(price)
                
            endpoint = "order/limit" if order_type == 'limit' else "order/market"
            
            result = self._make_request('POST', endpoint, params)
            self.logger.info(f"Order placed: {symbol} {side} {amount} @ {price}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            raise
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            params = {
                'market': symbol,
                'id': order_id
            }
            
            endpoint = "order/pending/cancel"
            result = self._make_request('POST', endpoint, params)
            self.logger.info(f"Order cancelled: {order_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Get order status"""
        try:
            params = {
                'market': symbol,
                'id': order_id
            }
            
            endpoint = "order/status"
            return self._make_request('GET', endpoint, params)
            
        except Exception as e:
            self.logger.error(f"Error getting order status {order_id}: {e}")
            raise
    
    def get_open_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get open orders"""
        try:
            params = {}
            if symbol:
                params['market'] = symbol
            
            endpoint = "order/pending"
            result = self._make_request('GET', endpoint, params)
            
            return result.get('data', []) if isinstance(result, dict) else []
            
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            raise
    
    def get_trade_history(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trade history"""
        try:
            params = {
                'market': symbol,
                'limit': limit
            }
            
            endpoint = "order/deals"
            result = self._make_request('GET', endpoint, params)
            
            return result.get('data', []) if isinstance(result, dict) else []
            
        except Exception as e:
            self.logger.error(f"Error getting trade history for {symbol}: {e}")
            raise
    
    def get_kline_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get candlestick data
        
        Args:
            symbol: Trading pair
            timeframe: Time interval (1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week)
            limit: Number of candles to fetch
        """
        try:
            params = {
                'market': symbol,
                'type': timeframe,
                'limit': limit
            }
            
            endpoint = "market/kline"
            result = self._make_request('GET', endpoint, params, auth_required=False)
            
            # Convert to standard format
            candles = []
            if isinstance(result, list):
                for candle in result:
                    if len(candle) >= 6:
                        candles.append({
                            'timestamp': int(candle[0]),
                            'open': float(candle[1]),
                            'close': float(candle[2]),
                            'high': float(candle[3]),
                            'low': float(candle[4]),
                            'volume': float(candle[5]),
                        })
            
            return candles
            
        except Exception as e:
            self.logger.error(f"Error getting kline data for {symbol}: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Try to get server time (doesn't require auth)
            endpoint = "common/timestamp"
            self._make_request('GET', endpoint, auth_required=False)
            
            # Try to get balance (requires auth)
            if self.api_key and self.secret_key:
                self.get_balance()
            
            self.logger.info("CoinEx API connection successful")
            return True
            
        except Exception as e:
            self.logger.error(f"CoinEx API connection failed: {e}")
            return False