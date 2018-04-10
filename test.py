from Scraper import Scraper
import json

DEEP = True
HEADLESS = False


def main():
    scraper = Scraper(headless=HEADLESS)
    course = scraper.scrape_specific_course('M', 32, deep=DEEP)
    with open('test.json', 'w') as out:
        json.dump(course, out)


if __name__ == '__main__':
    main()
