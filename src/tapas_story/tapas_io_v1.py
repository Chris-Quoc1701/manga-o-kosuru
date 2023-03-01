import json
import os
import random
import string
import time
from dataclasses import asdict, dataclass

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from requests_html import HTMLSession

NAME_ROOT = "storages"
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(CURRENT_PATH, NAME_ROOT)


@dataclass
class Story:
    title: str
    url: str
    thumbnail: str
    cover: str
    summary: str
    warning_content: str
    data_series_id: str
    total_chapter: int
    total_get_chapter: int
    genres: list


@dataclass
class Chapter:
    title: str
    url: str
    content: str


def remove_punctuation(text: str) -> str:
    # Remove all punctuation in text and return text
    new_text = text.translate(str.maketrans("", "", string.punctuation)).strip().lower()
    # Remove double space
    new_text = " ".join(new_text.split())
    print(new_text)
    return new_text


class ScraperTapasStory:
    def __init__(
        self, email: str, password: str, number_page: int, number_chapter: int
    ):
        self.session = HTMLSession()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",  # noqa
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "cn-CN,zh;q=0.9,en;q=0.8",
            "referer": "tapas.io",
            "DNT": "1",
            # "Cookie": "_ga_556R6VEF8S=GS1.1.1677508226.2.1.1677508664.59.0.0; _ga=GA1.2.103204514.1675872139; AWSALB=PB0gVU4kPKEFx7TxxWE0AI3JFkD+ORgTapHOxH71QnQXeo6hWMekw5aZrKSdPIpM7qlS8xBJ0SMeLhZ5YjTWfeufB/cka20Sa8CFlTiJo9BJFNugf6nMMG1lD3XX; AWSALBCORS=PB0gVU4kPKEFx7TxxWE0AI3JFkD+ORgTapHOxH71QnQXeo6hWMekw5aZrKSdPIpM7qlS8xBJ0SMeLhZ5YjTWfeufB/cka20Sa8CFlTiJo9BJFNugf6nMMG1lD3XX; JSESSIONID=33CC5A1E48C619AA2CA551F262FECB14; _scid=abbaa911-bfa1-4bdc-b84f-1c3912952108; ab.storage.deviceId.afcaafae-e8f9-4378-b159-9ae951b90f26=%7B%22g%2…2zbbi_rmMmdVHpaQ1alr2; _cpc_=bmhveGdhdW1vdHNhY2gyMDE2JTQwZ21haWwuY29tOjE2Nzg3MTgyNjIxNjg6MzA3MjFmMTk0OGU2MTgxMjE3MGU1NjcwY2JjZjViYjM; P_SIVERSION=13204312-1677495892396; ab.storage.userId.afcaafae-e8f9-4378-b159-9ae951b90f26=%7B%22g%22%3A%2213204312%22%2C%22c%22%3A1677508664466%2C%22l%22%3A1677508664466%7D; ab.storage.sessionId.afcaafae-e8f9-4378-b159-9ae951b90f26=%7B%22g%22%3A%224d97f7ac-81ab-3f49-6539-6bdc7ec52a75%22%2C%22e%22%3A1677510465102%2C%22c%22%3A1677508664467%2C%22l%22%3A1677508665102%7D; _gat=1",
        }
        self.email = email
        self.password = password
        self.number_page = number_page
        self.number_chapter = number_chapter

    def login(self):
        url_login = "https://tapas.io/"
        payload = {
            "email": self.email,
            "password": self.password,
        }
        response = self.session.post(
            url_login,
            data=payload,
            headers=self.headers,
        )
        print(f"Login status: {response.status_code}")
        time.sleep(10)
        self.cookies = response.cookies
        print(self.cookies)

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

    def create_folder_story(self, story: Story):
        story_name = remove_punctuation(story.title).replace(" ", "_")
        path_story = os.path.join(ROOT_PATH, story_name)
        if not os.path.exists(path_story):
            os.mkdir(path_story)
            print(f"Create folder {path_story}")
        return path_story

    def get_list_story(self, page: int = 1) -> list:
        url = f"https://tapas.io/novels?b=POPULAR&g=0&f=NONE&pageNumber={page}&pageSize=20&since=&"
        response = self.session.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"Error when get list story: {response.status_code}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")

        # List story "li.list__item list__item--row js-list-item"
        list_story = soup.find_all(
            "li", {"class": "list__item list__item--row js-list-item"}
        )
        list_url = []
        for story in list_story:
            # get url story in "a.row-item js-fb-tracking"
            url = story.find("a", {"class": "row-item js-fb-tracking"})["href"]
            full_url = f"https://tapas.io{url}/info/"
            list_url.append(full_url)
        print("Get list story success ", len(list_url))
        return list_url

    def get_information_story(self, url: str) -> Story:
        response = self.session.get(url, headers=self.headers)
        print(f"Get information story: {url}")
        if response.status_code != 200:
            print(f"Error when get information story: {response.status_code}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        containers = soup.select_one(".section-sub-wrapper")
        try:
            cover_url = containers.select_one("info info--top js-top-banner").attrs[
                "style"
            ]
            cover = cover_url[cover_url.index("https") : cover_url.index(");")]
        except:
            cover = ""
        try:
            # container genres "div.info-detail js-top-banner-inner"
            genres = containers.select_one(
                "div.info-detail.js-top-banner-inner"
            ).find_all("a")
            genres = [genre.text for genre in genres]
            print(genres)
        except Exception as e:
            print(e)
            genres = []

        try:
            name = containers.select_one(".title").getText()
            thumbnail_url = containers.findChild("img")["src"]
            description = soup.select_one(".description__body").getText()
            href_id = containers.select_one(
                "#page-wrap > div > div.section-wrapper > div > section.section.section--left > div:nth-child(2) > div.info.info--bottom > div.info__right > div.stats > a.stats__row.js-subscribe-cnt.js-tooltip"
            ).attrs["href"]
            extract_id = href_id[href_id.index("=") + 1 :]  # noqa
            total_chapter = soup.find("p", class_="episode-cnt").text
            total_chapter = int(remove_punctuation(total_chapter).split(" ")[0])
        except Exception as e:
            print(e)
            return None
        story = Story(
            title=name,
            cover=cover,
            thumbnail=thumbnail_url,
            summary=description,
            warning_content="everyone",
            data_series_id=extract_id,
            url=url,
            total_chapter=total_chapter,
            total_get_chapter=0,
            genres=genres,
        )
        print(story)
        return story

    def get_list_chapter(self, story: Story, max_limit: int, page: int) -> list:
        chapters = []
        url_api = f"https://tapas.io/series/{story.data_series_id}/episodes?page={page}&max_limit={max_limit}"
        response = self.session.get(url_api, headers=self.headers)
        if response.status_code != 200:
            print(f"Error when get list chapter: {response.status_code}")
            return []
        html_doc = response.json()
        for item in html_doc["data"]["episodes"]:
            if item["free"] is True:
                chapters.append(item["id"])
        print(f"total chapters: {len(chapters)}")
        return chapters

    def get_content_chapter(self, episode_id: int) -> Chapter:
        url_content = f"https://tapas.io/episode/{episode_id}"
        try:
            response = self.session.get(url_content, headers=self.headers)
            if response.status_code != 200:
                print(f"Error when get content chapter: {response.status_code}")
                return ""
            print(response.links)
            print(f"Get content chapter: {url_content}, status: {response.status_code}")
            soup = BeautifulSoup(response.text, "html.parser")
            try:
                article = soup.select_one(".ep-epub-content").getText()
            except:
                article = soup.select("article.viewer__body p")
                for p in article:
                    content.append(p.text.strip())
                article = "".join(content)
            title = (
                soup.select_one("div.viewer__header").select_one("p.title").getText()
            )
            chapter = Chapter(
                title=title,
                content=article,
                url=url_content,
            )
        except:
            content = []
            # use playwright to get content
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=True)
                context = browser.new_context(
                    extra_http_headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                        "Cookie": "_ga_556R6VEF8S=GS1.1.1677508226.2.1.1677508664.59.0.0; _ga=GA1.2.103204514.1675872139; AWSALB=PB0gVU4kPKEFx7TxxWE0AI3JFkD+ORgTapHOxH71QnQXeo6hWMekw5aZrKSdPIpM7qlS8xBJ0SMeLhZ5YjTWfeufB/cka20Sa8CFlTiJo9BJFNugf6nMMG1lD3XX; AWSALBCORS=PB0gVU4kPKEFx7TxxWE0AI3JFkD+ORgTapHOxH71QnQXeo6hWMekw5aZrKSdPIpM7qlS8xBJ0SMeLhZ5YjTWfeufB/cka20Sa8CFlTiJo9BJFNugf6nMMG1lD3XX; JSESSIONID=33CC5A1E48C619AA2CA551F262FECB14; _scid=abbaa911-bfa1-4bdc-b84f-1c3912952108; ab.storage.deviceId.afcaafae-e8f9-4378-b159-9ae951b90f26=%7B%22g%2…2zbbi_rmMmdVHpaQ1alr2; _cpc_=bmhveGdhdW1vdHNhY2gyMDE2JTQwZ21haWwuY29tOjE2Nzg3MTgyNjIxNjg6MzA3MjFmMTk0OGU2MTgxMjE3MGU1NjcwY2JjZjViYjM; P_SIVERSION=13204312-1677495892396; ab.storage.userId.afcaafae-e8f9-4378-b159-9ae951b90f26=%7B%22g%22%3A%2213204312%22%2C%22c%22%3A1677508664466%2C%22l%22%3A1677508664466%7D; ab.storage.sessionId.afcaafae-e8f9-4378-b159-9ae951b90f26=%7B%22g%22%3A%224d97f7ac-81ab-3f49-6539-6bdc7ec52a75%22%2C%22e%22%3A1677510465102%2C%22c%22%3A1677508664467%2C%22l%22%3A1677508665102%7D; _gat=1",
                    }
                )
                page = context.new_page()
                page.set_default_timeout(9000000)
                page.goto(url_content, timeout=9000000)
                page.wait_for_load_state("load")
                # stop loading page when html loaded
                time.sleep(5)
                page.evaluate("window.stop()")
                html_doc = page.content()

                browser.close()
                soup = BeautifulSoup(html_doc, "html.parser")
                # content "article.viewer__body p"
                article = soup.select("article.viewer__body p")
                for p in article:
                    content.append(p.text.strip())

                title = (
                    soup.select_one("div.viewer__header")
                    .select_one("p.title")
                    .getText()
                )
                chapter = Chapter(
                    title=title,
                    content="".join(content),
                    url=url_content,
                )
        return chapter

    def begin_suffer(self):
        self.login()
        print(self.headers)
        list_url = self.get_list_story(page=6)
        for url in list_url:
            story = self.get_information_story(url)
            file_info = "info.json"
            path_story = self.create_folder_story(story)
            if os.path.exists(f"{path_story}/{file_info}"):
                with open(f"{path_story}/{file_info}", "r") as f:
                    story.__dict__ = json.load(f)
            else:
                with open(f"{path_story}/{file_info}", "w") as f:
                    json.dump(story.__dict__, f, indent=4)
            self.download_image(
                url=story.cover, path=path_story, filename="cover.jpg"
            ) if story.cover else None
            self.download_image(
                url=story.thumbnail, path=path_story, filename="thumbnail.jpg"
            ) if story.thumbnail else None
            if story is None:
                continue
            list_chapter = self.get_list_chapter(
                story=story, max_limit=20, page=self.number_page
            )
            index_chapter = story.total_get_chapter
            for index, chapter_id in enumerate(
                list_chapter[story.total_get_chapter :], start=index_chapter
            ):
                if index > self.number_chapter:
                    break
                filename = f"chapter_{index + 1}.json"
                # check chapter is exist
                if os.path.exists(f"{path_story}/{filename}"):
                    continue
                chapter = self.get_content_chapter(chapter_id)
                # write json file
                with open(f"{path_story}/{filename}", "w") as f:
                    json.dump(chapter.__dict__, f, indent=4)
                print(f"Write {filename} success")
                # update index chapter
                story.total_get_chapter = index + 1
                with open(f"{path_story}/{file_info}", "w") as f:
                    json.dump(story.__dict__, f, indent=4)
                # sleep 2s
                time.sleep(2)
