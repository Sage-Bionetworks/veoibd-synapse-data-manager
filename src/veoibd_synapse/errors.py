#!/usr/bin/env python
"""Provide error classes for veoibd-synapse-data-manager."""

# Imports


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"




class VEOIBDSynapseError(Exception):

    """Base error class for veoibd-synapse-data-manager."""


class NoResult(VEOIBDSynapseError):
    
    """Raise when an iteration has nothing to return, but normally would."""
