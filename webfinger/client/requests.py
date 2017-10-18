"""WebFinger client based around the requests library.

This module is probably what you want, if all you want is a working WebFinger
client.
"""


import requests
import logging

from webfinger.client import BaseWebFingerClient
from webfinger.exceptions import WebFingerHTTPError, WebFingerNetworkError, \
    WebFingerJRDError, WebFingerContentError


logger = logging.getLogger("webfinger.client.requests")


class WebFingerClient(BaseWebFingerClient):
    """An implementation of BaseWebFingerClient using requests..

    You can subclass this for your own needs.
    """

    def __init__(self, timeout=None, session=None):
        """Create a WebFingerClient instance.

        args:
        timeout - default timeout to use (default None)
        session - requests session to use (default is to create our own)
        """
        self.timeout = timeout
        self.session = session

    def __del__(self):
        self.close()

    def get(self, url, params, headers):
        """Perform HTTP request."""
        if self.session is None:
            # Lazily create session
            self.session = requests.Session()

        response = self.session.get(url, params=params, headers=headers,
                                    timeout=self.timeout, verify=True)
        response.raise_for_status()
        return response

    def close(self):
        """Close HTTP session"""
        if self.session:
            self.session.close()

    def parse_response(self, response):
        """Parse the response.

        This function is given a response object from requests. The parser
        parameter is not allowed with this method; it will be deduced.
        """
        try:
            content_type = response.headers["Content-Type"]
        except KeyError:
            raise WebFingerContentError("No Content-Type from server")

        content_type = response.headers["Content-Type"]
        content_type = content_type.split(";", 1)[0].strip()
        logger.debug("response content type: %s" % content_type)

        if content_type not in self.WEBFINGER_TYPES:
            raise WebFingerContentError("Unacceptable content type")

        parser = self.WEBFINGER_TYPES[content_type][1]
        return super().parse_response(response.text, parser)

    def finger(self, resource, host=None, rel=None, raw=False, params=dict(),
               headers=dict()):
        """Perform a WebFinger lookup.

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
            response = self.get(url, params, headers)
        except requests.exceptions.HTTPError as e:
            raise WebFingerHTTPError("Error with request", str(e)) from e
        except requests.exceptions.SSLError as e:
            raise WebFingerNetworkError("SSL error", str(e)) from e
        except Exception as e:
            raise WebFingerNetworkError("Could not connect", str(e)) from e

        if raw:
            return response.text

        return self.parse_response(response)
