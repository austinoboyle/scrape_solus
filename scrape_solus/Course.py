from selenium.common.exceptions import NoSuchElementException


class Course(object):
    def __init__(self, course, sections=False):
        self.course = course

    def by_id(self, _id):
        return self.course.find_element_by_id(_id)

    def text_or_default(self, el, selector, default="UNKNOWN"):
        try:
            return el.find_element_by_css_selector(selector).text
        except:
            return default

    def id_text(self, _id, with_default=True, default="UNKNOWN"):
        try:
            return self.by_id(_id).text
        except NoSuchElementException:
            print(
                "COURSE: NO ELEMENT WITH ID: {}".format(_id))
            return default

    def get_course_component_details(self, row):
        component = {}
        component['name'] = self.text_or_default(
            row, 'span[id^="DERIVED_CRSECAT_DESCR$"]')
        component['required'] = self.text_or_default(
            row, 'span[id^="DERIVED_CRSECAT_DESCRSHORT$"]'
        )
        return component

    @property
    def details(self):
        details = {}
        try:
            full_title = self.id_text(
                'DERIVED_CRSECAT_DESCR200', default='ZZZZ 999 - ERROR/UNKNOWN')
            details['code'] = full_title.split(' - ', 2)[0]
            details['title'] = full_title.split(' - ', 2)[1]

            details['career'] = self.id_text(
                'SSR_CRSE_OFF_VW_ACAD_CAREER$0')
            details['units'] = self.course.id_text(
                'DERIVED_CRSECAT_UNITS_RANGE$0')
            details['grading_basis'] = self.id_text(
                'SSR_CRSE_OFF_VW_GRADING_BASIS$0')
            details['campus'] = self.id_text(
                'CAMPUS_TBL_DESCR$0')
            details['academic_group'] = self.id_text(
                'ACAD_GROUP_TBL_DESCR$0')
            details['academic_organization'] = self.id_text(
                'ACAD_ORG_TBL_DESCR$0')
            table = self.course.find_element_by_id('ACE_SSR_DUMMY_RECVW$0')
            component_rows = table.find_elements_by_tag_name('tr')
            details['course_components'] = list(
                map(self.get_course_component_details, component_rows[1:]))
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

    @property
    def all_info(self):
        return {
            'description': self.description,
            'details': self.details,
            'enrollment_info': self.enrollment_info
        }
