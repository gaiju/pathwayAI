import base64
from io import BytesIO
import unittest
from PIL import Image
from visual_assets import PHOTO_FILES, photo_data_uri


class BannerTests(unittest.TestCase):
    def test_all_banners_are_valid_local_jpegs_with_working_display_data(self):
        self.assertEqual(set(PHOTO_FILES), {'lake','forest','tick_leaf','river'})
        for name,path in PHOTO_FILES.items():
            with self.subTest(banner=name):
                data=path.read_bytes()
                self.assertTrue(data.startswith(b'\xff\xd8'))
                self.assertTrue(data.endswith(b'\xff\xd9'))
                with Image.open(BytesIO(data)) as image:
                    self.assertEqual(image.format,'JPEG')
                    self.assertGreater(image.width/image.height,3.5)
                    image.verify()
                self.assertEqual(base64.b64decode(photo_data_uri(name).split(',',1)[1],validate=True),data)


if __name__ == '__main__':
    unittest.main()
