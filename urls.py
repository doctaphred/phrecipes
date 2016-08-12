from urllib.parse import ParseResult, urlencode, urlparse, urlunparse


def url(scheme='', netloc='', path='', params='', query=(), fragment=''):
    """Construct a URL from individual components.

    <scheme>://<netloc>/<path>;<params>?<query>#<fragment>

    Args:
        schema: "http", "https", etc
        netloc: aka "host"
        path: "/path/to/resource". Leading slash is automatic.
        params: Rarely used; you probably want query.
        query: May be a dict or a sequence of 2-tuples.
        fragment: Position on page; usually used only by the browser.
    """
    return urlunparse(
        (scheme, netloc, path, params, urlencode(query), fragment))


def alter_url(url, **components):
    """
    >>> alter_url('http://placekitten.com', path='200/300')
    'http://placekitten.com/200/300'
    """
    original = urlparse(url)._asdict()
    original.update(components)
    return ParseResult(**original).geturl()


def query_string(**kwargs):
    return '?' + urlencode(kwargs)
