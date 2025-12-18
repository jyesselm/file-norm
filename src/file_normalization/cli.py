"""Command-line interface for file normalization."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from file_normalization.dates import DateFormat
from file_normalization.normalizer import normalize_directory, normalize_file


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="file-norm",
        description="Standardize file names with consistent formatting.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="File or directory to process (default: current directory)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process directories recursively",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without doing it",
    )
    parser.add_argument(
        "-d",
        "--add-date",
        action="store_true",
        help="Add file creation date as prefix (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--year-month",
        action="store_true",
        help="Use YYYY-MM format for dates",
    )
    parser.add_argument(
        "--year-only",
        action="store_true",
        help="Use YYYY format for dates",
    )
    parser.add_argument(
        "-e",
        "--ext",
        action="append",
        metavar="EXT",
        help="Only process files with these extensions (can be repeated)",
    )
    parser.add_argument(
        "--dirs",
        action="store_true",
        help="Also normalize directory names",
    )
    return parser


def collect_files(
    path: Path,
    recursive: bool,
    extensions: Optional[list[str]],
) -> list[Path]:
    """Collect files to process based on arguments.

    Args:
        path: Starting path (file or directory).
        recursive: Whether to search recursively.
        extensions: Optional list of extensions to filter.

    Returns:
        List of file paths to process.
    """
    if path.is_file():
        files = [path]
    elif recursive:
        files = [f for f in path.rglob("*") if f.is_file()]
    else:
        files = [f for f in path.iterdir() if f.is_file()]

    if not extensions:
        return sorted(files)

    normalized_exts = normalize_extensions(extensions)
    return sorted(f for f in files if f.suffix.lower() in normalized_exts)


def collect_directories(path: Path, recursive: bool) -> list[Path]:
    """Collect directories to process, sorted deepest first.

    Args:
        path: Starting path (must be a directory).
        recursive: Whether to search recursively.

    Returns:
        List of directory paths sorted by depth (deepest first).
    """
    if not path.is_dir():
        return []

    if recursive:
        dirs = [d for d in path.rglob("*") if d.is_dir()]
    else:
        dirs = [d for d in path.iterdir() if d.is_dir()]

    # Sort by depth (deepest first) so renaming parents doesn't break child paths
    return sorted(dirs, key=lambda p: len(p.parts), reverse=True)


def normalize_extensions(extensions: list[str]) -> set[str]:
    """Normalize extension list to include leading dots.

    Args:
        extensions: List of extensions with or without dots.

    Returns:
        Set of lowercase extensions with leading dots.
    """
    return {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions
    }


def get_date_format(year_month: bool, year_only: bool) -> str:
    """Determine the date format from flags.

    Args:
        year_month: Whether to use YYYY-MM format.
        year_only: Whether to use YYYY format.

    Returns:
        The date format string.
    """
    if year_only:
        return DateFormat.YEAR
    if year_month:
        return DateFormat.YEAR_MONTH
    return DateFormat.FULL


def process_files(
    files: list[Path],
    add_date: bool,
    dry_run: bool,
    date_format: str = DateFormat.FULL,
) -> int:
    """Process and rename files.

    Args:
        files: List of files to process.
        add_date: Whether to add date prefix.
        dry_run: Whether to skip actual renaming.
        date_format: The date format to use.

    Returns:
        Number of files renamed.
    """
    renamed = 0
    for filepath in files:
        result = normalize_file(
            filepath, add_date=add_date, dry_run=dry_run, date_format=date_format
        )
        if not result:
            continue
        old, new = result
        prefix = "[DRY RUN] " if dry_run else ""
        print(f"{prefix}{old.name} -> {new.name}")
        renamed += 1
    return renamed


def process_directories(dirs: list[Path], dry_run: bool) -> int:
    """Process and rename directories.

    Args:
        dirs: List of directories to process (should be sorted deepest first).
        dry_run: Whether to skip actual renaming.

    Returns:
        Number of directories renamed.
    """
    renamed = 0
    for dirpath in dirs:
        result = normalize_directory(dirpath, dry_run=dry_run)
        if not result:
            continue
        old, new = result
        prefix = "[DRY RUN] " if dry_run else ""
        print(f"{prefix}{old.name}/ -> {new.name}/")
        renamed += 1
    return renamed


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    path = Path(args.path).resolve()
    if not path.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        return 1

    date_format = get_date_format(args.year_month, args.year_only)
    files = collect_files(path, args.recursive, args.ext)
    renamed_files = process_files(files, args.add_date, args.dry_run, date_format)

    renamed_dirs = 0
    if args.dirs and path.is_dir():
        dirs = collect_directories(path, args.recursive)
        renamed_dirs = process_directories(dirs, args.dry_run)

    action = "Would rename" if args.dry_run else "Renamed"
    print(f"\n{action} {renamed_files} file(s)")
    if args.dirs:
        print(f"{action} {renamed_dirs} directory(ies)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
