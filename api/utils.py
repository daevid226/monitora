from functools import lru_cache
from posixpath import join as path_urljoin

import httpx
import requests
from fake_headers import Headers
from monitora.settings import REQUEST_TIMEOUT
from requests import PreparedRequest
from urljoin import url_path_join


@lru_cache
def is_http2(url: str, timeout=REQUEST_TIMEOUT) -> bool:
    with httpx.Client(http2=True, timeout=timeout) as client:
        response = client.get(url)
        print(f"URL: {response.url} HTTP VERSION: {response.http_version}")
        return response.http_version.find("2") != -1


def url_join(url, *urls, **query):
    if urls:
        url = url_path_join(url, path_urljoin(*urls))
    if query:
        req = PreparedRequest()
        req.prepare_url(url, query)
        url = req.url
    return url


@lru_cache
def get_fake_header():
    header = Headers(browser="chrome", os="win", headers=True)
    return header.generate()


def send_request(url, **kwargs):
    timeout = kwargs.get("timeout", REQUEST_TIMEOUT)
    request_kwargs = {
        "url": url,
        "method": kwargs.get("method", "get"),
        "timeout": timeout,
        "headers": kwargs.get("header", get_fake_header()),
        "follow_redirects": True,
        **kwargs,
    }

    if is_http2(url, timeout=timeout):
        with httpx.Client() as client:
            response = client.request(**request_kwargs)
            if response.status_code != 200:
                raise requests.HTTPError("Failed status code")
            content = response.text
    else:
        response = requests.request(**request_kwargs)
        response.raise_for_status()
        content = response.text

    return content
