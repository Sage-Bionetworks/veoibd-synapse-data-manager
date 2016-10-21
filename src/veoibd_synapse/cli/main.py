#!/usr/bin/env python
"""Provide command line interface to the synapse manager."""

# Imports

from pathlib import Path
import datetime as dt
import shutil

import munch
import ruamel.yaml as yaml

import click
from click import echo

import veoibd_synapse.cli.config as _config


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"



def process_config(config=None):
    """
    Prepare user's config file.

    Also handles validation.

    Args:
        config (str): path to config file.

    Returns:
        conf (dict): configuration values.
    """
    if config is None:
        conf = munch.Munch()
        conf.metadata = munch.Munch()
        conf.metadata.path = None
    else:
        conf = munch.munchify(yaml.load(config))
        conf.metadata = munch.Munch()
        conf.metadata.path = os.path.abspath(config.name)


    return conf


@click.group()
@click.option('--config', default=None,
              help="Path to optional config.yaml",
              type=click.File())
@click.pass_context
def run(ctx=None, config=None):
    """Command interface to the veoibd-synapse-manager.

    For command specific help text, call the specific
    command followed by the --help option.
    """
    ctx.obj = munch.Munch()

    ctx.obj.CONFIG = process_config(config)




@run.command()
@click.option('-k', '--kind',
              type=click.Choice(['all', 'site', 'users', 'projects']),
              help="Which type of config?",
              show_default=True,
              default='all')
@click.argument("base_dir",
                type=click.Path(exists=True))
@click.pass_context
def config(ctx, kind, base_dir):
    """Generate a fresh default config of selected type.

    Will backup copies if files exists.

    \b
    Positional Args:
        BASE_DIR    Path to the top directory in your veoibd-synapse-data-manager installation.
    """
    base_dir = Path(base_dir)
    factory_resets = Path('configs/factory_resets')
    default_files = {"all": factory_resets.glob('*.yaml'),
                     "site": factory_resets / 'site.yaml',
                     "users": factory_resets / 'users.yaml',
                     "projects": factory_resets / 'projects.yaml'
                     }

    if kind == 'all':
        for p in default_files['all']:
            _config.replace_config(name=p.name, factory_resets=factory_resets)
    else:
        p = default_files[kind]
        _config.replace_config(name=p.name, factory_resets=factory_resets)









# Business
if __name__ == '__main__':
    run(obj=munch.Munch())
