from Scraper import Scraper
import json
#import logging
import datetime
DEEP = True
HEADLESS = False


def main():
    # formatted_time = datetime.datetime.now().strftime("%Y-%m-%d")
    # logging.basicConfig(
    #     format='%(asctime)s--%(levelname)s:%(message)s',
    #     datefmt='%m/%d/%Y %I:%M:%S %p',
    #     level=logging.INFO)
    scraper = Scraper(headless=HEADLESS)
    course = scraper.scrape_specific_course('M', 32, deep=DEEP)
    with open('data_dump/test.json', 'w') as out:
        json.dump(course, out)


if __name__ == '__main__':
    main()
