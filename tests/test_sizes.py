import pytest

from sizes import format_file_size, parse_file_size


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("500KB", 500 * 1024),
        ("5MB", 5 * 1024 * 1024),
        ("10mb", 10 * 1024 * 1024),
        ("5242880", 5 * 1024 * 1024),
        ("1.5MB", 1536 * 1024),
    ],
)
def test_parse_file_size(value, expected):
    assert parse_file_size(value) == expected


@pytest.mark.parametrize("value", ["abc", "5XYZ", "-5MB", "0", "1.1B", ""])
def test_parse_file_size_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="size"):
        parse_file_size(value)


@pytest.mark.parametrize(
    ("size", "expected"),
    [(100, "100 B"), (1024, "1.0 KB"), (5 * 1024 * 1024, "5.0 MB")],
)
def test_format_file_size(size, expected):
    assert format_file_size(size) == expected
