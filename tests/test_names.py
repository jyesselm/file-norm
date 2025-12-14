"""Tests for the names module."""

from file_normalization.names import (
    collapse_hyphens,
    join_name_and_extension,
    replace_separators,
    sanitize_name,
    split_name_and_extension,
    strip_edge_hyphens,
    to_lowercase,
)


class TestReplaceSeparators:
    """Tests for replace_separators function."""

    def test_replace_spaces(self) -> None:
        """Test replacing spaces with hyphens."""
        result = replace_separators("hello world")
        assert result == "hello-world"

    def test_replace_underscores(self) -> None:
        """Test replacing underscores with hyphens."""
        result = replace_separators("hello_world")
        assert result == "hello-world"

    def test_replace_mixed(self) -> None:
        """Test replacing both spaces and underscores."""
        result = replace_separators("hello_world test")
        assert result == "hello-world-test"

    def test_no_separators(self) -> None:
        """Test string without separators is unchanged."""
        result = replace_separators("helloworld")
        assert result == "helloworld"


class TestCollapseHyphens:
    """Tests for collapse_hyphens function."""

    def test_collapse_multiple(self) -> None:
        """Test collapsing multiple hyphens."""
        result = collapse_hyphens("hello---world")
        assert result == "hello-world"

    def test_collapse_double(self) -> None:
        """Test collapsing double hyphens."""
        result = collapse_hyphens("hello--world")
        assert result == "hello-world"

    def test_single_hyphen_unchanged(self) -> None:
        """Test single hyphens are unchanged."""
        result = collapse_hyphens("hello-world")
        assert result == "hello-world"


class TestStripEdgeHyphens:
    """Tests for strip_edge_hyphens function."""

    def test_strip_leading(self) -> None:
        """Test stripping leading hyphens."""
        result = strip_edge_hyphens("--hello")
        assert result == "hello"

    def test_strip_trailing(self) -> None:
        """Test stripping trailing hyphens."""
        result = strip_edge_hyphens("hello--")
        assert result == "hello"

    def test_strip_both(self) -> None:
        """Test stripping both leading and trailing."""
        result = strip_edge_hyphens("--hello--")
        assert result == "hello"

    def test_no_edge_hyphens(self) -> None:
        """Test string without edge hyphens is unchanged."""
        result = strip_edge_hyphens("hello-world")
        assert result == "hello-world"


class TestToLowercase:
    """Tests for to_lowercase function."""

    def test_uppercase(self) -> None:
        """Test converting uppercase to lowercase."""
        result = to_lowercase("HELLO")
        assert result == "hello"

    def test_mixed_case(self) -> None:
        """Test converting mixed case to lowercase."""
        result = to_lowercase("HelloWorld")
        assert result == "helloworld"

    def test_already_lowercase(self) -> None:
        """Test already lowercase is unchanged."""
        result = to_lowercase("hello")
        assert result == "hello"


class TestSanitizeName:
    """Tests for sanitize_name function."""

    def test_full_sanitization(self) -> None:
        """Test full sanitization pipeline."""
        result = sanitize_name("Hello_World Test")
        assert result == "hello-world-test"

    def test_complex_case(self) -> None:
        """Test complex sanitization case."""
        result = sanitize_name("__My  File__Name__")
        assert result == "my-file-name"

    def test_simple_name(self) -> None:
        """Test simple name passes through."""
        result = sanitize_name("document")
        assert result == "document"


class TestSplitNameAndExtension:
    """Tests for split_name_and_extension function."""

    def test_simple_extension(self) -> None:
        """Test splitting simple filename."""
        name, ext = split_name_and_extension("document.pdf")
        assert name == "document"
        assert ext == ".pdf"

    def test_no_extension(self) -> None:
        """Test splitting filename without extension."""
        name, ext = split_name_and_extension("document")
        assert name == "document"
        assert ext == ""

    def test_multiple_dots(self) -> None:
        """Test splitting filename with multiple dots."""
        name, ext = split_name_and_extension("file.name.txt")
        assert name == "file.name"
        assert ext == ".txt"


class TestJoinNameAndExtension:
    """Tests for join_name_and_extension function."""

    def test_with_dot(self) -> None:
        """Test joining with extension that has dot."""
        result = join_name_and_extension("document", ".pdf")
        assert result == "document.pdf"

    def test_without_dot(self) -> None:
        """Test joining with extension without dot."""
        result = join_name_and_extension("document", "pdf")
        assert result == "document.pdf"

    def test_empty_extension(self) -> None:
        """Test joining with empty extension."""
        result = join_name_and_extension("document", "")
        assert result == "document"
