#!/usr/bin/env python
"""Provide code to extract subject ID out of various forms used at BCH."""

# Imports
import logging
log = logging.getLogger(__name__)

import veoibd_synapse.errors as e


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


# Functions
def subject_from_regeneron1_fname(fname):
    """Parse a file name from the REGENERON1 data batch to as close to a subject_id as possible.
    
    Args:
        fname (``str``): a file name.
        
    Returns:
        ``str``
    """
    return fname.split('_')[1].rstrip('P').rstrip('M').rstrip('D').rstrip('F')