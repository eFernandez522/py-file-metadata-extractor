"""Single-stat metadata extraction.

The goal is to make exactly one ``os.stat`` call per path and return
plain Python types.  ``os.stat`` already returns a named tuple with all
the fields we need, so wrapping it in a dict is cheap and keeps the
caller from having to remember the field names.

A deliberate trade-off: we do not follow symlinks.  ``os.stat`` follows
symlinks by default, and a metadata extractor that silently reports the
target's size is surprising when the caller asked about a path.  Using
``os.lstat`` instead would report the link's own metadata, but many
callers do want the target's metadata when the path is a symlink.  We
chose to follow symlinks because that matches what ``stat(1)`` does by
default and what most users expect from "the file at this path".  The
README states this explicitly.
"""

from __future__ import annotations

import os
from typing import TypedDict


class FileMetadata(TypedDict):
    """Shape returned by :func:`extract_metadata`.

    Using a ``TypedDict`` documents the keys without adding a runtime
    dependency or forcing callers to use a class.
    """

    size: int
    mtime: float
    ctime: float
    mode: int
    uid: int
    gid: int


def extract_metadata(path: str | os.PathLike[str]) -> FileMetadata:
    """Return size, mtime, ctime, mode, uid and gid for *path*.

    The function performs a single ``os.stat`` call.  ``os.stat``
    follows symlinks; the returned values therefore describe the target
    of a symlink, not the link itself.  ``st_mtime`` and ``st_ctime``
    are returned as floats because that is what ``os.stat`` produces and
    converting to ``int`` would lose sub-second precision that callers
    sometimes need.

    Parameters
    ----------
    path:
        A filesystem path as ``str`` or an object implementing
        ``os.PathLike``.

    Returns
    -------
    FileMetadata
        A ``dict`` with keys ``size``, ``mtime``, ``ctime``, ``mode``,
        ``uid`` and ``gid``.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    OSError
        For any other stat failure (permissions, I/O error, etc.).
    """
    st = os.stat(path)
    return {
        "size": st.st_size,
        "mtime": st.st_mtime,
        "ctime": st.st_ctime,
        "mode": st.st_mode,
        "uid": st.st_uid,
        "gid": st.st_gid,
    }
