import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "rexster-rest",
    version = "0.0.1",
    author = "Roman Suvorov",
    author_email = "windj007@gmail.com",
    description = ("Simple Rexster REST client"),
    license = "BSD",
    keywords = "rest client Rexster",
    url = "http://packages.python.org/rexster-rest",
    packages=['rexster_rest', 'rexster_rest.tests'],
    package_data={'rexster_rest': ['scripts/*.groovy']},
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
    ],
    requires = ['resxter_rest', 'resxter_rest.tests'],
    test_suite = "rexster_rest.tests.all_tests",
)