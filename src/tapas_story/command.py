import argparse
import os
import sys

import tapas_io_v1
import transfer_data_tapas_io


def main():
    parser = argparse.ArgumentParser(
        description="""
    Two Options:
    1. Scrape data from tapas.io
    2. Transfer data from scraping to API server
    """
    )
    # 2 options: scraping and transfer
    parser.add_argument(
        "-s", "--scrape", help="Scrape data from tapas.io", action="store_true"
    )
    parser.add_argument(
        "-t",
        "--transfer",
        help="Transfer data from scraping to API server",
        action="store_true",
    )
    # if scrape option is selected we need number page contain lsit comics and how many chapter
    parser.add_argument("-p", "--page", help="Page number for scraping")
    parser.add_argument("-c", "--chapter", help="How many chapter for scraping")
    # if transfer option is selected then we need email, password and number chapter for transfer
    parser.add_argument("-E", "--EMAIL", help="Email login")
    parser.add_argument("-P", "--PASSWORD", help="Password login")
    parser.add_argument("-C", "--CHAPTER", help="Number chapter for transfer")
    # if scrape with premium account for Scraping with premium account
    parser.add_argument("-ep", "--email_premium", help="Email login of premium account")
    parser.add_argument(
        "-pp", "--password_premium", help="Password login of premium account"
    )

    args = parser.parse_args()
    if args.scrape:
        if args.page and args.chapter:
            scraper = tapas_io_v1.ScraperTapasStory(
                email=args.email_premium,
                password=args.password_premium,
                number_chapter=int(args.chapter),
                number_page=int(args.page),
            )
            scraper.begin_suffer()
        else:
            print("Please enter number page and number chapter")
            sys.exit(1)
    elif args.transfer:
        if args.EMAIL and args.PASSWORD and args.CHAPTER:
            transfer = transfer_data_tapas_io.TransferDataTapasIO(
                number_chapter=int(args.CHAPTER),
                email=args.EMAIL,
                password=args.PASSWORD,
            )
            transfer.begin_transfer()
        else:
            print("Please enter email, password and number chapter")
            sys.exit(1)
    else:
        print("Please select option")
        sys.exit(1)


if __name__ == "__main__":
    main()
