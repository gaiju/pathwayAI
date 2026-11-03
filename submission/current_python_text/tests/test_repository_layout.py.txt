"""Protect ZIP downloads on case-insensitive macOS and Windows filesystems."""
import unittest
from pathlib import Path


class RepositoryLayoutTests(unittest.TestCase):
    def test_entrypoint_has_no_case_insensitive_collision(self):
        root = Path(__file__).resolve().parents[1]
        entrypoints = sorted(p.name for p in root.iterdir()
                             if p.is_file() and p.name.casefold() == "app.py")
        self.assertEqual(entrypoints, ["app.py"])
