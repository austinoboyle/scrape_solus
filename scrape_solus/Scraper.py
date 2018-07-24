from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import json
from .config import USER, PASS
from .Course import Course
from .Section import Section
#import logging

COURSE_CAT_URL = 'https://saself.ps.queensu.ca/psc/saself/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_BROWSE_CATLG_P.GBL'
LOGIN_URL = 'login.queensu.ca'
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

COURSE_DETAIL_SELECTOR = '#ACE_DERIVED_SAA_CRS_GROUP1'
COURSE_CATALOG_SELECTOR = '#ACE_DERIVED_SAA_CRS_GROUP1'

ALPHASEARCH_ID_TEMPLATE = 'DERIVED_SSS_BCC_SSR_ALPHANUM_{}'
MAX_CONSECUTIVE_ERRORS = 3
INCREMENT = 30


class Scraper(object):
    def __init__(self, user=USER, password=PASS, headless=False):
        chrome_options = Options()
        if(headless):
            chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get(COURSE_CAT_URL)
        self.login(user, password)
        # print("DEFAULT WINDOW SIZE: ", self.driver.get_window_size())
        self.driver.set_window_size(1100, 900)

    def by_id(self, id):
        return self.driver.find_element_by_id(id)

    def default_scrape(self, output_file="data_dump/all.json", start=0, increment=1, deep=False):
        all_courses = []
        for letter in LETTERS:
            all_courses += self.scrape_page_by_letter(
                letter=letter, increment=increment, deep=deep, start=start)
        with open(output_file, 'w') as out:
            json.dump(all_courses, out)

    def scrape_page_by_letter(self, letter, start=0, increment=1, deep=False):
        self.select_letter(letter)
        consecutive_errors = 0
        courses = []
        course_num = start
        scraped_all = False
        while not scraped_all:
            try:
                course_link = self.by_id(
                    'CRSE_TITLE${}'.format(course_num))
                course_title = course_link.text
                print("{}: Attempting to scrape {}".format(
                    self.letter, course_title))
                info = self.get_course_info(course_link, deep=deep)
                try:
                    if 'options' in info:
                        print("SCRAPED: {} - {}".format(
                            info['options'][0]['details']['code'], info['options'][0]['details']['title']))
                    else:
                        print(
                            "SCRAPED: {} - {}".format(info['details']['code'], info['details']['title']))
                except:
                    pass
                courses.append(info)
                course_num += increment
                consecutive_errors = 0
            except NoSuchElementException:
                scraped_all = True
            except Exception as e:
                print(
                    "ERROR SCRAPING COURSE {}, {}".format(course_num, e))
                consecutive_errors += 1
                if (consecutive_errors >= MAX_CONSECUTIVE_ERRORS):
                    course_num += increment
                else:
                    print("RETRYING")

        return courses

    def scrape_specific_course(self, subject, code, deep=True):
        subject, code = subject.strip().upper(), str(code).strip().upper()
        self.go_to_course_catalogue()
        letter_button = self.by_id(
            ALPHASEARCH_ID_TEMPLATE.format(subject[0].upper()))
        self.click_and_wait(letter_button)
        subject_link = self.driver.find_element_by_partial_link_text(
            '{} -'.format(subject.upper()))
        self.click_and_wait(subject_link)
        course_link = self.driver.find_element_by_partial_link_text(code)
        info = self.get_course_info(course_link, deep=deep)
        return info

    def go_to_course_catalogue(self):
        self.driver.get(COURSE_CAT_URL)

    def select_letter(self, letter):
        print("SELECTING LETTER: {}".format(letter))
        button = self.by_id(
            ALPHASEARCH_ID_TEMPLATE.format(letter))
        self.click_and_wait(button)
        self.letter = letter
        self.expand_all()

    def login(self, user, password):
        print("LOGGING IN...")
        self.wait_for_element('#username')

        username_input = self.by_id('username')
        password_input = self.by_id('password')
        username_input.send_keys(user)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        self.wait_for_initial_load()
        print("DONE LOGGING IN")

    def get_course_info(self, link, deep=False):
        self.click_and_wait(link)
        all_info = {}
        # Courses with multiple offerings (Bader, Distance, etc)
        if self.page_title == 'Select Course Offering':
            retrieved_all_options = False
            option_num = 0
            options = []
            consecutive_errors = 0
            while not retrieved_all_options:
                try:
                    course_link = self.by_id(
                        'CAREER${}'.format(option_num))
                    options.append(self.get_course_info(
                        course_link, deep=deep))
                    option_num += 1
                    consecutive_errors = 0
                except NoSuchElementException:
                    retrieved_all_options = True
                except Exception as e:
                    print(
                        "ERROR SCRAPING OPTION {}, {}".format(option_num, e))
                    consecutive_errors += 1
                    if (consecutive_errors >= MAX_CONSECUTIVE_ERRORS):
                        option_num += 1
                    else:
                        print("RETRYING")
                    self.click_and_wait(self.return_button)

            all_info['options'] = options
        else:
            course_page = self.by_id(
                'win0divPSPAGECONTAINER')
            all_info = Course(course_page).all_info
            if deep:
                sections = self.get_sections()
                all_info['sections'] = sections

        self.click_and_wait(self.return_button)
        return all_info

    def get_sections(self):
        sections = []
        view_class_sections_btn = None

        try:
            view_class_sections_btn = self.by_id(
                'DERIVED_SAA_CRS_SSR_PB_GO')
            self.click_and_wait(view_class_sections_btn)
        except NoSuchElementException:
            return sections

        terms_scheduled = self.driver.find_elements_by_css_selector(
            '#DERIVED_SAA_CRS_TERM_ALT option')
        terms_scheduled = list(filter(lambda x: int(x) >= 2189, map(
            lambda x: x.get_attribute('value'), terms_scheduled)))

        for term in terms_scheduled:
            # print("TERM: {}".format(term))
            term_select = Select(self.by_id('DERIVED_SAA_CRS_TERM_ALT'))
            term_select.select_by_value(term)
            show_sections_btn = view_all_btn = None
            try:
                show_sections_btn = self.by_id('DERIVED_SAA_CRS_SSR_PB_GO$3$')
                self.click_and_wait(show_sections_btn)
            except:
                continue

            try:
                view_all_btn = self.by_id(
                    'CLASS_TBL_VW5$hviewall$0')
                if view_all_btn.text.strip().lower() == 'view all':
                    self.click_and_wait(view_all_btn)
            except NoSuchElementException:
                pass

            section_num = 0
            scraped_all_sections = False
            consecutive_errors = 0
            while not scraped_all_sections:
                try:
                    link = self.by_id('CLASS_SECTION${}'.format(section_num))
                    section_name = link.text.split(' ', 2)[0]
                    self.click_and_wait(link)
                    sections.append(
                        Section(self.by_id('ACE_width'), section_name).all_info)
                    self.click_and_wait(self.return_button)
                    section_num += 1
                except NoSuchElementException:
                    scraped_all_sections = True
                except Exception as e:
                    print(
                        "ERROR SCRAPING SECTION {}, {}".format(section_num, e))
                    consecutive_errors += 1
                    if (consecutive_errors >= MAX_CONSECUTIVE_ERRORS):
                        section_num += 1
                    else:
                        print("RETRYING")
                    self.click_and_wait(self.return_button)

        return sections

    @property
    def return_button(self):

        # Multiple Course Offerings
        if self.page_title == 'Select Course Offering':
            return self.by_id('DERIVED_SSS_SEL_RETURN_PB')

        # Course Info
        elif self.page_title == 'Course Detail':
            return self.by_id('DERIVED_SAA_CRS_RETURN_PB')

        # Section Info
        elif self.page_title == 'Class Details':
            return self.by_id('CLASS_SRCH_WRK2_SSR_PB_CLOSE')
        else:
            try:
                return self.by_id('DERIVED_SAA_CRS_RETURN_PB')
            except NoSuchElementException:
                return None

    @property
    def page_title(self):
        try:
            return self.by_id('DERIVED_REGFRM1_TITLE1').text
        except NoSuchElementException:
            return None

    def get_all_course_links(self):
        return self.driver.find_elements_by_css_selector(
            'a[id^="CRSE_NBR$"]')

    def get_all_tables(self):
        return self.driver.find_elements_by_css_selector(
            'table[id^="ACE_DERIVED_SSS_BCC_GROUP_BOX_1$"]')

    def get_all_courses(self, table):
        return table.find_elements_by_css_selector('tr[id^="trCOURSE_LIST$"]')

    def wait_for_initial_load(self):
        self.wait_for_element('span.PAPAGETITLE')

    def expand_all(self):
        try:
            button = self.driver.find_element_by_css_selector(
                'input[title="Expand All Sections"]')
            button.click()
            self.wait_for_element('table[id^="COURSE_LIST$scroll"]')
        except:
            pass

    def click_and_wait(self, el, timeout=120):
        oldVal = self.by_id(
            'ICStateNum').get_attribute('value')
        try:
            el.click()
            el = WebDriverWait(self.driver, timeout).until(EC.text_to_be_present_in_element_value(
                (By.ID, 'ICStateNum'), str(int(oldVal) + 1)
            ))
            return el
        except TimeoutException:
            print("TIMEOUT EXCEPTION WHILE WAITING FOR {}".format(el))
        except Exception as e:
            print("EXCEPTION WHILE CLICKING/WAITING FOR {}".format(el))
            print(e)

    def wait_for_element(self, selector, timeout=120):
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)
            ))
            return el
        except TimeoutException:
            print(
                "UNABLE TO FIND ELEMENT WITH SELECTOR: {}".format(selector))
