import os


class Config:
    POKEMON_API_URL = os.getenv(
        "POKEMON_API_URL", "https://pokeapi.co/api/v2/pokemon-species/"
    )
    TRANSLATOR_API_URL = os.getenv(
        "TRANSLATOR_API_URL",
        "https://api.funtranslations.com/translate/shakespeare.json",
    )
