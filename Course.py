from selenium.common.exceptions import NoSuchElementException


class Course(object):
    def __init__(self, course, sections=False):
        self.course = course

    def get_course_component_details(self, row):
        component = {}
        component['name'] = row.find_element_by_css_selector(
            'span[id^="DERIVED_CRSECAT_DESCR$"]').text
        component['required'] = row.find_element_by_css_selector(
            'span[id^="DERIVED_CRSECAT_DESCRSHORT$"]').text
        return component

    @property
    def details(self):
        details = {}
        try:
            full_title = self.course.find_element_by_id(
                'DERIVED_CRSECAT_DESCR200').text
            details['code'] = full_title.split(' - ', 2)[0]
            details['title'] = full_title.split(' - ', 2)[1]

            details['career'] = self.course.find_element_by_id(
                'SSR_CRSE_OFF_VW_ACAD_CAREER$0').text
            details['units'] = self.course.find_element_by_id(
                'DERIVED_CRSECAT_UNITS_RANGE$0').text
            details['grading_basis'] = self.course.find_element_by_id(
                'SSR_CRSE_OFF_VW_GRADING_BASIS$0').text

            table = self.course.find_element_by_id('ACE_SSR_DUMMY_RECVW$0')
            component_rows = table.find_elements_by_css_selector(
                'tr')

            details['course_components'] = list(
                map(self.get_course_component_details, component_rows[1:]))

            details['campus'] = self.course.find_element_by_id(
                'CAMPUS_TBL_DESCR$0').text
            details['academic_group'] = self.course.find_element_by_id(
                'ACAD_GROUP_TBL_DESCR$0').text
            details['academic_organization'] = self.course.find_element_by_id(
                'ACAD_ORG_TBL_DESCR$0').text
        except NoSuchElementException:
            pass
        return details

    @property
    def enrollment_info(self):
        info = {}
        try:
            table = self.course.find_element_by_id(
                'ACE_DERIVED_CRSECAT_SSR_GROUP2$0')
            rows = table.find_elements_by_css_selector('tr')
            for row in rows[1:]:
                key = row.find_element_by_css_selector(
                    'td[align="right"]').text
                val = row.find_element_by_css_selector('td[align="left"]').text
                info[key] = val
            return info
        except NoSuchElementException:
            pass
        return info

    @property
    def description(self):
        try:
            table = self.course.find_element_by_id(
                'ACE_DERIVED_CRSECAT_SSR_GROUP3$0')
            return table.find_element_by_id('SSR_CRSE_OFF_VW_DESCRLONG$0').text
        except NoSuchElementException:
            return ''

    def all_info(self):
        info = {
            'description': self.description,
            'details': self.details,
            'enrollment_info': self.enrollment_info
        }
        print("INFO", info)
        return info
