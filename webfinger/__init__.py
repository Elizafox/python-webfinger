"""A simple Python client implementation of WebFinger (RFC 7033).

WebFinger is a discovery protocol that allows you to find information about
people or things in a standardized way.
"""


__version__ = "3.0.0dev0"


# Backwards compatibility stubs
from webfinger.client.requests import WebFingerClient
from webfinger.exceptions import *


_client = WebFingerClient()


def finger(resource, rel=None):
    """Invoke finger without creating a WebFingerClient instance.

    args:
    resource - resource to look up
    rel - relation to request from the server
    """
    return _client.finger(resource, rel=rel)
