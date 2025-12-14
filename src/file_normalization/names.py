"""Name sanitization utilities for file normalization."""

import re
from pathlib import Path


def replace_separators(name: str) -> str:
    """Replace spaces and underscores with hyphens.

    Args:
        name: The string to process.

    Returns:
        The string with separators replaced.
    """
    name = name.replace(" ", "-")
    name = name.replace("_", "-")
    return name


def collapse_hyphens(name: str) -> str:
    """Collapse multiple consecutive hyphens into one.

    Args:
        name: The string to process.

    Returns:
        The string with collapsed hyphens.
    """
    return re.sub(r"-+", "-", name)


def strip_edge_hyphens(name: str) -> str:
    """Remove leading and trailing hyphens.

    Args:
        name: The string to process.

    Returns:
        The string with edge hyphens removed.
    """
    return name.strip("-")


def to_lowercase(name: str) -> str:
    """Convert string to lowercase.

    Args:
        name: The string to process.

    Returns:
        The lowercase string.
    """
    return name.lower()


def sanitize_name(name: str) -> str:
    """Apply all sanitization rules to a name.

    Args:
        name: The filename (without extension) to sanitize.

    Returns:
        The sanitized name.
    """
    name = to_lowercase(name)
    name = replace_separators(name)
    name = collapse_hyphens(name)
    name = strip_edge_hyphens(name)
    return name


def split_name_and_extension(filename: str) -> tuple[str, str]:
    """Split a filename into name and extension.

    Args:
        filename: The full filename.

    Returns:
        Tuple of (name, extension) where extension includes the dot.
    """
    path = Path(filename)
    return path.stem, path.suffix


def join_name_and_extension(name: str, extension: str) -> str:
    """Join a name and extension into a filename.

    Args:
        name: The file name without extension.
        extension: The file extension (with or without dot).

    Returns:
        The combined filename.
    """
    if extension and not extension.startswith("."):
        extension = f".{extension}"
    return f"{name}{extension}"
