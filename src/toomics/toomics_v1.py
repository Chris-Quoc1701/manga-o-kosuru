import concurrent.futures
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from requests_html import HTMLSession
from utils import combine_image


@dataclass
class Toon:
    id: int
    name: str
    genres: list
    summary: str
    warning_content: str
    url_background: str
    url_foreground: str
    path_thumbnail: str
    path_cover: str
    chapters: list
    total_chapter: int
    total_get: int


@dataclass
class Chapter:
    name: str
    path_thumbnail: str
    number: int
    images: list
    total_image: int
    total_get: int


# remove punctuation
def remove_punctuation(text):
    punctuation = """!()-[]{};:'"\,<>./?@#$%^&*_~"""
    for char in text:
        if char in punctuation:
            text = text.replace(char, "")
    return text


# create folder store data
def create_folder_data() -> str:
    name = "storages"
    if not os.path.exists(name):
        os.mkdir(name)
        print("Folder data created")
    else:
        print("Folder data already exists")
    path = os.path.join(os.getcwd(), name)
    return path


# create folder store toon
def create_folder_toon(name: str) -> str:
    name = (remove_punctuation(name)).replace(" ", "_").lower().strip()
    try:
        os.mkdir(f"storages/{name}")
        print(f"Folder {name} created")
    except FileExistsError:
        print(f"Folder {name} already exists")
    path = os.path.join(os.getcwd(), f"storages/{name}")
    return path


# change format cookies
def change_format_cookies(toon_id: str) -> str:
    cookies = f"_ga_XCVE4C6ZQR=GS1.1.1672389190.8.1.1672392429.0.0.0; content_lang=en; GTOOMICScisession=a%3A11%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2298b22529a14a7e94f7ad0cad96911f6e%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A14%3A%2215.235.156.228%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A70%3A%22Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A108.0%29+Gecko%2F20100101+Firefox%2F108.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1672392398%3Bs%3A11%3A%22keep_cookie%22%3Bs%3A1%3A%221%22%3Bs%3A7%3A%22display%22%3Bs%3A1%3A%22A%22%3Bs%3A11%3A%22family_mode%22%3Bs%3A1%3A%22Y%22%3Bs%3A8%3A%22ext_name%22%3Bs%3A5%3A%22email%22%3Bs%3A4%3A%22lang%22%3Bs%3A7%3A%22english%22%3Bs%3A8%3A%22lang_seg%22%3Bs%3A2%3A%22en%22%3Bs%3A6%3A%22viewer%22%3Bs%3A1%3A%22S%22%3B%7Ddf6a7c22fc6bf3598ef8bf987788c0fed19f821f; GTOOMICS_ext_id=t.1.1672280962.63acfb820b609; GTOOMICSpid_join=pid%3DdefaultPid%26subpid%3DdefaultSubPid%26subpid2%3DdefaultSubPid%26subpid3%3DdefaultSubPid%26channel%3DdefaultChannel; GTOOMICSpid_last=pid%3DdefaultPid%26subpid%3DdefaultSubPid%26subpid2%3DdefaultSubPid%26subpid3%3DdefaultSubPid%26channel%3DdefaultChannel; _gcl_au=1.1.1950241583.1672280964; _ga=GA1.2.612977837.1672280964; __lt__cid=8843e139-d754-45d0-828e-263e2c3de937; g4_client_id=612977837.1672280964; _tt_enable_cookie=1; _ttp=nbMv27AtNVOSZBhWNpEjzjOzlU5; _scid=07f6b93c-52bc-45c5-875f-57231c4a944f; _ts_yjad=1672280965150; _gid=GA1.2.700814670.1672280966; _sctr=1|1672246800000; _fbp=fb.1.1672280966758.843370594; GTOOMICSremember_id=a%3A2%3A%7Bs%3A7%3A%22user_id%22%3Bs%3A19%3A%22chimzase5%40gmail.com%22%3Bs%3A3%3A%22key%22%3Bs%3A32%3A%2298969670f6a98223124e0e2946d165c5%22%3B%7D; GTOOMICSlogin_chk_his=Y; GTOOMICSslave=sdb3; GTOOMICScountry=country%3DUS%26time_zone%3D-07%3A00; GTOOMICSpidIntro=1; backurl=https%3A//toomics.com/en/webtoon/episode/toon/{toon_id}; first_open_episode=loading_bg; __lt__sid=fbdd6292-42d407b6; GTOOMICSsearch_cookie_en=%7B%22result%22%3A%5B%221695%22%5D%2C%22search%22%3A%22High%22%7D; GTOOMICSsearch_log=%7B%22keyword%22%3A%22High%22%7D; GTOOMICSreread_list_toon={toon_id}; GTOOMICSfirst_reading_toon=2022-12-30+18%3A27%3A07"  # noqa
    return cookies


class CheckIp:
    def __init__(self):
        self.folder = create_folder_data()
        self.session = HTMLSession()
        # Header for get information
        self.headers_1 = {
            "Host": "toomics.com",
            "Connection": "keep-alive",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="93", "Google Chrome";v="93"',  # noqa
            "sec-ch-ua-mobile": "?0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",  # noqa
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",  # noqa
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://toomics.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            # "Cookie": "_ga_XCVE4C6ZQR=GS1.1.1672416701.12.1.1672425691.0.0.0; content_lang=en; GTOOMICScisession=a%3A11%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%22a139f92be6c150723bf06967b402f3df%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A14%3A%2215.235.156.228%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A70%3A%22Mozilla%2F5.0+%28X11%3B+Linux+x86_64%3B+rv%3A108.0%29+Gecko%2F20100101+Firefox%2F108.0%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1672425674%3Bs%3A11%3A%22keep_cookie%22%3Bs%3A1%3A%221%22%3Bs%3A7%3A%22display%22%3Bs%3A1%3A%22A%22%3Bs%3A11%3A%22family_mode%22%3Bs%3A1%3A%22Y%22%3Bs%3A8%3A%22ext_name%22%3Bs%3A5%3A%22email%22%3Bs%3A4%3A%22lang%22%3Bs%3A7%3A%22english%22%3Bs%3A8%3A%22lang_seg%22%3Bs%3A2%3A%22en%22%3Bs%3A6%3A%22viewer%22%3Bs%3A1%3A%22S%22%3B%7D7b6562df9ad3044b03fe0699ad3e053bf5dcb5af; GTOOMICS_ext_id=t.1.1672280962.63acfb820b609; GTOOMICSpid_join=pid%3DdefaultPid%26subpid%3DdefaultSubPid%26subpid2%3DdefaultSubPid%26subpid3%3DdefaultSubPid%26channel%3DdefaultChannel; GTOOMICSpid_last=pid%3DdefaultPid%26subpid%3DdefaultSubPid%26subpid2%3DdefaultSubPid%26subpid3%3DdefaultSubPid%26channel%3DdefaultChannel; _gcl_au=1.1.1950241583.1672280964; _ga=GA1.2.612977837.1672280964; __lt__cid=8843e139-d754-45d0-828e-263e2c3de937; g4_client_id=612977837.1672280964; _tt_enable_cookie=1; _ttp=nbMv27AtNVOSZBhWNpEjzjOzlU5; _scid=07f6b93c-52bc-45c5-875f-57231c4a944f; _ts_yjad=1672280965150; _gid=GA1.2.700814670.1672280966; _sctr=1|1672246800000; _fbp=fb.1.1672280966758.843370594; GTOOMICSremember_id=a%3A2%3A%7Bs%3A7%3A%22user_id%22%3Bs%3A19%3A%22chimzase5%40gmail.com%22%3Bs%3A3%3A%22key%22%3Bs%3A32%3A%229ed30ff8e3b59910cb1391d4f97dae70%22%3B%7D; GTOOMICSlogin_chk_his=Y; first_open_episode=loading_bg; GTOOMICSslave=sdb1; GTOOMICScountry=country%3DUS%26time_zone%3D-07%3A00; GTOOMICSpidIntro=1; backurl=https%3A//toomics.com/en/webtoon/episode/toon/2271; __lt__sid=fbdd6292-5ba54dfb; GTOOMICSvip_chk=email; GTOOMICSlogin_attempt=Y; _gat_UA-114646527-1=1; GTOOMICSreread_list_toon=2271; GTOOMICSsecond_reading_toon=2022-12-31+03%3A32%3A20"
        }
        # Header for download image gt 2
        self.headers_2 = {
            "Host": "toon-g2.toomics.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
            "Accept": "image/avif,image/webp,*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Proxy-Authorization": "Basic YXV0b3Byb3h5X0VuUFlaU1c3Om1XaUtSbzhaa1A=",
            "Connection": "keep-alive",
            "Referer": "https://toomics.com/",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers",
        }
        # Header for download image gt 1
        self.headers_3 = {
            "Host": "toon-g1.toomics.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
            "Accept": "image/avif,image/webp,*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Proxy-Authorization": "Basic YXV0b3Byb3h5X0VuUFlaU1c3Om1XaUtSbzhaa1A=",
            "Connection": "keep-alive",
            "Referer": "https://toomics.com/",
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers",
        }

    def check_ip(self) -> None:
        # Check ip
        response = self.session.get(
            "http://edns.ip-api.com/json",
        )
        infor = response.json()["dns"]
        headers = response.headers
        print(f"IP: {infor['ip']} \nGEO: {infor['geo']} \nHEADERS: {headers}")


class ScrapeToomics(CheckIp):
    def __init__(
        self, email: str, password: str, number_chapter: int = 0, mature: bool = False
    ):
        super().__init__()
        self.email = email
        self.password = password
        self.storage = create_folder_data()
        self.number_chapter = number_chapter
        self.mature = mature

    def parser_get_all_id_18(self, html) -> None:
        soup = BeautifulSoup(html, "html.parser")
        ids = []
        ids_2 = []
        container = soup.select("div.visual > a")
        for item in container:
            warning = item.select_one("p.ico_19plus")
            if warning:
                href = item.attrs["href"]
                id_ = href.split("/")[-1]
                name = item.select_one("h4.title").text
                ids.append(id_)
            else:
                href = item.attrs["href"]
                id_ = href.split("/")[-1]
                name = item.select_one("h4.title").text
                ids_2.append(id_)
        if self.mature:
            ids.sort()
            return ids
        else:
            ids_2.sort()
            return ids_2

    def parser_get_information(self, html):
        soup = BeautifulSoup(html, "html.parser")

        # Get information toon
        thumbnail = soup.select_one("meta[property='og:image']").attrs["content"]
        container = soup.find("section", class_="ep-header_ch")
        id_toon = container.select_one("a.btn_favorites_lp ").attrs["data-option"]
        url_background = container.select_one("header.ep-cover_ch").attrs["style"]
        url_foreground = container.select_one("div.inner_ch").attrs["style"]
        name = container.select_one("h1#episode_title").text
        summary = container.select_one("h2").text
        genre = (
            container.select_one("span.type")
            .text.strip()
            .replace("\n", "")
            .replace(" ", "")
            .split("/")
        )
        # extract url from url_background and url_foreground
        url_background = url_background[
            url_background.index("https") : url_background.index(")")
        ]
        url_foreground = url_foreground[
            url_foreground.index("https") : url_foreground.index(")")
        ]
        chapters = []
        container_chapter = soup.select("li.normal_ep")
        for chapter_id in container_chapter:
            # onclick="Webtoon.chkec(this);location.href='/en/webtoon/detail/code/100874/ep/0/toon/5062'"
            ref = chapter_id.select_one("a").attrs["onclick"].split("'")[1]
            chapters.append(ref)
        toon = Toon(
            id=id_toon,
            name=name,
            genres=genre,
            summary=summary,
            url_background=url_background,
            url_foreground=url_foreground,
            path_thumbnail=thumbnail,
            path_cover=None,
            chapters=chapters,
            total_chapter=len(chapters),
            total_get=0,
            warning_content="mature" if self.mature else "everyone",
        )
        return toon

    def create_folder_toon(self, toon_id: str) -> str:
        # tree storage/toon_name
        new_name = f"{toon_id}"
        # check if folder exist
        path = os.path.join(self.storage, new_name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def save_json(self, toon: Toon, path_toon: str) -> None:
        # save json
        path_json = os.path.join(path_toon, "toon.json")
        with open(path_json, "w") as file:
            json.dump(toon.__dict__, file, indent=4)

    def save_json_chapter(self, chapter: Chapter, path: str) -> None:
        # save json
        path_json = os.path.join(path, "chapter.json")
        with open(path_json, "w") as file:
            json.dump(chapter.__dict__, file, indent=4)

    def download_thumb_cover(self, url, name, path_save) -> str:
        type_image = url.split(".")[-1][:3]
        # check if not url return false
        if url.startswith("http") is False:
            return False
        name_image = f"{name}.{type_image}"
        path = os.path.join(path_save, name_image)
        if os.path.exists(path):
            return path
        else:
            response = self.session.get(url=url, stream=True)
            with open(path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            return path

    def parser_content(self, html):
        images = []
        soup = BeautifulSoup(html, "html.parser")
        thumbnail = soup.select_one("meta[property='og:image']").attrs["content"]
        info = soup.select_one("div.viewer-title")
        # name chapter inside info is a tag with attribute title="List"
        name = info.find("a", title="List").getText(separator=" ")
        # number chapter inside info is em tag
        number = info.select_one("em").text
        container_image = soup.select("div.viewer-imgs")
        for block in container_image:
            for image in block.select("img"):
                if "src" in image.attrs:
                    if ".com" in image.attrs["src"]:
                        images.append(image.attrs["src"])
                elif "data-src" in image.attrs:
                    if ".com" in image.attrs["data-src"]:
                        images.append(image.attrs["data-src"])
                else:
                    print("Not found url image")
        chapter = Chapter(
            name=name,
            path_thumbnail=thumbnail,
            number=number,
            images=images,
            total_image=len(images),
            total_get=0,
        )
        return chapter

    def download_image(
        self, url: str, path_child: str, name: str, toon_id: str
    ) -> None:
        print(f"Begin download {name}")
        if url.endswith(".jpg"):
            if "toon-g2" in url:
                self.headers_2["Cookie"] = change_format_cookies(toon_id=toon_id)
                print("Use header 2 with toon-g2")
                # get response with timeout 2 minutes
                response = self.session.get(
                    url,
                    headers=self.headers_2,
                    # auth=self.auth,
                    # proxies=self.proxies,
                    timeout=120,
                )
            else:
                self.headers_3["Cookie"] = change_format_cookies(toon_id=toon_id)
                print("Use header 3 with toon-g1")
                response = self.session.get(
                    url,
                    headers=self.headers_3,
                    # auth=self.auth,
                    # proxies=self.proxies,
                    timeout=120,
                )
        else:
            if "toon-g2" in url:
                self.headers_2["Cookie"] = change_format_cookies(toon_id=toon_id)
                response = self.session.get(
                    url,
                    headers=self.headers_2,
                    # auth=self.auth,
                    # proxies=self.proxies,
                    timeout=120,
                )
                print("Use header 2 with no png and toon-g2")
            else:
                self.headers_3["Cookie"] = change_format_cookies(toon_id=toon_id)
                response = self.session.get(
                    url,
                    headers=self.headers_3,
                    # auth=self.auth,
                    # proxies=self.proxies,
                    timeout=120,
                )
                print("Use header 3 with no png and toon-g1")
        print(response.status_code, response.url)
        if response.status_code != 200:
            print("Something wrong please check again")
            logging.error("Something wrong please check again")
            return {}
        time.sleep(4)
        with open(f"{path_child}/{name}.jpg", "wb") as f:
            f.write(response.content)
        path = f"{path_child}/{name}.jpg"
        print(f"Download {name} success image in {path_child}")
        time.sleep(5)
        return True

    # function create a thread pool with 4 workers
    def multi_thread(self, urls: list, path_chapter: str, toon_id: str) -> list:
        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_url = {
                # User enumberate to get index of list
                executor.submit(
                    self.download_image, url, path_chapter, f"{index}", toon_id
                ): url
                for index, url in enumerate(urls)
            }
            time.sleep(6)
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                time.sleep(6)
                return future.result()

    def suffer_comic(self):
        with sync_playwright() as p:
            browser = p.firefox.launch(
                headless=True,
            )
            # Check storage state is exist
            if os.path.exists("storage_state_pre_2.json"):
                context = browser.new_context(
                    extra_http_headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    },
                    storage_state="storage_state_pre_2.json",
                )
            else:
                context = browser.new_context(
                    extra_http_headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    },
                )
            page = context.new_page()
            page.set_default_timeout(9000000)

            # Logout first then login
            try:
                page.goto(
                    "https://toomics.com/en/auth/logout",
                    wait_until="networkidle",
                    timeout=9000000,
                )
            except Exception as e:
                print(f"Logout error {e}")
            page.goto(
                "https://toomics.com/",
                wait_until="networkidle",
                timeout=9000000,
            )
            try:
                button = page.click(selector="p.login")
                if button:
                    button.click()
                page.fill(selector="input#user_id", value=self.email)
                page.fill(selector="input#user_pw", value=self.password)
                page.click("#login_fieldset > button:nth-child(5)", click_count=1)
                time.sleep(2)
            except Exception as e:
                print(f"Login error {e}")
                pass
            page.wait_for_selector("h5.my", state="visible")
            show = page.query_selector("h5.my")
            print("open")
            if show:
                show.click(click_count=5, delay=1000)
            time.sleep(2)
            # Check login success
            page.wait_for_selector("em.user", state="visible")
            name_user = page.query_selector("em.user")
            if not name_user or name_user.text_content() != self.email:
                print("Login fail")
            print("Login success with email: ", name_user.text_content())

            # Enable Verify Content
            page.click(selector="div.section_19plus >span")
            button_verify = page.query_selector("button.button_yes")
            if button_verify:
                button_verify.click()
                print("Enable Verify Content")
            time.sleep(2)
            # Get all toon 18+
            page.goto(
                "https://toomics.com/en/webtoon/ranking",
                wait_until="networkidle",
                timeout=9000000,
            )
            # scroll to bottom page
            page.evaluate(
                """() => {
                window.scrollTo(0, document.body.scrollHeight);
                }"""
            )
            time.sleep(2)
            storage_state = page.context.storage_state(
                path="storage_state_pre_2.json",
            )
            html = page.content()
            toon_ids = self.parser_get_all_id_18(html)
            for toon_id in toon_ids:
                if os.path.exists(f"storages/{toon_id}"):
                    path_toon = f"storages/{toon_id}"
                    print(f"Folder {toon_id} is exist")
                    # load info.json
                    with open(f"storages/{toon_id}/toon.json", "r") as f:
                        toon = Toon(**json.load(f))
                else:
                    # Create folder toon
                    path_toon = self.create_folder_toon(toon_id=toon_id)
                    page.goto(
                        "https://toomics.com/",
                        wait_until="networkidle",
                        timeout=9000000,
                    )

                    # Direction to infor toon
                    url = f"https://toomics.com/en/webtoon/episode/toon/{toon_id}"
                    page.goto(
                        url,
                        wait_until="networkidle",
                        timeout=9000000,
                    )
                    time.sleep(2)
                    popup_login = page.is_visible("p.login")
                    if popup_login:
                        # fill password
                        page.fill(selector="input#user_id", value=self.email)
                        page.fill(selector="input#user_pw", value=self.password)
                        page.click(
                            "#login_fieldset > button:nth-child(5)", click_count=1
                        )
                        time.sleep(2)
                    # Get info toon
                    html = page.content()
                    toon = self.parser_get_information(html=html)
                    # Download thumbnail and cover
                    toon.path_thumbnail = self.download_thumb_cover(
                        name="thumbnail", url=toon.path_thumbnail, path_save=path_toon
                    )
                    back_ground = self.download_thumb_cover(
                        name="cover_background",
                        url=toon.url_background,
                        path_save=path_toon,
                    )
                    fore_ground = self.download_thumb_cover(
                        name="cover_foreground",
                        url=toon.url_foreground,
                        path_save=path_toon,
                    )
                    toon.path_cover = combine_image(
                        back=back_ground, front=fore_ground, path_save=path_toon
                    )
                    # Create file info.json
                    self.save_json(toon=toon, path_toon=path_toon)
                # Check toon is already Completed
                if toon.total_chapter == toon.total_get:
                    print(f"Completed toon {toon.name}")
                    continue
                # Loaded index chapter
                index_chapter = toon.total_get
                chapters = toon.chapters[index_chapter:]
                # Get all chapter of toon
                for index, chapter_url in enumerate(chapters, start=index_chapter):
                    if index > self.number_chapter:
                        break
                    url_content = f"https://toomics.com{chapter_url}"
                    folder_name = f"chapter_{index}"
                    # check path chapter exist in path toon and check chapter.json
                    path_chapter = os.path.join(path_toon, folder_name)
                    if os.path.exists(path_chapter) and os.path.exists(
                        f"{path_chapter}/chapter.json"
                    ):
                        path_chapter = os.path.join(path_toon, folder_name)
                        # loaded data from chapter.json
                        try:
                            with open(f"{path_chapter}/chapter.json", "r") as f:
                                chapter = Chapter(**json.load(f))
                        except:
                            os.rmdir(path=path_chapter)
                            return None
                    else:
                        # Create folder chapter
                        os.mkdir(path_chapter) if not os.path.exists(
                            path_chapter
                        ) else None
                        # Get content chapter
                        page.goto(
                            url=url_content,
                            timeout=9000000,
                        )
                        # check url page is != url_content
                        if page.url != url_content:
                            print("Content is not free")
                            # remove folder chapter
                            os.rmdir(path_chapter)
                            # update total_get
                            toon.total_get = index
                            self.save_json(toon=toon, path_toon=path_toon)
                            break
                        # click button change to viewer/S
                        button = page.query_selector(".viewer-method-toggle")
                        if button:
                            # get attribute href of button
                            href = button.get_attribute("href")
                            if "viewer/S" in href:
                                button.click()
                                time.sleep(2)
                        page.wait_for_load_state("networkidle")
                        # scroll to bottom
                        page.evaluate(
                            "() => window.scrollTo(0, document.body.scrollHeight)"
                        )
                        # no load css
                        page.add_style_tag(content="* { display: none !important; }")
                        # get content html
                        html = page.content()
                        chapter = self.parser_content(html=html)
                        # Download thumbnail
                        chapter.path_thumbnail = self.download_thumb_cover(
                            name="thumbnail",
                            url=chapter.path_thumbnail,
                            path_save=path_chapter,
                        )
                        # save chapter.json
                        self.save_json_chapter(chapter=chapter, path=path_chapter)
                    # Check chapter is already Completed
                    if chapter.total_image == chapter.total_get:
                        print(f"Completed chapter {chapter.name}")
                        continue
                    # Loaded index image for continue download
                    # path_chapter = os.path.join(path_toon, folder_name)
                    index_image = chapter.total_get
                    images = chapter.images[index_image:]
                    # Download images multi thread
                    self.multi_thread(
                        urls=images, path_chapter=path_chapter, toon_id=toon_id
                    )
                    # Update total_get in chapter.json
                    chapter.total_get = chapter.total_image
                    self.save_json_chapter(chapter=chapter, path=path_chapter)
                    print(
                        f"Completed chapter {chapter.name} - {chapter.total_get}/{chapter.total_image}"
                    )
                    index_chapter += 1
                # Update total_get in info.json
                toon.total_get = index_chapter
                self.save_json(toon=toon, path_toon=path_toon)
                print(
                    f"Completed toon {toon.name} - {toon.total_get}/{toon.total_chapter}"
                )
            # Update storage_state.json
            storage_state = page.context.storage_state(
                path="storage_state_post_2.json",
            )
