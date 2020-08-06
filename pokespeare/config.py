"""
pokespeare.config.py
~~~~~~~~~~~~~~~~~~~~

Simple configuration module. Used to load configuration on wep app.
"""

import os
from multiprocessing import cpu_count


def number_of_workers():
    """Retrieve a decent number of workers based on the number of cpu of the hosting machine"""
    return (cpu_count() * 2) + 1


class Config:
    CACHE_NAME = os.getenv("CACHE_NAME", "pokespeare_cache")
    CACHE_BACKEND = os.getenv("CACHE_BACKEND", "memory")
    CACHE_EXPIRATION = int(os.getenv("CACHE_EXPIRATION", "3600"))
    POKEMON_API_URL = os.getenv(
        "POKEMON_API_URL", "https://pokeapi.co/api/v2/pokemon-species/"
    )
    TRANSLATOR_API_URL = os.getenv(
        "TRANSLATOR_API_URL",
        "https://api.funtranslations.com/translate/shakespeare.json",
    )
    TRANSLATOR_API_KEY = os.getenv("TRANSLATOR_API_KEY")
    WSGI_SERVER = "flask"


class DevelopmentConfig(Config):
    WSGI_SERVER = "flask"


class ProductionConfig(Config):
    CACHE_BACKEND = os.getenv("CACHE_BACKEND", "sqlite")
    WSGI_SERVER = "gunicorn"
    WORKERS = int(os.getenv("WORKERS", str(number_of_workers())))
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", "5000"))
