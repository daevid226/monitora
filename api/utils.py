import asyncio
import functools
from functools import lru_cache
from posixpath import join as path_urljoin
from urllib.parse import urlsplit

import httpx
import requests
from cache import AsyncLRU
from fake_headers import Headers
from monitora.settings import REQUEST_TIMEOUT
from requests import PreparedRequest
from urljoin import url_path_join


def get_host_name(url):
    return "{0.scheme}://{0.netloc}/".format(urlsplit(url))
    
def async_wrap(func):
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run

def _is_http2(response):
    return response.http_version.find("2") != -1
    

@lru_cache(maxsize=300)
def is_http2(url: str, timeout=REQUEST_TIMEOUT) -> bool:
    with httpx.Client(http2=True, timeout=timeout) as client:
        response = client.get(url)
        return _is_http2(response)

@AsyncLRU(maxsize=300)
async def is_http2_async(url: str, timeout=REQUEST_TIMEOUT) -> bool:
    async with httpx.AsyncClient(http2=True, timeout=timeout) as client:
        response = await client.get(url)
        return _is_http2(response)
    

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

def _get_request_kwargs(url, **kwargs):
    timeout = kwargs.get("timeout", REQUEST_TIMEOUT)
    return {
        "url": url,
        "method": kwargs.get("method", "get"),
        "timeout": timeout,
        "headers": kwargs.get("header", get_fake_header()),
        "follow_redirects": True,
        **kwargs,
    }


def send_request(url, **kwargs):
    request_kwargs = _get_request_kwargs(url, **kwargs)
    
    if is_http2(get_host_name(url), timeout=request_kwargs["timeout"]):
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


async def send_request_async(url, **kwargs):
    request_kwargs = _get_request_kwargs(url, **kwargs)
    # only HTTP2 
    async with httpx.AsyncClient(http2=True, timeout=request_kwargs["timeout"]) as client:
        response = await client.request(**request_kwargs)
        if response.status_code != 200:
            raise requests.HTTPError("Failed status code")
        content = response.text
        print(url) 

    return content

