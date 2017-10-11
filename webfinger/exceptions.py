#!/usr/bin/env python3


"""WebFinger exceptions.

These are the exceptions raised by the WebFinger package.

The fundamental root of all WebFinger errors is the WebFingerException class.
"""


class WebFingerException(Exception):
    """Exception class for WebFinger errors.

    This can be raised due to content encoding or parsing errors.
    """


class WebFingerContentError(WebFingerException):
    """There was a problem with the WebFinger content.

    This error may be thrown if the server sends us the incorrect WebFinger
    content type.

    This is also the base class for WebFingerJRDError.
    """


class WebFingerJRDError(WebFingerContentError):
    """Error parsing the JRD.

    This could be due to expected elements that are missing, or the response
    is not a WebFinger response at all.
    """


class WebFingerNetworkError(WebFingerException):
    """An error occured on the network.

    This could be abrupt termination of the connection, or a connection could
    not be established.

    This is also the base class for WebFingerHTTPError.
    """


class WebFingerHTTPError(WebFingerNetworkError):
    """A bad HTTP response was received.

    Any HTTP code except 200 OK will cause this.
    """
