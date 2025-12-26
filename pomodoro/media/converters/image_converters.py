"""Convert image to webp."""

import io

from PIL import Image


async def convert_to_webp(
    image: bytes, quality: int = 75, method: int = 0
) -> io.BytesIO:
    """Return converted to WEBP  copy of this image.

    Args:     image: Image in bytes.     quality: Compression quality
    (0-100).     method: The number of passes during compression (0-6).

    Returns:     Converted to WEBP image in bytes.
    """
    output_buffer: io.BytesIO = io.BytesIO()

    with Image.open(io.BytesIO(image)) as img:
        img.save(
            fp=output_buffer,
            format="WEBP",
            quality=quality,
            method=method,
            lossless=False,
            optimize=True,
        )
    output_buffer.seek(0)
    return output_buffer


async def resize_image(
    image: io.BytesIO,
    width: int | None = None,
    height: int | None = None,
    quality: int = 90,
    method: int = 6,
) -> io.BytesIO:
    """Returns a resized copy of this image with the same proportions.

    Args:
        image: Image in bytes.
        width: Width output image.
        height: Height output image.
        quality: Compression quality (0-100).
        method: The number of passes during compression (0-6).

    Returns:
        Compressed image in bytes.
    """
    output_buffer: io.BytesIO = io.BytesIO()
    with Image.open(image) as img:
        original_width: int = img.width
        original_height: int = img.height
        if width is None and height is None:
            raise ValueError(
                "Нужно передать хотя бы один из параметров: "
                "width (ширина (в пикселях) файла на выходе), "
                "или height (высота (в пикселях) файла на выходе)"
            )
        if width is None:
            ratio: float = height / original_height
            width = img.width * ratio
        elif height is None:
            ratio: float = width / original_width
            height = img.height * ratio

        resized_image = img.resize(size=(int(width), int(height)))
        resized_image.save(
            fp=output_buffer,
            format="WEBP",
            quality=quality,
            method=method,
            lossless=False,
            optimize=True,
        )
    resized_image.seek(0)
    return output_buffer
