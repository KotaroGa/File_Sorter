
"""
Core file sorting functionality.
Uses ConfigManager for configuration.
"""

import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime

from .config_manager import ConfigManager



class FileSorter:
    """Main class for sorting files."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize File Sorter with configuratin.

        Args:
            config_path: Path to configuration file. If None, uses defautl.
        """
        self.config_manager = ConfigManager(config_path)
        self.categories = self.config_manager.get_categories()
        self.options = self.config_manager.get_options()
    
        # Setup loging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        self.logger.info("FileSorter initialized")
        self.logger.info(f"Categories: {list(self.categories.keys())}")
        self.logger.info(f"Options: {self.options}")

    

    def setup_logging(self) -> None:
        "Setup basic logging configuration."
        log_level = self.options.get("log_level", "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format='%(asctime)s - %(name)s -%(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('file_sorter.log'),
                logging.StreamHandler()
            ]
        )
    


    def __str__(self) -> str:
        """String representation of FileSorter."""
        return f"FileSorter(categories={len(self.categories)}, options={self.options})"
    


    def __repr__(self) -> str:
        """Detailed representation of FileSorter."""
        return f"FileSorter(config_path={self.config_manager.config_path})"
    