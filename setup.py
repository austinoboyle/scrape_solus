from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='scrape_solus',
      version="0.0.1",
      description="Selenium Scraper for Queen's Courses on SOLUS",
      long_description=readme(),
      author="Austin O'Boyle",
      author_email='hello@austinoboyle.com',
      license="(c) Austin O'Boyle - Proprietary",
      url='https://github.com/austinoboyle/scrape_solus',
      packages=['scrape_solus'],
      entry_points={'console_scripts': [
          'scrapesolus=scrape_solus.cli:scrape',
          'cleancourses=scrape_solus.cli:clean'
      ]},
      keywords='selenium scraper web scraping queens',
      #   include_package_data=True,
      #   package_data={'scraper': ['data/*.txt']},
      zip_safe=False,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'License :: Other/Proprietary License'
      ],
      install_requires=[
          'beautifulsoup4>=4.6.0',
          'bs4',
          'selenium',
          'click',
          'joblib'
      ]
      )
