"""WebFinger client implementation.

The top-level module contains BaseWebFingerClient, which is a basic interface
for other implementations.
"""

import abc

from webfinger import __version__ as version
from webfinger.objects.jrd import WebFingerJRD
from webfinger.exceptions import WebFingerContentError


class BaseWebFingerClient(abc.ABC):
    """The base WebFinger client interface

    All WebFinger clients implement at least this interface.
    """

    WEBFINGER_TYPES = {"application/jrd+json": (1, "json"),
                       "application/json": (0.9, "json"),
                       "application/xrd+xml": (0.5, "xml"),
                       "application/xml": (0.4, "xml")}
    """Webfinger MIME types, mapped to q values and parser type."""

    WEBFINGER_URL = "https://{host}/.well-known/webfinger"
    """Format of WebFinger endpoint."""

    USER_AGENT = "Python-Webfinger/{version}".format(version=version)
    """User agent to use."""

    JRD_OBJECT = WebFingerJRD
    """JRD object to use for parsing and emitting (default is WebFingerJRD)."""

    def generate_accept_header(self):
        """Generate an accept header."""
        return '; '.join("q={}, {}".format(v[0], k) for k, v in
                        self.WEBFINGER_TYPES.items())

    @staticmethod
    def parse_host(resource):
        """Parse WebFinger URI."""
        host = resource.split("@")[-1]
        return host

    def parse_response(self, response, parser):
        """Parse WebFinger response using the given parser."""
        parser_name = "from_{}".format(parser)
        parser = getattr(self.JRD_OBJECT, parser_name, None)
        assert parser is not None, "Invalid content type parser"
        return parser(response)

    @abc.abstractmethod
    def get(self, url, params, headers):
        """Perform HTTP request."""
        raise NotImplementedError

    @abc.abstractmethod
    def finger(self, resource, host=None, rel=None, raw=False, params=None,
               headers=None):
        """Perform finger on a given host."""
        raise NotImplementedError
