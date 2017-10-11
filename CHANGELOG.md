# Change log

# v2.1
Version 2.1 is a bugfix and minor feature update.

You should use this instead of v2.0.

## Major changes
- Fix host parsing bug in 2.0
- Create an exception hierarchy; WebFingerException can still be caught
..- New exceptions include `WebFingerContentError`, `WebFingerJRDError`, `WebFingerNetworkError`, and `WebFingerHTTPError`
- Allow custom `requests` sessions to be passed into WebFingerClient
- Allow custom headers for the request to be passed in

# v2.0
Version 2.0 is the first release of webfinger2 (for continuity with the original webfinger package).

## Major changes
- Attribute access is gone, since it's a messy hack; use the new `WebFingerResponse.rels` dictionary
- `WebFingerResponse.rel` returns a list, since duplicate rels can happen
- New `WebFingerResponse.rels` dictionary which contains links by their rels
- Remove support for unofficial endpoints since they rely on webfist (which has little support and is beyond the scope of this library)
- Move a few global variables into `WebFingerClient` class and create new class attributes
..- Move `RELS`, `WEBFINGER\_TYPE`, and `LEGACY\_WEBFINGER\_TYPES` into `WebFingerClient` class as static attributes
..- Create new `REL\_NAMES` attribute as a reverse mapping of the `RELS` attribute.
..- Create `WEBFINGER\_URL` static attribute in WebFinger client to allow customisation of WebFinger endpoint
..- Create `USER\_AGENT` static attribute to allow customisation of WebFinger user agent

## Minor changes
- Make `aliases`, `properties`, `links`, and `subject` proper attributes, not properties
- Fix testsuite
- Minor cleanups
