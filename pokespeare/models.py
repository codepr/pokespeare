from dataclasses import dataclass
from .exceptions import MalformedJSONResponseError

from marshmallow import (
    Schema,
    EXCLUDE,
    fields,
    pre_load,
    post_load,
)


@dataclass
class Pokemon:
    """Simple container class for Pokemon descriptions"""

    name: str
    description: str


class PokemonSchema(Schema):
    """JSON Schema class for Pokemon dataclass, all ser. deser. logics should
    be handled here """

    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True)
    description = fields.String(required=True)

    @pre_load
    def get_description(self, data, **kwargs):
        if "flavor_text_entries" not in data:
            raise MalformedJSONResponseError(
                "No flavor text entries for this item"
            )
        try:
            descriptions = [
                desc
                for desc in data["flavor_text_entries"]
                if desc["language"]["name"] == "en"
            ]
        except (KeyError, IndexError):
            raise MalformedJSONResponseError(
                "No flavor text entries for this item"
            )
        if not descriptions:
            raise MalformedJSONResponseError(
                "No flavor text entries for this item"
            )
        data["description"] = descriptions[0]["flavor_text"]
        data.pop("flavor_text_entries")
        return data

    @post_load
    def make_pokemon(self, data, **kwargs):
        return Pokemon(**data)


@dataclass
class ShakespeareText:
    """Simple container class for shakespereanized text"""

    translated: str


class ShakespeareTextSchema(Schema):

    """JSON Schema class for ShakespeareText dataclass, all ser. deser.
     logics should be handled here """

    class Meta:
        unknown = EXCLUDE

    translated = fields.String(required=True)

    @pre_load
    def get_translated_text(self, data, **kwargs):
        if (
            "contents" not in data
            or data["contents"]["translation"] != "shakespeare"
        ):
            raise MalformedJSONResponseError("Unable to translate the text")
        data["translated"] = data["contents"]["translated"]
        return data

    @post_load
    def make_shakespeare_text(self, data, **kwargs):
        return ShakespeareText(**data)
