
### Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### [Unreleased]

---

### [v0.2.0] - 04.12.2025

#### Added
- Configuration system with JSON support
- ConfigManager class for loading/saving configurations
- Default categories: Images, Documents, Archives, Audio, Video, Code, etc.
- Configuration options: preserve_folder_structure, conflict_resolution, dry_run, log_level
- Unit tests for configuration system
- Proper GitFlow workflow with feature branches

#### Fixed
- Import path resolution for test files
- Type hints for Optional parameters

---

### [v0.1.0] 01.12.2025

#### Added
- Basic file sorting by extension
- CLI interface with dry-run mode
- JSON configuration support
- Logging system