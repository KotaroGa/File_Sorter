
"""
File Sorter - A smart tool to organize your files automatically.
"""

__version__ = "0.2.0"
__author__ = "KotaroGa"

# Expose main classes at package level
from .config_manager import ConfigManager
from .file_sorter import FileSorter

__all__ = ['ConfigManager', 'FileSorter']
