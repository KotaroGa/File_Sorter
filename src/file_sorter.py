
"""
Core file sorting functionality.
Uses ConfigManager for configuration.
"""

import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
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



    def resolve_conflict(self, target_path: Path) -> Path:
        """
        Handle file name conflicts based on configuration.
        
        Args:
            target_path: Original target path
            
        Returns:
            New path that doesn't conflict
            
        Conflict resolution strategies:
            - 'append_number': file.txt → file (1).txt → file (2).txt
            - 'skip': keep original path (caller should handle)
            - 'overwrite': keep original path (file will be overwritten)
        """
        conflict_strategy = self.options.get("conflict_resolution", "append_number")
        
        # If file doesn't exist, no conflict
        if not target_path.exists():
            return target_path
        
        self.logger.debug(f"Conflict detected for {target_path.name}, strategy: {conflict_strategy}")
        
        # Handle each strategy
        if conflict_strategy == "skip":
            self.logger.info(f"Skipping {target_path.name} (file already exists)")
            return target_path  # Return original path - caller checks if exists
        
        elif conflict_strategy == "overwrite":
            self.logger.warning(f"Will overwrite {target_path}")
            return target_path  # Return original path - caller will overwrite
        
        elif conflict_strategy == "append_number":
            # Find a non-conflicting name: file.txt → file (1).txt → file (2).txt
            counter = 1
            while True:
                # Create new filename with number
                stem = target_path.stem
                suffix = target_path.suffix
                
                # Handle existing numbers in filename
                if " (" in stem and ")" in stem:
                    # Remove existing number: "file (1)" → "file"
                    base_stem = stem.rsplit(" (", 1)[0]
                else:
                    base_stem = stem
                
                new_name = f"{base_stem} ({counter}){suffix}"
                new_path = target_path.parent / new_name
                
                if not new_path.exists():
                    self.logger.info(f"Resolved conflict: {target_path.name} → {new_name}")
                    return new_path
                
                counter += 1
        
        else:
            self.logger.error(f"Unknown conflict strategy: {conflict_strategy}")
            raise ValueError(f"Unknown conflict strategy: {conflict_strategy}")


    def prepare_move(self, source_path: Path, dry_run: bool = False) -> Tuple[Path, Path]:
        """
        Prepare to move a file: calculate target path and resolve conflicts.
        
        Args:
            source_path: Path to source file
            dry_run: If True, don't actually move, just calculate
            
        Returns:
            Tuple of (source_path, target_path)
            If file should be skipped, returns (source_path, source_path)
            
        Note:
            If dry_run is True, only calculates and logs
        """
        if not source_path.exists():
            self.logger.error(f"Source file does not exist: {source_path}")
            raise FileNotFoundError(f"Source file does not exist: {source_path}")
        
        if not source_path.is_file():
            self.logger.error(f"Source is not a file: {source_path}")
            raise ValueError(f"Source is not a file: {source_path}")
        
        # Get category
        category = self.get_file_category(source_path)
        if not category:
            self.logger.warning(f"No category for {source_path.name}, will not move")
            return (source_path, source_path)  # Return same path for no move
        
        # Calculate target path
        target_path = self.get_target_path(source_path, category)
        
        # Create target directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Resolve conflicts
        final_target_path = self.resolve_conflict(target_path)
        
        # Check if we should skip (for both dry_run and actual move)
        conflict_strategy = self.options.get("conflict_resolution", "append_number")

        if conflict_strategy == "skip" and target_path.exists():
            self.logger.info(f"Skipping {source_path.name} (already exists at destination)")
            return (source_path, source_path)  # Same path means skip
        
        # Log the planned move
        action = "Would move" if dry_run else "Moving"
        self.logger.info(f"{action}: {source_path.name} → {final_target_path.relative_to(source_path.parent.parent)}")
        
        return (source_path, final_target_path)



    def sort_file(self, source_path: Path, dry_run: Optional[bool] = None) -> bool:
        """
        Sort a single file based on configuration.
        
        Args:
            source_path: Path to the file to sort
            dry_run: If True, only simulate. If None, uses config setting.
            
        Returns:
            True if file was moved (or would be moved), False if skipped or error
            
        Note:
            Uncategorized files are not moved (returns False)
        """
        # Use dry_run from config if not specified
        if dry_run is None:
            dry_run_value = self.options.get("dry_run", False)
        else:
            dry_run_value = dry_run  # dry_run is guaranteed to be bool here (not None)
        
        try:
            # Prepare the move - use dry_run_value which is definitely bool
            source, target = self.prepare_move(source_path, dry_run_value)
            
            # If source and target are same, file should be skipped
            if source == target:
                if self.get_file_category(source_path):
                    # File has category but was skipped (e.g., conflict strategy = skip)
                    self.logger.info(f"Skipped: {source_path.name}")
                else:
                    # File has no category
                    self.logger.debug(f"Not moving uncategorized file: {source_path.name}")
                return False
            
            # If dry run, just log
            if dry_run_value:
                self.logger.info(f"[DRY RUN] Would move: {source_path.name} → {target.name}")
                return True
            
            # Actually move the file
            try:
                shutil.move(str(source), str(target))
                self.logger.info(f"Moved: {source_path.name} → {target.name}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to move {source_path.name}: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing {source_path.name}: {e}")
            return False
        


    def sort_directory(self, directory_path: Path, dry_run: Optional[bool] = None) -> Dict[str, Any]:
        """
        Sort all files in a directory (recursively).
        
        Args:
            directory_path: Directory to sort
            dry_run: If True, only simulate. If None, uses config setting.
            
        Returns:
            Dictionary with sorting statistics
        """
        if not directory_path.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")
        
        # Use dry_run from config if not specified
        if dry_run is None:
            dry_run_value = self.options.get("dry_run", False)
        else:
            dry_run_value = dry_run
        
        self.logger.info(f"{'[DRY RUN] ' if dry_run_value else ''}Sorting directory: {directory_path}")
        
        # Scan directory first
        categorized_files = self.scan_directory(directory_path)
        
        stats: Dict[str, Any] = {
            "total_files": 0,
            "moved": 0,
            "skipped": 0,
            "errors": 0,
            "categories": {},
            "uncategorized": 0
        }
        
        # Sort each file
        for category, file_list in categorized_files.items():
            if category == "Uncategorized":
                stats["uncategorized"] = len(file_list)
                continue
            
            stats["categories"][category] = 0
            stats["total_files"] += len(file_list)
            
            for file_path in file_list:
                moved = self.sort_file(file_path, dry_run_value)
                
                if moved:
                    stats["moved"] += 1
                    stats["categories"][category] += 1
                else:
                    stats["skipped"] += 1
        
        # Log summary
        summary = (f"Sorting complete. Total: {stats['total_files']}, "
                  f"Moved: {stats['moved']}, Skipped: {stats['skipped']}, "
                  f"Errors: {stats['errors']}, Uncategorized: {stats['uncategorized']}")
        
        if dry_run_value:
            self.logger.info(f"[DRY RUN] {summary}")
        else:
            self.logger.info(summary)
        
        return stats
