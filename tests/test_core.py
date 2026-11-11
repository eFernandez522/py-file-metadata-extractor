"""Tests for :mod:`py_file_metadata_extractor`.

These tests exercise the real ``os.stat`` behaviour on temporary files
and directories.  They avoid asserting on wall-clock values; mtime and
ctime are only checked for type and for being non-negative, because
their exact values depend on the filesystem and the clock.
"""

import os
import stat
import tempfile
import unittest

from py_file_metadata_extractor import extract_metadata


class ExtractMetadataTests(unittest.TestCase):
    def test_regular_file_returns_all_keys(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"hello world")
            path = fh.name
        try:
            meta = extract_metadata(path)
            self.assertEqual(
                set(meta),
                {"size", "mtime", "ctime", "mode", "uid", "gid"},
            )
            self.assertEqual(meta["size"], 11)
        finally:
            os.unlink(path)

    def test_types_are_plain_python(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            path = fh.name
        try:
            meta = extract_metadata(path)
            self.assertIsInstance(meta, dict)
            self.assertIsInstance(meta["size"], int)
            self.assertIsInstance(meta["mtime"], float)
            self.assertIsInstance(meta["ctime"], float)
            self.assertIsInstance(meta["mode"], int)
            self.assertIsInstance(meta["uid"], int)
            self.assertIsInstance(meta["gid"], int)
        finally:
            os.unlink(path)

    def test_mode_contains_file_type_bits(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            path = fh.name
        try:
            meta = extract_metadata(path)
            self.assertTrue(stat.S_ISREG(meta["mode"]))
        finally:
            os.unlink(path)

    def test_directory_is_reported_as_directory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            meta = extract_metadata(d)
            self.assertTrue(stat.S_ISDIR(meta["mode"]))
            self.assertGreaterEqual(meta["size"], 0)

    def test_missing_path_raises_file_not_found(self) -> None:
        missing = os.path.join(tempfile.gettempdir(), "py-fme-does-not-exist-12345")
        with self.assertRaises(FileNotFoundError):
            extract_metadata(missing)

    def test_pathlike_object_is_accepted(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"abc")
            path = fh.name
        try:
            meta = extract_metadata(type("P", (), {"__fspath__": lambda self: path})())
            self.assertEqual(meta["size"], 3)
        finally:
            os.unlink(path)

    def test_symlink_follows_target(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"target-data")
            target = fh.name
        link = target + ".link"
        try:
            os.symlink(target, link)
            target_meta = extract_metadata(target)
            link_meta = extract_metadata(link)
            self.assertEqual(link_meta["size"], target_meta["size"])
            self.assertEqual(link_meta["mode"], target_meta["mode"])
        finally:
            os.unlink(link)
            os.unlink(target)

    def test_uid_and_gid_match_os_stat(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            path = fh.name
        try:
            st = os.stat(path)
            meta = extract_metadata(path)
            self.assertEqual(meta["uid"], st.st_uid)
            self.assertEqual(meta["gid"], st.st_gid)
        finally:
            os.unlink(path)

    def test_mtime_and_ctime_are_non_negative(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            path = fh.name
        try:
            meta = extract_metadata(path)
            self.assertGreaterEqual(meta["mtime"], 0.0)
            self.assertGreaterEqual(meta["ctime"], 0.0)
        finally:
            os.unlink(path)

    def test_single_stat_call(self) -> None:
        """The implementation promises one stat call; verify it."""
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            path = fh.name
        try:
            calls = {"n": 0}
            real_stat = os.stat

            def counting_stat(p, *args, **kwargs):
                calls["n"] += 1
                return real_stat(p, *args, **kwargs)

            import py_file_metadata_extractor.core as core

            original = core.os.stat
            core.os.stat = counting_stat
            try:
                extract_metadata(path)
            finally:
                core.os.stat = original
            self.assertEqual(calls["n"], 1)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
