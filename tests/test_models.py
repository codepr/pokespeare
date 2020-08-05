import unittest
from pokespeare.exceptions import MalformedJSONResponseError
from pokespeare.models import (
    Pokemon,
    PokemonSchema,
    ShakespeareText,
    ShakespeareTextSchema,
)


class TestModel(unittest.TestCase):
    def setUp(self):
        """Planning to use marshmallow to define simple schemas to validate
        JSON responses from the API calls"""
        self.schema = PokemonSchema()
        self.shk_schema = ShakespeareTextSchema()

    def test_model_pokemon_create(self):
        pokemon = Pokemon("squirtle", "Sprinkle water.")
        self.assertEqual(pokemon.name, "squirtle")
        self.assertEqual(pokemon.description, "Sprinkle water.")

    def test_model_pokemon_load(self):
        # Following pokeapi.co/v2 documentations, the real json is much bigger,
        # we only need to consider these fields
        pokemon_dic = {
            "name": "squirtle",
            "flavor_text_entries": [
                {"language": {"name": "en"}, "flavor_text": "Sprinkle water."}
            ],
            "to_be_ignored": "ignore me",
        }
        pokemon = self.schema.load(pokemon_dic)
        self.assertEqual(pokemon.name, "squirtle")
        self.assertEqual(pokemon.description, "Sprinkle water.")

    def test_model_pokemon_dump(self):
        pokemon = Pokemon("squirtle", "Sprinkle water.")
        pokemon_dic = self.schema.dump(pokemon)
        self.assertEqual(pokemon_dic["name"], "squirtle")
        self.assertEqual(pokemon_dic["description"], "Sprinkle water.")

    def test_model_pokemon_load_missing_description(self):
        pokemon_dic = {"name": "squirtle"}
        with self.assertRaises(MalformedJSONResponseError):
            _ = self.schema.load(pokemon_dic)

    def test_model_pokemon_load_missing_language(self):
        pokemon_dic = {
            "name": "squirtle",
            "flavor_text_entries": [{"flavor_text": "Sprinkle water."}],
        }
        with self.assertRaises(MalformedJSONResponseError):
            _ = self.schema.load(pokemon_dic)

    def test_model_pokemon_load_missing_language_en(self):
        # Setting language to `Japanese` instead of `English`
        pokemon_dic = {
            "name": "squirtle",
            "flavor_text_entries": [
                {"language": {"name": "ja"}, "flavor_text": "Sprinkle water."}
            ],
        }
        with self.assertRaises(MalformedJSONResponseError):
            _ = self.schema.load(pokemon_dic)

    def test_model_shakespeare_text_create(self):
        shakespeare_text = ShakespeareText("'t Sprinkle water.")
        self.assertEqual(shakespeare_text.translated, "'t Sprinkle water.")

    def test_model_shakespeare_text_load(self):
        # Directly from the funtranlations doc page
        shakespeare_text_dic = {
            "success": {"total": 1},
            "contents": {
                "translated": "Thee did giveth mr. Tim a hearty meal,  but "
                "unfortunately what he did doth englut did maketh him kicketh "
                "the bucket.",
                "text": "You gave Mr. Tim a hearty meal, but unfortunately "
                "what he ate made him die.",
                "translation": "shakespeare",
            },
        }
        shakespeare_text = self.shk_schema.load(shakespeare_text_dic)
        self.assertEqual(
            shakespeare_text.translated,
            "Thee did giveth mr. Tim a hearty meal,  but unfortunately what"
            " he did doth englut did maketh him kicketh the bucket.",
        )

    def test_model_shakespeare_text_dump(self):
        shakespeare_text = ShakespeareText("'t Sprinkle water.")
        shakespeare_text_dic = self.shk_schema.dump(shakespeare_text)
        self.assertEqual(
            shakespeare_text_dic["translated"], "'t Sprinkle water."
        )

    def test_model_shakespeare_text_missing_contents(self):
        shakespeare_text_dic = {"name": "squirtle"}
        with self.assertRaises(MalformedJSONResponseError):
            _ = self.shk_schema.load(shakespeare_text_dic)

    def test_model_shakespeare_text_wrong_translation_type(self):
        shakespeare_text_dic = {
            "success": {"total": 1},
            "contents": {
                "translated": "Thee did giveth mr. Tim a hearty meal,  but "
                "unfortunately what he did doth englut did maketh him kicketh "
                "the bucket.",
                "text": "You gave Mr. Tim a hearty meal, but unfortunately "
                "what he ate made him die.",
                "translation": "yoda",
            },
        }
        with self.assertRaises(MalformedJSONResponseError):
            _ = self.shk_schema.load(shakespeare_text_dic)
