
"""
Command-line interface for File Sorter.
"""
import argparse
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

from . import FileSorter, ConfigManager


class Colors:
    """Simple ANSI color codes for terminal output."""
    # Check if terminal supports color
    HAS_COLOR = sys.stdout.isatty()
    
    # Colors
    RED = '\033[91m' if HAS_COLOR else ''
    GREEN = '\033[92m' if HAS_COLOR else ''
    YELLOW = '\033[93m' if HAS_COLOR else ''
    BLUE = '\033[94m' if HAS_COLOR else ''
    MAGENTA = '\033[95m' if HAS_COLOR else ''
    CYAN = '\033[96m' if HAS_COLOR else ''
    WHITE = '\033[97m' if HAS_COLOR else ''
    
    # Styles
    BOLD = '\033[1m' if HAS_COLOR else ''
    UNDERLINE = '\033[4m' if HAS_COLOR else ''
    
    # Reset
    RESET = '\033[0m' if HAS_COLOR else ''
    
    @classmethod
    def colored(cls, text: str, color: str) -> str:
        """Return colored text if terminal supports it."""
        if cls.HAS_COLOR:
            return f"{color}{text}{cls.RESET}"
        return text
    
    @classmethod
    def success(cls, text: str) -> str:
        return cls.colored(text, cls.GREEN)
    
    @classmethod
    def error(cls, text: str) -> str:
        return cls.colored(text, cls.RED)
    
    @classmethod
    def warning(cls, text: str) -> str:
        return cls.colored(text, cls.YELLOW)
    
    @classmethod
    def info(cls, text: str) -> str:
        return cls.colored(text, cls.CYAN)
    
    @classmethod
    def highlight(cls, text: str) -> str:
        return cls.colored(text, cls.BOLD + cls.WHITE)


class ProgressIndicator:
    """Simple progress indicator for CLI operations."""
    
    def __init__(self, total: int = 0, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1, message: str = ""):
        """Update progress and display."""
        self.current += increment
        
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            bar_length = 30
            filled_length = int(bar_length * self.current // self.total)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            elapsed = time.time() - self.start_time
            if self.current > 0:
                estimated_total = elapsed * self.total / self.current
                remaining = estimated_total - elapsed
                time_str = f"{remaining:.1f}s remaining"
            else:
                time_str = ""
            
            sys.stdout.write(f"\r{self.description}: [{bar}] {percentage:.1f}% ({self.current}/{self.total}) {time_str} {message}")
            sys.stdout.flush()
        else:
            # Spinner for unknown total
            spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            frame = spinner[int(time.time() * 10) % len(spinner)]
            sys.stdout.write(f"\r{self.description} {frame} {self.current} files {message}")
            sys.stdout.flush()
    
    def complete(self, message: str = ""):
        """Mark progress as complete."""
        if self.total > 0:
            bar = '█' * 30
            elapsed = time.time() - self.start_time
            sys.stdout.write(f"\r{self.description}: [{bar}] 100.0% ({self.total}/{self.total}) Completed in {elapsed:.1f}s {message}\n")
        else:
            elapsed = time.time() - self.start_time
            sys.stdout.write(f"\r{self.description} ✓ {self.current} files processed in {elapsed:.1f}s {message}\n")
        sys.stdout.flush()


class FileSorterCLI:
    """Command-line interface for File Sorter."""
    
    def __init__(self):
        self.parser = self.create_parser()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description=f"{Colors.highlight('Smart File Sorter')} - Organize your files automatically",
            epilog=Colors.info("Examples:") + "\n"
                   "  " + Colors.success("file-sorter sort ~/Downloads") + "\n"
                   "  " + Colors.success("file-sorter dry-run ~/Downloads --config myconfig.json") + "\n"
                   "  " + Colors.success("file-sorter config --generate") + "\n",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '--version', '-v',
            action='version',
            version=f'{Colors.highlight("File Sorter")} v0.4.0'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Command to execute',
            required=True
        )
        
        # sort command
        sort_parser = subparsers.add_parser(
            'sort',
            help='Sort files in a directory',
            description='Sort files into organized folders'
        )
        sort_parser.add_argument(
            'directory',
            type=Path,
            help='Directory to sort'
        )
        sort_parser.add_argument(
            '--config', '-c',
            type=Path,
            help='Configuration file (default: config.json)'
        )
        sort_parser.add_argument(
            '--verbose', '-V',
            action='store_true',
            help='Show detailed output'
        )
        sort_parser.add_argument(
            '--no-progress',
            action='store_true',
            help='Disable progress indicator'
        )
        
        # dry-run command
        dryrun_parser = subparsers.add_parser(
            'dry-run',
            help='Preview sorting without actually moving files',
            description='Show what would happen without moving files'
        )
        dryrun_parser.add_argument(
            'directory',
            type=Path,
            help='Directory to analyze'
        )
        dryrun_parser.add_argument(
            '--config', '-c',
            type=Path,
            help='Configuration file (default: config.json)'
        )
        dryrun_parser.add_argument(
            '--verbose', '-V',
            action='store_true',
            help='Show detailed output'
        )
        dryrun_parser.add_argument(
            '--no-progress',
            action='store_true',
            help='Disable progress indicator'
        )
        
        # config command
        config_parser = subparsers.add_parser(
            'config',
            help='Configuration management',
            description='Manage configuration files'
        )
        config_parser.add_argument(
            '--generate', '-g',
            action='store_true',
            help='Generate a default configuration file'
        )
        config_parser.add_argument(
            '--show', '-s',
            action='store_true',
            help='Show current configuration'
        )
        config_parser.add_argument(
            '--path', '-p',
            type=Path,
            default='config.json',
            help='Configuration file path (default: config.json)'
        )
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """
        Run the CLI.
        
        Args:
            args: Command-line arguments. If None, uses sys.argv[1:].
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        parsed_args = self.parser.parse_args(args)
        
        try:
            if parsed_args.command == 'sort':
                return self.handle_sort(parsed_args)
            elif parsed_args.command == 'dry-run':
                return self.handle_dry_run(parsed_args)
            elif parsed_args.command == 'config':
                return self.handle_config(parsed_args)
            else:
                self.parser.print_help()
                return 1
                
        except KeyboardInterrupt:
            print(f"\n{Colors.error('❌ Operation cancelled by user')}")
            return 130
        except Exception as e:
            print(f"{Colors.error('❌ Error:')} {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def handle_sort(self, args) -> int:
        """Handle the sort command."""
        print(f"{Colors.info('📁')} {Colors.highlight('Sorting directory:')} {args.directory}")
        
        # Check if directory exists
        if not args.directory.exists():
            print(f"{Colors.error('❌ Directory does not exist:')} {args.directory}")
            return 1
        
        if not args.directory.is_dir():
            print(f"{Colors.error('❌ Not a directory:')} {args.directory}")
            return 1
        
        # Create sorter
        config_path = str(args.config) if args.config else None
        sorter = FileSorter(config_path)
        
        # Scan directory first to get file count
        print(f"{Colors.info('🔍')} Scanning directory...")
        categorized_files = sorter.scan_directory(args.directory)
        total_files = sum(len(files) for files in categorized_files.values())
        
        if total_files == 0:
            print(f"{Colors.warning('⚠️')} No files found to sort in {args.directory}")
            return 0
        
        # Set up progress indicator
        progress = None
        if not args.no_progress and total_files > 10:
            progress = ProgressIndicator(total_files, "Sorting files")
            
            # Get the UNBOUND method from the class
            from .file_sorter import FileSorter as FileSorterClass
            original_sort_file = FileSorterClass.sort_file
            
            # Use a list to make progress mutable in closure
            progress_ref = [progress]
            
            def patched_sort_file(self, source_path, dry_run=False):
                # Call the original UNBOUND method
                result = original_sort_file(self, source_path, dry_run)
                if progress_ref[0]:
                    progress_ref[0].update(1)
                return result
            
            # Replace the method on THIS instance
            sorter.sort_file = lambda *args, **kwargs: patched_sort_file(sorter, *args, **kwargs)
            
        # Sort the directory
        print(f"{Colors.info('🔄')} Starting sorting process...")
        start_time = time.time()
        
        stats = sorter.sort_directory(args.directory, dry_run=False)
        
        # Complete progress
        if progress:
            progress.complete()
        
        elapsed = time.time() - start_time
        
        # Show results
        self.print_statistics(stats, dry_run=False, elapsed=elapsed)
        
        return 0
    
    def handle_dry_run(self, args) -> int:
        """Handle the dry-run command."""
        print(f"{Colors.info('🔍')} {Colors.highlight('Previewing sort for directory:')} {args.directory}")
        print(f"   {Colors.warning('(No files will be moved)')}")
        
        # Check if directory exists
        if not args.directory.exists():
            print(f"{Colors.error('❌ Directory does not exist:')} {args.directory}")
            return 1
        
        if not args.directory.is_dir():
            print(f"{Colors.error('❌ Not a directory:')} {args.directory}")
            return 1
        
        # Create sorter with dry-run enabled in config
        config_path = str(args.config) if args.config else None
        sorter = FileSorter(config_path)
        sorter.options['dry_run'] = True  # Force dry-run
        
        # Scan directory first to get file count
        print(f"{Colors.info('🔍')} Scanning directory...")
        categorized_files = sorter.scan_directory(args.directory)
        total_files = sum(len(files) for files in categorized_files.values())
        
        if total_files == 0:
            print(f"{Colors.warning('⚠️')} No files found to analyze in {args.directory}")
            return 0
        
        # Set up progress indicator
        progress = None
        if not args.no_progress and total_files > 10:
            progress = ProgressIndicator(total_files, "Analyzing files")
            
            # Get the UNBOUND method from the class
            from .file_sorter import FileSorter as FileSorterClass
            original_sort_file = FileSorterClass.sort_file
            
            # Use a list to make progress mutable in closure
            progress_ref = [progress]
            
            def patched_sort_file(self, source_path, dry_run=False):
                # Call the original UNBOUND method
                result = original_sort_file(self, source_path, dry_run)
                if progress_ref[0]:
                    progress_ref[0].update(1)
                return result
            
            # Replace the method on THIS instance
            sorter.sort_file = lambda *args, **kwargs: patched_sort_file(sorter, *args, **kwargs)
        
        # Dry-run the directory
        print(f"{Colors.info('🔄')} Analyzing files...")
        start_time = time.time()
        
        stats = sorter.sort_directory(args.directory, dry_run=True)
        
        # Complete progress
        if progress:
            progress.complete()
        
        elapsed = time.time() - start_time
        
        # Show results
        self.print_statistics(stats, dry_run=True, elapsed=elapsed)
        
        return 0
    
    def handle_config(self, args) -> int:
        """Handle the config command."""
        if args.generate:
            print(f"{Colors.info('📄')} {Colors.highlight('Generating default configuration at:')} {args.path}")
            
            # Create ConfigManager which generates default config
            config_manager = ConfigManager(str(args.path))
            
            if args.path.exists():
                print(f"{Colors.success('✅ Configuration file created:')} {args.path}")
                print(f"\n{Colors.info('💡 You can now edit this file to customize categories and options.')}")
            else:
                print(f"{Colors.error('❌ Failed to create configuration file')}")
                return 1
        
        elif args.show:
            print(f"{Colors.info('📋')} {Colors.highlight('Current configuration:')}")
            
            if args.path.exists():
                config_manager = ConfigManager(str(args.path))
                import json
                print(json.dumps(config_manager.config, indent=2))
            else:
                print(f"{Colors.error('❌ Configuration file not found:')} {args.path}")
                print(f"   {Colors.info('Use')} {Colors.success('file-sorter config --generate')} {Colors.info('to create one')}")
                return 1
        
        else:
            print(f"{Colors.info('ℹ️')} {Colors.highlight('Configuration management')}")
            print(f"   Use {Colors.success('--generate')} to create a default config")
            print(f"   Use {Colors.success('--show')} to display current config")
        
        return 0
    
    def print_statistics(self, stats: Dict[str, Any], dry_run: bool = False, elapsed: float = 0) -> None:
        """Print sorting statistics in a user-friendly format."""
        print("\n" + Colors.highlight("="*50))
        
        if dry_run:
            print(f"{Colors.info('📊')} {Colors.highlight('DRY RUN RESULTS')} {Colors.warning('(no files were moved)')}")
        else:
            print(f"{Colors.info('📊')} {Colors.highlight('SORTING RESULTS')}")
        
        print(Colors.highlight("="*50))
        
        total = stats.get('total_files', 0)
        moved = stats.get('moved', 0)
        skipped = stats.get('skipped', 0)
        errors = stats.get('errors', 0)
        uncategorized = stats.get('uncategorized', 0)
        
        print(f"{Colors.info('📁')} Total files processed: {Colors.highlight(str(total))}")
        print(f"{Colors.success('✅')} Files {'would be ' if dry_run else ''}moved: {Colors.success(str(moved))}")
        
        if skipped > 0:
            print(f"{Colors.warning('⏭️')} Files skipped: {Colors.warning(str(skipped))}")
        
        if errors > 0:
            print(f"{Colors.error('❌')} Errors: {Colors.error(str(errors))}")
        
        if uncategorized > 0:
            print(f"{Colors.info('❓')} Uncategorized files: {Colors.info(str(uncategorized))}")
        
        if elapsed > 0:
            print(f"{Colors.info('⏱️')} Time elapsed: {Colors.info(f'{elapsed:.2f}s')}")
        
        if stats.get('categories'):
            print(f"\n{Colors.info('📂')} {Colors.highlight('Files by category:')}")
            for category, count in stats['categories'].items():
                if count > 0:
                    icon = "•"
                    if "Images" in category: icon = "🖼️"
                    elif "Documents" in category: icon = "📄"
                    elif "Code" in category: icon = "💻"
                    elif "Audio" in category: icon = "🎵"
                    elif "Video" in category: icon = "🎬"
                    elif "Archives" in category: icon = "📦"
                    
                    print(f"  {icon} {category}: {Colors.highlight(str(count))} file{'s' if count != 1 else ''}")
        
        print(Colors.highlight("="*50))
        
        if dry_run:
            print(f"{Colors.info('💡')} To actually sort files, run: {Colors.success('file-sorter sort <directory>')}")
        else:
            print(f"{Colors.success('🎉')} {Colors.highlight('Sorting complete!')}")


def main() -> int:
    """Main entry point for the CLI."""
    cli = FileSorterCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())