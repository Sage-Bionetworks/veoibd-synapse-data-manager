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
def cli(ctx=None, config=None):
    """Command interface to the veoibd-synapse-manager.

    For command specific help text, call the specific
    command followed by the --help option.
    """
    ctx.obj = munch.Munch()

    ctx.obj.CONFIG = process_config(config)




@cli.command()
@click.option('-k', '--kind',
              type=click.Choice(['all', 'site', 'api']),
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
                     "api": factory_resets / 'synapse_api.yaml',}

    if kind == 'all':
        for p in default_files['all']:
            replace_config(name=p.name, factory_resets=factory_resets)
    else:
        p = default_files[kind]
        replace_config(name=p.name, factory_resets=factory_resets)


def replace_config(name, factory_resets):
    """Replace existing config file or generate initial one.

    Backup existing file.
    """
    default_path = factory_resets / name
    conf_path = factory_resets.parent / name

    # print(default_path)
    # print(conf_path)
    # print(bk_path)



    if conf_path.exists():
        bk_path = Path('{name}.bkdup_on_{stamp}'.format(name=str(conf_path),
                                                        stamp=dt.datetime.today().isoformat()))
        shutil.move(src=str(conf_path), dst=str(bk_path))


    shutil.copy(src=str(default_path), dst=str(conf_path))







# Business
if __name__ == '__main__':
    cli(obj=munch.Munch())
