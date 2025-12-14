# file-norm

A command-line tool for standardizing file names with consistent formatting.

## Features

- Converts spaces and underscores to hyphens
- Converts all characters to lowercase
- Standardizes dates to YYYY-MM-DD format (or YYYY-MM, YYYY)
- Detects existing dates in filenames and reformats them
- Optionally adds file creation date as prefix
- Handles naming conflicts automatically

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```bash
# Normalize files in current directory (dry run)
file-norm -n

# Normalize a specific file
file-norm -n myfile.txt

# Normalize a directory
file-norm -n /path/to/directory

# Actually rename files (remove -n flag)
file-norm /path/to/directory
```

### Options

| Option | Description |
|--------|-------------|
| `-n, --dry-run` | Show what would be renamed without doing it |
| `-r, --recursive` | Process directories recursively |
| `-d, --add-date` | Add file creation date as prefix |
| `--year-month` | Use YYYY-MM format for dates |
| `--year-only` | Use YYYY format for dates |
| `-e, --ext EXT` | Only process files with specified extensions |

### Examples

```bash
# Preview changes without renaming
file-norm -n .

# Normalize all files recursively
file-norm -r /path/to/directory

# Add creation date prefix to files
file-norm -d -n .

# Use year-month format for dates
file-norm -d --year-month -n .

# Use year-only format for dates
file-norm -d --year-only -n .

# Only process .txt and .pdf files
file-norm -e txt -e pdf -n .
```

### Transformations

| Before | After |
|--------|-------|
| `Hello_World.txt` | `hello-world.txt` |
| `My Document.PDF` | `my-document.pdf` |
| `2024_05_15_Report.docx` | `2024-05-15-report.docx` |
| `20240515-notes.txt` | `2024-05-15-notes.txt` |

With `-d` flag (adds creation date):

| Before | After |
|--------|-------|
| `document.txt` | `2024-12-13-document.txt` |

With `--year-month` flag:

| Before | After |
|--------|-------|
| `2024_05_15_Report.txt` | `2024-05-report.txt` |

With `--year-only` flag:

| Before | After |
|--------|-------|
| `2024_05_15_Report.txt` | `2024-report.txt` |

## Development

### Running Tests

```bash
pytest
```

### Linting and Formatting

```bash
# Check for issues
ruff check src tests

# Format code
ruff format src tests

# Type checking
mypy src
```

## License

MIT
