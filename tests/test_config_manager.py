"""
Simple working test for ConfigManager.
"""
import json
import tempfile
from pathlib import Path
import sys
import os

# SIMPLE FIX: Just go up one level from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config_manager import ConfigManager

def test_default_config():
    print("🧪 Testing default config...")
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test.json"
        cm = ConfigManager(str(config_path))
        assert "Images" in cm.get_categories()
        print("✅ Default config test passed")
        return True

def main():
    print("🧪 Running ConfigManager tests")
    print("=" * 40)
    
    try:
        test_default_config()
        print("=" * 40)
        print("🎉 All tests passed!")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)