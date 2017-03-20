#!/usr/bin/env python
"""Provide code supporting the running and automating of Snakemake rules."""

# Imports
from pathlib import Path
import inspect

import munch

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


__all__ = ["pathify_by_key_ends","SnakeRun","SnakeRule"]


def pathify_by_key_ends(dictionary):
    """Return a dict that has had all values with keys marked as '*_PATH' or '*_DIR' converted to Path() instances."""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            pathify_by_key_ends(value)
        elif key.endswith("_PATH") or key.endswith("_DIR"):
            dictionary[key] = Path(value)

    return dictionary


class SnakeRun(object):

    """Initialize and manage information common to the whole run."""

    def __init__(self, cfg):
        """Initialize common information for a run."""
        assert isinstance(cfg, dict)

        common = cfg["COMMON"]

        self.snakefile = cfg.SNAKEFILE
        self.globals = munch.Munch()
        self.cfg = cfg
        self.name = common["RUN_NAME"]
        self.d = common["SHARED"]
        self.out_dir = Path("{base_dir}/{run_name}".format(base_dir=common["OUT_DIR"],
                                                           run_name=self.name
                                                           )
                            )
        self.pretty_names = {}
        self.log_dir = self.out_dir / "logs"

class SnakeRule(object):

    """Manage the initialization and deployment of rule-specific information."""

    def __init__(self, run, name, pretty_name=None):
        """Initialize logs, inputs, outputs, params, etc for a single rule."""
        assert isinstance(run, SnakeRun)

        if pretty_name is None:
            pretty_name = name

        self.run = run
        self.name = name.lower()
        self.pretty_name = pretty_name

        self.run.pretty_names[self.name] = pretty_name

        self.log_dir = run.log_dir / self.name
        self.log = self.log_dir / "{name}.log".format(name=self.name)
        self.out_dir = run.out_dir / self.name
        self.i = munch.Munch() # inputs
        self.o = munch.Munch() # outputs
        self.p = munch.Munch() # params

        self._import_config_dict()

    def _import_config_dict(self):
        """Inport configuration values set for this rule so they are directly accessable as attributes."""
        try:
            for key, val in self.run.cfg[self.name.upper()].items():
                self.__setattr__(key, val)
            self.cfg = True
        except KeyError:
            self.cfg = False