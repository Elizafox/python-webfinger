# Change log

# v3.0.0dev1
Version 3.0.0dev1 is a development marker and not an actual release.

## Major changes
- Move `RELS` and `REL\_NAMES` out of the `WebFingerResponse` object
- New `WebFingerBuilder` class for constructing WebFinger JRDs
- `webfinger.objects` has been split into the `response` and `builder` submodules

## Minor changes
- Sessions are lazily created in all backends now, if one is not passed in
- More unit tests

# v3.0.0dev0
Version 3.0.0dev0 is a development marker and not an actual release.

## Major changes
- Now follows semantic versioning
- Restructure package from single file, should be mostly backwards-compatible
- `\_parse_headers` and `\_parse_host` methods have leading underscore removed
- Experimental aiohttp-based version; requires aiohttp and Python 3.4 or above
- Properly close HTTP session on `WebFingerClient` deletion
- Add `close()` method to `WebFingerClient` to close the session
- Add `__del__` methods to backends close session properly
- Throw correct errors when HTTP request fails

## Minor changes
- New `get()` method in `WebFingerClient` to perform actual HTTP request
- Classes no longer inherit from object, since Python 3 support is required
- `BaseWebFingerClient` is now the base class for `WebFingerClient` and can be used as an interface for custom implementations

# v2.1
Version 2.1 is a bugfix and minor feature update.

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
- Require Python 3

## Minor changes
- Make `aliases`, `properties`, `links`, and `subject` proper attributes, not properties
- Fix testsuite
- Minor cleanups
