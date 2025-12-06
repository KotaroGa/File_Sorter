
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
    


    def get_file_category(self, file_path: Path) -> Optional[str]:
        """
        Determine which category a file belongs to based on extension.
        
        Args:
            file_path: Path to the file

        Returns:
            Category name or None if no category matches

        Example:
            >>> sorter.get_file_category(path("photo.jpg"))
            'Images
        """
        if not file_path.is_file():
            self.logger.warning(f"Not a file: {file_path}")
            return None
        
        extension = file_path.suffix.lower()

        for category, extensions in self.categories.items():
            if extension in [ext.lower() for ext in extensions]:
                self.logger.debug(f"File {file_path.name} -> Category: {category}")
                return category
            
        self.logger.debug(f"No category for {file_path.name} (extension: {extension})")
        return None
    


    def get_target_path(self, source_path: Path, category: str) -> Path:
        """
        Determine where a file should be moved based on configuration.

        Args:
            source_path_ Original file path
            category: Category name

        Returns:
            Target path where file should be moved

        Note:
            Respects 'preserve_folder_structure' option
        """
        # Base target is source's parent / category
        source_parents = source_path.parent
        target_dir = source_parents / category

        # If preserve_folder_structure is False, flattern structure
        if not self.options.get("preserve_folder_structure", True):
            # For flattering, we use just the category folder
            # But we need to handle name conflicts (done in resolve_conflict)
            return target_dir / source_path.name
        
        # If preserving structure, keep relative path
        # Example: /home/user/Docs/Project/report.pdf -> /home/user/Docs/Project/Documents/report.pdf
        return target_dir / source_path.relative_to(source_parents)
    


    def scan_directory(self, directory_path: Path) -> Dict[str, List[Path]]:
        """
        Scan a directory and categorize all files.

        Args:
            directory_path: Directory to scan

        Returns:
            Dictionary: {category: [List_of_file_path], 'Uncategorized': [...]}    
        """
        if not directory_path.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")
        
        categorized_files = {}
        uncategorized_files = []

        self.logger.info(f"Scanning directory: {directory_path}")

        # Recursively walk through directory
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                category = self.get_file_category(file_path)

                if category:
                    categorized_files.setdefault(category, []).append(file_path)
                else:
                    uncategorized_files.append(file_path)

        # Add uncategorized files to result
        if uncategorized_files:
            categorized_files["Uncategorized"] = uncategorized_files

        # Log results
        for category, files in categorized_files.items():
            self.logger.info(f"Found {len(files)} files in category: {category}")

        total_files = sum(len(files) for files in categorized_files.values())
        self.logger.info(f"Total files found: {total_files}")

        return categorized_files
