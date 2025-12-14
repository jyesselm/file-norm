"""Tests for the normalizer module."""

import tempfile
from pathlib import Path

from file_normalization.normalizer import (
    normalize_file,
    normalize_filename,
    resolve_name_conflict,
)


class TestNormalizeFilename:
    """Tests for normalize_filename function."""

    def test_basic_normalization(self) -> None:
        """Test basic filename normalization."""
        result = normalize_filename("Hello_World.PDF")
        assert result == "hello-world.pdf"

    def test_spaces_replaced(self) -> None:
        """Test spaces are replaced with hyphens."""
        result = normalize_filename("My Document.txt")
        assert result == "my-document.txt"

    def test_existing_date_preserved(self) -> None:
        """Test existing date is preserved and standardized."""
        result = normalize_filename("2024_01_15_My_File.pdf")
        assert result == "2024-01-15-my-file.pdf"

    def test_add_date_with_creation_date(self) -> None:
        """Test adding date prefix."""
        result = normalize_filename(
            "document.txt",
            add_date=True,
            creation_date_str="2024-03-20",
        )
        assert result == "2024-03-20-document.txt"

    def test_add_date_without_creation_date(self) -> None:
        """Test add_date without creation_date_str does nothing."""
        result = normalize_filename("document.txt", add_date=True)
        assert result == "document.txt"

    def test_existing_date_overrides_add_date(self) -> None:
        """Test existing date in filename takes precedence."""
        result = normalize_filename(
            "2024-01-15-document.txt",
            add_date=True,
            creation_date_str="2024-03-20",
        )
        assert result == "2024-01-15-document.txt"

    def test_extension_lowercased(self) -> None:
        """Test extension is lowercased."""
        result = normalize_filename("file.TXT")
        assert result == "file.txt"


class TestNormalizeFile:
    """Tests for normalize_file function."""

    def test_normalize_file_dry_run(self) -> None:
        """Test normalize_file in dry run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "Hello_World.txt"
            filepath.touch()

            result = normalize_file(filepath, dry_run=True)

            assert result is not None
            old, new = result
            assert old == filepath
            assert new.name == "hello-world.txt"
            assert filepath.exists()  # Original still exists

    def test_normalize_file_actual_rename(self) -> None:
        """Test normalize_file actually renames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "Hello_World.txt"
            filepath.touch()

            result = normalize_file(filepath, dry_run=False)

            assert result is not None
            old, new = result
            assert not old.exists()
            assert new.exists()
            assert new.name == "hello-world.txt"

    def test_normalize_file_no_change_needed(self) -> None:
        """Test normalize_file returns None when no change needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "already-normalized.txt"
            filepath.touch()

            result = normalize_file(filepath, dry_run=False)

            assert result is None

    def test_normalize_file_with_add_date(self) -> None:
        """Test normalize_file with date prefix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "document.txt"
            filepath.touch()

            result = normalize_file(filepath, add_date=True, dry_run=True)

            assert result is not None
            _, new = result
            assert new.name.startswith("20")  # Year prefix

    def test_normalize_file_nonexistent(self) -> None:
        """Test normalize_file with nonexistent file."""
        result = normalize_file(Path("/nonexistent/file.txt"))
        assert result is None

    def test_normalize_file_directory(self) -> None:
        """Test normalize_file with directory returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = normalize_file(Path(tmpdir))
            assert result is None


class TestResolveNameConflict:
    """Tests for resolve_name_conflict function."""

    def test_no_conflict(self) -> None:
        """Test when there's no conflict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_path = Path(tmpdir) / "new-file.txt"
            original = Path(tmpdir) / "original.txt"

            result = resolve_name_conflict(new_path, original)

            assert result == new_path

    def test_with_conflict(self) -> None:
        """Test when there's a naming conflict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = Path(tmpdir) / "file.txt"
            existing.touch()
            new_path = Path(tmpdir) / "file.txt"
            original = Path(tmpdir) / "original.txt"

            result = resolve_name_conflict(new_path, original)

            assert result.name == "file-1.txt"

    def test_multiple_conflicts(self) -> None:
        """Test with multiple conflicting files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file.txt").touch()
            (Path(tmpdir) / "file-1.txt").touch()
            new_path = Path(tmpdir) / "file.txt"
            original = Path(tmpdir) / "original.txt"

            result = resolve_name_conflict(new_path, original)

            assert result.name == "file-2.txt"

    def test_same_file(self) -> None:
        """Test when new path is same as original."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "file.txt"
            filepath.touch()

            result = resolve_name_conflict(filepath, filepath)

            assert result == filepath
