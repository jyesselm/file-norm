"""Main normalization logic for file names."""

from pathlib import Path
from typing import Optional

from file_normalization.dates import (
    DateFormat,
    extract_date_from_filename,
    format_date,
    get_file_creation_date,
    strip_date_from_filename,
    strip_date_prefix,
)
from file_normalization.names import (
    join_name_and_extension,
    sanitize_name,
    split_name_and_extension,
)


def normalize_filename(
    filename: str,
    add_date: bool = False,
    creation_date_str: Optional[str] = None,
    date_format: str = DateFormat.FULL,
) -> str:
    """Normalize a filename according to standardization rules.

    Args:
        filename: The original filename.
        add_date: Whether to add a date prefix.
        creation_date_str: Optional date string to use as prefix.
        date_format: The date format to use (full, year-month, or year).

    Returns:
        The normalized filename.
    """
    name, extension = split_name_and_extension(filename)
    existing_date = extract_date_from_filename(name)
    if existing_date:
        name_without_date = strip_date_from_filename(name)
    else:
        name_without_date = strip_date_prefix(name)
    clean_name = sanitize_name(name_without_date)
    extension = extension.lower()

    if existing_date:
        date_prefix = format_date(existing_date, date_format)
        return join_name_and_extension(f"{date_prefix}-{clean_name}", extension)

    if add_date and creation_date_str:
        return join_name_and_extension(f"{creation_date_str}-{clean_name}", extension)

    return join_name_and_extension(clean_name, extension)


def normalize_file(
    filepath: Path,
    add_date: bool = False,
    dry_run: bool = False,
    date_format: str = DateFormat.FULL,
) -> Optional[tuple[Path, Path]]:
    """Normalize a file's name on disk.

    Args:
        filepath: Path to the file to rename.
        add_date: Whether to add creation date as prefix.
        dry_run: If True, don't actually rename.
        date_format: The date format to use (full, year-month, or year).

    Returns:
        Tuple of (old_path, new_path) if renamed, None if unchanged.
    """
    if not filepath.is_file():
        return None

    creation_date_str = None
    if add_date:
        creation_date = get_file_creation_date(filepath)
        creation_date_str = format_date(creation_date, date_format)

    new_name = normalize_filename(
        filepath.name, add_date, creation_date_str, date_format
    )
    new_path = filepath.parent / new_name

    if new_path == filepath:
        return None

    new_path = resolve_name_conflict(new_path, filepath)

    if not dry_run:
        filepath.rename(new_path)

    return (filepath, new_path)


def resolve_name_conflict(new_path: Path, original_path: Path) -> Path:
    """Resolve naming conflicts by adding a counter suffix.

    Args:
        new_path: The desired new path.
        original_path: The original file path.

    Returns:
        A path that doesn't conflict with existing files.
    """
    if not new_path.exists() or new_path == original_path:
        return new_path

    counter = 1
    stem = new_path.stem
    suffix = new_path.suffix

    while new_path.exists():
        new_name = f"{stem}-{counter}{suffix}"
        new_path = new_path.parent / new_name
        counter += 1

    return new_path
