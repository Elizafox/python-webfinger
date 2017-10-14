#!/usr/bin/env python3


"""WebFinger fundamental objects.

This at present only contains the WebFingerResponse class.
"""


import json

from collections import OrderedDict
from collections.abc import Mapping

from webfinger.exceptions import WebFingerJRDError


__version__ = "2.2dev"

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
"""URI to friendly name mapping."""

RELS = {v: k for k, v in REL_NAMES.items()}
"""Friendly name to URI mapping."""


class WebFingerResponse:
    """Response that wraps an RD object.

    It stores the aliases, properties, and links fields from the JRD. If these
    are not present, the attributes are set to blank.

    For conveience, links are also stored in as lists in rels, using the rel
    attribute of links as a key (or None for links where rel is ommitted).
    URI's will be mapped to friendly attribute names if known.
    """

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
            rel = REL_NAMES.get(rel, rel)

            if rel not in self.rels:
                rel_list = self.rels[rel] = list()
            else:
                rel_list = self.rels[rel]

            rel_list.append(link)

    def rel(self, relation, attr=None):
        """Return a given relation, with an optional attribute.

        If attr is not set, nothing is returned.
        """
        if relation in REL_NAMES:
            relation = REL_NAMES[relation]

        if relation not in self.rels:
            return

        rel = self.rels[relation]

        if attr is not None:
            return [x[attr] for x in rel]

        return rel


class WebFingerBuilder:
    """Build up a JRD response to a WebFinger request.

    This class is designed to be used in servers, to make it easier to create
    a WebFinger server.
    """

    def __init__(self, subject):
        """Initalise a WebFingerBuilder object.

        args:
        subject - subject of the JRD
        """
        if "@" not in subject:
            raise WebFingerJRDError("subject must be in user@host format")

        if not isinstance(subject, str):
            raise WebFingerJRDError("subject must be a string")

        if not subject.startswith("acct:"):
            subject = "acct:" + subject

        self.jrd = {"subject": subject}

    @staticmethod
    def _is_uri(uri):
        # Super basic check
        return ":" in uri

    def add_alias(self, alias):
        """Add an alias to the JRD.

        args:
        alias - the alias to add to the JRD. Must be a string and a valid URI.
        """
        if "aliases" not in self.jrd:
            self.jrd["aliases"] = []

        if not isinstance(alias, str):
            raise WebFingerJRDError("alias must be a string")

        if not self._is_uri(alias):
            raise WebFingerJRDError("alias must be a URI")

        self.jrd["aliases"].append(alias)

    def add_property(self, uri, value=None):
        """Add a property to the JRD.

        args:
        uri - uri for the property
        value - value to assign for the property; must be either a string or
                None
        """
        if "properties" not in self.jrd:
            self.jrd["properties"] = {}

        if not isinstance(uri, str):
            raise WebFingerJRDError("uri must be a string")

        if not isinstance(value, (str, None)):
            raise WebFingerJRDError("value for uri must be a string or None")

        if not self._is_uri(uri):
            raise WebFingerJRDError("uri must be a URI")

        self.jrd["properties"][uri] = value

    def add_link(self, rel, type, href, titles, properties, misc=None):
        """Add a link to the JRD.

        args:
        rel - the relation type of the link
        type - MIME type the dereferencing link
        href - target URI of the link
        properties - mapping (both keys and values must be strings) containing
                     URI's and values
        misc - a mapping of other items to add to the link
        """
        if "links" not in self.jrd:
            self.jrd["links"] = []

        link = {}

        if rel in RELS:
            # Convert rel into URI
            rel = RELS[rel]

        link["rel"] = rel

        if type:
            if not isinstance(type, str):
                raise WebFingerJRDError("type must be a string")

            link["type"] = type

        if href:
            if not isinstance(href, str):
                raise WebFingerJRDError("href must be a string")

            if not self._is_uri(href):
                # Really basic check
                raise WebFingerJRDError("href must be a valid URI")

            link["href"] = href

        if titles:
            if not isinstance(titles, Mapping):
                raise WebFingerJRDError("titles must be a mapping")

            for k, v in titles.items():
                if not isinstance(k, str):
                    raise WebFingerJRDError("title keys must be strings", k)

                if not isinstance(v, str):
                    raise WebFingerJRDError("title values must be strings", v)

            link["titles"] = titles

        if properties:
            if not isinstance(properties, Mapping):
                raise WebFingerJRDError("properties must be a mapping")

            for k, v in properties.items():
                if not isinstance(k, str):
                    raise WebFingerJRDError("property keys must be strings",
                                            k)

                if not isinstance(v, (str, None)):
                    raise WebFingerJRDError(
                        "property values must be either strings or None", v)

            link["properties"] = properties

        if misc:
            if not isinstance(misc, Mapping):
                raise WebFingerJRDError("misc must be a mapping")

            for k, v in misc.items():
                link[k] = v

        self.jrd["links"].append(link)

    def add_misc(self, key, value):
        """Add an otherwise unknown key and value to the JRD."""
        self.jrd[key] = value

    def to_json(self):
        """Convert JRD into a json string."""
        return json.dumps(self.jrd)

    def __str__(self):
        return self.to_json()
