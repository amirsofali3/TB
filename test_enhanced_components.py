"""
Basic tests for enhanced components
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os

# Test the enhanced components
from indicators.enhanced_calculator import EnhancedIndicatorCalculator
from ml.enhanced_labeling import EnhancedTargetLabeler
from utils.prediction_scheduler import AdaptiveThresholdManager
from config.config_loader import ConfigLoader

class TestEnhancedComponents(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        # Create sample OHLCV data
        dates = pd.date_range(start='2023-01-01', periods=1000, freq='4H')
        np.random.seed(42)
        
        # Generate realistic price data
        close_prices = 100 + np.cumsum(np.random.randn(1000) * 0.5)
        high_prices = close_prices + np.abs(np.random.randn(1000) * 0.5)
        low_prices = close_prices - np.abs(np.random.randn(1000) * 0.5)
        open_prices = np.roll(close_prices, 1)
        open_prices[0] = close_prices[0]
        volumes = np.random.uniform(1000, 10000, 1000)
        
        self.sample_data = pd.DataFrame({
            'timestamp': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        })
        
        # Test configuration
        self.test_config = {
            'ml': {
                'labeling': {
                    'up_threshold': 0.02,
                    'down_threshold': -0.02
                },
                'class_balance': {
                    'method': 'class_weight',
                    'max_class_ratio': 0.7
                }
            },
            'adaptive_threshold': {
                'enabled': True,
                'target_signals_per_24h': 5,
                'min_threshold': 0.5,
                'max_threshold': 0.85,
                'adjustment_rate': 0.05,
                'evaluation_window': 24
            }
        }
    
    def test_enhanced_indicator_calculator(self):
        """Test enhanced indicator calculations"""
        calculator = EnhancedIndicatorCalculator()
        
        # Test individual indicators
        donchian_high = calculator.calculate_donchian(self.sample_data, 'Donchian_High_20', 20)
        self.assertIsInstance(donchian_high, pd.Series)
        self.assertEqual(len(donchian_high), len(self.sample_data))
        
        # Test OBV
        obv = calculator.calculate_obv(self.sample_data)
        self.assertIsInstance(obv, pd.Series)
        self.assertTrue(all(np.diff(obv[1:10]) != 0))  # OBV should change
        
        # Test CMF
        cmf = calculator.calculate_cmf(self.sample_data, 'CMF_20', 20)
        self.assertIsInstance(cmf, pd.Series)
        self.assertTrue(all(cmf.abs() <= 1))  # CMF should be between -1 and 1
        
        # Test full calculation
        enhanced_data = calculator.calculate_all_enhanced_indicators(self.sample_data)
        self.assertIsInstance(enhanced_data, pd.DataFrame)
        self.assertGreater(len(enhanced_data.columns), len(self.sample_data.columns))
        
        # Check that new indicators were added
        expected_indicators = ['Donchian_High_20', 'OBV', 'CMF_20', 'QStick_20']
        for indicator in expected_indicators:
            self.assertIn(indicator, enhanced_data.columns)
        
        print(f"✅ Enhanced indicators test passed - {len(enhanced_data.columns)} features calculated")
    
    def test_enhanced_target_labeler(self):
        """Test enhanced target labeling"""
        labeler = EnhancedTargetLabeler(self.test_config)
        
        # Test forward returns calculation
        returns = labeler.calculate_forward_returns(self.sample_data, periods=1)
        self.assertIsInstance(returns, pd.Series)
        self.assertEqual(len(returns), len(self.sample_data))
        
        # Test labeling
        labels = labeler.label_returns(returns)
        self.assertIsInstance(labels, pd.Series)
        
        # Check label values
        unique_labels = set(labels.dropna().unique())
        expected_labels = {'UP', 'DOWN', 'NEUTRAL'}
        self.assertTrue(unique_labels.issubset(expected_labels))
        
        # Test full labeling pipeline
        labeled_data, final_labels = labeler.create_labels(self.sample_data)
        self.assertIsInstance(labeled_data, pd.DataFrame)
        self.assertIsInstance(final_labels, pd.Series)
        self.assertEqual(len(labeled_data), len(final_labels))
        
        # Test labeling stats
        stats = labeler.get_labeling_stats(final_labels)
        self.assertIn('total_samples', stats)
        self.assertIn('class_distribution', stats)
        self.assertGreater(stats['total_samples'], 0)
        
        print(f"✅ Target labeling test passed - {stats['num_classes']} classes created")
    
    def test_adaptive_threshold_manager(self):
        """Test adaptive threshold management"""
        manager = AdaptiveThresholdManager(self.test_config)
        
        # Test initial threshold
        threshold = manager.get_threshold('BTCUSDT')
        self.assertIsInstance(threshold, float)
        self.assertGreaterEqual(threshold, manager.min_threshold)
        self.assertLessEqual(threshold, manager.max_threshold)
        
        # Test recording predictions
        manager.record_prediction('BTCUSDT', 0.8, 'UP')
        manager.record_prediction('BTCUSDT', 0.6, 'DOWN')
        
        # Test recording signals
        initial_threshold = manager.get_threshold('BTCUSDT')
        
        # Record multiple signals to trigger threshold adjustment
        for i in range(10):
            manager.record_signal('BTCUSDT', 'UP', 0.8, 
                                datetime.now() - timedelta(hours=i))
        
        # Check if threshold was adjusted (should increase due to high signal rate)
        new_threshold = manager.get_threshold('BTCUSDT')
        
        # Test status
        status = manager.get_status()
        self.assertIn('enabled', status)
        self.assertIn('symbols', status)
        self.assertIn('BTCUSDT', status['symbols'])
        
        print(f"✅ Adaptive threshold test passed - threshold: {initial_threshold:.3f} → {new_threshold:.3f}")
    
    def test_config_loader(self):
        """Test configuration loading"""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
trading:
  symbols: ["BTCUSDT", "ETHUSDT"]
  confidence_threshold: 0.75
  
ml:
  model_type: "catboost"
  
adaptive_threshold:
  enabled: true
  target_signals_per_24h: 8
""")
            temp_config_path = f.name
        
        try:
            # Test loading
            loader = ConfigLoader(temp_config_path)
            config = loader.load_config()
            
            self.assertIsInstance(config, dict)
            self.assertEqual(config['trading']['symbols'], ["BTCUSDT", "ETHUSDT"])
            self.assertEqual(config['trading']['confidence_threshold'], 0.75)
            self.assertEqual(config['ml']['model_type'], "catboost")
            self.assertTrue(config['adaptive_threshold']['enabled'])
            
            # Test get method
            symbols = loader.get('trading.symbols')
            self.assertEqual(symbols, ["BTCUSDT", "ETHUSDT"])
            
            # Test default value
            unknown_value = loader.get('unknown.key', 'default')
            self.assertEqual(unknown_value, 'default')
            
            print("✅ Configuration loader test passed")
            
        finally:
            os.unlink(temp_config_path)
    
    def test_feature_statistics(self):
        """Test feature statistics calculation"""
        calculator = EnhancedIndicatorCalculator()
        
        # Add some NaN values to test missing ratio
        test_data = self.sample_data.copy()
        test_data.loc[0:10, 'close'] = np.nan
        
        # Calculate indicators
        enhanced_data = calculator.calculate_all_enhanced_indicators(test_data)
        
        # Get statistics
        stats = calculator.get_feature_statistics(enhanced_data)
        
        self.assertIsInstance(stats, dict)
        self.assertGreater(len(stats), 0)
        
        # Check that statistics contain expected fields
        for feature_name, feature_stats in stats.items():
            self.assertIn('missing_ratio', feature_stats)
            self.assertIn('dtype', feature_stats)
            self.assertIn('variance', feature_stats)
            self.assertIsInstance(feature_stats['missing_ratio'], float)
        
        print(f"✅ Feature statistics test passed - {len(stats)} features analyzed")
    
    def test_class_balance_validation(self):
        """Test class balance detection"""
        labeler = EnhancedTargetLabeler(self.test_config)
        
        # Create imbalanced labels
        imbalanced_labels = pd.Series(['UP'] * 100 + ['DOWN'] * 10 + ['NEUTRAL'] * 5)
        
        # Test validation
        validation = labeler.validate_labeling_quality(self.sample_data, imbalanced_labels)
        
        self.assertIsInstance(validation, dict)
        self.assertIn('is_valid', validation)
        self.assertIn('issues', validation)
        self.assertIn('warnings', validation)
        
        # Should detect imbalance
        self.assertFalse(validation['is_valid'])
        
        print("✅ Class balance validation test passed")

class TestHealthCheck(unittest.TestCase):
    """Basic health check tests"""
    
    def test_basic_imports(self):
        """Test that all enhanced modules can be imported"""
        try:
            from config.config_loader import load_config
            from utils.logging import get_logger
            from utils.api_client import MultiSourceAPIClient
            from ml.enhanced_model import EnhancedTradingModel
            from ml.enhanced_feature_selection import EnhancedFeatureSelector
            print("✅ All enhanced modules import successfully")
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_config_loading(self):
        """Test basic config loading"""
        try:
            from config.config_loader import load_config
            config = load_config()
            self.assertIsInstance(config, dict)
            print("✅ Configuration loads successfully")
        except Exception as e:
            self.fail(f"Config loading failed: {e}")

if __name__ == '__main__':
    print("🧪 Running Enhanced Trading Bot Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestHealthCheck))
    suite.addTest(unittest.makeSuite(TestEnhancedComponents))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for failure in result.failures:
            print(f"FAILED: {failure[0]}")
        for error in result.errors:
            print(f"ERROR: {error[0]}")
    
    print(f"Tests run: {result.testsRun}")
    print("=" * 50)