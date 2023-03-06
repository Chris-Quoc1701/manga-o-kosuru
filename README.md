# **Manga-o-kosuru Scrape and Transfer Data to API**

[![Python version](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Requests version](https://img.shields.io/badge/requests-2.28.0-blue.svg)](https://pypi.org/project/requests/) [![Playwright version](https://img.shields.io/badge/playwright-1.12.3-blue.svg)](https://pypi.org/project/playwright/) [![BeautifulSoup version](https://img.shields.io/badge/beautifulsoup4-4.9.3-blue.svg)](https://pypi.org/project/beautifulsoup4/) [![PyYAML version](https://img.shields.io/badge/pyyaml-5.4.1-blue.svg)](https://pypi.org/project/PyYAML/) [![pip version](https://img.shields.io/badge/pip-21.0.1-blue.svg)](https://pypi.org/project/pip/)

## Table of Contents

- [Introduction](#introduction)
    - This project is a manga scraper and transfer data to API 
- [Installation](#installation)
    - [Clone](#clone)
        > Clone this repo to your local machine using `git clone git@github.com:Chris-Quoc1701/manga-o-kosuru.git`
    - [Setup](#setup)
        > install python3.8 and create virtual environment

        >> activate virtual environment and install requirements with command `pip install -r requirements.txt`

### First time setup config file:
For the first time, you need to run the command `python manage.py --setup` to setup config file follow the instruction in the terminal or step by step below:

- **Step 1:** With Manga API, run the command `python manage.py --setup -gm genre_manga_1 genre_manga_2 -gid genre_id_1 genre_id_2 -m manga_api -mc manga_chapter_api -mm manga_media_api`

- **Step 2:** With Story API, run the command `python manage.py --setup -gs genre_story_1 genre_story_2 -gid genre_id_1 genre_id_2 -s story_api -sc story_chapter_api`

- **Step 3:** With Login API, run the command `python manage.py --setup -l login_api`

**Note:** Dont run the command `python manage.py --setup` again if you dont want to update the config file and -gm and -gs dont use with each other but both use with -gid

*This code above will create a config file. You can update the config file by running the command `python manage.py --setup` again with the same command above*


**Note:** You can run the command `python manage.py --help` to see the instruction in the terminal


### Run the project after setup config file:

- Every app must run, you must `cd to the app folder` and run file command `python command.py`
- You can run the command `python command.py --help` to see the instruction in the terminal
- 3 apps with same action in command line:
    - `--scrapte`: Scrapte data from website
    - `--transfer`: Transfer data to API

1. App **Readcomiconline**
    - **Step 1:** Run the command `python command.py --scrapte` to scrapte data from website

        - with argument `-c` or `--chapter` to how many chapter you want to scrapte
        - with argument `-p` or `--page` page number you want to scrapte
        
        > Example: `python command.py --scrapte -c 10 -p 1` 
        >> This command above will scrapte 10 chapter and get list comics in page 1

    - **Step 2:** Run the command `python command.py --transfer` to transfer data to API
        - with argument `-c` or `--chapter` to how many chapter you want to transfer
        - with argument `-E` or `--email` email for login to API
        - with argument `-P` or `--password` password for login to API

        > Example: `python command.py --transfer -c 10 -E email -P password`
        >> This command above will transfer 10 chapter and login to API with email and password

2. App **Toomics**
    - **Step 1:** Run the command `python command.py --scrapte` to scrapte data from website

        - with argument `-c` or `--chapter` to how many chapter you want to scrapte
        - with argument `-w` or `--warning` mean if exist warning the scraper will get all list toon 18+ or not
        - with argument `-ep` or `--email_premium` email for login to premium account of Toomics (Accept not premium account) **Require** 
        - with argument `-pp` or `--password_premium` password for login to premium account of Toomics (Accept not premium account) **Require**
        
        > Example: `python command.py --scrapte -c 10 -p 1` 
        >> This command above will scrapte 10 chapter and get list comics in page 1

    - **Step 2:** Run the command `python command.py --transfer` to transfer data to API
    
        - with argument `-c` or `--chapter` to how many chapter you want to transfer
        - with argument `-E` or `--email` email for login to API
        - with argument `-P` or `--password` password for login to API
    
        > Example: `python command.py --transfer -c 10 -E email -P password`
        >> This command above will transfer 10 chapter and login to API with email and password

3. App **Tapas.io**

    - **Step 1:** Run the command `python command.py --scrapte` to scrapte data from website

        - with argument `-c` or `--chapter` to how many chapter you want to scrapte
        - with argument `-p` or `--page` page number you want to scrapte
        - with argument `-ep` or `--email_premium` email for login to premium account of Tapas.io (Accept not premium account) **Require**
        - with argument `-pp` or `--password_premium` password for login to premium account of Tapas.io (Accept not premium account) **Require**
        
        > Example: `python command.py --scrapte -c 10 -p 1` 
        >> This command above will scrapte 10 chapter and get list comics in page 1

    - **Step 2:** Run the command `python command.py --transfer` to transfer data to API

        - with argument `-c` or `--chapter` to how many chapter you want to transfer
        - with argument `-E` or `--email` email for login to API
        - with argument `-P` or `--password` password for login to API

        > Example: `python command.py --transfer -c 10 -E email -P password`
        >> This command above will transfer 10 chapter and login to API with email and password

## What actually this project do?

- Scrapte data from website save in folder storages every file scraped has file json stored information of data scraped
- Transfer data to API will get list file comics or story in folder storages and send to API while processing the data scraped will create a new file json with name upload.json and save in folder storages
- Every folder data has file json with mean flag data scrape or transfer to API is Completed or not
- **Note** This scrape will get list data not single data, This Feature will be updated in the future [!WIP]
- **Note** This Transfer will transfer list data not single data, This Feature will be updated in the future [!WIP]