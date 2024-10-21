import requests

from tools.user_agent import generate_headers


def get_proxied_session(proxy: str = None):
    session = requests.Session()
    if proxy:
        session.proxies = {
            'http': proxy,
            'https': proxy
        }
    session.headers.update(generate_headers())
    session.request = lambda *args, **kwargs: requests.Session.request(session, *args, timeout=60, **kwargs)
    return session
