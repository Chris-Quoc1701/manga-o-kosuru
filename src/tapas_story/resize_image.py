import os

from PIL import Image


def reduce_size_image(path_image, validate_size: int = 300000):
    quality = 95
    while os.path.getsize(path_image) > validate_size:
        image = Image.open(path_image)
        image = image.convert("RGB")
        image.save(path_image, quality=quality)
        # avoid make image blur when reduce size
        if quality > 50:
            quality -= 5
        else:
            quality -= 1
        if quality <= 0:
            break

    print(
        f"Reduce size image from size {os.path.getsize(path_image)} to {os.path.getsize(path_image)}"
    )
