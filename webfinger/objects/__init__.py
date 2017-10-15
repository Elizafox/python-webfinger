"""WebFinger library objects.

This contains objects returned and used by the WebFinger library, including
helper objects.
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
"""URI to friendly name mapping."""

RELS = {v: k for k, v in REL_NAMES.items()}
"""Friendly name to URI mapping."""
