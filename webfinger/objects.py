#!/usr/bin/env python3


"""WebFinger fundamental objects.

This at present only contains the WebFingerResponse class.
"""


from collections import OrderedDict

from webfinger.exceptions import WebFingerJRDError


__version__ = "2.2dev"


class WebFingerResponse:
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
