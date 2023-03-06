import json
import os
import string
import time
from dataclasses import asdict, dataclass

import requests_html
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from requests_html import HTMLSession

NAME_ROOT = "storages"
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(CURRENT_PATH, NAME_ROOT)


@dataclass
class Comic:
    title: str
    url: str
    thumbnail: str
    chapters: list
    genres: list
    summary: str
    warnings_content: str = "everyone"
    total_chapters: int = 0
    total_download: int = 0


@dataclass
class Chapter:
    title: str
    url: str
    total_images: int = 0
    total_download: int = 0
    images: list = None


def remove_punctuation(text: str) -> str:
    # Remove all punctuation in text and return text
    new_text = text.translate(str.maketrans("", "", string.punctuation)).strip().lower()
    # Remove double space
    new_text = " ".join(new_text.split())
    print(new_text)
    return new_text


def check_storages_folder() -> None:
    # Check storages folder is exist
    if not os.path.exists(ROOT_PATH):
        os.mkdir(ROOT_PATH)
    return ROOT_PATH


class ScraperReadComicsOnline:
    def __init__(self, page_number: int, number_chapter: int):
        self.session = HTMLSession()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Content-Type": "text/html; charset=utf-8",
            "Content-Encoding": "gzip, deflate",
        }
        self.storages = (
            ROOT_PATH if os.path.exists(ROOT_PATH) else check_storages_folder()
        )
        self.page = page_number
        self.chapter = number_chapter

    def download_image(self, url: str, filename: str, path: str) -> str:
        # check thumbnail is exist
        if os.path.exists(f"{path}/{filename}"):
            return f"{path}/{filename}"
        # Download image
        re = self.session.get(url, stream=True, headers=self.headers)
        with open(f"{path}/{filename}", "wb") as f:
            for chunk in re.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        time.sleep(2)
        print(f"Download {filename} success")
        return f"{path}/{filename}"

    def create_folder_comic(self, comic_title: str) -> str:
        # Create folder "Storages/comic_title"
        new_title = remove_punctuation(comic_title).replace(" ", "_")
        path = os.path.join(self.storages, new_title)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def create_folder_chapter(self, path: str, chapter_title: str) -> str:
        # Create folder "Storages/genre/comic_title/chapter_title"
        path = os.path.join(path, chapter_title)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def save_progress_comic_json(self, path: str, comic: Comic) -> str:
        # Save progress comic to json file in "Storages/genre/comic_title/comic.json"
        path = os.path.join(path, "comic.json")
        # Convert comic object to dict
        comic_dict = asdict(comic)
        with open(path, "w") as f:
            json.dump(comic_dict, f, indent=4)
        return path

    def load_progress_comic_json(self, path: str) -> Comic:
        # Load progress comic from json file in "Storages/genre/comic_title/comic.json"
        path = os.path.join(path, "comic.json")
        with open(path, "r") as f:
            comic_dict = json.load(f)
        comic = Comic(**comic_dict)
        return comic

    def save_progress_chapter_json(self, path: str, chapter: Chapter) -> str:
        # Save progress chapter to json file in "Storages/genre/comic_title/chapter_title/chapter.json"
        path = os.path.join(path, "chapter.json")
        # Convert chapter object to dict
        chapter_dict = asdict(chapter)
        with open(path, "w") as f:
            json.dump(chapter_dict, f, indent=4)
        return path

    def load_progress_chapter_json(self, path: str) -> Chapter:
        # Load progress chapter from json file in "Storages/genre/comic_title/chapter_title/chapter.json"
        path = os.path.join(path, "chapter.json")
        with open(path, "r") as f:
            chapter_dict = json.load(f)
        chapter = Chapter(**chapter_dict)
        return chapter

    def create_comic_object(
        self,
        comic_title: str,
        comic_url: str,
        comic_thumbnail: str,
        comic_genres: list,
        chapters: list,
        comic_summary: str,
        total_chapters: int,
    ) -> Comic:
        # Create comic object
        comic = Comic(
            title=comic_title,
            url=comic_url,
            thumbnail=comic_thumbnail,
            chapters=[],
            genres=comic_genres,
            summary=comic_summary,
            warnings_content="everyone",
            total_chapters=total_chapters,
            total_download=0,
        )
        return comic

    def get_chapter_images(self, chapter_url: str) -> list:
        # Get all images in chapter
        param = "&readType=1#1"
        param_url = chapter_url + param
        with sync_playwright() as p:
            browser = p.firefox.launch(
                headless=True,
            )
            context = browser.new_context(
                extra_http_headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Cache-Control": "max-age=0",
                },
            )
            page = context.new_page()
            page.set_default_timeout(900000)
            page.set_default_navigation_timeout(900000)
            page.wait_for_load_state("networkidle")
            page.goto(param_url)
            # Step 1: Scroll to bottom 2 time of page to load all images
            time_ = 0
            while time_ < 3:
                # script for page scroll slowly every 1 second until page reach bottom of page
                page.evaluate("() => { window.scrollBy(0, window.innerHeight); }")
                time_ += 1
                time.sleep(1)
            # Step 2: Get all images in page
            soup = BeautifulSoup(page.content(), "html.parser")
            # Get all images in page "div.divImage"
            container = soup.find("div", {"id": "divImage"})
            images = container.find_all("img")
            # Get all images url
            image_urls = []
            for image in images:
                image_url = image["src"]
                image_urls.append(image_url)
            # Close browser
            browser.close()
        return image_urls

    def suffer_comic(self):
        session = HTMLSession()
        url = f"https://readcomiconline.li/ComicList/Newest?page={self.page}"
        r = session.get(
            url, headers=self.headers, timeout=10, allow_redirects=True, stream=True
        )
        if r.status_code == 200:
            print(f"Page {self.page} is working")
            print(r.status_code, r.url)
        else:
            print(f"Page {self.page} is not working")
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        # Get containers containing comic info with  "div.list-comic"
        comic_containers = soup.find("div", {"class": "list-comic"}).find_all(
            "div", {"class": "item"}
        )
        print(len(comic_containers))
        comic_urls = []
        for comic_container in comic_containers:
            comic_url = comic_container.find("a")["href"]
            print(comic_url)
            comic_urls.append(comic_url)

        for comic_url in comic_urls:
            print(f"Checking comic {comic_url} ...")
            combine_url = f"https://readcomiconline.li{comic_url}"
            r = self.session.get(combine_url, headers=self.headers)
            if r.status_code == 200:
                print(f"Comic {comic_url} is working")
            else:
                print(f"Comic {comic_url} is not working")
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            # Get container content with "div.bigBarContainer"
            comic_containers = soup.find_all("div", {"class": "bigBarContainer"})
            # Get title and url with "a.bigChar"
            comic_title = comic_containers[0].find("a", {"class": "bigChar"}).text
            comic_url = comic_containers[0].find("a", {"class": "bigChar"}).get("href")
            # get container <p>
            genres = []
            p_tags = comic_containers[0].find_all("p")
            for p in p_tags:
                a_genres = p.find_all("a")
                for a in a_genres:
                    if "Genre" in a.attrs["href"].split("/"):
                        genres.append(a.text)
                # Get summary with "p"
                if "Summary" in p.text:
                    summary = p.text

            # get Thumbnail "div#rightside"
            thumbnail = soup.find("div", {"id": "rightside"}).find("img").get("src")
            # table chapters "table.listing"
            table_chapters = soup.find("table", {"class": "listing"})
            # get all tr in table chapters
            trs = table_chapters.find_all("tr")
            # find a in trs/td
            chapters = []
            for tr in trs:
                td = tr.find("td")
                if not td:
                    continue
                a = td.find("a")
                href = a.get("href")
                chapter_title = a.text
                chapters.append({"title": chapter_title, "url": href})

            # get total chapters
            total_chapters = len(chapters)
            # Reverse chapters
            chapters = chapters[::-1]
            # create comic folder
            comic_folder = self.create_folder_comic(comic_title)
            # check if comic.json is exist in comic folder
            if not os.path.exists(os.path.join(comic_folder, "comic.json")):
                # create comic object
                comic = self.create_comic_object(
                    comic_title=comic_title,
                    comic_url=comic_url,
                    comic_thumbnail=thumbnail,
                    comic_summary=summary,
                    comic_genres=genres,
                    chapters=chapters,
                    total_chapters=total_chapters,
                )
                # save comic.json
                self.save_progress_comic_json(comic_folder, comic)
            else:
                # load comic.json
                comic = self.load_progress_comic_json(comic_folder)
            # check if comic is downloaded
            if comic.total_download == comic.total_chapters:
                print(f"Comic {comic.title} is downloaded")
                continue
            # check thumbnail is exist in comic folder
            if not os.path.exists(os.path.join(comic_folder, "thumbnail.jpg")):
                # download thumbnail
                url_thumbnail = f"https://readcomiconline.li{thumbnail}"
                self.download_image(
                    path=comic_folder, url=url_thumbnail, filename="thumbnail.jpg"
                )
            # load index chapter
            index_chapter = comic.total_download
            # get chapter url
            for number, chapter in enumerate(
                chapters[index_chapter:], start=index_chapter
            ):
                if number >= self.chapter:
                    print(f"Chapter {number + 1} is downloaded")
                    break
                chapter_url = f"https://readcomiconline.li{chapter['url']}"
                # get chapter title
                chapter_title = chapter["title"]
                # create chapter folder
                folder_name = f"chapter_{number + 1}"
                chapter_folder = self.create_folder_chapter(comic_folder, folder_name)
                # get chapter images
                chapter_images = self.get_chapter_images(chapter_url)
                # check if chapter_images is None
                if not chapter_images:
                    continue
                # get total images
                total_images = len(chapter_images)
                # check if chapter.json is exist in chapter folder
                if not os.path.exists(os.path.join(chapter_folder, "chapter.json")):
                    # create chapter object
                    chapter = Chapter(
                        title=chapter_title,
                        url=chapter_url,
                        images=chapter_images,
                        total_images=total_images,
                        total_download=0,
                    )
                    # save chapter.json
                    self.save_progress_chapter_json(chapter_folder, chapter)
                else:
                    # load chapter.json
                    chapter = self.load_progress_chapter_json(chapter_folder)
                # check if chapter is downloaded
                if chapter.total_download == chapter.total_images:
                    print(f"Chapter {chapter.title} is downloaded")
                    continue
                # load index image
                index_image = chapter.total_download
                # download images
                for order, image_url in enumerate(chapter_images[index_image:]):
                    # download image
                    self.download_image(
                        filename=f"{order}.jpg", url=image_url, path=chapter_folder
                    )
                    # update chapter
                    chapter.images.append(image_url)
                    chapter.total_download += 1
                    # save chapter.json
                    self.save_progress_chapter_json(chapter_folder, chapter)
                # update comic
                comic.total_download += 1
                # save comic.json
                self.save_progress_comic_json(comic_folder, comic)
                # sleep 1s
                time.sleep(1)
