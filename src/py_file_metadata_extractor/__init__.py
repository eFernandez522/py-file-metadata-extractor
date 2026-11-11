"""Public API for py-file-metadata-extractor.

Only :func:`extract_metadata` is exported.  Keeping the public surface
small means callers can rely on the return shape without reading the
implementation.
"""

from .core import extract_metadata

__all__ = ["extract_metadata"]
