from urllib.parse import urlencode


base_url = 'https://www.google.com/maps/search/'


def google_maps_link(query):
    """Create a valid Google Maps URL for the given search query.

    See https://developers.google.com/maps/documentation/urls/guide

    >>> google_maps_link('CenturyLink Field')
    'https://www.google.com/maps/search/?api=1&query=CenturyLink+Field'
    >>> google_maps_link('City Hall, New York, NY')
    'https://www.google.com/maps/search/?api=1&query=City+Hall%2C+New+York%2C+NY'
    """
    return base_url + '?' + urlencode({'api': 1, 'query': query})
