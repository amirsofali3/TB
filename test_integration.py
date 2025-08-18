#!/usr/bin/env python3
"""
Simple integration test for enhanced components
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all enhanced modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from config.config_loader import ConfigLoader
        print("✅ Config loader imported")
        
        from utils.logging import SafeFormatter, JSONFormatter
        print("✅ Logging utilities imported")
        
        # Test config loading
        config = ConfigLoader().load_config()
        print(f"✅ Configuration loaded: {len(config)} sections")
        
        # Test logging formatter
        formatter = SafeFormatter(emoji_strip=True)
        print("✅ Safe formatter created")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_config_structure():
    """Test configuration structure"""
    print("\n🔧 Testing configuration structure...")
    
    try:
        from config.config_loader import ConfigLoader
        config = ConfigLoader().load_config()
        
        # Check required sections
        required_sections = ['trading', 'ml', 'adaptive_threshold', 'logging', 'web']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing config section: {section}")
                return False
            print(f"✅ Config section present: {section}")
        
        # Check specific values
        if config['ml']['model_type'] not in ['xgboost', 'catboost']:
            print(f"❌ Invalid model type: {config['ml']['model_type']}")
            return False
        
        print(f"✅ Model type configured: {config['ml']['model_type']}")
        print(f"✅ Symbols configured: {config['trading']['symbols']}")
        print(f"✅ Adaptive thresholds: {'enabled' if config['adaptive_threshold']['enabled'] else 'disabled'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config structure test failed: {e}")
        return False

def test_api_client_structure():
    """Test API client class structure"""
    print("\n🌐 Testing API client structure...")
    
    try:
        from utils.api_client import RobustAPIClient, CoinExAPIClient, BinanceAPIClient
        print("✅ API client classes imported")
        
        # Test that classes have required methods
        required_methods = ['_make_request_with_retry', 'get_health_status']
        
        for method in required_methods:
            if not hasattr(RobustAPIClient, method):
                print(f"❌ Missing method in RobustAPIClient: {method}")
                return False
        
        print("✅ RobustAPIClient has required methods")
        
        return True
        
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        return False

def test_indicator_structure():
    """Test indicator calculator structure"""
    print("\n📊 Testing indicator calculator structure...")
    
    try:
        from indicators.enhanced_calculator import EnhancedIndicatorCalculator
        print("✅ Enhanced indicator calculator imported")
        
        calculator = EnhancedIndicatorCalculator()
        
        # Check indicator registry
        registry = calculator.indicator_registry
        if not registry:
            print("❌ Empty indicator registry")
            return False
        
        print(f"✅ Indicator registry loaded: {len(registry)} indicators")
        
        # Check for specific indicators
        expected_indicators = [
            'Donchian_High_20', 'OBV', 'CMF_20', 'Force_Index_2', 
            'QStick_20', 'KST', 'TSI_25_13', 'Heikin_Ashi_Close'
        ]
        
        missing_indicators = [ind for ind in expected_indicators if ind not in registry]
        if missing_indicators:
            print(f"❌ Missing indicators: {missing_indicators}")
            return False
        
        print("✅ All expected indicators present in registry")
        
        return True
        
    except Exception as e:
        print(f"❌ Indicator structure test failed: {e}")
        return False

def test_ml_components_structure():
    """Test ML components structure"""
    print("\n🤖 Testing ML components structure...")
    
    try:
        # Test enhanced model
        from ml.enhanced_model import EnhancedTradingModel
        print("✅ Enhanced trading model imported")
        
        # Test enhanced feature selection
        from ml.enhanced_feature_selection import EnhancedFeatureSelector
        print("✅ Enhanced feature selector imported")
        
        # Test enhanced labeling
        from ml.enhanced_labeling import EnhancedTargetLabeler
        print("✅ Enhanced target labeler imported")
        
        return True
        
    except Exception as e:
        print(f"❌ ML components test failed: {e}")
        return False

def test_signal_management_structure():
    """Test signal management structure"""
    print("\n📡 Testing signal management structure...")
    
    try:
        from utils.signal_manager import SignalManager, SignalPersistence, WebSocketBroadcaster
        from utils.prediction_scheduler import PredictionScheduler, AdaptiveThresholdManager
        print("✅ Signal management components imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Signal management test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Enhanced Trading Bot - Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Structure", test_config_structure),
        ("API Client Structure", test_api_client_structure),
        ("Indicator Structure", test_indicator_structure),
        ("ML Components Structure", test_ml_components_structure),
        ("Signal Management Structure", test_signal_management_structure)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("🚀 Enhanced trading bot components are ready!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
    
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)