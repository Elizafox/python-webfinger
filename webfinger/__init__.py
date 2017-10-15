"""A simple Python client implementation of WebFinger (RFC 7033).

WebFinger is a discovery protocol that allows you to find information about
people or things in a standardized way.

This package provides a few tools for using WebFinger, including:
    - requests-based webfinger client (webfinger.client.requests.WebFingerClient)
    - aiohttp-based webfinger client(webfinger.client.aiohttp.WebFingerClient)
    - a class to build WebFinger JRD's (webfinger.objects.WebFingerBuilder)

In this module, the following are exposed:
    - BaseWebFingerClient (from webfinger.client)
    - WebFingerClient (from webfinger.client.requests  for backwards
      compatibility)
    - The WebFingerJRD object (from webfinger.objects.jrd)
    - Exceptions (from webfinger.exceptions)
    - A simple helper for basic finger requests (the finger function)
"""


__version__ = "3.0.0.dev1"


from webfinger.client import BaseWebFingerClient
from webfinger.client.requests import WebFingerClient
from webfinger.objects import RELS, REL_NAMES
from webfinger.objects.jrd import WebFingerJRD
from webfinger.exceptions import *


_client = WebFingerClient()


def finger(resource, rel=None):
    """Invoke finger without creating a WebFingerClient instance.

    args:
    resource - resource to look up
    rel - relation to request from the server
    """
    return _client.finger(resource, rel=rel)
