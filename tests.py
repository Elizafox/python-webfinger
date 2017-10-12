import unittest
from webfinger import finger, WebFingerClient, WebFingerResponse


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
        self.response = WebFingerResponse(jrd)

    def test_subject(self):
        self.assertEqual(self.response.subject, "acct:Elizafox@mst3k.interlinked.me")

    def test_rel_longname(self):
        self.assertEqual(self.response.rel("http://webfinger.net/rel/profile-page", "href"), ["https://mst3k.interlinked.me/@Elizafox"])

    def test_rel_shortname(self):
        self.assertEqual(self.response.rel("profile", "href"), ["https://mst3k.interlinked.me/@Elizafox"])

    def test_invalid_rel(self):
        self.assertEqual(self.response.rel(""), None)

    def test_rels_dict(self):
        self.assertEqual(self.response.rels["profile"],
                         [{"href": "https://mst3k.interlinked.me/@Elizafox",
                           "rel": "http://webfinger.net/rel/profile-page",
                           "type": "text/html"}])


if __name__ == "__main__":
    unittest.main()
