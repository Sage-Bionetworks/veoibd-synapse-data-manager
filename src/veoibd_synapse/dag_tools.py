#!/usr/bin/env python
"""Provide functions for working with our DAGs."""

# Imports
from logzero import logger as log

from functools import partial
from collections import deque

import networkx as nx

from munch import Munch, munchify

import synapseclient as synapse

import veoibd_synapse.errors as e

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


# Classes
class SynNode(Munch):

    """Provide methods and attributes to model an entity node in a DAG of Synapse Entities."""

    def __init__(self, entity_dict, synapse_session=None, is_root=False, ):
        """Initialize an entity node object."""
        new_dict = self._process_entity_dict(entity_dict=entity_dict)
        new_dict['is_root'] = is_root
        Munch.__init__(self, new_dict)

        self.syn = synapse_session
        self.obj = self.syn.get(self.id)
        self.needs_update = False

    def store(self):
        """If self.needs_update is True, run sys.store and reset needs_update."""
        if self.needs_update:
            self.syn.store(self.obj)
            self.needs_update = False

    def _process_entity_dict(self, entity_dict):
        new_dict = {}
        for name, value in entity_dict.items():
            attr_name = name.replace('entity.','')
            new_dict[attr_name] = value

            # if name.startswith('entity.'):
            #     attr_name = name.replace('entity.','')
            #     new_dict[attr_name] = value
            # else:
            #     msg = """We expect all keys in an entity-query-result dict to begin with 'entity.', \n\tinstead we found: '{key}'.""".format(key=name)
            #     raise e.ValidationError(msg)
        return new_dict


    def __str__(self):
        """Override this."""
        return self.id

    def __hash__(self):
        """Return hash value."""
        return hash(self.__repr__())

    def __eq__(self, other):
        """Return True if equal."""
        return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        """Return True if NOT equal."""
        return self.__hash__() != other.__hash__()




class ProjectDAG(nx.DiGraph):

    """Class to generate and manage our project structure."""

    def __init__(self, project_id, synapse_session):
        """Set up instance."""
        super(ProjectDAG, self).__init__()

        self.node = munchify(self.node)
        self.project_id = project_id
        self.syn = synapse_session

    def check_children(self, node_id, func):
        """Return list of child-ids where `func` returns True."""
        children = self[node_id]
        successes = []
        for child in children.keys():
            if func(self.node[child]):
                successes.append(child)

        return successes

    def follow_path_to_folder(self, path, origin=None, create=False):
        """Return terminal folder's synID after traversing the defined path."""
        if origin is None:
            origin = self.project_id

        try:
            name = path.popleft()
        except AttributeError:
            path = deque(path)
            name = path.popleft()

        try:
            is_folder_named_x_partial = partial(is_folder_named_x, name=name)
            next_node_id = self.check_children(node_id=origin, func=is_folder_named_x_partial)[0]
        except IndexError:
            # If no child is found:
            if create:
                # create synapse folder object if we were told to
                parent_obj = self.node[origin].obj
                new_folder = synapse.Folder(name, parent=parent_obj)
                new_folder = self.syn.store(new_folder)
                new_folder_id = new_folder['id']

                # add new edge to DAG and mark for update
                self.add_edge(u=origin, v=new_folder_id, attr_dict=None)

                entity_dict = {k:v  for k,v in new_folder.items()}
                self.node[new_folder_id] = SynNode(entity_dict=entity_dict,
                                                   synapse_session=self.syn,
                                                   is_root=False)

                # send the final result back up the chain.
                return new_folder_id

            else:
                # raise an error otherwise
                raise e.NoResult()

        # send next_node_id along to next level
        # or send the final result back up the chain.
        if path:
            return self.follow_path_to_folder(path=path, origin=next_node_id, create=create)
        else:
            return next_node_id






# Test Functions
def is_folder_named_x(child, name):
    """Return True if `child` is a folder named `name`."""
    try:
        return (child.nodeType == 'folder') and (child.name == name)
    except (KeyError, AttributeError):
        # import ipdb; ipdb.set_trace()
        return False
