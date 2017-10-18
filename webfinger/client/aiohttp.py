"""WebFinger client based around the aiohttp library.

This module requires Python 3.4 or later and aiohttp.
"""


import asyncio
import logging

import aiohttp

from webfinger.client import BaseWebFingerClient
from webfinger.exceptions import WebFingerHTTPError, WebFingerNetworkError, \
    WebFingerJRDError, WebFingerContentError


logger = logging.getLogger("webfinger.client.aiohttp")


class WebFingerClient(BaseWebFingerClient):
    """An implementation of BaseWebFingerClient using aiohttp.

    You can subclass this for your own needs.
    """

    def __init__(self, timeout=None, session=None):
        """Create a WebFingerClient instance.

        args:
        timeout - timeout to use (default None)
        session - aiohttp ClientSession to use (default is to create our own
                  with the default event loop)
        """
        self.timeout = timeout
        self.session = session

    @asyncio.coroutine
    def get(self, url, params, headers):
        """Perform HTTP request."""
        if self.session is None:
            # Create transient session (done here and not __init__ to avoid
            # ResourceWarning)
            self.session = aiohttp.ClientSession()

        with aiohttp.Timeout(self.timeout):
            response = yield from self.session.get(url, params=params,
                                                   headers=headers)
            response.raise_for_status()

        return response

    @asyncio.coroutine
    def close(self):
        """Close HTTP session and perform any cleanup actions"""
        if self.session:
            yield from self.session.close()

    @asyncio.coroutine
    def parse_response(self, response):
        """Parse the response.

        This is specially optimised for JSON parsing.

        This function is given a response object from aiohttp. The parser
        parameter is not allowed with this method; it will be deduced.
        """
        content_type = response.headers["Content-Type"]
        content_type = content_type.split(";", 1)[0].strip()
        logger.debug("response content type: %s" % content_type)

        if content_type not in self.WEBFINGER_TYPES:
            raise WebFingerContentError("Unacceptable content type")

        parser = self.WEBFINGER_TYPES[content_type][1]
        if parser == "json":
            json = yield from response.json(content_type=None)
            return WebFingerJRD(json)
        else:
            text = yield from response.text()
            return super().parse_response(text, parser)

    @asyncio.coroutine
    def finger(self, resource, host=None, rel=None, raw=False, params=dict(),
               headers=dict()):
        """Perform a WebFinger lookup.

        This method is a coroutine.

        args:
        resource - resource to look up
        host - host to use for resource lookup
        rel - relation to request
        raw - return unparsed JRD
        params - HTTP parameters to pass (note: resource and rel will be
                 overwritten)
        headers - HTTP headers to send with the request
        """
        if not host:
            host = self.parse_host(resource)

        url = self.WEBFINGER_URL.format(host=host)

        params["resource"] = resource
        if rel:
            params["rel"] = rel

        headers["User-Agent"] = self.USER_AGENT
        headers["Accept"] = self.generate_accept_header()

        logger.debug("fetching JRD from %s" % url)
        try:
            response = yield from self.get(url, params, headers)
        except aiohttp.ClientResponseError as e:
            raise WebFingerHTTPError("Error with request", str(e)) from e
        except Exception as e:
            raise WebFingerNetworkError("Could not connect", str(e)) from e

        if raw:
            response = yield from response.text()
            return response

        response = yield from self.parse_response(response)
        return response
