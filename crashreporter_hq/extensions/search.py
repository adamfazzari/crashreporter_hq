import requests

STACKOVERFLOW_QUERY = 'http://stackoverflow.com/search?q=%s'
GOOGLE_QUERY = 'http://www.google.com/#q=%s'

_queries = {'google': GOOGLE_QUERY,
            'stackoverflow': STACKOVERFLOW_QUERY}


def get_search_link(query, searchstring):
    _string = searchstring.replace(' ', '+')
    return _queries[query] % _string


def search_stackoverflow(query, searchstring):
    response = requests.get(get_search_link(query, searchstring))
    return response
