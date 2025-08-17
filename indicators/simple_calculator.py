"""
Simple Technical Indicators Calculator
Works without pandas and ta-lib dependencies
"""

import logging
import math
from typing import List, Dict, Any, Tuple

class SimpleIndicatorCalculator:
    """
    Simplified technical indicators calculator
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_indicators(self, ohlcv_data: List[Tuple[float, float, float, float, float]]) -> Dict[str, List[float]]:
        """
        Calculate basic technical indicators from OHLCV data
        
        Args:
            ohlcv_data: List of tuples (open, high, low, close, volume)
            
        Returns:
            Dictionary of indicator name -> list of values
        """
        if not ohlcv_data or len(ohlcv_data) < 20:
            self.logger.warning("Not enough data for indicator calculation")
            return {}
        
        indicators = {}
        
        # Extract OHLCV arrays
        opens = [x[0] for x in ohlcv_data]
        highs = [x[1] for x in ohlcv_data]
        lows = [x[2] for x in ohlcv_data]
        closes = [x[3] for x in ohlcv_data]
        volumes = [x[4] for x in ohlcv_data]
        
        try:
            # Basic price indicators
            indicators['close'] = closes
            indicators['high'] = highs
            indicators['low'] = lows
            indicators['open'] = opens
            indicators['volume'] = volumes
            
            # Prerequisites
            indicators['Prev Close'] = [0] + closes[:-1]
            indicators['Prev High'] = [0] + highs[:-1]
            indicators['Prev Low'] = [0] + lows[:-1]
            indicators['Typical Price (TP)'] = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
            indicators['Median Price (MP)'] = [(h + l) / 2 for h, l in zip(highs, lows)]
            indicators['HLC3'] = indicators['Typical Price (TP)']
            indicators['OHLC4'] = [(o + h + l + c) / 4 for o, h, l, c in zip(opens, highs, lows, closes)]
            
            # Simple Moving Averages
            for period in [5, 9, 10, 14, 20, 21, 26, 50, 100, 200]:
                indicators[f'SMA_{period}'] = self._sma(closes, period)
            
            # Exponential Moving Averages
            for period in [12, 26, 50, 200]:
                indicators[f'EMA_{period}'] = self._ema(closes, period)
            
            # RSI indicators
            for period in [14, 21]:
                indicators[f'RSI_{period}'] = self._rsi(closes, period)
            
            # Stochastic indicators
            for period in [5, 9, 14]:
                stoch_k = self._stochastic_k(highs, lows, closes, period)
                indicators[f'Stoch_%K_{period}'] = stoch_k
                indicators[f'Stoch_%D_{period}'] = self._sma(stoch_k, 3)
            
            # Williams %R
            for period in [7, 14, 20]:
                indicators[f'Williams_%R_{period}'] = self._williams_r(highs, lows, closes, period)
            
            # ROC (Rate of Change)
            for period in [1, 2, 5, 10, 20]:
                indicators[f'ROC_{period}'] = self._roc(closes, period)
            
            # Momentum
            for period in [10, 14, 20]:
                indicators[f'Momentum_{period}'] = self._momentum(closes, period)
            
            # MACD
            ema12 = self._ema(closes, 12)
            ema26 = self._ema(closes, 26)
            macd_line = [a - b for a, b in zip(ema12, ema26)]
            indicators['MACD'] = macd_line
            indicators['MACD_Signal'] = self._ema(macd_line, 9)
            indicators['MACD_Histogram'] = [a - b for a, b in zip(macd_line, indicators['MACD_Signal'])]
            
            # Bollinger Bands
            sma20 = self._sma(closes, 20)
            bb_upper, bb_lower = self._bollinger_bands(closes, 20, 2)
            indicators['Bollinger_Upper'] = bb_upper
            indicators['Bollinger_Lower'] = bb_lower
            indicators['Bollinger_Middle'] = sma20
            indicators['Bollinger_Width'] = [(u - l) / m if m != 0 else 0 for u, l, m in zip(bb_upper, bb_lower, sma20)]
            indicators['Bollinger_%B'] = [((c - l) / (u - l)) if (u - l) != 0 else 0.5 for c, u, l in zip(closes, bb_upper, bb_lower)]
            
            # ATR (Average True Range)
            indicators['ATR_14'] = self._atr(highs, lows, closes, 14)
            
            # Volume indicators
            indicators['Volume_SMA_20'] = self._sma(volumes, 20)
            indicators['Volume_Ratio'] = [v / avg if avg != 0 else 1 for v, avg in zip(volumes, indicators['Volume_SMA_20'])]
            
            # Price changes
            indicators['Price_Change'] = [0] + [closes[i] - closes[i-1] for i in range(1, len(closes))]
            indicators['Price_Change_Pct'] = [0] + [(closes[i] - closes[i-1]) / closes[i-1] * 100 if closes[i-1] != 0 else 0 for i in range(1, len(closes))]
            
            # High-Low indicators
            indicators['High_Low_Pct'] = [(h - l) / l * 100 if l != 0 else 0 for h, l in zip(highs, lows)]
            
            self.logger.info(f"Calculated {len(indicators)} technical indicators")
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return {}
    
    def _sma(self, values: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        result = []
        for i in range(len(values)):
            if i < period - 1:
                result.append(values[i])  # Not enough data, use current value
            else:
                avg = sum(values[i-period+1:i+1]) / period
                result.append(avg)
        return result
    
    def _ema(self, values: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        if not values:
            return []
        
        alpha = 2 / (period + 1)
        result = [values[0]]  # First value
        
        for i in range(1, len(values)):
            ema = alpha * values[i] + (1 - alpha) * result[-1]
            result.append(ema)
        
        return result
    
    def _rsi(self, closes: List[float], period: int) -> List[float]:
        """Relative Strength Index"""
        if len(closes) < period + 1:
            return [50.0] * len(closes)
        
        gains = []
        losses = []
        
        # Calculate price changes
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            gains.append(max(0, change))
            losses.append(max(0, -change))
        
        # Calculate RSI
        result = [50.0]  # First value
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        for i in range(period, len(gains)):
            if avg_loss == 0:
                result.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                result.append(rsi)
            
            # Update averages
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        # Pad beginning with first calculated value
        while len(result) < len(closes):
            result.insert(0, result[0])
        
        return result[:len(closes)]
    
    def _stochastic_k(self, highs: List[float], lows: List[float], closes: List[float], period: int) -> List[float]:
        """%K Stochastic"""
        result = []
        
        for i in range(len(closes)):
            if i < period - 1:
                result.append(50.0)  # Default value
            else:
                high_n = max(highs[i-period+1:i+1])
                low_n = min(lows[i-period+1:i+1])
                
                if high_n == low_n:
                    k_percent = 50.0
                else:
                    k_percent = ((closes[i] - low_n) / (high_n - low_n)) * 100
                
                result.append(k_percent)
        
        return result
    
    def _williams_r(self, highs: List[float], lows: List[float], closes: List[float], period: int) -> List[float]:
        """Williams %R"""
        result = []
        
        for i in range(len(closes)):
            if i < period - 1:
                result.append(-50.0)  # Default value
            else:
                high_n = max(highs[i-period+1:i+1])
                low_n = min(lows[i-period+1:i+1])
                
                if high_n == low_n:
                    williams_r = -50.0
                else:
                    williams_r = ((high_n - closes[i]) / (high_n - low_n)) * -100
                
                result.append(williams_r)
        
        return result
    
    def _roc(self, closes: List[float], period: int) -> List[float]:
        """Rate of Change"""
        result = []
        
        for i in range(len(closes)):
            if i < period:
                result.append(0.0)  # Default value
            else:
                if closes[i-period] != 0:
                    roc = ((closes[i] - closes[i-period]) / closes[i-period]) * 100
                else:
                    roc = 0.0
                result.append(roc)
        
        return result
    
    def _momentum(self, closes: List[float], period: int) -> List[float]:
        """Momentum"""
        result = []
        
        for i in range(len(closes)):
            if i < period:
                result.append(0.0)  # Default value
            else:
                momentum = closes[i] - closes[i-period]
                result.append(momentum)
        
        return result
    
    def _bollinger_bands(self, closes: List[float], period: int, std_dev: float) -> Tuple[List[float], List[float]]:
        """Bollinger Bands Upper and Lower"""
        sma = self._sma(closes, period)
        upper = []
        lower = []
        
        for i in range(len(closes)):
            if i < period - 1:
                upper.append(closes[i] + std_dev)
                lower.append(closes[i] - std_dev)
            else:
                # Calculate standard deviation
                values = closes[i-period+1:i+1]
                mean = sma[i]
                variance = sum((x - mean) ** 2 for x in values) / period
                std = math.sqrt(variance)
                
                upper.append(mean + std_dev * std)
                lower.append(mean - std_dev * std)
        
        return upper, lower
    
    def _atr(self, highs: List[float], lows: List[float], closes: List[float], period: int) -> List[float]:
        """Average True Range"""
        if len(closes) < 2:
            return [0.0] * len(closes)
        
        true_ranges = []
        
        for i in range(1, len(closes)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        # Calculate ATR using EMA
        atr_values = [true_ranges[0]] if true_ranges else [0.0]
        alpha = 1.0 / period
        
        for i in range(1, len(true_ranges)):
            atr = alpha * true_ranges[i] + (1 - alpha) * atr_values[-1]
            atr_values.append(atr)
        
        # Pad beginning
        result = [atr_values[0]] + atr_values
        return result[:len(closes)]