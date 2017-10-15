#!/usr/bin/env python3


import unittest
from webfinger import (finger, WebFingerClient, WebFingerJRD,
    WebFingerJRDError)


try:
    import aiohttp
except ImportError:
    aiohttp = None
else:
    import asyncio
    from webfinger.client.aiohttp import WebFingerClient as WebFingerAioHTTPClient


class TestHostParsing(unittest.TestCase):
    def setUp(self):
        self.client = WebFingerClient()

    def test_parsing(self):
        host = self.client.parse_host("Elizafox@mst3k.interlinked.me")
        self.assertEqual(host, "mst3k.interlinked.me")


class TestWebFingerRequest(unittest.TestCase):
    def setUp(self):
        self.client = WebFingerClient()

    def test_subject(self):
        wf = self.client.finger("acct:Elizafox@mst3k.interlinked.me")
        self.assertEqual(wf.subject, "acct:Elizafox@mst3k.interlinked.me")


class TestWebFingerResponse(unittest.TestCase):
    def setUp(self):
        jrd = {"aliases": ["https://mst3k.interlinked.me/@Elizafox",
                           "https://mst3k.interlinked.me/users/Elizafox"],
               "links": [{"href": "https://mst3k.interlinked.me/@Elizafox",
                          "rel": "http://webfinger.net/rel/profile-page",
                          "type": "text/html"},
                         {"href": "https://mst3k.interlinked.me/users/Elizafox.atom",
                          "rel": "http://schemas.google.com/g/2010#updates-from",
                          "type": "application/atom+xml"},
                         {"href": "https://mst3k.interlinked.me/users/Elizafox",
                          "rel": "self",
                          "type": "application/activity+json"},
                         {"href": "https://mst3k.interlinked.me/api/salmon/1",
                          "rel": "salmon"},
                         {"rel": "http://ostatus.org/schema/1.0/subscribe",
                          "template": "https://mst3k.interlinked.me/authorize_follow?acct={uri}"}],
               "subject": "acct:Elizafox@mst3k.interlinked.me"}
        self.response = WebFingerJRD(jrd)

    def test_subject(self):
        self.assertEqual(self.response.subject, "acct:Elizafox@mst3k.interlinked.me")

    def test_rel_longname(self):
        rel = self.response.rel("http://webfinger.net/rel/profile-page", "href")
        self.assertEqual(rel, ["https://mst3k.interlinked.me/@Elizafox"])

    def test_rel_shortname(self):
        rel = self.response.rel("profile", "href")
        self.assertEqual(rel, ["https://mst3k.interlinked.me/@Elizafox"])

    def test_invalid_rel(self):
        self.assertEqual(self.response.rel(""), None)

    def test_link_rels_dict(self):
        self.assertEqual(self.response.link_rels["profile"],
                         [{"href": "https://mst3k.interlinked.me/@Elizafox",
                           "rel": "http://webfinger.net/rel/profile-page",
                           "type": "text/html"}])


class TestWebFingerBuild(unittest.TestCase):
    def setUp(self):
        self.builder = WebFingerJRD.build("acct:Elizafox@mst3k.interlinked.me")

        self.builder.add_property("http://example.com", "test")

        self.builder.add_link(rel="profile", type="text/html",
            href="https://mst3k.interlinked.me/users/Elizafox.atom",
            misc={"test": "test extra param"})

        self.builder.add_alias("http://example.org")

        self.builder.add_misc("test-extra", "123")

        self.response = WebFingerJRD(self.builder.jrd)
        self.response_json = WebFingerJRD(self.builder.to_json())

    def test_subject(self):
        self.assertEqual(self.response.subject,
            "acct:Elizafox@mst3k.interlinked.me")

    def test_link(self):
        self.assertEqual(self.response.links,
            [{"rel": "http://webfinger.net/rel/profile-page",
              "type": "text/html",
              "href": "https://mst3k.interlinked.me/users/Elizafox.atom",
              "test": "test extra param"}])

    def test_properties(self):
        self.assertEqual(self.response.properties,
            {"http://example.com": "test"})

    def test_alias(self):
        self.assertEqual(self.response.aliases, ["http://example.org"])

    def test_misc(self):
        self.assertEqual(self.response.jrd["test-extra"], "123")

    def test_json(self):
        self.assertEqual(self.response.jrd, self.response_json.jrd)

    def test_invalid_link_rel(self):
        self.assertRaises(WebFingerJRDError, self.builder.add_link,
            rel="invalid")
        self.assertNotIn({"rel": "invalid"}, self.builder.jrd["links"])

    def test_invalid_link_href(self):
        self.assertRaises(WebFingerJRDError, self.builder.add_link,
            rel="http://test.example", href="invalid")
        self.assertNotIn({"rel": "http://test.example", "href": "invalid"},
            self.builder.jrd["links"])

    def test_invalid_link_type(self):
        self.assertRaises(WebFingerJRDError, self.builder.add_link,
            rel="http://test.example", type=4)
        self.assertNotIn({"rel": "http://test.example", "type": 4},
            self.builder.jrd["links"])

    def test_invalid_property_key_number(self):
        self.assertRaises(WebFingerJRDError, self.builder.add_property,
            4, "invalid")
        self.assertNotIn(4, self.builder.jrd["properties"])

    def test_invalid_property_key_not_uri(self):
        self.assertRaises(WebFingerJRDError, self.builder.add_property,
            "test", "invalid")
        self.assertNotIn("test", self.builder.jrd["properties"])

    def test_invalid_property_value(self):
        self.assertRaises(WebFingerJRDError, self.builder.add_property,
            "http://valid.example", 4)
        self.assertNotIn("http://valid.example", self.builder.jrd["properties"])

    def test_property_none(self):
        self.builder.add_property("http://uri.example", None)
        self.assertIn("http://uri.example", self.builder.jrd["properties"])


@unittest.skipIf(aiohttp is None, "aiohttp is not importable")
class TestAioHTTPClient(unittest.TestCase):
    def setUp(self):
        self.client = WebFingerAioHTTPClient()
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.run_until_complete(self.client.close())

    def test_subject(self):
        wf = self.loop.run_until_complete(self.client.finger("acct:Elizafox@mst3k.interlinked.me"))
        self.assertEqual(wf.subject, "acct:Elizafox@mst3k.interlinked.me")


if __name__ == "__main__":
    unittest.main()
