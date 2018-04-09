from Scraper import Scraper
from joblib import Parallel, delayed


def job(headless=False, output_file="data_dump/all.json", start=0, increment=1, deep=False):
    Scraper(headless=headless).default_scrape(
        output_file=output_file, start=start, increment=increment, deep=deep)


def main():
    NUM_JOBS = 12
    HEADLESS = True
    Parallel(n_jobs=NUM_JOBS)(delayed(job)(headless=HEADLESS, output_file='data_dump/{}.json'.format(i),
                                           start=i, increment=NUM_JOBS) for i in range(NUM_JOBS))


if __name__ == '__main__':
    main()
