# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from setuptools import find_packages
import importlib
import pkgutil
import re
from os import path
from pytest import mark

EXCLUDES = []  # Regex: remember to use \. !


root_path = path.join(path.dirname(__file__), "..")


@mark.parametrize("package",
                  find_packages(where=root_path, exclude=['tests', 'tests.*']))
def test_import(package):
    """Tests if all (sub-)packages are importables."""
    module = importlib.import_module(package)
    prefix = "{}.".format(package)
    for _, mod, _ in pkgutil.walk_packages(module.__path__, prefix=prefix):
        if not any([re.search(exclude, mod) for exclude in EXCLUDES]):
            importlib.import_module(mod)
