import click
import os
import json
from .scrape_jobs import scrape as parallel_scrape
from .Scraper import Scraper


@click.command()
@click.option('--scrape_type', '-t', default='alpha', type=click.Choice(['alpha', 'interval']))
@click.option('--num_workers', '-n', type=click.INT, default=8)
@click.option('--output_dir', '-o', type=click.Path(exists=True), default=os.curdir,
              help='Output directory for data dump')
@click.option('--deep', '-d', type=click.BOOL, default=True, help='Do you want Section Data?')
@click.option('--headless', '-h', type=click.BOOL, default=True)
@click.option('--letter', '-l', type=click.STRING)
@click.option('--course_num', '-c', type=click.INT)
def scrape(scrape_type, num_workers, output_dir, deep, headless, letter, course_num):
    if letter:
        scraper = Scraper(headless=headless)
        letter = letter.upper()
        if course_num is not None:
            results = scraper.scrape_specific_course(
                letter=letter, course=course_num, deep=deep)
            filename = os.path.join(output_dir, '{}.json'.format(letter))
        else:
            filename = os.path.join(
                output_dir, '{}-{}.json'.format(letter, course_num))
            results = scraper.scrape_page_by_letter(letter, deep=deep)
        with open(filename, 'w') as f:
            json.dump(results, f)

    else:
        parallel_scrape(output_folder=output_dir,
                        scrape_type=scrape_type, processes=num_workers, headless=headless)
