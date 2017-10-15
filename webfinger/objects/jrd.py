#!/usr/bin/env python3


"""WebFinger JRD object.

This class contains the WebFinger JRD object, which can contain a response to
a request, or be used to build a response.
"""


import json

from collections import OrderedDict
from collections.abc import Mapping

from webfinger.exceptions import WebFingerJRDError
from webfinger.objects import RELS, REL_NAMES
from webfinger.objects.link import WebFingerLink
from webfinger.utils import is_uri


class WebFingerJRD:
    """Wrapper around a JRD object.

    It stores the aliases, properties, and links fields from the JRD. If these
    are not present, the attributes are set to blank.

    For convenience, links are also stored in as lists in rels, using the rel
    attribute of links as a key (or None for links where rel is ommitted).
    URI's will be mapped to friendly attribute names if known.

    The add_* methods can be used to update the JRD with various attributes.
    A JSON representation can be retrieved with the to_json() method.
    """

    def __init__(self, jrd):
        """Initalise WebFingerJRD object with jrd.

        args:
        jrd - the JRD of the WebFinger response.
        """
        if isinstance(jrd, str):
            try:
                jrd = json.loads(jrd)
            except Exception as e:
                raise WebFingerJRDError("error parsing JRD") from e
        elif not isinstance(jrd, Mapping):
            raise WebFingerJRDError("JRD must be a mapping or a string")

        self.jrd = jrd

        try:
            self.subject = jrd["subject"]
        except Exception as e:
            raise WebFingerJRDError("subject is required in JRD") from e

        self.aliases = jrd.get("aliases", [])

        self.properties = jrd.get("properties", {})

        self.links = []
        for link in jrd.get("links", []):
            self.links.append(WebFingerLink(**link))

        # Create rels list
        self.link_rels = OrderedDict()
        for link in self.links:
            rel = REL_NAMES.get(link.rel, link.rel)

            if rel not in self.link_rels:
                rel_list = self.link_rels[rel] = list()
            else:
                rel_list = self.link_rels[rel]

            rel_list.append(link)

    @classmethod
    def build(cls, subject):
        """Create a WebFingerJRD object based around the given subject.

        args:
        subject - subject of the JRD
        """
        if "@" not in subject:
            raise WebFingerJRDError("subject must be in user@host format")

        if not isinstance(subject, str):
            raise WebFingerJRDError("subject must be a string")

        if not subject.startswith("acct:"):
            subject = "acct:" + subject

        return cls({"subject": subject})
    
    def rel(self, relation, attr=None):
        """Return a given relation, with an optional attribute.

        If attr is not set, nothing is returned.
        """
        if relation in REL_NAMES:
            relation = REL_NAMES[relation]

        if relation not in self.link_rels:
            return

        rel = self.link_rels[relation]

        if attr is not None:
            return [x[attr] for x in rel]

        return rel

    # NOTE: all add_* methods must maintain their relevant instance variables,
    # as well as update the JRD object.

    def add_alias(self, alias):
        """Add an alias to the JRD.

        args:
        alias - the alias to add to the JRD. Must be a string and a valid URI.
        """
        if "aliases" not in self.jrd:
            self.jrd["aliases"] = []

        if not isinstance(alias, str):
            raise WebFingerJRDError("alias must be a string")

        if not is_uri(alias):
            raise WebFingerJRDError("alias must be a URI")

        self.aliases.append(alias)
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

        if not is_uri(uri):
            raise WebFingerJRDError("uri must be a URI")

        if not isinstance(value, (str, type(None))):
            raise WebFingerJRDError("value for uri must be a string or None")

        self.properties[uri] = value
        self.jrd["properties"][uri] = value

    def add_link(self, rel, *, type=None, href=None, titles=None,
                 properties=None, misc=dict(), **kwargs):
        """Add a link to the JRD.

        args:
        rel - the relation type of the link
        type - MIME type the dereferencing link
        href - target URI of the link
        properties - mapping (both keys and values must be strings) containing
                     URI's and values
        misc - a mapping of other items to add to the link
        kwargs - other items to add to the link
        """
        if "links" not in self.jrd:
            self.jrd["links"] = []

        if rel in RELS:
            # Convert rel into URI
            rel = RELS[rel]

        if not is_uri(rel):
            raise WebFingerJRDError("rel must be a valid URI")

        args = {"rel": rel}

        if type:
            args["type"] = type

        if href:
            args["href"] = href

        if titles:
            args["titles"] = titles

        if properties:
            args["properties"] = properties
        
        if not isinstance(misc, Mapping):
            raise WebFingerJRDError("misc must be a mapping")

        args.update(misc)
        args.update(kwargs)
        
        self.links.append(WebFingerLink(**args))
        self.jrd["links"].append(args)

    def add_misc(self, key, value):
        """Add an otherwise unknown key and value to the JRD."""
        self.jrd[key] = value

    def to_json(self):
        """Convert JRD into a json string."""
        return json.dumps(self.jrd)

    def __str__(self):
        return self.to_json()
