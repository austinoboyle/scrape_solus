from Scraper import Scraper
import json
#import logging
import datetime
DEEP = True
HEADLESS = True


def main():
    # formatted_time = datetime.datetime.now().strftime("%Y-%m-%d")
    # logging.basicConfig(
    #     format='%(asctime)s--%(levelname)s:%(message)s',
    #     datefmt='%m/%d/%Y %I:%M:%S %p',
    #     level=logging.INFO)
    scraper = Scraper(headless=HEADLESS)
    course = scraper.scrape_specific_course('A', 1, deep=DEEP)
    # LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # for letter in LETTERS:
    #     print("LETTER", letter)
    #     scraper.select_letter(letter)
    with open('data_dump/test.json', 'w') as out:
        json.dump(course, out)


if __name__ == '__main__':
    main()
