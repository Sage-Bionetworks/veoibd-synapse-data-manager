#!/usr/bin/env python
"""Provide error classes for veoibd-synapse-data-manager."""

# Imports


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"




class VEOIBDSynapseError(Exception):

    """Base error class for veoibd-synapse-data-manager."""


class NotImplementedYet(NotImplementedError,VEOIBDSynapseError):

    """Raise when a section of code that has been left for another time is asked to execute."""

    def __init__(self, msg=None):
        """Set up the Exception."""
        if msg is None:
            msg = "That bonehead {author} should really hear your rage about this disgraceful result! Feel free to tell them at {email}".format(author=__author__,email=__email__)

        self.args = (msg, *self.args)



class NoResult(VEOIBDSynapseError):

    """Raise when an iteration has nothing to return, but normally would."""

class ValidationError(VEOIBDSynapseError):

    """Raise when a validation/sanity check comes back with unexpected value."""
