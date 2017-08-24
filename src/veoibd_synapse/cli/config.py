#!/usr/bin/env python
"""Provide functions used in cli.config."""

# Imports
from logzero import logger as log
from pathlib import Path
import shutil
import datetime as dt

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


def replace_config(name, factory_resets, prefix):
    """Replace existing config file or generate initial one.

    Backup existing file.
    """

    default_path = factory_resets / name
    new_path = factory_resets.parent / '{prefix}.{name}'.format(name=name,
                                                                prefix=prefix)

    if new_path.exists():
        stamp = dt.datetime.today().isoformat()
        new_path = Path('{name}.bkdup_{stamp}'.format(name=str(new_path),
                                                      stamp=stamp))

    shutil.copy(src=str(default_path), dst=str(new_path))
    log.info("Generated new config: {path}".format(path=new_path))
