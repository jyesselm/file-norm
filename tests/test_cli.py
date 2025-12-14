"""Tests for the CLI module."""

import tempfile
from pathlib import Path

import pytest

from file_normalization.cli import (
    collect_files,
    create_parser,
    get_date_format,
    main,
    normalize_extensions,
    process_files,
)
from file_normalization.dates import DateFormat


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_creation(self) -> None:
        """Test parser is created successfully."""
        parser = create_parser()
        assert parser is not None

    def test_default_path(self) -> None:
        """Test default path is current directory."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.path == "."

    def test_custom_path(self) -> None:
        """Test custom path is parsed."""
        parser = create_parser()
        args = parser.parse_args(["/some/path"])
        assert args.path == "/some/path"

    def test_recursive_flag(self) -> None:
        """Test recursive flag parsing."""
        parser = create_parser()
        args = parser.parse_args(["-r"])
        assert args.recursive is True

    def test_dry_run_flag(self) -> None:
        """Test dry-run flag parsing."""
        parser = create_parser()
        args = parser.parse_args(["-n"])
        assert args.dry_run is True

    def test_add_date_flag(self) -> None:
        """Test add-date flag parsing."""
        parser = create_parser()
        args = parser.parse_args(["-d"])
        assert args.add_date is True

    def test_extension_filter(self) -> None:
        """Test extension filter parsing."""
        parser = create_parser()
        args = parser.parse_args(["-e", "txt", "-e", "pdf"])
        assert args.ext == ["txt", "pdf"]

    def test_year_month_flag(self) -> None:
        """Test year-month flag parsing."""
        parser = create_parser()
        args = parser.parse_args(["--year-month"])
        assert args.year_month is True

    def test_year_only_flag(self) -> None:
        """Test year-only flag parsing."""
        parser = create_parser()
        args = parser.parse_args(["--year-only"])
        assert args.year_only is True


class TestGetDateFormat:
    """Tests for get_date_format function."""

    def test_default_format(self) -> None:
        """Test default returns full format."""
        result = get_date_format(year_month=False, year_only=False)
        assert result == DateFormat.FULL

    def test_year_month_format(self) -> None:
        """Test year-month flag returns year-month format."""
        result = get_date_format(year_month=True, year_only=False)
        assert result == DateFormat.YEAR_MONTH

    def test_year_only_format(self) -> None:
        """Test year-only flag returns year format."""
        result = get_date_format(year_month=False, year_only=True)
        assert result == DateFormat.YEAR

    def test_year_only_takes_precedence(self) -> None:
        """Test year-only takes precedence over year-month."""
        result = get_date_format(year_month=True, year_only=True)
        assert result == DateFormat.YEAR


class TestNormalizeExtensions:
    """Tests for normalize_extensions function."""

    def test_without_dots(self) -> None:
        """Test extensions without dots get dots added."""
        result = normalize_extensions(["txt", "pdf"])
        assert result == {".txt", ".pdf"}

    def test_with_dots(self) -> None:
        """Test extensions with dots are preserved."""
        result = normalize_extensions([".txt", ".pdf"])
        assert result == {".txt", ".pdf"}

    def test_mixed(self) -> None:
        """Test mixed extensions are normalized."""
        result = normalize_extensions(["txt", ".PDF"])
        assert result == {".txt", ".pdf"}


class TestCollectFiles:
    """Tests for collect_files function."""

    def test_collect_single_file(self) -> None:
        """Test collecting a single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.txt"
            filepath.touch()

            result = collect_files(filepath, recursive=False, extensions=None)

            assert result == [filepath]

    def test_collect_directory(self) -> None:
        """Test collecting files from directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.txt").touch()
            (Path(tmpdir) / "file2.txt").touch()

            result = collect_files(Path(tmpdir), recursive=False, extensions=None)

            assert len(result) == 2

    def test_collect_recursive(self) -> None:
        """Test collecting files recursively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.txt").touch()
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (subdir / "file2.txt").touch()

            result = collect_files(Path(tmpdir), recursive=True, extensions=None)

            assert len(result) == 2

    def test_collect_non_recursive(self) -> None:
        """Test collecting files non-recursively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.txt").touch()
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (subdir / "file2.txt").touch()

            result = collect_files(Path(tmpdir), recursive=False, extensions=None)

            assert len(result) == 1

    def test_collect_with_extension_filter(self) -> None:
        """Test collecting files with extension filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.txt").touch()
            (Path(tmpdir) / "file2.pdf").touch()

            result = collect_files(Path(tmpdir), recursive=False, extensions=["txt"])

            assert len(result) == 1
            assert result[0].suffix == ".txt"


class TestProcessFiles:
    """Tests for process_files function."""

    def test_process_files_dry_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test processing files in dry run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "Hello_World.txt"
            filepath.touch()

            renamed = process_files([filepath], add_date=False, dry_run=True)

            assert renamed == 1
            captured = capsys.readouterr()
            assert "[DRY RUN]" in captured.out

    def test_process_files_no_changes(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test processing files when no changes needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "already-normalized.txt"
            filepath.touch()

            renamed = process_files([filepath], add_date=False, dry_run=True)

            assert renamed == 0


class TestMain:
    """Tests for main function."""

    def test_main_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main function with valid path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.txt"
            filepath.touch()

            result = main([tmpdir, "-n"])

            assert result == 0

    def test_main_nonexistent_path(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Test main function with nonexistent path."""
        result = main(["/nonexistent/path"])

        assert result == 1
        captured = capsys.readouterr()
        assert "does not exist" in captured.err

    def test_main_with_file(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test main function with single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "Hello_World.txt"
            filepath.touch()

            result = main([str(filepath), "-n"])

            assert result == 0
            captured = capsys.readouterr()
            assert "hello-world.txt" in captured.out
