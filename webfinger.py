#!/usr/bin/env python

from copy import deepcopy
from collections import OrderedDict
import logging
import requests

__version__ = "2.0"

WEBFINGER_TYPE = "application/jrd+json"
LEGACY_WEBFINGER_TYPES = ["application/json"]

UNOFFICIAL_ENDPOINTS = {
    "facebook.com": "facebook-webfinger.appspot.com",
    "twitter.com": "twitter-webfinger.appspot.com",
}

REL_NAMES = {
    "http://activitystrea.ms/spec/1.0": "activity_streams",
    "http://webfinger.net/rel/avatar": "avatar",
    "http://microformats.org/profile/hcard": "hcard",
    "http://specs.openid.net/auth/2.0/provider": "open_id",
    "http://ns.opensocial.org/2008/opensocial/activitystreams": "opensocial",
    "http://portablecontacts.net/spec/1.0": "portable_contacts",
    "http://webfinger.net/rel/profile-page": "profile",
    "http://webfist.org/spec/rel": "webfist",
    "http://gmpg.org/xfn/11": "xfn",
}

RELS = {v: k for k, v in REL_NAMES.items()}

logger = logging.getLogger("webfinger")


class WebFingerException(Exception):
    pass


class WebFingerResponse(object):
    """ Response that wraps an RD object. It provides attribute-style access
        to links for specific rels, responding with the href attribute
        of the matched element.
    """

    def __init__(self, jrd):
        self.jrd = jrd

        try:
            self.subject = jrd["subject"]
        except IndexError:
            raise WebFingerException("subject is required in jrd")

        self.aliases = jrd.get("aliases", [])
        self.properties = jrd.get("properties", {})

        self.links = jrd.get("links", [])

        self.rels = OrderedDict()
        for link in self.links:
            rel = link.get("rel", None)
            rel = REL_NAMES.get(rel, rel)

            if rel not in self.rels:
                rel_list = self.rels[rel] = list()
            else:
                rel_list = self.rels[rel]

            rel_list.append(link)

    def rel(self, relation, attr="href"):
        if relation in REL_NAMES:
            relation = REL_NAMES[relation]

        if relation not in self.rels:
            return

        rel = self.rels[relation]

        if attr is not None:
            return [x[attr] for x in rel]

        return rel


class WebFingerClient(object):

    def __init__(self, timeout=None, official=False):
        self.official = official
        self.timeout = timeout

    def _parse_host(self, resource):
        host = resource.split("@")[-1]

        if host in UNOFFICIAL_ENDPOINTS and not self.official:
            unofficial_host = UNOFFICIAL_ENDPOINTS[host]
            logging.debug("host %s is not supported, using unofficial endpoint %s" % (host, unofficial_host))
            host = unofficial_host

        return host

    def finger(self, resource, host=None, rel=None, raw=False):
        if not host:
            host = self._parse_host(resource)

        url = "https://%s/.well-known/webfinger" % host

        headers = {
            "User-Agent": "python-webfinger/%s" % __version__,
            "Accept": WEBFINGER_TYPE,
        }

        params = {"resource": resource}
        if rel:
            params["rel"] = rel

        resp = requests.get(url, params=params, headers=headers, timeout=self.timeout, verify=True)
        logging.debug("fetching JRD from %s" % resp.url)

        content_type = resp.headers.get("Content-Type", "").split(";", 1)[0].strip()
        logging.debug("response content type: %s" % content_type)

        if content_type != WEBFINGER_TYPE and content_type not in LEGACY_WEBFINGER_TYPES:
            raise WebFingerException("Invalid response type from server")

        if raw:
            return resp.json()

        return WebFingerResponse(resp.json())


def finger(resource, rel=None):
    """ Convenience method for invoking WebFingerClient.
    """
    return WebFingerClient().finger(resource, rel=rel)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Simple webfinger client.")
    parser.add_argument("acct", metavar="URI", help="account URI")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", help="print debug logging output to console")
    parser.add_argument("-r", "--rel", metavar="REL", dest="rel", help="desired relation")

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
