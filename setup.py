from setuptools import setup, find_packages

setup(
    name="pokespeare",
    version="0.0.1",
    url="http://github.com/codepr/pokespeare",
    license="MIT",
    author="Andrea Giacomo Baldan",
    author_email="a.g.baldan@gmail.com",
    description="",
    packages=find_packages(exclude=["tests"]),
    platforms="any",
    python_requires=">=3.7",
    test_suite="tests",
)
