import click
from click import ClickException
from selenium.common.exceptions import NoSuchElementException
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
@click.option('--course_code', '-c', type=click.STRING)
def scrape(scrape_type, num_workers, output_dir, deep, headless, letter, course_code):
    if course_code:
        scraper = Scraper(headless=headless)
        try:
            subject, code = tuple(course_code.strip().upper().split(' '))
            results = scraper.scrape_specific_course(
                subject=subject, code=code)
            filename = os.path.join(output_dir, '{}.json'.format(course_code))
            with open(filename, 'w') as f:
                json.dump(results, f)
        except NoSuchElementException:
            raise ClickException(
                "No Course Found with Code: {}".format(course_code))
        except ValueError:
            raise ClickException(
                "Invalid Course Code - Proper format: 'APSC 123'")
        except Exception as e:
            print("UNKNOWN ERROR")
            raise e
    elif letter:
        scraper = Scraper(headless=headless)
        letter = letter.upper()
        filename = os.path.join(
            output_dir, '{}.json'.format(letter))
        results = scraper.scrape_page_by_letter(letter, deep=deep)
        with open(filename, 'w') as f:
            json.dump(results, f)

    else:
        parallel_scrape(output_folder=output_dir,
                        scrape_type=scrape_type, processes=num_workers, headless=headless)
