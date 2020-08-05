import requests
from flask import Flask, abort, jsonify
from .models import PokemonSchema, ShakespeareTextSchema
from .exceptions import MalformedJSONResponseError

flask_app = Flask(__name__)


@flask_app.route("/pokemon/<string:pokemon_name>", methods=["GET"])
def get_pokemon_description(pokemon_name):
    schema = PokemonSchema()
    try:
        response = requests.get(
            f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name}"
        )
        response.raise_for_status()
        print(response)
        pokemon = schema.load(response.json())
        shakespeare = requests.post(
            "https://api.funtranslations.com/translate/shakespeare.json",
            json={"text": pokemon.description},
        )
        shakespeare.raise_for_status()
    except (
        MalformedJSONResponseError,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
    ) as err:
        abort(404, description=err)
    except:
        abort(404)
    pokemon.description = shakespeare.translated
    return jsonify(schema.dump(pokemon))


def run():
    flask_app.run(debug=True)
