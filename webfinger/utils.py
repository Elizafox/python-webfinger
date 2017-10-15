#!/usr/bin/env python3

"""Internal utilities used around WebFinger.

Everthing in this module should be considered a private API.
"""

def is_uri(string):
    """Validate if the given string is a URI."""
    return ":" in string
