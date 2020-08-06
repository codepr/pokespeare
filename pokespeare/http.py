"""
pokespeare.http.py
~~~~~~~~~~~~~~~~~~

Contains definitions of custom HTTP clients, allowing for more flexibility on
the library choice
"""

import abc
import requests
from typing import Dict, Tuple, Any
from .exceptions import HTTPError, UnexpectedError
import requests_cache


class HTTPClient(abc.ABC):
    """Basic interface class. Allow to define custom HTTP clients giving
    stronger contract behaviour

    :type cache_name: str
    :param cache_name: The name of the cache, corresponds to the name of the
                       sqlite DB on the filesystem if the `beckend` is sqlite
                       or the name of the redis namespace in case of `redis`
                       backend.

    :type backend: str
    :param backend: The backend to use, can be either `memory` to use a simple
                    python dict, `sqlite` to use a sqlite DB on the filesystem
                    or `redis` for a redis cache

    :type expire_after: int
    :param expire_after: Define after how many seconds each key in the cache
                         have to be evicted

    :type allowable_methods: Tuple[str]
    :param allowable_methods: A tuple of strings defining for which HTTP
                              methods to apply caching

    Also supports `connection` in case of a redis connection on kwargs,
    for more info `https://requests-cache.readthedocs.io/en/latest/api.html`
    """

    def __init__(
        self,
        cache_name: str = "",
        *,
        backend: str = "memory",
        expire_after: int = 3600,
        allowable_methods: Tuple[str] = ("GET",),
        **kwargs
    ):
        self.cache_name = cache_name
        self.backend = backend
        self.expire_after = expire_after
        self.allowable_methods = allowable_methods
        self.cache_enabled = False
        if self.cache_name:
            self.enable_cache(**kwargs)

    @abc.abstractmethod
    def enable_cache(self, **kwargs: Dict[str, Any]) -> None:
        """Enable caching for each request"""
        pass

    @abc.abstractmethod
    def disable_cache(self) -> None:
        """Disable caching"""
        pass

    @abc.abstractmethod
    def get(self, url: str, **kwargs: Dict[str, Any]) -> Any:
        """Perform GET request to a defined URL"""
        pass

    @abc.abstractmethod
    def post(self, url: str, **kwargs: Dict[str, Any]) -> Any:
        """Perform POST request to a defined URL"""
        pass


class RequestsHTTPClient(HTTPClient):
    """
    Simple wrapper class around requests library, which is used as the
    main engine for each call. Allow better unit-testing overall.
    """

    def enable_cache(self, **kwargs: Dict[str, Any]) -> None:
        requests_cache.install_cache(
            self.cache_name,
            backend=self.backend,
            expire_after=self.expire_after,
            allowable_methods=self.allowable_methods,
            **kwargs
        )
        self.cache_enabled = True

    def disable_cache(self) -> None:
        requests_cache.disable_cache()
        requests_cache.uninstall_cache()
        self.cache_enabled = False

    def get(self, url: str, **kwargs: Dict[str, Any]) -> Any:
        try:
            response = requests.get(url, **kwargs)
            response.raise_for_status()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.TooManyRedirects,
        ) as e:
            raise HTTPError(e)
        except (requests.exceptions.RequestException, Exception) as e:
            raise UnexpectedError(e)
        return response

    def post(self, url: str, **kwargs: Dict[str, Any]) -> Any:
        try:
            response = requests.post(url, **kwargs)
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.TooManyRedirects,
        ) as e:
            raise HTTPError(e)
        except (requests.exceptions.RequestException, Exception) as e:
            raise UnexpectedError(e)
        return response
