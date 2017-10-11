#!/usr/bin/env python3


"""WebFinger client based around the requests library.

This module is probably what you want, if all you want is a working WebFinger
client.
"""


import requests
import logging

from webfinger.client import BaseWebFingerClient
from webfinger.objects import WebFingerResponse
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
        if session is None:
            session = self.session = requests.Session()
        else:
            self.session = session

        headers = session.headers
        headers["User-Agent"] = self.USER_AGENT
        headers["Accept"] = self.WEBFINGER_TYPE

    def __del__(self):
        self.close()

    def get(self, url, params, headers):
        """Perform HTTP request."""
        resp = self.session.get(url, params=params, headers=headers,
                                timeout=self.timeout, verify=True)
        resp.raise_for_status()
        return resp

    def close(self):
        """Close HTTP session"""
        self.session.close()

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

        logger.debug("fetching JRD from %s" % url)
        try:
            resp = self.get(url, params, headers)
        except requests.exceptions.HTTPError as e:
            raise WebFingerHTTPError("Error with request", str(e)) from e
        except requests.exceptions.SSLError as e:
            raise WebFingerNetworkError("SSL error", str(e)) from e
        except Exception as e:
            raise WebFingerNetworkError("Could not connect", str(e)) from e

        try:
            content_type = resp.headers["Content-Type"]
        except KeyError:
            raise WebFingerContentError("Invalid Content-Type from server",
                                        content_type)

        content_type = content_type.split(";", 1)[0].strip()
        logger.debug("response content type: %s" % content_type)

        if (content_type != self.WEBFINGER_TYPE and content_type not in
                self.LEGACY_WEBFINGER_TYPES):
            raise WebFingerContentError("Invalid Content-Type from server",
                                        content_type)

        response = resp.json()
        if raw:
            return response

        return self.parse_response(response)
