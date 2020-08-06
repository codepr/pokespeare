from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="pokespeare",
    version="0.0.1",
    url="http://github.com/codepr/pokespeare",
    license="MIT",
    author="Andrea Giacomo Baldan",
    author_email="a.g.baldan@gmail.com",
    description="Simple REST API to get a Pokemon description Shakespereanized",
    long_description=readme,
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
    tests_require=requirements,
    platforms="any",
    python_requires=">=3.7",
    test_suite="tests",
)
