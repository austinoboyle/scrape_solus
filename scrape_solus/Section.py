from selenium.common.exceptions import NoSuchElementException
#import logging


class Section(object):
    def __init__(self, section, name):
        self.section = section
        self.name = name

    def by_id(self, _id):
        return self.section.find_element_by_id(_id)

    def id_text(self, _id, with_default=True, default="UNKNOWN"):
        try:
            return self.by_id(_id).text
        except NoSuchElementException:
            print(
                "{} - {}: NO ELEMENT WITH ID: {}".format(self.name, self.section, _id))
            return default

    @property
    def details(self):
        details = {}
        details['open'] = self.id_text('SSR_CLS_DTL_WRK_SSR_DESCRSHORT')
        details['class_number'] = self.id_text('SSR_CLS_DTL_WRK_CLASS_NBR')

        header = self.id_text('DERIVED_CLSRCH_SSS_PAGE_KEYDESCR')
        details['term'] = header.split(' | ', 3)[1]
        details['type'] = header.split(' | ', 3)[2]
        return details

    @property
    def availability(self):
        availability = {}
        availability['capacity'] = self.id_text('SSR_CLS_DTL_WRK_ENRL_CAP')
        availability['enrollment'] = self.id_text('SSR_CLS_DTL_WRK_ENRL_TOT')
        availability['available_seats'] = self.id_text(
            'SSR_CLS_DTL_WRK_AVAILABLE_SEATS')
        availability['wait_list_capacity'] = self.id_text(
            'SSR_CLS_DTL_WRK_WAIT_CAP')
        availability['wait_list_total'] = self.id_text(
            'SSR_CLS_DTL_WRK_WAIT_TOT')

        for key in availability:
            try:
                availability[key] = int(availability[key])
            except:
                availability[key] = 0

        return availability

    @property
    def meeting_info(self):
        meeting_info = []
        row_num = 1
        found_all_days = False
        while not found_all_days:
            try:
                row = self.by_id('trSSR_CLSRCH_MTG$0_row{}'.format(row_num))
                day = {}
                day['days_and_times'] = self.id_text('MTG_SCHED$0')
                day['room'] = self.id_text('MTG_LOC$0')
                day['instructor'] = self.id_text('MTG_INSTR$0')
                day['dates'] = self.id_text('MTG_DATE$0')
                meeting_info.append(day)
                row_num += 1
            except NoSuchElementException:
                found_all_days = True
        return meeting_info

    @property
    def all_info(self):
        return {
            'meeting_info': self.meeting_info,
            'availability': self.availability,
            'details': self.details,
            'name': self.name
        }
