#!/usr/bin/env python3
"""
Test file for INSIGHT Mark I API components
"""

import json
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from insight_core.config.config_manager import ConfigManager
from insight_bridge import InsightBridge

def test_config_manager():
    """Test ConfigManager functionality"""
    print("🧪 Testing ConfigManager...")
    
    # Test 1: Load existing config
    config_manager = ConfigManager()
    original_config = config_manager.load_config()
    print(f"✅ Original config loaded: {len(original_config)} keys")
    
    # Test 2: Test valid update
    test_update = {
        "sources": {
            "rss": {
                "enabled": True,
                "feeds": ["https://test-feed.com"]
            }
        }
    }
    
    result = config_manager.update_config(test_update)
    if result:
        print("✅ Valid update successful")
    else:
        print("❌ Valid update failed")
    
    # Test 3: Test invalid update
    invalid_update = {"invalid": "structure"}
    result = config_manager.update_config(invalid_update)
    if result is None:
        print("✅ Invalid update correctly rejected")
    else:
        print("❌ Invalid update incorrectly accepted")
    
    # Test 4: Restore original config
    config_manager.update_config(original_config)
    print("✅ Original config restored")

def test_bridge():
    """Test InsightBridge functionality"""
    print("\n🧪 Testing InsightBridge...")
    
    bridge = InsightBridge()
    
    # Test 1: Get sources
    sources = bridge.get_sources()
    print(f"✅ Sources retrieved: {len(sources)} keys")
    
    # Test 2: Get enabled sources
    enabled = bridge.get_enabled_sources()
    print(f"✅ Enabled sources: {enabled}")
    
    # Test 3: Update config through bridge
    test_update = {
        "sources": {
            "telegram": {
                "enabled": False,
                "channels": ["test_channel"]
            }
        }
    }
    
    result = bridge.update_config(test_update)
    if result:
        print("✅ Bridge update successful")
        
        # Verify update
        new_sources = bridge.get_sources()
        if not new_sources["sources"]["telegram"]["enabled"]:
            print("✅ Update verified in memory")
        else:
            print("❌ Update not reflected in memory")
    else:
        print("❌ Bridge update failed")

def test_data_persistence():
    """Test that updates persist to file"""
    print("\n🧪 Testing Data Persistence...")
    
    # Create first instance and update
    bridge1 = InsightBridge()
    original_config = bridge1.get_sources()
    
    test_update = {
        "metadata": {
            "name": "Test Update",
            "description": "Testing persistence",
            "version": "1.0.1"
        }
    }
    
    result = bridge1.update_config(test_update)
    if result:
        print("✅ Update applied by first instance")
        
        # Create second instance and check
        bridge2 = InsightBridge()
        new_config = bridge2.get_sources()
        
        if new_config["metadata"]["name"] == "Test Update":
            print("✅ Changes persisted to file")
        else:
            print("❌ Changes not persisted")
        
        # Restore original
        bridge2.update_config(original_config)
        print("✅ Original config restored")
    else:
        print("❌ Update failed")

def test_error_handling():
    """Test error handling"""
    print("\n🧪 Testing Error Handling...")
    
    bridge = InsightBridge()
    
    # Test invalid structure
    invalid_configs = [
        {},  # Empty
        {"sources": "invalid"},  # Wrong type
        {"metadata": {"name": "test"}},  # Missing sources
        "not a dict",  # Not a dictionary
    ]
    
    for i, invalid_config in enumerate(invalid_configs):
        result = bridge.update_config(invalid_config)
        if result is None:
            print(f"✅ Invalid config {i+1} correctly rejected")
        else:
            print(f"❌ Invalid config {i+1} incorrectly accepted")

def main():
    """Run all tests"""
    print("🚀 Starting INSIGHT Mark I API Tests")
    print("=" * 50)
    
    try:
        test_config_manager()
        test_bridge()
        test_data_persistence()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        print("🔧 You can now test the API with:")
        print("   uvicorn main:app --reload")
        print("   Then visit: http://localhost:8000/api/sources")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()