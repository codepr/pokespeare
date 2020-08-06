"""
pokespeare.exceptions.py
~~~~~~~~~~~~~~~~~~~~~~~~

Custom exceptions module
"""


class PokespeareError(Exception):
    """Base application error"""

    ...


class MalformedJSONResponseError(PokespeareError):
    """Validation error for wrong formatted JSON payloads"""

    ...


class HTTPError(PokespeareError):
    """Generic error on HTTP calls"""

    ...


class UnexpectedError(PokespeareError):
    """Unknown error, mainly used on HTTP calls with unexpected outcome"""

    ...
