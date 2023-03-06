import os

from PIL import Image


def reduce_size_image(path_image: str) -> str:
    """Reduce size image if above 100Kb"""
    size_kb = os.path.getsize(path_image) / 1024
    if size_kb > 100:
        image = Image.open(path_image)
        # convert image to RGB
        try:
            image = image.convert("RGB")
        except:
            image = image.convert("RGBA")
        # reduce by resize image with ideal size
        image = image.resize((250, 250))
        # save image with quality 85% and type .JPEG
        image.save(path_image, quality=85, optimize=True, format="JPEG")
        # get size image
        size_kb = os.path.getsize(path_image) / 1024
    return path_image


def combine_image(back: str, front: str, path_save: str) -> str:
    # Combine image
    back = Image.open(back)
    front = Image.open(front)
    # convert front image to RGBA
    try:
        front = front.convert("RGBA")
    except:
        front = front.convert("RGB")
    # resize back image
    back = back.resize(front.size)
    # combine image
    back.paste(front, (0, 0), front)
    # save image
    path = os.path.join(path_save, "cover_combine.jpg")
    back.save(path, "JPEG", quality=92)
    return path


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
