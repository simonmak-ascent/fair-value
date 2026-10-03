"""A-011: input validation and document-injection / macro guards for report review.

These are defensive checks applied before any document is parsed:

- :func:`validate_path` — existence, regular-file, non-empty, size limit, no symlink.
- :func:`detect_macros` — refuse macro-enabled office files (VBA ``vbaProject.bin``).
- :func:`find_injection_indicators` — flag spreadsheet formulas that pull remote
  data or invoke external programs (``WEBSERVICE``/``IMPORTDATA``/``DDE``/…).

No optional dependency is required: macro detection reads the OOXML zip container
directly with the standard library.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Set

MAX_FILE_BYTES = 200 * 1024 * 1024  # 200 MiB

# Extensions that can carry VBA: rejected outright (defence in depth).
MACRO_EXTENSIONS: Set[str] = {
    ".xlsm",
    ".xltm",
    ".xlam",
    ".docm",
    ".dotm",
    ".pptm",
    ".potm",
    ".ppam",
    ".sldm",
}

# OOXML containers that may embed a vbaProject.bin even with a non-macro extension.
_OOXML_EXTENSIONS: Set[str] = {
    ".xlsx",
    ".xlsm",
    ".xltx",
    ".xltm",
    ".docx",
    ".docm",
    ".dotx",
    ".dotm",
    ".pptx",
    ".pptm",
}

# Formula / content tokens that reach outside the document.
INJECTION_TOKENS = (
    "WEBSERVICE",
    "IMPORTDATA",
    "IMPORTXML",
    "IMPORTFEED",
    "RTD(",
    "DDE",
    "HYPERLINK(",
)


class InputValidationError(ValueError):
    """Raised when a review input fails a guard; carries a stable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def validate_path(
    path: str,
    allowed_exts: Optional[Set[str]] = None,
    max_bytes: int = MAX_FILE_BYTES,
) -> Path:
    """Validate a review input path; raise :class:`InputValidationError` if unsafe."""
    p = Path(path)
    if not p.exists():
        raise InputValidationError("FILE_NOT_FOUND", f"file not found: {path}")
    if p.is_symlink():
        raise InputValidationError("SYMLINK_REJECTED", f"symlink not allowed: {path}")
    if not p.is_file():
        raise InputValidationError("NOT_A_FILE", f"not a regular file: {path}")
    if allowed_exts is not None and p.suffix.lower() not in allowed_exts:
        raise InputValidationError("UNSUPPORTED_FILE_TYPE", f"unsupported file type: {p.suffix}")
    size = p.stat().st_size
    if size == 0:
        raise InputValidationError("EMPTY_FILE", f"empty file: {path}")
    if size > max_bytes:
        raise InputValidationError("FILE_TOO_LARGE", f"file exceeds {max_bytes} bytes: {path}")
    return p


def detect_macros(path: str) -> Dict:
    """Detect embedded VBA macros and external-link parts in an OOXML file.

    Returns a dict with ``is_macro_capable`` (extension may carry macros),
    ``has_macros`` (a ``vbaProject.bin`` part is present), and ``sources``.
    A non-zip / corrupt container is reported via ``error`` and treated as no
    macros (the caller may still reject on other grounds).
    """
    p = Path(path)
    suffix = p.suffix.lower()
    result: Dict = {
        "is_macro_capable": suffix in MACRO_EXTENSIONS,
        "has_macros": False,
        "sources": [],
    }
    if suffix in _OOXML_EXTENSIONS:
        try:
            with zipfile.ZipFile(p) as zf:
                names = zf.namelist()
            for name in names:
                low = name.lower()
                if "vbaproject.bin" in low:
                    result["has_macros"] = True
                    result["sources"].append(name)
                elif "externallink" in low:
                    result["sources"].append(name)
        except zipfile.BadZipFile:
            result["error"] = "not a valid OOXML (zip) container"
        except OSError as exc:  # pragma: no cover - filesystem race
            result["error"] = str(exc)
    return result


def find_injection_indicators(value: object) -> List[str]:
    """Return the external-content / injection tokens present in ``value``."""
    if not isinstance(value, str):
        return []
    upper = value.upper()
    return [token for token in INJECTION_TOKENS if token in upper]
