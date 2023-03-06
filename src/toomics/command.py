import argparse
import os
import sys

import toomics_v1
import transfer_data_toomics
from utils import clear_all_image_content


def main():
    parser = argparse.ArgumentParser(
        description="""
    Two Options:
    1. Scrape data from toomics.com
    2. Transfer data from scraping to API server
    3. Clear data from scraping exclude upload.json
    """
    )
    # 2 Options choice scraping data
    parser.add_argument(
        "-s", "--scrape", help="Scrape data from toomics.com", action="store_true"
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
        help="Clear data from scraping exclude upload.json",
        action="store_true",
    )
    # if scrape option is selected we need number page contain lsit comics and how many chapter
    parser.add_argument("-c", "--chapter", help="Number chapter for scraping")
    parser.add_argument(
        "-w",
        "--warning",
        help="With yes is scraping NSFW comics, with no is scraping SFW comics",
        action="store_true",
    )
    # if transfer option is selected then we need email, password and number chapter for transfer
    parser.add_argument("-E", "--email", help="Email login")
    parser.add_argument("-P", "--password", help="Password login")
    # if scrape with premium account for Scraping with premium account
    parser.add_argument("-ep", "--email_premium", help="Email login of premium account")
    parser.add_argument(
        "-pp", "--password_premium", help="Password login of premium account"
    )

    args = parser.parse_args()
    if args.scrape:
        if args.chapter and args.email_premium and args.password_premium:
            scrape = toomics_v1.ScrapeToomics(
                email=args.email_premium,
                password=args.password_premium,
                number_chapter=int(args.chapter),
                mature=True if args.warning else False,
            )
            scrape.suffer_comic()
        else:
            print("Please enter all arguments")
    elif args.transfer:
        if args.email and args.password and args.chapter:
            transfer = transfer_data_toomics.TransferDataToomics(
                email=args.email,
                password=args.password,
                number_chapter=int(args.chapter),
            )
            transfer.begin_transfer()
        else:
            print("Please enter all arguments")
    elif args.clear:
        clear_all_image_content()
    else:
        print("Please enter all arguments")


if __name__ == "__main__":
    main()
