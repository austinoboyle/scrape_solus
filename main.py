from Scraper import Scraper
from joblib import Parallel, delayed
from SleepInhibitor import WindowsInhibitor
import os
#import logging
import datetime
import sys
import json


def job(headless=False, output_file="data_dump/all.json", start=0, increment=1, deep=False):
    Scraper(headless=headless).default_scrape(
        output_file=output_file, start=start, increment=increment, deep=deep)


def alpha_job(letter, headless=False, output_file="data_dump/all.json", start=0, increment=1, deep=False):
    results = Scraper(headless=headless).scrape_page_by_letter(
        letter, start=start, increment=increment, deep=deep)
    with open(output_file, 'w') as f:
        json.dump(results, f)


def main():
    NUM_JOBS = 16
    HEADLESS = True
    # logging.basicConfig(
    #     format='%(asctime)s--%(levelname)s:%(message)s',
    #     datefmt='%m/%d/%Y %I:%M:%S %p',
    #     level=logging.INFO)
    # Parallel(n_jobs=NUM_JOBS)(delayed(job)(
    #     headless=HEADLESS,
    #     output_file='data_dump/{}.json'.format(i),
    #     start=i,
    #     increment=NUM_JOBS,
    #     deep=True
    # ) for i in range(NUM_JOBS))
    Parallel(n_jobs=NUM_JOBS)(delayed(alpha_job)(
        letter,
        headless=HEADLESS,
        output_file='data_dump/{}.json'.format(letter),
        start=0,
        increment=1,
        deep=True
    ) for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')


if __name__ == '__main__':
    osSleep = None
    if os.name == 'nt':
        osSleep = WindowsInhibitor()
        osSleep.inhibit()

    main()

    if osSleep:
        osSleep.uninhibit()
