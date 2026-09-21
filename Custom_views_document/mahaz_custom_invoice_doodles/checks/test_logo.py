"""Run directly with Python/Pillow; no Odoo database is required."""

import base64
import importlib.util
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageChops

SPEC = importlib.util.spec_from_file_location(
    "mahaz_logo", Path(__file__).parents[1] / "logo_utils.py"
)
LOGO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LOGO)


class TestInvoiceLogo(unittest.TestCase):
    def normalize(self, image, image_format):
        stream = BytesIO()
        image.save(stream, format=image_format)
        result = LOGO.prepare_invoice_logo(base64.b64encode(stream.getvalue()))
        output = Image.open(BytesIO(base64.b64decode(result)))
        self.assertEqual(output.format, "PNG")
        self.assertEqual(output.mode, "RGB")
        self.assertEqual(output.size, (1200, 696))
        return output

    def test_cmyk_jpeg(self):
        self.normalize(Image.new("CMYK", (100, 60), (0, 80, 80, 0)), "JPEG")

    def test_transparency_is_flattened_on_white(self):
        output = self.normalize(Image.new("RGBA", (100, 60), (0, 0, 0, 0)), "PNG")
        self.assertEqual(output.getpixel((0, 0)), (255, 255, 255))

    def test_padding_removed_without_distorting_artwork(self):
        image = Image.new("RGB", (500, 400), "white")
        image.paste((20, 40, 60), (200, 170, 300, 220))
        output = self.normalize(image, "PNG")
        bounds = ImageChops.difference(
            output, Image.new("RGB", output.size, "white")
        ).getbbox()
        width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        self.assertAlmostEqual(width / height, 2, delta=0.03)
        self.assertGreater(width, 1000)

    def test_palette_image(self):
        self.normalize(Image.new("P", (80, 50)), "GIF")

    def test_invalid_image_is_rejected(self):
        with self.assertRaises(OSError):
            LOGO.prepare_invoice_logo(base64.b64encode(b"not an image"))


if __name__ == "__main__":
    unittest.main()
