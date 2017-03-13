#!/usr/bin/env python
"""Provide code devoted to retrieving and building the most up-to-date metadata database info from Synapse."""

# Imports
import logging
log = logging.getLogger(__name__)

from pathlib import Path
# import datetime as dt
# import glob
# from collections import deque

import networkx as nx
import synapseclient as synapse

from munch import Munch, munchify

import veoibd_synapse.errors as e
# from veoibd_synapse.misc import process_config, chunk_md5
# import veoibd_synapse.dag_tools as dtools


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"



# Functions







def main(ctx, user, team_name):
    """"""
    main_confs = ctx.obj.CONFIG
    
    

    