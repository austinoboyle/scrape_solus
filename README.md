# scrape_solus

## Introduction

`scrape_solus` is a python utility to scrape all details from from the Queen's
course enrollment site.

## Installation

1. `git clone https://github.com/austinoboyle/scrape_solus` and cd into the folder
2. (Ideal, but not necessary) create a virtual env
3. `pip install -e .` to install the project in development mode. This will allow you to easily make changes on the fly.
4. Set your SOLUS_USER and SOLUS_PASS env variables
5. You should now have the `scrapesolus` command available. Run `scrapesolus --help` to see available commands.

## CLI (scrapsolus)

Usage: scrapesolus [OPTIONS]

Options:

-   -t, --scrape_type alpha|interval (default=alpha). alpha: each job scrapes a letter. interval: each job scrapes every Nth course.
-   -n, --num_workers INTEGER (default=8) number of selenium instances to run in parallel
-   -o, --output_dir PATH Output directory for data dump
-   -d, --deep BOOLEAN Do you want Section Data?
-   -h, --headless BOOLEAN (default: True). Set to False for debugging.
-   -l, --letter TEXT Scrape all courses that start with this letter
-   -c, --course_code TEXT Scrape a specific course code
-   --help Show this message and exit.

## Examples

### Scrape a specific course

`scrapesolus -c "MATH 281"`

### Scrape a course without headless selenium for debugging

`scrapesolus -h False -c "MATH 281"`

### Scrape a specific course and only want the course info/description (no sections/schedule data)?

`scrapesolus -c "MATH 281" -d False`

### Scrape all course codes beginning with the letter A

`scrapesolus -l A`

### Full scrape of courses with (default) 8 workers

`scrapesolus`

### Full scrape with 2 workers

`scrapesolus -n 2`
