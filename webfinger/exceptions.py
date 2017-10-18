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


class WebFingerRDError(WebFingerContentError):
    """Error parsing an RD.

    This could be due to expected elements that are missing, or the response
    is not a WebFinger response at all.

    This is intended for use as a base class.
    """


class WebFingerJRDError(WebFingerRDError):
    """Error parsing a JRD.

    This could be due to expected elements that are missing, or the response
    is not a WebFinger response at all. The response may also be an XRD, not
    a JRD.
    """


class WebFingerXRDError(WebFingerRDError):
    """Error parsing an XRD

    This could be due to expected elements that are missing, or the response
    is not a WebFinger response at all. The response may also be a JRD, not an
    XRD.
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
