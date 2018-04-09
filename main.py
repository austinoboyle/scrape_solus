from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from config import USER, PASS
from Course import Course
COURSE_CAT_URL = 'https://saself.ps.queensu.ca/psc/saself/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSS_BROWSE_CATLG_P.GBL'
LOGIN_URL = 'login.queensu.ca'
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

COURSE_DETAIL_SELECTOR = '#ACE_DERIVED_SAA_CRS_GROUP1'
COURSE_CATALOG_SELECTOR = '#ACE_DERIVED_SAA_CRS_GROUP1'

ALPHASEARCH_ID_TEMPLATE = 'DERIVED_SSS_BCC_SSR_ALPHANUM_{}'


class Scraper(object):
    def __init__(self, user=USER, password=PASS):
        self.driver = webdriver.Chrome()
        self.driver.get(COURSE_CAT_URL)
        self.login(user, password)
        for letter in LETTERS:
            self.select_letter(letter)
            self.scrape_page()
        self.actionCounter = 0

    def scrape_page(self):
        self.expand_all()
        tables = self.get_all_tables()
        num_tables = len(tables)
        courses = []
        course_count = 0
        scraped_all = False
        # while not scraped_all:

        for i in range(num_tables):
            table = self.driver.find_element_by_id(
                "ACE_DERIVED_SSS_BCC_GROUP_BOX_1${}".format(i))
            dept = table.find_element_by_css_selector(
                'a[name^="DERIVED_SSS_BCC_GROUP_BOX_1$147$$"]').text
            dept_letters = dept[0:4]
            courses_obj = {}
            courses = self.get_all_courses(table)
            num_courses = len(courses)
            for j in range(num_courses):
                table = self.driver.find_element_by_id(
                    "ACE_DERIVED_SSS_BCC_GROUP_BOX_1${}".format(i))
                course_link = table.find_element_by_id(
                    'CRSE_NBR${}'.format(j))
                code = course_link.text
                courses_obj[dept_letters +
                            code] = self.get_course_info(course_link)

            page_obj[dept] = courses_obj
        print("PAGE OBJECT", page_obj)

    def select_letter(self, letter):
        button = self.driver.find_element_by_id(
            ALPHASEARCH_ID_TEMPLATE.format(letter))
        self.click_and_wait(button)

    def login(self, user, password):
        while LOGIN_URL not in self.driver.current_url:
            time.sleep(0.1)
        username = self.driver.find_element_by_id('username')
        password = self.driver.find_element_by_id('password')
        username.send_keys(USER)
        password.send_keys(PASS)
        password.send_keys(Keys.ENTER)
        self.wait_for_initial_load()

    def get_course_info(self, link):
        self.click_and_wait(link)
        course_page = self.driver.find_element_by_id('win0divPSPAGECONTAINER')
        return_button = self.driver.find_element_by_id(
            'DERIVED_SAA_CRS_RETURN_PB')
        info = Course(course_page).all_info()
        self.click_and_wait(return_button)
        return info

    def get_all_courses

    def get_all_tables(self):
        return self.driver.find_elements_by_css_selector(
            'table[id^="ACE_DERIVED_SSS_BCC_GROUP_BOX_1$"]')

    def get_all_courses(self, table):
        return table.find_elements_by_css_selector('tr[id^="trCOURSE_LIST$"]')

    def wait_for_initial_load(self):
        self.wait_for_element('span.PAPAGETITLE')

    def wait_for_change(self):
        pass

    def expand_all(self):
        button = self.driver.find_element_by_css_selector(
            'input[title="Expand All Sections"]')
        button.click()
        self.wait_for_element('table[id^="COURSE_LIST$scroll"]')

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


def main():
    scraper = Scraper()


if __name__ == '__main__':
    main()
