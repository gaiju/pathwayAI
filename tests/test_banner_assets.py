import ast
import base64
from pathlib import Path
import unittest


class BannerTests(unittest.TestCase):
    def test_all_banners_are_valid_embedded_jpeg_data(self):
        tree = ast.parse(Path("app.py").read_text())
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                          and any(getattr(target, "id", "") == "PATHWAY_PHOTOS116"
                                  for target in node.targets))
        photos = ast.literal_eval(assignment.value)
        self.assertEqual(set(photos), {"lake", "forest", "tick_leaf", "river"})
        for name, encoded in photos.items():
            with self.subTest(banner=name):
                data = base64.b64decode(encoded, validate=True)
                self.assertTrue(data.startswith(b"\xff\xd8"))
                self.assertTrue(data.endswith(b"\xff\xd9"))


if __name__ == "__main__":
    unittest.main()
