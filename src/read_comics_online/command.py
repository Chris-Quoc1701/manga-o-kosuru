import argparse
import os
import sys

from read_comics_online_v1 import ScraperReadComicsOnline
from transfer_data_read_comics_online import TransferDataReadComicOnline
from utils import clear_all_image_content


def main():
    parser = argparse.ArgumentParser(
        description="""
    Two Options:
    1. Scrape data from readcomiconline.to
    2. Transfer data from scraping to API server
    3. Clear data from scraping exclude upload.json and comic.json
    """
    )
    # 2 options: scraping and transfer
    parser.add_argument(
        "-s",
        "--scrape",
        help="Scrape data from readcomiconline.to",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--transfer",
        help="Transfer data from scraping to API server",
        action="store_true",
    )
    parser.add_argument(
        "-cls",
        "--clear",
        help="Clear data from scraping exclude upload.json and comic.json",
        action="store_true",
    )
    # if scrape option is selected we need number page contain lsit comics and how many chapter
    parser.add_argument("-p", "--page", help="Page number for scraping")
    parser.add_argument(
        "-c", "--chapter", help="Number chapter for scraping or transfer"
    )
    # if transfer option is selected then we need email, password and number chapter for transfer
    parser.add_argument("-E", "--email", help="Email login")
    parser.add_argument("-P", "--password", help="Password login")

    args = parser.parse_args()
    if args.scrape:
        if args.page and args.chapter:
            scraper = ScraperReadComicsOnline(
                page_number=args.page, number_chapter=int(args.chapter)
            )
            scraper.suffer_comic()
        else:
            print("Please enter page number and how many chapter for scraping")
            sys.exit(1)
    elif args.transfer:
        if args.email and args.password and args.chapter:
            transfer = TransferDataReadComicOnline(
                number_chapter=int(args.chapter),
                email=args.email,
                password=args.password,
            )
            transfer.begin_transfer()
        else:
            print("Please enter email, password and number chapter for API MC")
            sys.exit(1)
    elif args.clear:
        clear_all_image_content()
    else:
        print("Please select option")
        sys.exit(1)


if __name__ == "__main__":
    main()
