import unittest
from unittest.mock import patch
from pokespeare.app import flask_app
from pokespeare.exceptions import HTTPError
from pokespeare.config import DevelopmentConfig

# Well formed response from pokeapi.co/v2 GET call
expected_pokemon_response = {
    "name": "haunter",
    "flavor_text_entries": [
        {"language": {"name": "en"}, "flavor_text": "The best one."}
    ],
    "to_be_ignored": "ignore me",
}

# Malformed formed response from pokeapi.co/v2 GET call
wrong_pokemon_response = {
    "name": "haunter",
    "wrong_field": [
        {"language": {"name": "en"}, "flavor_text": "The best one."}
    ],
    "to_be_ignored": "ignore me",
}

# Well formed response from funtranslations service POST call
expected_shakespeare_response = {
    "success": {"total": 1},
    "contents": {
        "translated": "'t The best one.'",
        "text": "The best one.",
        "translation": "shakespeare",
    },
}

# Malformed formed response from funtranslations service POST call
wrong_shakespeare_response = {
    "success": {"total": 1},
    "contents": {
        "translated": "'t The best one.'",
        "text": "The best one.",
        "translation": "yoda",
    },
}


class FakeResponse:
    """Just a simple response mock"""

    def __init__(self, expected_status_code, content):
        self.expected_status_code = expected_status_code
        self.content = content
        self.status_code = expected_status_code

    def json(self):
        return self.content

    def raise_for_status(self):
        if self.expected_status_code == 403:
            raise HTTPError("Forbidden")
        if self.expected_status_code == 429:
            raise HTTPError("Reached max number of requests")


class FakeRequests:
    """Simple HTTP client mock, mimics all required methods"""

    def __init__(
        self,
        expected_status_code,
        wrong_pokemon_payload=False,
        wrong_shk_payload=False,
    ):
        self.expected_status_code = expected_status_code
        self.wrong_pokemon_payload = wrong_pokemon_payload
        self.wrong_shk_payload = wrong_shk_payload

    def get(self, *args, **kwargs):
        if self.expected_status_code == 200 and not self.wrong_pokemon_payload:
            return FakeResponse(200, expected_pokemon_response)
        if self.expected_status_code == 200 and self.wrong_pokemon_payload:
            return FakeResponse(200, wrong_pokemon_response)
        return FakeResponse(self.expected_status_code, "{}")

    def post(self, *args, **kwargs):
        if self.expected_status_code == 200 and not self.wrong_shk_payload:
            return FakeResponse(200, expected_shakespeare_response,)
        if self.expected_status_code == 200 and self.wrong_shk_payload:
            return FakeResponse(200, wrong_shakespeare_response,)
        return FakeResponse(self.expected_status_code, "{}")


class AppTest(unittest.TestCase):
    def setUp(self):
        flask_app.config.from_object(DevelopmentConfig)
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
        "pokespeare.app.get_http_client", return_value=FakeRequests(403),
    )
    def test_get_pokemon_description_http_error(self, req_mock):
        result = self.app.get("/pokemon/haunter")
        self.assertEqual(result.status_code, 404)

    @patch(
        "pokespeare.app.get_http_client", return_value=FakeRequests(200, True),
    )
    def test_get_pokemon_description_validation_error_on_pokemon_call(
        self, req_mock
    ):
        result = self.app.get("/pokemon/haunter")
        self.assertEqual(result.status_code, 404)

    @patch(
        "pokespeare.app.get_http_client",
        return_value=FakeRequests(200, False, True),
    )
    def test_get_pokemon_description_validation_error_on_shakespeare_call(
        self, req_mock
    ):
        result = self.app.get("/pokemon/haunter")
        self.assertEqual(result.status_code, 404)

    @patch(
        "pokespeare.app.get_http_client", return_value=FakeRequests(200),
    )
    def test_get_pokemon_description_success_call(self, req_mock):
        result = self.app.get("/pokemon/haunter")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(
            result.json,
            {"description": "'t The best one.'", "name": "haunter"},
        )
