import json
import sys
import os
import re
import collections
import itertools

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def trim_whitespace(string):
    return ' '.join(string.split())


import collections


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def default_course():
    return {
        "description": "",
        "details": {
            "code": "",
            "title": "",
            "career": "",
            "units": "",
            "grading_basis": "",
            "course_components": [],
            "campus": "",
            "academic_group": "",
            "academic_organization": ""
        },
        "enrollment_info": {},
        "sections": []
    }


def fill_with_defaults(course):
    if 'options' in course:
        for i in range(len(course['options'])):
            default = default_course()
            default = update(default, course['options'][i])
            course['options'][i] = default
        return course
    else:
        default = default_course()
        default = update(default, course)
        return default


def obj_to_arr(obj):
    """Convert dict to array"""
    if isinstance(obj, list):
        return obj
    arr = []
    for key in obj:
        arr.append(obj[key])
    return arr


def show_last_courses(scrape_dir):
    for c in LETTERS:
        print("LETTER", c)
        with open(os.path.join(scrape_dir, '{}.json'.format(c)), 'r') as f:
            data = json.load(f)
            if data:
                try:
                    print(data[-1]['details']['code'])
                except:
                    print(data[-1]['options'][0]['details']['code'])


def get_unique_id(course):
    details = course['details']
    items = [details['code'], details['career'], details['campus']]
    items = map(lambda x: x.replace(' ', ''), items)
    return "-".join(items)


def meeting_info_to_array(course):
    for i in range(len(course['offerings'])):
        sections = course['offerings'][i]['sections']
        for j in range(len(sections)):
            if isinstance(sections[j]['meeting_info'], collections.Mapping):
                course['offerings'][i]['sections'][j]['meeting_info'] = [
                    sections[j]['meeting_info']]
    return course


def sections_to_offerings(course):
    try:
        if 'sections' in course:
            course['offerings'] = []
            course['offerings'].append({
                'career': course['details']['career'],
                'campus': course['details']['campus'],
                'sections': course['sections']
            })
            del course['sections']
            del course['details']['career']
            del course['details']['campus']
            return course
        elif 'options' in course:
            options = course['options']
            course['description'] = options[0]['description']
            course['details'] = options[0]['details']
            course['enrollment_info'] = options[0]['enrollment_info']
            course['offerings'] = list(map(lambda x: {
                'career': x['details']['career'],
                'campus': x['details']['campus'],
                'sections': x['sections']
            }, options))
            del course['options']
            del course['details']['campus']
            del course['details']['career']
            return course
    except Exception as e:
        print(course)
        raise e


def group_by_term(course):
    """Group sections by term and output a new offering for each term"""

    updated_offerings = []
    for i in range(len(course['offerings'])):
        off = course['offerings'][i]
        sections = off['sections']
        if not sections:
            updated_offerings.append(off)
        grouped = itertools.groupby(sections, lambda x: x['details']['term'])
        for term, sections in grouped:
            updated_offerings.append({
                'term': term,
                'career': off['career'],
                'campus': off['campus'],
                'sections': [i for i in sections]
            })
    course['offerings'] = updated_offerings
    return course


def clean(scrape_dir, output_file, type='alpha'):
    all_data = []
    for fname in os.listdir(scrape_dir):
        with open(os.path.join(scrape_dir, fname), 'r') as f:
            courses = json.load(f)
            length = len(courses)
            for i in range(length):
                courses[i] = fill_with_defaults(courses[i])
                courses[i] = sections_to_offerings(courses[i])
                courses[i] = meeting_info_to_array(courses[i])
                # courses[i]['guid'] = get_unique_id(courses[i])
                courses[i]['code'] = trim_whitespace(
                    courses[i]['details']['code'])
                del courses[i]['details']['code']
                courses[i]['title'] = trim_whitespace(
                    courses[i]['details']['title'])
                del courses[i]['details']['title']
                courses[i] = group_by_term(courses[i])
            all_data += courses

    with open(output_file, 'w') as f:
        all_data.sort(key=lambda x: x['code'])
        # all_data = list(filter(lambda x: x['code'] == 'CISC 235', all_data))
        json.dump(all_data, f)
