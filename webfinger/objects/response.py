#!/usr/bin/env python3


"""WebFinger response objects.

This contains the WebFingerResponse class, used to (obviously) store WebFinger
responses.
"""


import json

from collections import OrderedDict

from webfinger.exceptions import WebFingerJRDError
from webfinger.objects import RELS, REL_NAMES


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
        if isinstance(jrd, str):
            try:
                jrd = json.loads(jrd)
            except Exception as e:
                raise WebFingerError("error parsing JRD") from e

        self.jrd = jrd

        try:
            self.subject = jrd["subject"]
        except KeyError:
            raise WebFingerJRDError("subject is required in JRD")
        except Exception as e:
            raise WebFingerJRDError("malformed JRD") from e

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
