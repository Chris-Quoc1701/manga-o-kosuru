import json
import os
import random
import time

import yaml
from requests_html import HTMLSession

FOLDER_STORAGE = "storages"
PATH_STORAGE = os.path.join(os.getcwd(), FOLDER_STORAGE)
PATH_PROJECT = os.path.dirname(os.path.dirname(os.getcwd()))
PATH_CONFIG = os.path.join(PATH_PROJECT, "general_config")

# Loaded file general_config/config.yaml
with open(f"{PATH_CONFIG}/config.yaml", "r") as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)
# GLOBAL VARIABLES
API_LOGIN = CONFIG["LOGIN"]["login_api"]
API_STORY = CONFIG["STORY"]["story_api"]
API_CHAPTER = CONFIG["STORY_CHAPTER"]["story_chapter_api"]

LIST_TUPLE_GENRES = CONFIG["GENRES_STORY"]

LIST_OF_SCHEDULE = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


class TransferDataTapasIO:
    def __init__(self, email: str, password: str, number_chapter: int):
        self.email = email
        self.password = password
        self.session = HTMLSession()
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "Connection": "keep-alive",
            "Accept": "*/*",
        }
        self.number_chapter = number_chapter

    def get_folder_comic(self, comic_name: str) -> str:
        return os.path.join(PATH_STORAGE, comic_name)

    def login(self):
        payload = json.dumps({"email": self.email, "password": self.password})
        response = self.session.post(API_LOGIN, data=payload, headers=self.headers)
        print(response.cookies)
        print(response.json())
        if not response.ok:
            raise Exception("Login failed!")
        return response.json()["data"]["refresh_token"]

    def choice_genre(self, genres: list) -> list:
        choices = []
        for genre in genres:
            for choice in LIST_TUPLE_GENRES:
                if genre.lower() == choice[1].lower():
                    choices.append(int(choice[0]))
        # if choices is empty then random base number
        if not choices:
            number = random.randint(1, 3)
            # many genres base on number
            while number > 0:
                # append random genre
                choices.append(random.choice(LIST_TUPLE_GENRES)[0])
                number -= 1
        return choices

    def create_story(self, data: dict) -> int:
        if self.headers.get("Content-Type"):
            self.headers.pop("Content-Type")
        path_thumbnail = os.path.join(data["thumbnail"])
        genres = self.choice_genre(data["genres"])
        schedules = random.sample(LIST_OF_SCHEDULE, random.randint(1, 3))
        payload = {
            "name": data["title"],
            "summary": data["summary"],
            "genre": genres,
            "status": "published",
            "schedules": schedules,
        }
        basename_thumbnail = os.path.basename(data["thumbnail"])
        files = [
            (
                "thumbnail",
                (basename_thumbnail, open(path_thumbnail, "rb"), "image/jpeg"),
            ),
            (
                "vertical_thumbnail",
                (basename_thumbnail, open(path_thumbnail, "rb"), "image/jpeg"),
            ),
        ]
        print(data["cover"])
        if data["cover"]:
            basename_cover = os.path.basename(data["cover"])
            path_cover = os.path.join(data["cover"])
            files.append(
                ("cover", (basename_cover, open(path_cover, "rb"), "image/jpeg"))
            )
            files.append(
                ("cover_mobile", (basename_cover, open(path_cover, "rb"), "image/jpeg"))
            )
        else:
            files.append(
                (
                    "cover",
                    (basename_thumbnail, open(path_thumbnail, "rb"), "image/jpeg"),
                )
            )
            files.append(
                (
                    "cover_mobile",
                    (basename_thumbnail, open(path_thumbnail, "rb"), "image/jpeg"),
                )
            )

        response = self.session.post(
            API_STORY, data=payload, files=files, headers=self.headers
        )
        if not response.ok:
            print(response.json())
            raise Exception("Create story failed!")
        return response.json()["data"]["id"]

    def create_chapter(self, data: dict, story_id: int, index: int) -> int:
        if self.headers.get("Content-Type"):
            self.headers.pop("Content-Type")
        payload = {
            "name": str(data["title"]),
            "story": story_id,
            "status": "published",
            "is_free": True,
            "enable_comment": True,
            "content": data["content"],
            "number": index,
        }
        path_thumbnail = os.path.join(data["thumbnail"])
        basename_thumbnail = os.path.basename(data["thumbnail"])
        files = [
            (
                "thumbnail",
                (basename_thumbnail, open(path_thumbnail, "rb"), "image/jpeg"),
            ),
        ]
        response = self.session.post(
            url=API_CHAPTER, data=payload, headers=self.headers, files=files
        )
        print(response.url)
        if not response.ok:
            print(response.json())
            raise Exception("Create chapter failed!")
        time.sleep(1)
        return response.json()["data"]["id"]

    def begin_transfer(self):
        data = {}
        refresh_token = self.login()
        # get list story in folder storages
        list_story = os.listdir(os.path.basename(PATH_STORAGE))
        for basename in list_story:
            # Get folder story
            folder_story = self.get_folder_comic(basename)
            # Get list json chapter
            list_json_chapter = os.listdir(folder_story)
            list_json_chapter = [
                file for file in list_json_chapter if file.startswith("chapter")
            ]
            list_json_chapter = sorted(
                list_json_chapter, key=lambda x: int(x.split("_")[1].split(".")[0])
            )
            total_chapter = len(list_json_chapter)
            file_save = "upload.json"
            file_save = os.path.join(folder_story, file_save)

            # Get path thumbnail and cover
            path_thumbnail = os.path.join(folder_story, "thumbnail.jpg")
            path_cover = os.path.join(folder_story, "cover.jpg")
            # load file info.json
            with open(os.path.join(folder_story, "info.json"), "r") as f:
                story_data = json.load(f)
            story_data["thumbnail"] = path_thumbnail
            # Check cover.jpg is not exist
            if not os.path.exists(path_cover):
                story_data["cover"] = None
            else:
                story_data["cover"] = path_cover
            # Check file save is exist then load
            if os.path.exists(file_save):
                with open(file_save, "r") as f:
                    story = json.load(f)
                # check story is upload complete
                if story["total_chapter"] == story["total_upload"]:
                    print("Story is upload complete!")
                    continue
            else:
                story_id = self.create_story(story_data)
                with open(file_save, "w") as f:
                    json.dump(
                        {
                            "story_id": story_id,
                            "total_chapter": total_chapter,
                            "total_upload": 0,
                        },
                        f,
                        indent=4,
                    )
                story = {
                    "story_id": story_id,
                    "total_chapter": total_chapter,
                    "total_upload": 0,
                }
            # Get story id
            story_id = story["story_id"]
            # Get total chapter
            total_chapter = story["total_chapter"]
            # Get total upload
            total_upload = story["total_upload"]
            # Sort list json chapter
            for index, chapter in enumerate(
                list_json_chapter[total_upload:], start=total_upload
            ):
                if index > self.number_chapter:
                    break
                path_json_chapter = os.path.join(folder_story, chapter)
                with open(path_json_chapter, "r") as f:
                    data_chapter = json.load(f)
                # Create chapter
                data_chapter["thumbnail"] = path_thumbnail
                chapter_id = self.create_chapter(data_chapter, story_id, index + 1)
                # Update total upload
                total_upload += 1
                # Update file save
                with open(file_save, "w") as f:
                    json.dump(
                        {
                            "story_id": story_id,
                            "total_chapter": total_chapter,
                            "total_upload": total_upload,
                        },
                        f,
                        indent=4,
                    )
                print(f"Upload chapter {index + 1}/{total_chapter} success!")
            print("Upload all chapter success!")
