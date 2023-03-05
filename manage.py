import os
import yaml
import argparse

FOLDER_SETTING = "general_config"

class Config:
    def __init__(self):
        self.config_yaml = {}
        self.config_yaml["GENRES_MANGA"] = {}
        self.config_yaml["MANGA"] = {}
        self.config_yaml["MANGA_CHAPTER"] = {}
        self.config_yaml["MANGA_MEDIA"] = {}
        self.config_yaml["GENRES_STORY"] = {}
        self.config_yaml["STORY"] = {}
        self.config_yaml["STORY_CHAPTER"] = {}
        self.config_yaml["LOGIN"] = {}
    
    def create_section_genre(self, args):
        # check args.genre is manga or story
        if args.genres_manga and args.id_genres:
            # update list of tuple genre [(genre_id, genre_name), ...]
            list_tuple_genre = list(zip((args.id_genres), args.genres_manga))
            self.config_yaml["GENRES_MANGA"]= list_tuple_genre

        if args.genres_story and args.id_genres:
            # update list of tuple genre [(genre_id, genre_name), ...]
            list_tuple_genre = list(zip((args.id_genres), args.genres_story))
            self.config_yaml["GENRES_STORY"]= list_tuple_genre

    def create_section_manga(self, args):
        if args.mangas:
            self.config_yaml["MANGA"]["manga_api"] = args.mangas
        if args.manga_chapter:
            self.config_yaml["MANGA_CHAPTER"]["manga_chapter_api"] = args.manga_chapter
        if args.manga_media:
            self.config_yaml["MANGA_MEDIA"]["manga_media_api"] = args.manga_media

    def create_section_story(self, args):
        if args.story:
            self.config_yaml["STORY"]["story_api"] = args.story
        if args.story_chapter:
            self.config_yaml["STORY_CHAPTER"]["story_chapter_api"] = args.story_chapter

    def create_section_login(self, args):
        if args.login:
            self.config_yaml["LOGIN"]["login_api"] = args.login

    def create_config_file(self, args):
        # check file config exist if not create new file else load file
        if not os.path.exists(FOLDER_SETTING):
            os.mkdir(FOLDER_SETTING)
        if not os.path.exists(os.path.join(FOLDER_SETTING, "config.yaml")):
            with open(os.path.join(FOLDER_SETTING, "config.yaml"), "w") as f:
                yaml.dump(self.config_yaml, f)
        else:
            with open(os.path.join(FOLDER_SETTING, "config.yaml"), "r") as f:
                self.config_yaml = yaml.load(f, Loader=yaml.FullLoader)

        # Start update config file
        self.create_section_genre(args)
        self.create_section_manga(args)
        self.create_section_story(args)
        self.create_section_login(args)

        # write config file
        with open(os.path.join(FOLDER_SETTING, "config.yaml"), "w") as f:
            yaml.dump(self.config_yaml, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create config file for first time run app",
        formatter_class=argparse.RawTextHelpFormatter,
        
    )
    parser.add_argument(
        "-h2",
        "--help2",
        action="help",
        default=argparse.SUPPRESS,
        help="""
        INTRODUCE HELP:
        "To create for first time or update config file, you need to run this file with --setup argument"
        -gm, --genres_manga: genres name manga
        -gs, --genres_story: genres name story
        -gid, --id_genres: genres id
        -m, --mangas: manga api
        -mc, --manga_chapter: manga chapter api
        -mm, --manga_media: manga media api
        -s, --story: story api
        -sc, --story_chapter: story chapter api
        -l, --login: login api
        ```Example: python manage.py --setup -gm genre_manga_1 genre_manga_2 -gid 1 2 -m manga_api -mc manga_chapter_api -mm manga_media_api -l login_api```
        Note that: 
            **-gm and -gs use with -gid and not use with each other**
        """,
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup config file",
    )
    parser.add_argument(
        "-gm",
        "--genres_manga",
        nargs="+",
        help="Genres name manga",
    )
    parser.add_argument(
        "-gs",
        "--genres_story",
        nargs="+",
        help="Genres name story",
    )
    parser.add_argument(
        "-gid",
        "--id_genres",
        nargs="+",
        help="Genres id", 
    )
    parser.add_argument(
        "-m",
        "--mangas",
        action="store",
        help="Manga api",
    )
    parser.add_argument(
        "-mc",
        "--manga_chapter",
        action="store",
        help="Manga chapter api",
    )
    parser.add_argument(
        "-mm",
        "--manga_media",
        action="store",
        help="Manga media api",
    )

    parser.add_argument(
        "-s",
        "--story",
        nargs="+",
        help="Story api",
    )
    parser.add_argument(
        "-sc",
        "--story_chapter",
        action="store",
        help="Story chapter api",
    )
    parser.add_argument(
        "-l",
        "--login",
        action="store",
        help="Login api",
    )
    args = parser.parse_args()


    config = Config()
    config.create_config_file(args)
