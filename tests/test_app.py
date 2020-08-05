import unittest
from unittest.mock import patch
from pokespeare.app import flask_app
from pokespeare.exceptions import MalformedJSONResponseError


expected_response = {
    "name": "haunter",
    "flavor_text_entries": [
        {"language": {"name": "en"}, "flavor_text": "The best one."}
    ],
    "to_be_ignored": "ignore me",
}

wrong_response = {
    "name": "haunter",
    "wrong_field": [
        {"language": {"name": "en"}, "flavor_text": "The best one."}
    ],
    "to_be_ignored": "ignore me",
}


class FakeResponse:
    def __init__(self, status_code, expected_response):
        self.status_code = status_code
        self.expected_response = expected_response

    def json(self):
        return self.expected_response


class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = flask_app.test_client()
        self.app.testing = True

    def tearDown(self):
        self.app.testing = False

    def test_get_pokemon_description_wrong_path(self):
        result = self.app.get("/")
        self.assertEqual(result.status_code, 404)

    def test_get_pokemon_description_wrong_method(self):
        result = self.app.post("/pokemon/haunter")
        self.assertEqual(result.status_code, 405)

    @patch(
        "pokespeare.app.requests.get",
        return_value=FakeResponse(200, wrong_response),
    )
    def test_get_pokemon_description_wrong_field(self, requests_mock):
        result = self.app.get("/pokemon/haunter")
        self.assertTrue(result.status_code == 404)
