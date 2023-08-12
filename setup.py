from setuptools import setup, find_packages

packages = find_packages(where=".", include=["hsms*"])

setup(
    packages=packages,
)
