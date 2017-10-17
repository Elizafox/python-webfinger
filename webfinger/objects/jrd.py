"""WebFinger JRD object.

This class contains the WebFinger JRD object, which can contain a response to
a request, or be used to build a response.
"""


import json

from xml.etree import ElementTree
from collections import OrderedDict
from collections.abc import Mapping

from defusedxml import ElementTree as DefusedElementTree

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
        if not isinstance(jrd, Mapping):
            raise WebFingerJRDError("JRD must be a Mapping")

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
    def from_json(cls, text):
        try:
            jrd = json.loads(text)
        except Exception as e:
            raise WebFingerJRDError("error parsing JRD") from e

        return cls(jrd)

    @classmethod
    def from_xml(cls, text):
        XMLNSMAP = {"XRD": 'http://docs.oasis-open.org/ns/xri/xrd-1.0'}

        def parse_properties(node):
            ret = {}
            properties = node.findall("XRD:Property", XMLNSMAP)
            if not properties:
                return ret

            for property in properties:
                if "type" not in property.attrib:
                    raise WebFingerJRDError("type is required with property")

                key = property.attrib["type"]
                has_nil = property.attrib.get("xsi:nil", "").lower()
                if has_nil and has_nil == "true":
                    value = None
                else:
                    value = property.text

                ret[key] = value

            return ret

        try:
            root = DefusedElementTree.fromstring(text)
        except Exception as e:
            # TODO - better error
            raise WebFingerJRDERror("error parsing XRD") from e

        subject = root.find("XRD:Subject", XMLNSMAP)
        if subject is None:
            raise WebFingerJRDError("subject is required")

        jrd = {"subject": subject.text}

        aliases = root.findall("XRD:Alias", XMLNSMAP)
        if aliases:
            aliases_jrd = jrd["aliases"] = []
            for alias in aliases:
                if not alias.text:
                    # TODO - better error
                    raise WebFingerJRDError("alias had no content")
                aliases_jrd.append(alias.text)

        properties = parse_properties(root)
        if properties:
            jrd["properties"] = properties

        links = root.findall("XRD:Link", XMLNSMAP)
        if links:
            links_jrd = jrd["links"] = []
            for link in links:
                link_jrd = {}

                # Retrieve basic attributes
                for attrib, value in link.attrib.items():
                    link_jrd[attrib] = value

                # Properties
                properties = parse_properties(link)
                if properties:
                    link_jrd["properties"] = properties

                # Titles
                titles = link.findall("XRD:Title", XMLNSMAP)
                if titles:
                    titles_jrd = jrd["titles"] = {}
                    for title in titles:
                        lang = title.attrib.get("xml:lang", "und")
                        title = title.text
                        titles_jrd[title] = lang

                links_jrd.append(link_jrd)

        # TODO - any other elements
        return cls(jrd)

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

    def to_xml(self):
        """Convert JRD into XML"""
        def serialise_property(node, properties):
            for tag, value in properties.items():
                elem = ElementTree.SubElement("Property", {"type": tag})
                if value is not None:
                    elem.text = value
                else:
                    elem.attrib["xsi:nil"] = "true"

        tree = ElementTree.TreeBuilder()
        root = tree.start("XRD",
            {"xmlns": "http://docs.oasis-open.org/ns/xri/xrd-1.0"})

        subject = ElementTree.SubElement(root, "Subject")
        subject.text = self.subject

        for a in self.aliases:
            alias = ElementTree.SubElement(root, "Alias")
            alias.text = a

        serialise_property(root, self.properties)

        for l in self.links:
            link = ElementTree.SubElement(root, "Link")

            # XXX this is all really ugly!
            for elem, attr in l.items():
                if isinstance(attr, str):
                    # Set as simple attribute
                    link.attrib[elem] = attr
                elif isinstance(attr, Mapping):
                    # Serialise as a property
                    if elem.lower() == "titles":
                        # Serialise as titles
                        for title, language in v.items():
                            title_elem = ElementTree.SubElement(link, "Title",
                                {"xml:lang": language})
                            title_elem.text = title
                    elif elem.lower() == "properties":
                        # Serialise properties
                        serialise_property(link, attr)
                    else:
                        # TODO - better error
                        raise WebFingerJRDError(
                            "Can't serialise link attribute", elem, attr)
                else:
                    # TODO - better error
                    raise WebFingerJRDError("Can't serialise type into XML",
                        type(attr), attr)

        # TODO - serialise other elements

        try:
            return ElementTree.tostring(tree.close(), encoding="unicode")
        except Exception as e:
            # TODO - better error
            raise WebFingerJRDError("Could not serialise into XML", e) from e

    def __str__(self):
        return self.to_json()
