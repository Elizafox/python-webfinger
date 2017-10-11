#!/usr/bin/env python3


"""WebFinger client implementation.

The top-level module contains BaseWebFingerClient, which is a basic interface
for other implementations.
"""

import abc

from webfinger import __version__ as version
from webfinger.objects import WebFingerResponse


class BaseWebFingerClient(abc.ABC):
    """The base WebFinger client interface

    All WebFinger clients implement at least this interface.
    """
    
    WEBFINGER_TYPE = "application/jrd+json"
    LEGACY_WEBFINGER_TYPES = ["application/json"]
    WEBFINGER_URL = "https://{host}/.well-known/webfinger"
    USER_AGENT = "Python-Webfinger/{version}".format(version=version)
    
    def parse_host(self, resource):
        """Parse WebFinger URI."""
        host = resource.split("@")[-1]
        return host

    def parse_response(self, response):
        """Parse WebFinger response."""
        return WebFingerResponse(response)

    @abc.abstractmethod
    def get(self, url, params, headers):
        """Perform HTTP request."""
        raise NotImplementedError

    @abc.abstractmethod
    def finger(self, resource, host=None, rel=None, raw=False, params=None,
               headers=None):
        """Perform finger on a given host."""
        raise NotImplementedError
