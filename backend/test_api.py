#!/usr/bin/env python3
"""
Test file for INSIGHT Mark I API components
"""

import json
import sys
import os
import asyncio
from datetime import datetime, timedelta

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

def test_mark_i_engine():
    """Test Mark I Foundation Engine"""
    print("\n🧪 Testing Mark I Foundation Engine...")
    
    try:
        # Test 1: Engine initialization
        config_manager = ConfigManager()
        config_manager.load_config()
        
        from insight_core.engines.mark_i_foundation_engine import MarkIFoundationEngine
        engine = MarkIFoundationEngine(config_manager)
        print("✅ Engine initialized successfully")
        
        # Test 2: Test invalid date format
        async def test_invalid_date():
            result = await engine.get_daily_briefing("invalid-date")
            if "error" in result:
                print("✅ Invalid date correctly rejected")
            else:
                print("❌ Invalid date incorrectly accepted")
        
        asyncio.run(test_invalid_date())
        
        # Test 3: Test valid date (today)
        async def test_valid_date():
            today = datetime.now().strftime("%Y-%m-%d")
            result = await engine.get_daily_briefing(today)
            
            if "error" in result:
                print(f"⚠️ Briefing failed: {result['error']}")
            elif "briefing" in result:
                print("✅ Briefing generated successfully")
                print(f"📊 Posts processed: {result.get('posts_processed', 'N/A')}")
            else:
                print("❌ Unexpected response format")
        
        asyncio.run(test_valid_date())
        
    except Exception as e:
        print(f"❌ Engine test failed: {e}")

def test_daily_briefing_api():
    """Test Daily Briefing API Integration"""
    print("\n🧪 Testing Daily Briefing API...")
    
    try:
        # Test 1: Bridge daily briefing
        bridge = InsightBridge()
        
        async def test_bridge_briefing():
            today = datetime.now().strftime("%Y-%m-%d")
            result = await bridge.daily_briefing(today)
            
            if "error" in result:
                print(f"⚠️ Bridge briefing failed: {result['error']}")
            elif "briefing" in result:
                print("✅ Bridge briefing generated successfully")
            else:
                print("❌ Unexpected bridge response")
        
        asyncio.run(test_bridge_briefing())
        
        # Test 2: Test with past date (likely to have posts)
        async def test_past_date():
            past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            result = await bridge.daily_briefing(past_date)
            
            if "error" in result:
                print(f"⚠️ Past date briefing failed: {result['error']}")
            elif "briefing" in result:
                print("✅ Past date briefing generated successfully")
            else:
                print("❌ Unexpected past date response")
        
        asyncio.run(test_past_date())
        
    except Exception as e:
        print(f"❌ API test failed: {e}")

def test_end_to_end_flow():
    """Test complete end-to-end flow"""
    print("\n🧪 Testing End-to-End Flow...")
    
    try:
        # Test complete flow: Config → Engine → Bridge → API
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Check enabled sources
        enabled = config_manager.get_enabled_sources(config)
        print(f"📊 Enabled sources: {list(enabled.keys())}")
        
        # Test bridge integration
        bridge = InsightBridge()
        
        async def test_complete_flow():
            # Test recent date
            recent_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            print(f"🗓️ Testing date: {recent_date}")
            
            result = await bridge.daily_briefing(recent_date)
            
            if "error" in result:
                print(f"⚠️ End-to-end test failed: {result['error']}")
                return False
            elif "briefing" in result:
                print("✅ End-to-end test successful!")
                print(f"📄 Briefing length: {len(result['briefing'])} characters")
                
                # Show first 200 characters of briefing
                briefing_preview = result['briefing'][:200] + "..." if len(result['briefing']) > 200 else result['briefing']
                print(f"📝 Briefing preview: {briefing_preview}")
                return True
            else:
                print("❌ Unexpected end-to-end response")
                return False
        
        success = asyncio.run(test_complete_flow())
        
        if success:
            print("🎉 All systems operational!")
        else:
            print("⚠️ System needs attention")
            
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")

# Update main function to include new tests
def main():
    """Run all tests"""
    print("🚀 Starting INSIGHT Mark I API Tests")
    print("=" * 50)
    
    try:
        test_config_manager()
        test_bridge()
        test_data_persistence()
        test_error_handling()
        
        # New tests
        test_mark_i_engine()
        test_daily_briefing_api()
        test_end_to_end_flow()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        print("🔧 You can now test the API with:")
        print("   uvicorn main:app --reload")
        print("   Then visit: http://localhost:8000/api/sources")
        print("   Test briefing: POST to /api/daily with JSON body")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()