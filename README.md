Pokespeare
==========

![test](https://github.com/codepr/pokespeare/workflows/test/badge.svg)

Simple REST API that, given a Pokemon name, returns its Shakesperean description.

The application exposes a single endpoint `/pokemon/<name>` which can be queried
via `GET` method passing the pokemon name and it will return a JSON in the form of
```json
{
  "name": "<pokemon_name>",
  "description": "<Shakesperean description>"
}
```

In case of error of any type it returns a `404 - Not found` with the explanation of
what happened.

Dependencies:
- python >= 3.7
- sqlite (optional)

## Quickstart

The project is written in python, it's advisable to create a [virtual environment](https://virtualenv.pypa.io/en/latest/installation.html)
to test it or use the `Dockerfile` to run it inside a container.

**Install dependencies**
```sh
$ pip install -r requirements.txt
```

**Set the configuration by env variable**
```sh
$ export APP_CONFIG=pokespeare.config.DevelopmentConfig
```

**Run application**
```sh
$ python start.py
```

**Docker build & run**

The host can be set only for `pokespeare.config.ProductionConfig` as for the development one it's standard on 127.0.0.1
```sh
$ docker build -t pokespeare . && docker run --rm -e "HOST=0.0.0.0" -p5000:5000 pokespeare
```

**Configuration**

There two configurations currently that can be set via ENV:
- `pokespeare.config.DevelopmentConfig`
- `pokespeare.config.ProductionConfig`

Practically every configuration key can be set via ENV variables, currently
support:

Dev and prod.

- `CACHE_NAME`
- `CACHE_BACKEND`
- `CACHE_EXPIRATION`
- `POKEMON_API_URL`
- `TRANSLATOR_API_URL`
- `TRANSLATOR_API_KEY`
- `WSGI_SERVER`

Production only

- `HOST`
- `PORT`

## Way of working

- Exploration of the domain, analysis of the external services documentations
  (return codes, format, limitations etc.)
- Rough estimation of the usage, traffic volume and possible future extensions
- Exploration and tradeoffs over the frameworks and libraries to adopt
- Development, mainly following a mixed TDD approach and prototyping a simple solution
- Improvements and refines

## Considerations

For the development of the application I decided to use python as it's the
language I feel more comfortable with at the moment and the one which I
know most frameworks and best practices overall.

The task is pretty simple but I tried to implement it with an eye for
maintenability and extensibility of the code, for this reason the final result
can seem a bit of an overkill in some parts but I also written some hints on the
code to express my opinions on what could have been a better choice to take.

### Frameworks & libraries

- **Flask:** battle-tested and the simplest solution for the domain, it's
  lightweight and being the problem essentially a stateless computation, I
  thought there was no need for fancy features or speedsters performance
  frameworks like `fastapi` or `async/await` based frameworks. Flask
  is more than capable of handling the volume of requests.
  If the traffic volume is expected to grow rapidly in the short-term (unlikely,
  given the hard-cap of the [shakesperean-translator](https://funtranslations.com/api/shakespeare#translate)
  of 12500 calls/day with the ultra plan) it's trivial to increase nodes and
  put a load-balancer in front of the application.

- **Requests:** Again, the most widespread library for HTTP calls, it does one thing
  and it does it well. Also there's no possibility of make the `pokeappi.co/v2` call
  and the `funtranslations.com` call concurrently as their sequentials: funtranslations
  needs the result of the `pokeappi.co/v2` call to give a result.

- **Requests-cache:** A super simple caching layer working out-of-the box paired with
  requests module to cache requests as also advised by `pokeappi.co/v2` documentation.
  Supports redis, mongodb, sqlite and also simple memory dict-based cache.
  I have to admit I'm not a huge fan of these under-the-hood monkey-patching mechanism
  or having a global objects like the request one in flask but it's a common pattern in python
  as long as it's well-tested, given the size of the project it's a good fast solution that
  fulfill all the needs.
  For something more complex I'd probably switch to different solutions or design a caching
  layer from scratch with more control over the logics.

- **Marshmallow:** JSON marshalling can be achieved in various ways and python offers built-ins
  that allow to handle them easily even without the needs of external libraries. Though I decided
  to use a marshalling library as it make simpler validations and typechecking without writing
  too much code, and it comes handy for future extensions of the codebase as it encapsulate
  all the serializations/deserializations logics.

I also made some assumptions:

- Expecting a low to medium traffic volume, given the limitations on the external services
  the API relies on, anyway it's easy to scale-out the application being it a stateless
  computation demanded to external APIs which ultimately define the limits of the app.
- An error at any stage results in a 404 - Not Found response

Assuming a noticeable increase of features and traffic for the future I'd
probably switch **Flask** with uvicorn ASGI based **FastApi** and **Requests**
with **aiohttp** or some other async solutions to increase performance by
several orders of magnitude.

A solution to tackle the problem of the scarce number of calls available toward
`funtranslations.com` beside the cache, could be to store results at each new
call in a persistent DB avoiding calls each time the cache is flushed.

## Notes

For the caching layer I've opted for simple in-memory dictionary for
development and sqlite for a persisted solution just to give the idea, it's
easy anyway to add redis for example as it's natively supported by the
**requests-cache** module adopted.

I didn't reach 100% test coverage as some parts I assume are already covered by
the external library they relies on as I don't make any modifications beside
calling their public methods (ex: pokespeare.http module).

### Rust implementation

I've tested a rough draft in Rust as well, very basic as I think I don't have
enough experience with the language. Anyway the libraries I explored/adopted
were [rocket](https://rocket.rs) as webframework with an eye for
[worp](https://docs.rs/warp/0.2.4/warp/) but being more async oriented I
ditched it. [serde](https://serde.rs/) for JSON marshalling and
[reqwest](https://docs.rs/reqwest/0.10.7/reqwest/) to make requests to external
APIs.

Beside the good old borrow checker, I think the main thing I found myself
unaccostumed it's the error handling and missing fields, but mainly because of
habit with exceptions system or plain old return codes C/Go like; but I think
it become very intuitive pretty fast and very powerful and neat as well.

I really like cargo and the toolchain offered, way better than the python one,
definetly interesting.
