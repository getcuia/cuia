"""Facilities for working with ANSI escape sequences."""


import re

PATTERN = re.compile(r"(\N{ESC}\[[\d;]*[a-zA-Z])")
