#!/usr/bin/env python3


"""A simple Python client implementation of WebFinger (RFC 7033).

WebFinger is a discovery protocol that allows you to find information about
people or things in a standardized way.
"""


from collections import OrderedDict

import logging
import requests


__version__ = "2.1"


logger = logging.getLogger("webfinger")


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


class WebFingerResponse(object):
    """Response that wraps an RD object.

    It stores the aliases, properties, and links fields from the JRD. If these
    are not present, the attributes are set to blank.

    For conveience, links are also stored in as lists in rels, using the rel
    attribute of links as a key (or None for links where rel is ommitted).
    URI's will be mapped to friendly attribute names if known (visible in the
    RELS attribute).
    """

    REL_NAMES = {
        "http://activitystrea.ms/spec/1.0": "activity_streams",
        "http://webfinger.net/rel/avatar": "avatar",
        "http://microformats.org/profile/hcard": "hcard",
        "http://specs.openid.net/auth/2.0/provider": "open_id",
        "http://ns.opensocial.org/2008/opensocial/activitystreams":
            "opensocial",
        "http://portablecontacts.net/spec/1.0": "portable_contacts",
        "http://webfinger.net/rel/profile-page": "profile",
        "http://webfist.org/spec/rel": "webfist",
        "http://gmpg.org/xfn/11": "xfn",
    }

    # Reverse mapping for convenience
    RELS = {v: k for k, v in REL_NAMES.items()}

    def __init__(self, jrd):
        """Initalise WebFingeResponse object with jrd.

        args:
        jrd - the JRD of the WebFinger response.
        """
        self.jrd = jrd

        try:
            self.subject = jrd["subject"]
        except KeyError:
            raise WebFingerJRDError("subject is required in jrd")

        self.aliases = jrd.get("aliases", [])
        self.properties = jrd.get("properties", {})
        self.links = jrd.get("links", [])
        self.rels = OrderedDict()
        for link in self.links:
            rel = link.get("rel", None)
            rel = self.REL_NAMES.get(rel, rel)

            if rel not in self.rels:
                rel_list = self.rels[rel] = list()
            else:
                rel_list = self.rels[rel]

            rel_list.append(link)

    def rel(self, relation, attr=None):
        """Return a given relation, with an optional attribute.

        If attr is not set, nothing is returned.
        """
        if relation in self.REL_NAMES:
            relation = self.REL_NAMES[relation]

        if relation not in self.rels:
            return

        rel = self.rels[relation]

        if attr is not None:
            return [x[attr] for x in rel]

        return rel


class WebFingerClient(object):
    """Class for requesting WebFinger lookups as a client.

    You can subclass this for your own needs.
    """

    WEBFINGER_TYPE = "application/jrd+json"
    LEGACY_WEBFINGER_TYPES = ["application/json"]
    WEBFINGER_URL = "https://{host}/.well-known/webfinger"
    USER_AGENT = "Python-Webfinger/{version}".format(version=__version__)

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

    def _parse_host(self, resource):
        """Parse WebFinger URI."""
        host = resource.split("@")[-1]
        return host

    def _parse_response(self, response):
        """Parse WebFinger response."""
        return WebFingerResponse(response)

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
            host = self._parse_host(resource)

        url = self.WEBFINGER_URL.format(host=host)

        params["resource"] = resource
        if rel:
            params["rel"] = rel

        resp = self.session.get(url, params=params, headers=headers,
                                timeout=self.timeout, verify=True)
        logging.debug("fetching JRD from %s" % resp.url)

        try:
            content_type = resp.headers["Content-Type"]
        except KeyError:
            raise WebFingerContentError("Invalid Content-Type from server",
                                        content_type)

        content_type = content_type.split(";", 1)[0].strip()
        logging.debug("response content type: %s" % content_type)

        if (content_type != self.WEBFINGER_TYPE and content_type not in
                self.LEGACY_WEBFINGER_TYPES):
            raise WebFingerContentError("Invalid Content-Type from server",
                                        content_type)

        response = resp.json()
        if raw:
            return response

        return self._parse_response(response)


_client = WebFingerClient()


def finger(resource, rel=None):
    """Invoke finger without creating a WebFingerClient instance.

    args:
    resource - resource to look up
    rel - relation to request from the server
    """
    return _client.finger(resource, rel=rel)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Simple webfinger client.")
    parser.add_argument("acct", metavar="URI", help="account URI")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                        help="print debug logging output to console")
    parser.add_argument("-r", "--rel", metavar="REL", dest="rel",
                        help="desired relation")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    wf = finger(args.acct, rel=args.rel)

    print("--- %s ---" % wf.subject)

    if args.rel:

        link = wf.rel(args.rel)

        if link is None:
            print("*** Link not found for rel=%s" % args.rel)

        print("%s:\n\t%s" % (args.rel, link))

    else:

        print("Activity Streams:  ", wf.activity_streams)
        print("Avatar:            ", wf.avatar)
        print("HCard:             ", wf.hcard)
        print("OpenID:            ", wf.open_id)
        print("Open Social:       ", wf.opensocial)
        print("Portable Contacts: ", wf.portable_contacts)
        print("Profile:           ", wf.profile)
        print("WebFist:           ", wf.webfist)
        print("XFN:               ", wf.rel("http://gmpg.org/xfn/11"))
