"""Tests for the dates module."""

import tempfile
from datetime import datetime
from pathlib import Path

from file_normalization.dates import (
    DateFormat,
    extract_date_from_filename,
    format_date,
    get_file_creation_date,
    strip_date_prefix,
)


class TestExtractDateFromFilename:
    """Tests for extract_date_from_filename function."""

    def test_yyyy_mm_dd_format(self) -> None:
        """Test extraction of YYYY-MM-DD format."""
        result = extract_date_from_filename("2024-01-15-document.pdf")
        assert result == datetime(2024, 1, 15)

    def test_yyyy_mm_dd_underscore_format(self) -> None:
        """Test extraction of YYYY_MM_DD format."""
        result = extract_date_from_filename("2024_01_15_document.pdf")
        assert result == datetime(2024, 1, 15)

    def test_yyyymmdd_format(self) -> None:
        """Test extraction of YYYYMMDD format."""
        result = extract_date_from_filename("20240115-document.pdf")
        assert result == datetime(2024, 1, 15)

    def test_mm_dd_yyyy_format(self) -> None:
        """Test extraction of MM-DD-YYYY format."""
        result = extract_date_from_filename("01-15-2024-document.pdf")
        assert result == datetime(2024, 1, 15)

    def test_mm_dd_yyyy_underscore_format(self) -> None:
        """Test extraction of MM_DD_YYYY format."""
        result = extract_date_from_filename("01_15_2024_document.pdf")
        assert result == datetime(2024, 1, 15)

    def test_no_date_returns_none(self) -> None:
        """Test that filenames without dates return None."""
        result = extract_date_from_filename("document.pdf")
        assert result is None

    def test_invalid_date_returns_none(self) -> None:
        """Test that invalid dates return None."""
        result = extract_date_from_filename("2024-13-45-document.pdf")
        assert result is None


class TestStripDatePrefix:
    """Tests for strip_date_prefix function."""

    def test_strip_yyyy_mm_dd(self) -> None:
        """Test stripping YYYY-MM-DD prefix."""
        result = strip_date_prefix("2024-01-15-document.pdf")
        assert result == "document.pdf"

    def test_strip_yyyy_mm_dd_with_space(self) -> None:
        """Test stripping YYYY-MM-DD prefix with space separator."""
        result = strip_date_prefix("2024-01-15 document.pdf")
        assert result == "document.pdf"

    def test_strip_yyyy_mm_dd_underscore(self) -> None:
        """Test stripping YYYY_MM_DD prefix."""
        result = strip_date_prefix("2024_01_15_document.pdf")
        assert result == "document.pdf"

    def test_strip_yyyymmdd(self) -> None:
        """Test stripping YYYYMMDD prefix."""
        result = strip_date_prefix("20240115-document.pdf")
        assert result == "document.pdf"

    def test_strip_mm_dd_yyyy(self) -> None:
        """Test stripping MM-DD-YYYY prefix."""
        result = strip_date_prefix("01-15-2024-document.pdf")
        assert result == "document.pdf"

    def test_no_date_unchanged(self) -> None:
        """Test that filenames without dates are unchanged."""
        result = strip_date_prefix("document.pdf")
        assert result == "document.pdf"


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_date_full(self) -> None:
        """Test date formatting to YYYY-MM-DD."""
        date = datetime(2024, 1, 15)
        result = format_date(date, DateFormat.FULL)
        assert result == "2024-01-15"

    def test_format_date_default_is_full(self) -> None:
        """Test default format is YYYY-MM-DD."""
        date = datetime(2024, 1, 15)
        result = format_date(date)
        assert result == "2024-01-15"

    def test_format_date_year_month(self) -> None:
        """Test date formatting to YYYY-MM."""
        date = datetime(2024, 1, 15)
        result = format_date(date, DateFormat.YEAR_MONTH)
        assert result == "2024-01"

    def test_format_date_year_only(self) -> None:
        """Test date formatting to YYYY."""
        date = datetime(2024, 1, 15)
        result = format_date(date, DateFormat.YEAR)
        assert result == "2024"

    def test_format_date_with_leading_zeros(self) -> None:
        """Test date formatting preserves leading zeros."""
        date = datetime(2024, 5, 3)
        result = format_date(date)
        assert result == "2024-05-03"

    def test_format_date_invalid_format_uses_full(self) -> None:
        """Test invalid format falls back to full."""
        date = datetime(2024, 1, 15)
        result = format_date(date, "invalid")
        assert result == "2024-01-15"


class TestGetFileCreationDate:
    """Tests for get_file_creation_date function."""

    def test_get_creation_date(self) -> None:
        """Test getting file creation date."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = Path(f.name)
        try:
            result = get_file_creation_date(filepath)
            assert isinstance(result, datetime)
            assert result.year >= 2024
        finally:
            filepath.unlink()
