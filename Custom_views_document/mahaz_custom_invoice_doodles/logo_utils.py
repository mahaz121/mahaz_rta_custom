# Copyright 2026 Mahaz (mahaz_abdullah@hotmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

import base64
from io import BytesIO

from PIL import Image, ImageChops, ImageOps


def prepare_invoice_logo(source: bytes) -> bytes:
    """Normalize raster formats and fit artwork to a consistent logo canvas."""
    with Image.open(BytesIO(base64.b64decode(source))) as original:
        if original.width * original.height > 50_000_000:
            raise ValueError("Invoice logo exceeds the image resolution limit.")
        image = ImageOps.exif_transpose(original).convert("RGBA")
        image.thumbnail((1200, 600))
        canvas = Image.new("RGB", image.size, "white")
        canvas.paste(image, mask=image.getchannel("A"))
        # Ignore near-white compression noise when locating the actual artwork.
        difference = ImageChops.difference(
            canvas, Image.new("RGB", canvas.size, "white")
        ).convert("L")
        bounds = difference.point(lambda value: 255 if value > 8 else 0).getbbox()
        if bounds:
            canvas = canvas.crop(bounds)
        artwork = ImageOps.contain(canvas, (1140, 636))
        canvas = Image.new("RGB", (1200, 696), "white")
        canvas.paste(artwork, (0, (696 - artwork.height) // 2))
        output = BytesIO()
        canvas.save(output, format="PNG")
        return base64.b64encode(output.getvalue())
