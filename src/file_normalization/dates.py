"""Date handling utilities for file normalization."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

# Patterns for extracting existing dates from filenames
DATE_PATTERNS = [
    (r"(\d{4})-(\d{2})-(\d{2})", "%Y-%m-%d"),  # 2024-01-15
    (r"(\d{4})_(\d{2})_(\d{2})", "%Y_%m_%d"),  # 2024_01_15
    (r"(\d{4})(\d{2})(\d{2})", "%Y%m%d"),  # 20240115
    (r"(\d{2})-(\d{2})-(\d{4})", "%m-%d-%Y"),  # 01-15-2024
    (r"(\d{2})_(\d{2})_(\d{4})", "%m_%d_%Y"),  # 01_15_2024
]

# Patterns to strip date prefixes from filenames
STRIP_PATTERNS = [
    r"^\d{4}-\d{2}-\d{2}[-_\s]*",
    r"^\d{4}_\d{2}_\d{2}[-_\s]*",
    r"^\d{8}[-_\s]*",
    r"^\d{2}-\d{2}-\d{4}[-_\s]*",
    r"^\d{2}_\d{2}_\d{4}[-_\s]*",
]


def get_file_creation_date(filepath: Path) -> datetime:
    """Get the creation date of a file.

    Args:
        filepath: Path to the file.

    Returns:
        The creation datetime of the file.
    """
    stat = filepath.stat()
    try:
        timestamp = stat.st_birthtime  # type: ignore[attr-defined]
    except AttributeError:
        timestamp = min(stat.st_ctime, stat.st_mtime)
    return datetime.fromtimestamp(timestamp)


def extract_date_from_filename(filename: str) -> Optional[datetime]:
    """Extract a date from a filename if present.

    Args:
        filename: The filename to parse.

    Returns:
        The extracted datetime or None if no date found.
    """
    for pattern, date_format in DATE_PATTERNS:
        match = re.search(pattern, filename)
        if not match:
            continue
        try:
            date_str = "".join(match.groups())
            clean_format = date_format.replace("-", "").replace("_", "")
            return datetime.strptime(date_str, clean_format)
        except ValueError:
            continue
    return None


def strip_date_prefix(filename: str) -> str:
    """Remove existing date prefix from filename.

    Args:
        filename: The filename to clean.

    Returns:
        The filename with date prefix removed.
    """
    for pattern in STRIP_PATTERNS:
        filename = re.sub(pattern, "", filename)
    return filename


class DateFormat:
    """Date format options."""

    FULL = "full"  # YYYY-MM-DD
    YEAR_MONTH = "year-month"  # YYYY-MM
    YEAR = "year"  # YYYY


DATE_FORMAT_PATTERNS = {
    DateFormat.FULL: "%Y-%m-%d",
    DateFormat.YEAR_MONTH: "%Y-%m",
    DateFormat.YEAR: "%Y",
}


def format_date(date: datetime, fmt: str = DateFormat.FULL) -> str:
    """Format a date according to the specified format.

    Args:
        date: The datetime to format.
        fmt: The format type (full, year-month, or year).

    Returns:
        The formatted date string.
    """
    pattern = DATE_FORMAT_PATTERNS.get(fmt, DATE_FORMAT_PATTERNS[DateFormat.FULL])
    return date.strftime(pattern)
