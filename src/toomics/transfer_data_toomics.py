import argparse
import json
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from requests_html import HTMLSession
from utils import reduce_size_image

FOLDER_STORAGE = "storages"
PATH_STORAGE = os.path.join(os.getcwd(), FOLDER_STORAGE)

PATH_PROJECT = os.path.dirname(os.path.dirname(os.getcwd()))
PATH_CONFIG = os.path.join(PATH_PROJECT, "general_config")

# Loaded file general_config/config.yaml
with open(f"{PATH_CONFIG}/config.yaml", "r") as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)

LIST_TUPLE_GENRES = CONFIG["GENRES_MANGA"]
API_LOGIN = CONFIG["LOGIN"]["login_api"]
API_MANGA = CONFIG["MANGA"]["manga_api"]
API_CHAPTER = CONFIG["MANGA_CHAPTER"]["manga_chapter_api"]
API_MEDIA = CONFIG["MANGA_MEDIA"]["manga_media_api"]
LIST_OF_SCHEDULE = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


class TransferDataToomics:
    def __init__(self, email: str, password: str, number_chapter: int):
        self.email = email
        self.password = password
        self.session = HTMLSession()
        self.headers = {
            # multipart/form-data
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "Connection": "keep-alive",
            "Accept": "*/*",
        }
        self.number_chapter = number_chapter
        self.path_storage = PATH_STORAGE

    def get_folder_comic(self, comic_name: str) -> str:
        return os.path.join(PATH_STORAGE, comic_name)

    def get_folders_chapter(self, comic_name: str) -> list:
        folders = []
        for folder in os.listdir(self.get_folder_comic(comic_name)):
            if folder.startswith("chapter"):
                folders.append(folder)
        # Sorted folders by "chapter_1", "chapter_2", ...
        folders = sorted(folders, key=lambda x: int(x.split("_")[1]))
        return folders

    def get_all_images(self, path_chapter: str) -> list:
        images = []
        for file in os.listdir(path_chapter):
            if file.endswith(".jpg") or file.endswith(".png"):
                # exclude thumbnail
                if not file.startswith("thumbnail"):
                    images.append(file)
        # sort images by "1.jpg", "2.jpg", "3.jpg", ...
        images = sorted(images, key=lambda x: int(x.split(".")[0]))
        return images

    def data_comic_json(self, path_comic: str) -> dict:
        with open(os.path.join(path_comic, "toon.json"), "r") as f:
            data = json.load(f)
        return data

    def data_chapter_json(self, path_chapter: str) -> dict:
        with open(os.path.join(path_chapter, "chapter.json"), "r") as f:
            data = json.load(f)
        return data

    def choice_genre(self, genres: list) -> list:
        choices = []
        for genre in genres:
            for choice in LIST_TUPLE_GENRES:
                if genre.lower() == choice[1].lower():
                    choices.append(int(choice[0]))
        # if choices is empty then random base number
        if not choices:
            number = random.randint(1, 2)
            # many genres base on number
            while number > 0:
                # append random genre
                choices.append(random.choice(LIST_TUPLE_GENRES)[0])
                number -= 1
        return choices

    def create_or_update_save_progress(self, data: dict, path_save: str) -> dict:
        if os.path.exists(os.path.join(path_save, "save_progress.json")):
            with open(os.path.join(path_save, "save_progress.json"), "r") as f:
                save_progress = json.load(f)
            save_progress.update(data)
            with open(os.path.join(path_save, "save_progress.json"), "w") as f:
                json.dump(save_progress, f)
        else:
            with open(os.path.join(path_save, "save_progress.json"), "w") as f:
                json.dump(data, f)
        return data

    def request_post_create_manga(self, data: dict) -> int:
        if self.headers.get("Content-Type"):
            self.headers.pop("Content-Type")
        path_thumbnail = os.path.join(data["thumbnail"])
        path_cover = os.path.join(data["cover_combine"])
        genres = self.choice_genre(data["genres"])
        # Choice 1-3 schedules
        schedules = random.sample(LIST_OF_SCHEDULE, random.randint(1, 3))
        payload = {
            "name": data["name"],
            "summary": data["summary"],
            "genre": genres,
            "status": "published",
            "schedules": schedules,
        }
        print("Create manga: ", data["name"])
        files = {
            "thumbnail": ("thumbnail.jpg", open(path_thumbnail, "rb"), "image/jpeg"),
            "vertical_thumbnail": "",
            "cover": ("cover_combine.jpg", open(path_cover, "rb"), "image/jpeg"),
            "mobile_cover": "",
        }

        response = self.session.post(
            API_MANGA, data=payload, headers=self.headers, files=files, timeout=(10, 20)
        )
        if not response.ok:
            print(response.json())
            raise Exception("Create manga failed!")
        id_manga = response.json()["data"]["id"]
        time.sleep(1)
        return id_manga

    def request_post_create_chapter(
        self, id_manga: int, chapter_name: str, path_thumbnail: str, index: int
    ) -> int:
        if self.headers.get("Content-Type"):
            self.headers.pop("Content-Type")
        payload = {
            "name": chapter_name,
            "manga": id_manga,
            "is_free": True,
            "status": "published",
            "number": index,
        }
        files = [
            ("thumbnail", ("thumbnail.jpg", open(path_thumbnail, "rb"), "image/jpeg")),
        ]
        response = self.session.post(
            API_CHAPTER, data=payload, headers=self.headers, files=files
        )
        if not response.ok:
            print(response.json())
            raise Exception("Create chapter failed!")
        id_chapter = response.json()["data"]["id"]
        return id_chapter

    def request_post_create_media(
        self, id_chapter: int, path_image: str, index: int
    ) -> int:
        dict_media = {}
        basename = os.path.basename(path_image)
        payload = {
            "chapter": id_chapter,
        }
        files = [
            ("file", (basename, open(path_image, "rb"), "image/jpeg")),
        ]
        print("Upload image: ", path_image)
        response = self.session.post(
            API_MEDIA, data=payload, files=files, headers=self.headers
        )
        if not response.ok:
            raise Exception("Create media failed!")
        print(f"Upload image {index} success!")
        media_id = response.json()["data"]["id"]
        dict_media[int(index)] = media_id
        return dict_media

    def request_post_update_chapter(self, media_order: list, id_chapter: int) -> None:
        print(media_order)
        if not self.headers.get("Content-Type"):
            self.headers["Content-Type"] = "application/json"
        payload = json.dumps(
            {
                "media_order": media_order,
            }
        )
        response = self.session.patch(
            f"{API_CHAPTER}{id_chapter}/", data=payload, headers=self.headers
        )
        if not response.ok:
            print(response.json())
            raise Exception("Update chapter failed!")
        print("Update chapter success!")
        print(response.json())
        return response.json()["data"]["id"]

    def multi_thread_upload(self, id_chapter: int, images: list, path_chapter: str):
        dict_upload = {}
        # multi thread upload images
        print("Begin upload images...")
        print("Images: ", images)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_for_upload = {
                executor.submit(
                    self.request_post_create_media,
                    id_chapter,
                    os.path.join(path_chapter, image),
                    index,
                ): image
                for index, image in enumerate(images)
            }
            time.sleep(1)
            for future in as_completed(future_for_upload):
                image = future_for_upload[future]
                try:
                    data = future.result()
                    print(f"{image} upload success!")
                    time.sleep(1)
                except Exception as exc:
                    print(f"{image} generated an exception: {exc}")
                else:
                    dict_upload.update(data)

        return dict_upload

    def login_get_access_token(self) -> str:
        payload = json.dumps({"email": self.email, "password": self.password})
        response = self.session.post(API_LOGIN, data=payload, headers=self.headers)
        print(response.cookies)
        print(response.json())
        if not response.ok:
            raise Exception("Login failed!")
        return response.json()["data"]["refresh_token"]

    def begin_transfer(self):
        data = {}
        # login for access token and set header
        refresh_token = self.login_get_access_token()
        # Get list folder comic
        list_folder_comic = os.listdir(self.path_storage)
        for folder_comic in list_folder_comic:
            self.name_comic = os.path.basename(folder_comic)
            # get path to comic
            path_comic = self.get_folder_comic(self.name_comic)
            # get data comic
            data_comic = self.data_comic_json(path_comic)
            # path to chapters
            folders_chapter = self.get_folders_chapter(self.name_comic)
            total_chapter = len(folders_chapter)
            # path to thumbnail of comic
            path_thumbnail = os.path.join(path_comic, "thumbnail.jpg")
            path_thumbnail = reduce_size_image(path_image=path_thumbnail)
            path_cover_combine = os.path.join(path_comic, "cover_combine.jpg")
            self.path_comic = path_comic
            data_comic["thumbnail"] = path_thumbnail
            data_comic["cover_combine"] = (
                path_cover_combine if path_cover_combine else ""
            )
            # save progess upload
            file_name = "upload.json"
            # check file upload.json exist for get manga id if not create new manga
            if os.path.exists(os.path.join(path_comic, file_name)):
                with open(os.path.join(path_comic, file_name), "r") as f:
                    data = json.load(f)
                manga_id = data[f"{self.name_comic}"]["manga_id"]
            else:
                manga_id = self.request_post_create_manga(data_comic)
                data[f"{self.name_comic}"] = {
                    "manga_id": manga_id,
                    "total_chapter": total_chapter,
                    "total_chapter_uploaded": 0,
                }
                with open(os.path.join(path_comic, file_name), "w") as f:
                    json.dump(data, f)
            print("Manga id: ", manga_id)
            # check comic is upload complete
            if (
                data[f"{self.name_comic}"]["total_chapter"]
                == data[f"{self.name_comic}"]["total_chapter_uploaded"]
            ):
                print("Comic is upload complete!")
                return True

            # Load index chapter
            index_chapter = data[f"{self.name_comic}"]["total_chapter_uploaded"]
            # Get folders chapter
            folders_chapter = self.get_folders_chapter(self.name_comic)
            for index, folder_chapter in enumerate(
                folders_chapter[index_chapter:], start=index_chapter
            ):
                if index > self.number_chapter:
                    break
                # loaded chapter.json
                chapter = self.data_chapter_json(
                    os.path.join(path_comic, folder_chapter)
                )
                chapter_name = f'{chapter["name"]}'
                path_chapter = os.path.join(path_comic, folder_chapter)
                # path thumbnail in chapters
                path_thumbnail = os.path.join(path_chapter, "thumbnail.jpg")
                path_thumbnail = reduce_size_image(path_image=path_thumbnail)
                images = self.get_all_images(path_chapter)
                total_images = len(images)
                media_order = []

                # check chapter is upload complete if not create new chapter
                if os.path.exists(os.path.join(path_chapter, "upload.json")):
                    with open(os.path.join(path_chapter, "upload.json"), "r") as f:
                        data_chapter = json.load(f)
                    if data_chapter[f"{folder_chapter}"]["is_upload_complete"]:
                        print(f"Chapter {index} is upload complete!")
                        continue
                    else:
                        id_chapter = data_chapter[f"{folder_chapter}"]["id_chapter"]
                else:
                    id_chapter = self.request_post_create_chapter(
                        id_manga=manga_id,
                        chapter_name=chapter_name,
                        path_thumbnail=path_thumbnail,
                        index=index,
                    )
                    data_chapter = {
                        f"{folder_chapter}": {
                            "id_chapter": id_chapter,
                            "total_images": total_images,
                            "media_order": media_order,
                            "is_upload_complete": False,
                        }
                    }
                    with open(os.path.join(path_chapter, "upload.json"), "w") as f:
                        json.dump(data_chapter, f)
                # check chapter is upload complete
                if data_chapter[f"{folder_chapter}"]["total_images"] == len(
                    data_chapter[f"{folder_chapter}"]["media_order"]
                ):
                    print(f"Chapter {index} is upload complete!")
                    continue
                # loaded index image
                index_image = len(data_chapter[f"{folder_chapter}"]["media_order"])
                # get images
                images = images[index_image:]
                # upload images
                dict_upload = self.multi_thread_upload(id_chapter, images, path_chapter)
                # sort dict upload
                dict_upload_sorted = dict(
                    sorted(dict_upload.items(), key=lambda item: item[0])
                )
                # get media order
                media_order = [value for value in dict_upload_sorted.values()]
                # update data chapter
                data_chapter[f"{folder_chapter}"]["media_order"] = media_order
                data_chapter[f"{folder_chapter}"]["is_upload_complete"] = True
                # update data comic
                data[f"{self.name_comic}"]["total_chapter_uploaded"] += 1
                # save data chapter
                with open(os.path.join(path_chapter, "upload.json"), "w") as f:
                    json.dump(data_chapter, f)
                # save data comic
                with open(os.path.join(path_comic, file_name), "w") as f:
                    json.dump(data, f)
                # update media order
                self.request_post_update_chapter(
                    id_chapter=id_chapter, media_order=media_order
                )
                print(f"Chapter {index + 1} is upload complete!")
                time.sleep(12)
            print("Comic is upload complete!")
