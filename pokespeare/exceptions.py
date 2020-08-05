"""
pokespear.exceptions.py
~~~~~~~~~~~~~~~~~~~~~~~

Custom exceptions module
"""


class PokespearError(Exception):
    pass


class MalformedJSONResponseError(PokespearError):
    pass
