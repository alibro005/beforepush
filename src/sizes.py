import re
from decimal import Decimal

_SIZE_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*(B|KB|MB)?$", re.IGNORECASE)
_UNIT_MULTIPLIERS = {"B": 1, "KB": 1024, "MB": 1024 * 1024}


def parse_file_size(value: str) -> int:
    """Parse a byte count or a size with B, KB, or MB units into bytes."""
    match = _SIZE_PATTERN.fullmatch(value.strip())
    if not match:
        raise ValueError("size must be a positive number optionally followed by B, KB, or MB")

    amount = Decimal(match.group(1))
    if amount <= 0:
        raise ValueError("size must be greater than zero")

    unit = (match.group(2) or "B").upper()
    size_bytes = amount * _UNIT_MULTIPLIERS[unit]
    if size_bytes != size_bytes.to_integral_value():
        raise ValueError("size must resolve to a whole number of bytes")
    return int(size_bytes)


def format_file_size(size_bytes: int) -> str:
    """Format a byte count with a readable binary unit."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"
