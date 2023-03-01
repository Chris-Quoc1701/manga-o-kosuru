import argparse
import os
import sys

from read_comics_online_v1 import ScraperReadComicsOnline
from transfer_data_read_comics_online import TransferDataReadComicOnline


def main():
    parser = argparse.ArgumentParser(
        description="""
    Two Options:
    1. Scrape data from readcomiconline.to
    2. Transfer data from scraping to API server
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
    # if scrape option is selected we need number page contain lsit comics and how many chapter
    parser.add_argument("-p", "--page", help="Number page for scraping")
    parser.add_argument("-c", "--chapter", help="Number chapter for scraping")
    # if transfer option is selected then we need email, password and number chapter for transfer
    parser.add_argument("-E", "--email", help="Email login")
    parser.add_argument("-P", "--password", help="Password login")
    parser.add_argument("-C", "--CHAPTER", help="Number chapter for transfer")

    args = parser.parse_args()
    if args.scrape:
        if args.page and args.chapter:
            scraper = ScraperReadComicsOnline(page=args.page, chapter=int(args.chapter))
            scraper.suffer_comic()
        else:
            print("Please enter page number and how many chapter for scraping")
            sys.exit(1)
    elif args.transfer:
        if args.email and args.password and args.CHAPTER:
            transfer = TransferDataReadComicOnline(
                number_chapter=int(args.CHAPTER),
                email=args.email,
                password=args.password,
            )
            transfer.begin_transfer()
        else:
            print("Please enter email, password and number chapter for API MC")
            sys.exit(1)
    else:
        print("Please select option")
        sys.exit(1)


if __name__ == "__main__":
    main()
