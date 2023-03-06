import os

from PIL import Image


def check_image_size(image_path: str) -> str:
    """Check size image if above 100Kb then reduce size image bellow 100Kb"""
    size_kb = os.path.getsize(image_path) / 1024
    while size_kb > 100:
        image = Image.open(image_path)
        # convert image to RGB
        image = image.convert("RGB")
        # get height and width image
        width, height = image.size
        # reduce by resize image with ideal size
        image = image.resize((width // 2, height // 2))
        # save image with quality 85% and type .JPEG
        image.save(image_path, quality=85, optimize=True, format="JPEG")
        # get size image
        size_kb = os.path.getsize(image_path) / 1024
    return image_path


def clear_all_image_content() -> None:
    """Clear all image inside chapter"""
    # Get folder storages
    folder_storages = os.listdir("storages")
    for folder in folder_storages:
        # Get list folder comic
        list_folder_comic = os.listdir(f"storages/{folder}")
        for folder_comic in list_folder_comic:
            # Get list folder chapter
            list_folder_chapter = os.listdir(f"storages/{folder}/{folder_comic}")
            for folder_chapter in list_folder_chapter:
                # Get list image "1.jpg", "2.jpg", ...
                list_image = os.listdir(
                    f"storages/{folder}/{folder_comic}/{folder_chapter}"
                )
                for image in list_image:
                    # check image name is number
                    if image.split(".")[0].isdigit():
                        # remove image
                        os.remove(
                            f"storages/{folder}/{folder_comic}/{folder_chapter}/{image}"
                        )
