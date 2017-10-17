#!/usr/bin/env python
"""Provide command line interface to the synapse manager."""

# Imports
import os
from pathlib import Path
import datetime as dt
import shutil

from munch import Munch, munchify, unmunchify
import ruamel.yaml as yaml

import click
from click import echo

import veoibd_synapse.cli.config as _config
import veoibd_synapse.cli.push as _push
import veoibd_synapse.cli.syncdb as _syncdb

from veoibd_synapse.misc import process_config, update_configs
import veoibd_synapse.errors as e

from logzero import logger as log

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"

HOME_DIR = (Path(os.path.realpath(__file__)).parent / '../../..').resolve()


def setup_logging(conf_dict):
    """Set up logging configurations."""
    # logging.config.dictConfig(config=conf_dict)
    # NOTE: converting to logzero. for now ignore logging config till I can learn how to alter logzero with the configs.
    log.debug(msg='Setup logging configurations.')


@click.group(invoke_without_command=True)
@click.option('-c', '--config', default=None,
              help="Path to optional config directory. If `None`, configs/ is searched for *.yaml files.",
              type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--home', default=None,
              help="Print the home directory of the install and exit.",
              is_flag=True)
@click.pass_context
def run(ctx=None, config=None, home=None):
    """Command interface to the veoibd-data-manager.

    For command specific help text, call the specific
    command followed by the --help option.
    """
    ctx.obj = Munch()
    ctx.obj.CONFIG = Munch()

    top_lvl_confs = HOME_DIR / 'configs'

    # Load the factory_resets/logging.yaml as an absolute fall-back logging config
    ctx.obj.CONFIG.LOGGING = process_config(config=top_lvl_confs / 'factory_resets/logging.yaml')

    ctx.obj.CONFIG = update_configs(directory=top_lvl_confs, to_update=ctx.obj.CONFIG)

    if config:
        ctx.obj.CONFIG = update_configs(directory=config, to_update=ctx.obj.CONFIG)

    setup_logging(conf_dict=ctx.obj.CONFIG.LOGGING)

    if home:
        log.debug("Printing HOME_DIR")
        print(HOME_DIR)
        exit(0)


valid_config_kinds = ['all',
                      'site',
                      'users',
                      'projects',
                      'push',
                      'pull',
                      'logging',
                      'mongodb']


@run.command()
@click.option("-l", "--list", "list_",
              is_flag=True,
              default=False,
              help="Print the configuration values that will be used and exit.")
@click.option('-g', '--generate-configs',
              is_flag=True,
              help="Copy one or more of the 'factory default' config files to the top-level "
              "config directory. Back ups will be made of any existing config files.",
              show_default=True,
              default=False)
@click.option('-k', '--kind',
              type=click.Choice(valid_config_kinds),
              help="Which type(s) of config should we replace? May be repeated.",
              multiple=True,
              show_default=True,
              default=['all'])
@click.option('-p', '--prefix',
              type=click.STRING,
              help="""A prefix to tag the new config file(s). Defaults to the ISO formatted time. Example: "2017-08-24T10:08:42.506279".""",
              show_default=False,
              default=None)
@click.pass_context
def configs(ctx, list_, generate_configs, kind, prefix):
    """Manage configuration values and files."""
    if prefix is None:
        prefix = dt.datetime.today().isoformat()

    log.debug("kind = {}".format(kind))

    if list_:
        log.info("Listing current configuration state.")
        conf_str = yaml.dump(unmunchify(ctx.obj.CONFIG), default_flow_style=False)
        echo(conf_str)
        exit(0)

    factory_resets = Path('configs/factory_resets')

    default_files = {k: factory_resets / '{kind}.yaml'.format(kind=k) for k in valid_config_kinds[1:]}
    default_files["all"] = factory_resets.glob('*.yaml')

    if generate_configs:
        if 'all' in kind:
            for p in default_files['all']:
                _config.replace_config(name=p.name,
                                       factory_resets=factory_resets,
                                       prefix=prefix)
        else:
            for k in kind:
                p = default_files[k]
                _config.replace_config(name=p.name,
                                       factory_resets=factory_resets,
                                       prefix=prefix)


@run.command()
@click.option("-u", "--user",
              type=str,
              default=None,
              help="Provide the ID for a user listed in the 'users' config file.")
@click.option("--push-config",
              type=click.Path(exists=True, file_okay=True, dir_okay=False),
              default=None,
              help="Path to the file where this specific 'push' is configured.")
@click.pass_context
def push(ctx, user, push_config):
    """Consume a push-config file, execute described transactions, save record of transactions."""

    _push.main(ctx, user, push_config)





@run.command()
@click.option("-u", "--user",
              type=str,
              default=None,
              help="Provide the ID for a user listed in the 'users' config file.")
@click.option("-t", "--team-name",
              type=str,
              default=None,
              help="Provide the team name in quotes.")
@click.pass_context
def syncdb(ctx, user, team_name):
    """Retrieve and build the most up-to-date metadata database info from Synapse for all Projects shared with ``team-name``."""

    _syncdb.main(ctx, user, team_name)




# Business
if __name__ == '__main__':
    run(obj=Munch())
