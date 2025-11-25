# -*- coding: utf-8 -*-
# (c) Copyright 2019 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function

import importlib.metadata as metadata
from typing import Final

version: Final[str] = metadata.version("sensirion_shdlc_driver")
