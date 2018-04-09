from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import json
from config import USER, PASS
from Course import Course

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
                course_link = self.driver.find_element_by_id(
                    'CRSE_NBR${}'.format(course_num))
                courses.append(self.get_course_info(course_link, deep=deep))
                course_num += increment
                consecutive_errors = 0
            except NoSuchElementException:
                scraped_all = True
            except Exception as e:
                print("ERROR SCRAPING COURSE {}, {}".format(course_num, e))
                consecutive_errors += 1
                if (consecutive_errors >= MAX_CONSECUTIVE_ERRORS):
                    course_num += 1
                else:
                    print("RETRYING")

        return courses

    def scrape_specific_course(self, letter, course):
        self.go_to_course_catalogue()
        self.select_letter(letter)
        course_link = self.driver.find_element_by_id(
            'CRSE_NBR${}'.format(course))
        info = self.get_course_info(course_link)
        return info

    def go_to_course_catalogue(self):
        self.driver.get(COURSE_CAT_URL)

    def select_letter(self, letter):
        button = self.driver.find_element_by_id(
            ALPHASEARCH_ID_TEMPLATE.format(letter))
        self.click_and_wait(button)
        self.expand_all()

    def login(self, user, password):
        while LOGIN_URL not in self.driver.current_url:
            time.sleep(0.1)
        username = self.driver.find_element_by_id('username')
        password = self.driver.find_element_by_id('password')
        username.send_keys(USER)
        password.send_keys(PASS)
        password.send_keys(Keys.ENTER)
        self.wait_for_initial_load()

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
                    course_link = self.driver.find_element_by_id(
                        'CAREER${}'.format(option_num))
                    options.append(self.get_course_info(
                        course_link, deep=deep))
                    option_num += 1
                    consecutive_errors = 0
                except NoSuchElementException:
                    retrieved_all_options = True
                except Exception as e:
                    print("ERROR SCRAPING OPTION {}, {}".format(option_num, e))
                    consecutive_errors += 1
                    if (consecutive_errors >= MAX_CONSECUTIVE_ERRORS):
                        option_num += 1
                    else:
                        print("RETRYING")
                    self.click_and_wait(self.return_button)

            all_info['options'] = options
        else:
            course_page = self.driver.find_element_by_id(
                'win0divPSPAGECONTAINER')
            all_info = Course(course_page).all_info()

        self.click_and_wait(self.return_button)
        return all_info

    @property
    def return_button(self):
        if self.page_title == 'Select Course Offering':
            return self.driver.find_element_by_id('DERIVED_SSS_SEL_RETURN_PB')
        elif self.page_title == 'Course Detail':
            return self.driver.find_element_by_id('DERIVED_SAA_CRS_RETURN_PB')
        else:
            try:
                return self.driver.find_element_by_id('DERIVED_SAA_CRS_RETURN_PB')
            except NoSuchElementException:
                return None

    @property
    def page_title(self):
        try:
            return self.driver.find_element_by_id('DERIVED_REGFRM1_TITLE1').text
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

    def wait_infinite(self):
        while True:
            time.sleep(0.1)

    def click_and_wait(self, el, timeout=60):
        print("WAITING FOR UPDATE...")
        oldVal = self.driver.find_element_by_id(
            'ICStateNum').get_attribute('value')
        el.click()
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.text_to_be_present_in_element_value(
                (By.ID, 'ICStateNum'), str(int(oldVal) + 1)
            ))
            print("FOUND")
            return el
        except TimeoutException:
            print("TIMEOUT EXCEPTION WHILE WAITING")

    def wait_for_element(self, selector, timeout=60):
        print("WAITING FOR ELEMENT: {} .....".format(selector))
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector)
            ))
            print("FOUND")
            return el
        except TimeoutException:
            print("UNABLE TO FIND ELEMENT WITH SELECTOR", selector)
