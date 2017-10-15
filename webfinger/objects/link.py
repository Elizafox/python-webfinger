"""WebFinger link object.

The links attr of the RD has numerous attrs, which are useful to
abstract. The WebFingerLinks object serves this role.
"""

from collections.abc import Mapping, MutableMapping

from webfinger.exceptions import WebFingerJRDError
from webfinger.utils import is_uri


class WebFingerLink(MutableMapping):
    """WebFinger links attr of the JRD.

    WebFinger JRD's may contain links attrs, which are lists of links and
    various metadata associated with said links. This object provides an
    abstraction to these objects.

    This object provides both attr-based access and mapping-based access.
    """

    def __init__(self, rel, *, type=None, href=None, titles=None,
                 properties=None, **kwargs):
        """Initalise the WebFingerLink object.

        args:
        rel - relation of the link; this is required
        
        keyword arguments:
        type - expected MIME type of the link
        href - URI for the link
        titles - a mapping of titles of the object to languages
        properties - a mapping of given properties of the subject

        All other arguments are set as attrs on this object.
        """
        self._link = {"rel": rel}

        if type is not None:
            if not isinstance(type, str):
                raise WebFingerJRDError("type must be a string")

            self._link["type"] = type

        if href is not None:
            if not isinstance(href, str):
                raise WebFingerJRDError("href must be a string")

            if not is_uri(href):
                raise WebFingerJRDError("href must be a valid URI")

            self._link["href"] = href

        if titles is not None:
            if not isinstance(titles, Mapping):
                raise WebFingerJRDError("titles must be a mapping")

            for k, v in titles.items():
                if not isinstance(k, str):
                    raise WebFingerJRDError("title must be a string")

                if not isinstance(v, str):
                    raise WebFingerJRDError("title language must be a string")

            self._link["titles"] = titles

        if properties is not None:
            if not isinstance(properties, Mapping):
                raise WebFingerJRDError("properties must be a mapping")

            for k, v in properties.items():
                if not is_uri(k):
                    raise WebFingerJRDError("properties keys must be URI's")

                if not isinstance(v, str) or v is not None:
                    raise WebFingerJRDError(
                        "properties values must be strings, or None", v)

            self._link["properties"] = properties

        for k, v in kwargs.items():
            # No validation performed on other items
            self._link[k] = v

    def __getattr__(self, attr):
        return self._link[attr]

    def __getitem__(self, key):
        return self._link[key]

    def __setitem__(self, key, value):
        self._link[key] = value

    def __delitem__(self, key):
        del self._link[key]

    def __iter__(self):
        return iter(self._link)

    def __len__(self):
        return len(self._link)
