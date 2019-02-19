import re
import purl
from jinja2 import Markup
from flask import request


def filter__is_current_nav(nav, main_nav=None):
    path = purl.URL(request.url).path()
    if 'full_matcher' in nav and nav['full_matcher']:
        return True if re.search(nav['full_matcher'], path) else False
    elif 'matcher' in nav and nav['matcher']:
        matcher = nav['matcher']
        if main_nav and 'matcher' in main_nav and main_nav['matcher']:
            matcher = main_nav['matcher'] + matcher
        return True if re.search(matcher, path) else False
    return False


global__main_navigation = [
    {
        'text': Markup('Best Community Service'),
        'route': "index.index",
        'route_params': None,
        'matcher': r'/',
        'full_matcher': None,
    },
    {
        'text': Markup('<i class="fa fa-sign-out" aria-hidden="true"></i> Log Out'),
        'route': 'user.logout',
        'route_params': None,
        'matcher': None,
        'full_matcher': None,
    }
]
