from typing import Tuple
from flask import Flask, abort, jsonify
from .models import PokemonSchema, ShakespeareTextSchema
from .exceptions import MalformedJSONResponseError, HTTPError, UnexpectedError
from .http import HTTPClient, RequestsHTTPClient

flask_app = Flask(__name__)


def get_http_client(
    cache_name: str = "",
    *,
    backend: str = "memory",
    expire_after: int = 3600,
    allowable_methods: Tuple[str] = ("GET",),
) -> HTTPClient:
    """Trivial factory function, could be extended to a dict-based registry
    with more choices, if a different more performant client is needed, or an HTTP/2
    client"""
    return RequestsHTTPClient(
        cache_name,
        backend=backend,
        expire_after=expire_after,
        allowable_methods=allowable_methods,
    )


@flask_app.errorhandler(404)
def resource_not_found(err):
    return jsonify(error=str(err)), 404


@flask_app.route("/pokemon/<string:pokemon_name>", methods=["GET"])
def get_pokemon_description(pokemon_name):
    http = get_http_client(
        "pokespeare_cache",
        backend="memory",
        expire_after=3600,
        allowable_methods=("GET", "POST"),
    )
    schema = PokemonSchema()
    sh_schema = ShakespeareTextSchema()
    try:
        response = http.get(
            f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name}"
        )
        pokemon = schema.load(response.json())
        shakespereanized = http.post(
            "https://api.funtranslations.com/translate/shakespeare.json",
            json={"text": pokemon.description},
        )
        shakespeare_text = sh_schema.load(shakespereanized.json())
    except (HTTPError, MalformedJSONResponseError) as err:
        abort(404, description=err)
    except UnexpectedError:
        abort(404)
    pokemon.description = shakespeare_text.translated
    return jsonify(schema.dump(pokemon))


def run():
    flask_app.run(debug=True)
