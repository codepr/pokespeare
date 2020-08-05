import unittest
from pokespeare.app import flask_app


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
