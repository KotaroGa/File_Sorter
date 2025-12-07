
"""
Command-line interface for File Sorter.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from . import FileSorter, ConfigManager
from .file_sorter import FileSorter as FileSorterClass



class FileSorterCLI:
    """Command-line interface for File Sorter."""
    
    def __init__(self):
        self.parser = self.create_parser()

    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description="Smart Filer Sorter - Organize your files automatically",
            epilog="Examples:\n"
                   " file-sorter sort ~/Downloads\n"
                   " file-sorter dry-run ~/Downloads --config myconfig.json\n"
                   " file-sorter config --generate\n",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument(
            '--version', '-v',
            action='version',
            version='File Sorter v0.3.0'
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
            help='Sort files in a directory'
        )
        sort_parser.add_argument(
            'directory',
            type=Path,
            help='Directory to sort'
        )
        sort_parser.add_argument(
            '--config', '-c',
            type=Path,
            help='Configuration file (default: config json)'
        )
        sort_parser.add_argument(
            '--verbose', '-V',
            action='store_true',
            help='Show detailed output'
        )

        # dry-run command
        dryrun_parser = subparsers.add_parser(
            'dry-run',
            help='Preview sorting without actually moving files'
        )
        dryrun_parser.add_argument(
            'directory',
            type=Path,
            help='Directory to analyze'
        )
        dryrun_parser.add_argument(
            '--config', '-c',
            type=Path,
            help='Configuration file (default: config json)'
        )
        dryrun_parser.add_argument(
            '--verbose', '-V',
            action='store_true',
            help='Show detailed output'
        )

        # config command
        config_parser = subparsers.add_parser(
            'config',
            help='Configuration management'
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
            print("\n❌ Operation cancelled by user")
            return 130
        except Exception as e:
            print(f"❌ Error: {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1
        

    def handle_sort(self, args) -> int:
        """Handle the sort command."""
        print(f"📁 Sorting directory: {args.directory}")

        # Check if directory exists
        if not args.directory.exists():
            print(f"❌ Directory does not exist: {args.directory}")
            return 1
        
        if not args.directory.is_dir():
            print(f"❌ Not a directory: {args.directory}")
            return 1
    
        # Create sorter
        config_path = str(args.config) if args.config else None
        sorter = FileSorter(config_path)

        # Sort the directory
        print("🔄 Starting sorting process...")
        stats = sorter.sort_directory(args.directory, dry_run=False)
        
        # Show results
        self.print_statistics(stats, dry_run=False)
        
        return 0
    


    def handle_dry_run(self, args) -> int:
        """Handle the dry-run command."""
        print(f"🔍 Previewing sort for directory: {args.directory}")
        print("   (No files will be moved)")
        
        # Check if directory exists
        if not args.directory.exists():
            print(f"❌ Directory does not exist: {args.directory}")
            return 1
        
        if not args.directory.is_dir():
            print(f"❌ Not a directory: {args.directory}")
            return 1
        
        # Create sorter with dry-run enabled in config
        config_path = str(args.config) if args.config else None
        sorter = FileSorter(config_path)
        sorter.options['dry_run'] = True  # Force dry-run
        
        # Dry-run the directory
        print("🔄 Analyzing files...")
        stats = sorter.sort_directory(args.directory, dry_run=True)
        
        # Show results
        self.print_statistics(stats, dry_run=True)
        
        return 0
    
    def handle_config(self, args) -> int:
        """Handle the config command."""
        if args.generate:
            print(f"📄 Generating default configuration at: {args.path}")
            
            # Create ConfigManager which generates default config
            config_manager = ConfigManager(str(args.path))
            
            if args.path.exists():
                print(f"✅ Configuration file created: {args.path}")
            else:
                print(f"❌ Failed to create configuration file")
                return 1
        
        elif args.show:
            print("📋 Current configuration:")
            
            if args.path.exists():
                config_manager = ConfigManager(str(args.path))
                import json
                print(json.dumps(config_manager.config, indent=2))
            else:
                print(f"❌ Configuration file not found: {args.path}")
                print("   Use 'file-sorter config --generate' to create one")
                return 1
        
        else:
            print("ℹ️  Configuration management")
            print("   Use --generate to create a default config")
            print("   Use --show to display current config")
        
        return 0
    
    def print_statistics(self, stats: dict, dry_run: bool = False) -> None:
        """Print sorting statistics in a user-friendly format."""
        print("\n" + "="*50)
        
        if dry_run:
            print("📊 DRY RUN RESULTS (no files were moved)")
        else:
            print("📊 SORTING RESULTS")
        
        print("="*50)
        
        print(f"📁 Total files processed: {stats.get('total_files', 0)}")
        print(f"✅ Files {'would be ' if dry_run else ''}moved: {stats.get('moved', 0)}")
        print(f"⏭️  Files skipped: {stats.get('skipped', 0)}")
        print(f"❌ Errors: {stats.get('errors', 0)}")
        print(f"❓ Uncategorized files: {stats.get('uncategorized', 0)}")
        
        if stats.get('categories'):
            print("\n📂 Files by category:")
            for category, count in stats['categories'].items():
                if count > 0:
                    print(f"  • {category}: {count} file{'s' if count != 1 else ''}")
        
        print("="*50)
        
        if dry_run:
            print("💡 To actually sort files, run: file-sorter sort <directory>")
        else:
            print("🎉 Sorting complete!")


def main() -> int:
    """Main entry point for the CLI."""
    cli = FileSorterCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
