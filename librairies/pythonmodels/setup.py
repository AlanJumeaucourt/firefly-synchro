from setuptools import find_packages, setup

setup(
    name='pythonmodels',
    packages=find_packages(include=['pythonmodels', "Kresus", "FireflyIIIApi"]),
    version='0.1.0',
    description='My first Python library',
    author='Alan Jumeaucourt',
    install_requires=["fuzzywuzzy", "requests"],
)
