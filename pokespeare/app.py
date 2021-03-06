"""
pokespeare.app.py
~~~~~~~~~~~~~~~~~

APIs definition and server related functions
"""

import os
import sys
from typing import Tuple
from flask import Flask, abort, jsonify
from gunicorn.app.base import BaseApplication
from .models import PokemonSchema, ShakespeareTextSchema
from .exceptions import MalformedJSONResponseError, HTTPError, UnexpectedError
from .http import HTTPClient, RequestsHTTPClient

flask_app = Flask(__name__)

# Just a simple esplicative check for configuration setup
if not os.getenv("APP_CONFIG"):
    print(
        "No configuration set: Please, try "
        "`export APP_CONFIG=pokespeare.config.ProductionConfig` or "
        "`export APP_CONFIG=pokespeare.config.DevelopmentConfig`"
    )
    sys.exit(0)

flask_app.config.from_object(os.getenv("APP_CONFIG"))
_http = None


def get_http_client(
    cache_name: str = "",
    *,
    backend: str = "memory",
    expire_after: int = 3600,
    allowable_methods: Tuple[str] = ("GET",),
    **kwargs
) -> HTTPClient:
    """Trivial factory function, could be extended to a dict-based registry
    with more choices, if a different more performant client is needed, or an HTTP/2
    client"""
    global _http
    if not _http:
        _http = RequestsHTTPClient(
            cache_name,
            backend=backend,
            expire_after=expire_after,
            allowable_methods=allowable_methods,
            **kwargs
        )
    return _http


@flask_app.errorhandler(404)
def resource_not_found(err):
    return jsonify(error=str(err)), 404


@flask_app.errorhandler(429)
def too_many_requests(_):
    return (
        jsonify(
            error="Too Many Requests: This user has exceeded an allotted "
            "request count. Try again later."
        ),
        404,
    )


@flask_app.route("/pokemon/<string:pokemon_name>", methods=["GET"])
def get_pokemon_description(pokemon_name):
    """Main GET handler for the application, exposes /pokemon/<name> and return
    a JSON with the name of the pokemon and the description shakespereanized.
    Giving the simplicity of the application it's defined here in the main app
    module, for a bigger REST service it would probably a better idea to move
    it into its own module for resources only.
    """
    # Get an HTTPClient instance, `get_http_client` is intended as a "poor"
    # factory to get external dependency, a requests wrapper in this case
    # to avoid strong coupling
    http = get_http_client(
        flask_app.config.get("CACHE_NAME"),
        backend=flask_app.config.get("CACHE_BACKEND"),
        expire_after=flask_app.config.get("CACHE_EXPIRATION"),
        allowable_methods=("GET", "POST"),
    )
    pokemon_url = flask_app.config.get("POKEMON_API_URL")
    translator_url = flask_app.config.get("TRANSLATOR_API_URL")
    # Optional API key
    translator_api = flask_app.config.get("TRANSLATOR_API_KEY")
    schema = PokemonSchema()
    sh_schema = ShakespeareTextSchema()
    try:
        # Call to pokeapi.co/v2
        response = http.get(os.path.join(pokemon_url, pokemon_name))
        pokemon = schema.load(response.json())
        # Call to funtranslations.com
        if translator_api:
            response = http.post(
                translator_url,
                json={"text": pokemon.description},
                headers={"X-Funtranslations-Api-Secret": translator_api},
            )
        else:
            response = http.post(
                translator_url, json={"text": pokemon.description},
            )
        # Avoid raise_for_status() call to have better control over the
        # return codes in case of 429 (too many requests, cap reached)
        # to return a better descriptive error
        if response.status_code == 429:
            abort(429)
        else:
            response.raise_for_status()
        shakespeare_text = sh_schema.load(response.json())
    except (HTTPError, MalformedJSONResponseError) as err:
        abort(404, description=err)
    except UnexpectedError:
        abort(404)
    pokemon.description = shakespeare_text.translated
    return jsonify(schema.dump(pokemon))


class WSGIApplication(BaseApplication):
    """Gunicorn standalone application, avoiding call gunicorn on shell"""

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(WSGIApplication, self).__init__()

    def load_config(self):
        config = dict(
            [
                (key, value)
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            ]
        )
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def serve():
    """Serve applicaton embedded gunicorn WSGI process or the Flask debug one
    based on the configuration choice"""
    if flask_app.config["WSGI_SERVER"] == "flask":
        flask_app.run(debug=True)
    elif flask_app.config["WSGI_SERVER"] == "gunicorn":
        options = {
            "bind": "%s:%s"
            % (flask_app.config["HOST"], str(flask_app.config["PORT"])),
            "workers": flask_app.config["WORKERS"],
            "accesslog": "-",
            "errorlog": "-",
        }
        WSGIApplication(flask_app, options).run()
