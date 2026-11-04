"""Optional source-byte bound check for the documented scalar-column convention."""
import hashlib

from .models import SourceLocation
from .validation import ContractViolation, check


def source_offsets(location: SourceLocation, source: bytes) -> tuple[int, int]:
    """Return Unicode-scalar offsets into UTF-8 decoded text, preserving raw LF/CRLF.

Tabs count as one scalar. Astral characters count as one scalar, not two UTF-16
units. Standalone CR and invalid UTF-8 require an unresolved location. This is a
data-boundary check, not an implicit adapter coordinate-system conversion.
"""
    check(location.resolution == 'RESOLVED', 'INVALID_CONTRACT', 'resolution')
    check(hashlib.sha256(source).hexdigest() == location.file_sha256, 'SCOPE_MISMATCH', 'file_sha256')
    try:
        text = source.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        raise ContractViolation('INVALID_CONTRACT', 'encoding') from None
    lines = text.split('\n')
    logical = [line[:-1] if index < len(lines) - 1 and line.endswith('\r') else line
               for index, line in enumerate(lines)]
    check(not any('\r' in line for line in logical), 'INVALID_CONTRACT', 'line_ending')
    offsets = []
    for line, column in [(location.start_line, location.start_column), (location.end_line, location.end_column)]:
        check(line <= len(lines) and column <= len(logical[line - 1]) + 1,
              'INVALID_CONTRACT', 'coordinates')
        offsets.append(sum(len(part) + 1 for part in lines[:line - 1]) + column - 1)
    return tuple(offsets)
