from .Scraper import Scraper
from joblib import Parallel, delayed
from .SleepInhibitor import WindowsInhibitor
import os
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


def scrape(output_folder, scrape_type='alpha', processes=8, headless=True, deep=True):
    osSleep = None
    if os.name == 'nt':
        osSleep = WindowsInhibitor()
        osSleep.inhibit()

    if scrape_type == 'alpha':
        Parallel(n_jobs=processes)(delayed(alpha_job)(
            letter,
            headless=headless,
            output_file=os.path.join(output_folder, '{}.json'.format(letter)),
            start=0,
            increment=1,
            deep=deep
        ) for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')

    elif scrape_type == 'interval':
        Parallel(n_jobs=processes)(delayed(job)(
            headless=headless,
            output_file='{}/{}.json'.format(output_folder, i),
            start=i,
            increment=processes,
            deep=deep
        ) for i in range(processes))

    if osSleep:
        osSleep.uninhibit()
