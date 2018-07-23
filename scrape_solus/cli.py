import click
import os
from .scrape_jobs import scrape as parallel_scrape


@click.command()
@click.option('--scrape_type', '-t', default='alpha', type=click.Choice(['alpha', 'interval']))
@click.option('--num_workers', '-n', type=click.INT, default=8)
@click.option('--output_dir', '-o', type=click.Path(exists=True), default=os.curdir,
              help='Output directory for data dump')
@click.option('--deep', '-d', type=click.BOOL, default=True, help='Do you want Section Data?')
@click.option('--headless', '-h', type=click.BOOL, default=True)
def scrape(scrape_type, num_workers, output_dir, deep, headless):
    parallel_scrape(output_folder=output_dir,
                    scrape_type=scrape_type, processes=num_workers, headless=headless)
