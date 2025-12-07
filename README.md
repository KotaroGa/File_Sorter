## File Sorter

A powerful, configurable file organization tool that automatically sorts files into categorized directories.

### ✨ Features

- **Smart Categorization**: Automatically detects and sorts files by type
- **Configurable Rules**: Customize categories and sorting behavior via JSON
- **Safe Operations**: Dry-run mode to preview changes before execution
- **Folder Preservation**: Option to preserve original folder structure
- **Conflict Resolution**: Multiple strategies for handling duplicate files
- **Comprehensive Logging**: Detailed logs of all operations
- **CLI Interface**: Easy-to-use command-line interface

### 🚀 Installation

#### From PyPI
```bash
pip install file-sorter-kotaroga
```
---

#### From Source

##### Clone the repository
- git clone https://github.com/KotaroGa/File_Sorter.git
- cd File_Sorter

##### Create virtual environment
- python -m venv venv
- source venv/bin/activate  # Linux/Mac
- venv\Scripts\activate  # Windows

##### Install in development mode
- pip install -e .

---

### 📖 Usage

##### Show version
- file-sorter --version

##### Show help
- file-sorter --help

##### Preview sorting without making changes
- file-sorter dry-run ~/Downloads

##### Execute sorting
- file-sorter sort ~/Downloads

##### Generate default configuration
- file-sorter config --generate

##### Show current configuration
- file-sorter config --show

---

### Configuration
- file-sorter config --generate

---

#### A HAND

If this tool helps organize your digital realm and you want to support its development:

- [🟢] BITCOIN (BTC): bc1qlhup35a64qq0e6uc2v07s64tzjrmj8j9e24jmr
- [🟢] ETHEREUM (ETH): 0x6D4DB084eaC2cF9D4BbF04FdCBd3e737FDD36dcc
- [🟢] SOLANA (SOL): 51ueAbc6TC52UExxTKRZuN6hMPUtu7aoYSKuiWnLSci2

>##### [💡] NOTE: Your support helps maintain and improve this project. All contributions are appreciated! ❤️
