"""
django-jquery-file-uploader
"""
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test

#def run_tests(*args):
    #from filterjs.tests import run_tests
    #errors = run_tests()
    #if errors:
        #sys.exit(1)
    #else:
        #sys.exit(0)

#test.run_tests = run_tests

setup(
    name="django-filterjs",
    version="0.0.2",
    packages=['filterjs'],
    license="The MIT License (MIT)",
    include_package_data = True,
    description=("A Django demo app for TypeWriter."),
    long_description=("A Django demo app for TypeWriter: "
                "https://github.com/rlalik/TypeWriter"),
    author="Rafal Lalik",
    author_email="rafallalik@gmail.com",
    maintainer="Rafal Lalik",
    maintainer_email="rafallalik@gmail.com",
    url="https://github.com/rlalik/django-filterjs/",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    test_suite="dummy",
)
