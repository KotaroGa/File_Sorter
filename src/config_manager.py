
"""
Configuration management for File Sorter.
Handles loading, validating, and providing default configurations.
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class ConfigManager:
    """Manages configuration for the file sorter."""
    
    # Default configuration if no config file exists
    DEFAULT_CONFIG = {
        "categories": {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "Audio": [".mp3", ".wav", ".flac", ".m4a", ".aac"],
            "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
            "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".json"],
            "Spreadsheets": [".xls", ".xlsx", ".csv"],
            "Presentations": [".ppt", ".pptx"],
        },
        "options": {
            "preserve_folder_structure": True,
            "conflict_resolution": "append_number",  # Options: append_number, skip, overwrite
            "dry_run": False,
            "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):  # FIXED: Added Optional[str]
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        self.config_path = Path(config_path) if config_path else Path("config.json")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Returns:
            Dictionary containing configuration.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # Merge user config with defaults (user config takes priority)
                config = self._merge_configs(self.DEFAULT_CONFIG, user_config)
                print(f"✅ Configuration loaded from {self.config_path}")
                return config
                
            except json.JSONDecodeError as e:
                print(f"⚠️  Error reading config file: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
            except Exception as e:
                print(f"⚠️  Unexpected error: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self._create_default_config()
            print(f"📄 Created default configuration at {self.config_path}")
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """
        Deep merge user config into default config.
        
        Args:
            default: Default configuration dictionary
            user: User configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                result[key] = self._merge_configs(result[key], value)
            else:
                # Overwrite with user value
                result[key] = value
        
        return result
    
    def _create_default_config(self) -> None:
        """Create a default configuration file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Failed to create config file: {e}")
    
    def get_categories(self) -> Dict[str, List[str]]:
        """Get the categories mapping."""
        return self.config.get("categories", {})
    
    def get_options(self) -> Dict[str, Any]:
        """Get the options."""
        return self.config.get("options", {})
    
    def save_config(self, config: Optional[Dict] = None) -> bool:  # FIXED: Added Optional[Dict]
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save. If None, saves current config.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            config_to_save = config if config is not None else self.config
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False


# Quick test function
def test_config_manager():
    """Test the ConfigManager class."""
    print("🧪 Testing ConfigManager...")
    
    # Test 1: Create manager without existing config
    print("\n1. Testing with no config file (will create default):")
    test_config_path = "test_config_temp.json"
    
    # Remove test file if it exists
    test_path = Path(test_config_path)
    if test_path.exists():
        test_path.unlink()
    
    cm = ConfigManager(test_config_path)
    print(f"   Categories: {list(cm.get_categories().keys())}")
    print(f"   Options: {cm.get_options()}")
    
    # Test 2: Modify and save
    print("\n2. Testing config modification:")
    config = cm.config.copy()
    config["options"]["log_level"] = "DEBUG"
    if cm.save_config(config):
        print("   Config modified and saved successfully")
    
    # Clean up
    if test_path.exists():
        test_path.unlink()
        print(f"   Cleaned up test file: {test_config_path}")
    
    print("\n✅ ConfigManager test complete!")


if __name__ == "__main__":
    # This runs when file is executed directly
    test_config_manager()