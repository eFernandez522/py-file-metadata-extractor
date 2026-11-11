# py-file-metadata-extractor

Returns size, mtime, ctime, mode, owner uid and gid for a path in a single
`os.stat` call, wrapped as a plain dictionary.

```python
from py_file_metadata_extractor import extract_metadata

meta = extract_metadata("/etc/hosts")
print(meta["size"], meta["mode"], meta["uid"], meta["gid"])
```

The dictionary always has exactly these keys:

- `size` — `st_size` as `int`
- `mtime` — `st_mtime` as `float`
- `ctime` — `st_ctime` as `float`
- `mode` — `st_mode` as `int` (includes the file-type bits)
- `uid` — `st_uid` as `int`
- `gid` — `st_gid` as `int`

## Why this exists

Getting file metadata usually means calling `os.stat` and then remembering
which `st_*` field maps to what.  That is fine once, but when the same
handful of fields is needed in several places the mapping gets copied
around and drifts.  This library fixes the mapping in one function so the
caller gets a stable dictionary shape.

The trade-off is that the return value is a `dict` rather than an object
with attributes.  A dict is trivial to serialise, compare and merge, and
it does not hide the fact that the values come straight from the OS.  The
cost is that a typo in a key name is a runtime error rather than an
attribute error at import time; the `TypedDict` in `core.py` documents
the keys for type checkers.

## The awkward edge

`os.stat` follows symbolic links.  If you pass a symlink, the returned
metadata describes the link target, not the link itself.  That matches
`stat(1)` and is the behaviour most callers want, but it is worth knowing
before you use this on a tree that contains symlinks.  If you need the
link's own metadata, call `os.lstat` yourself — this library does not
offer a flag for it, because a single clearly-documented behaviour is
better than a boolean that changes the meaning of every field.

## Errors

A missing path raises `FileNotFoundError`.  Any other stat failure
(permissions, I/O error) propagates the original `OSError` unchanged.
