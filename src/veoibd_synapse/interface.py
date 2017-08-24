#!/usr/bin/env python
"""Provide a representation of the interactions between a Synapse Project and other Synapse Entities."""

# Imports
from logzero import logger as log

import synapseclient as syn

import networkx as nx

from munch import Munch, munchify, unmunchify


import veoibd_synapse.errors as e

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


# Business


class VEOProject(object):

    """Manage a collection of Synapse Entities common to a single project."""

    def __init__(self, name=None, annotations=None, synapse_client=None, config_tree=None, **kwargs):
        """Initialize an empty ProjectData object."""
        self.name = name
        self.syn = synapse_client
        self._get_project_entity()
        self.syn_id = self.project['id']
        self._parent_id = self.project['parentId']
        self.conf = self._process_config_tree(config_tree)
        self.annotations = self._process_annotations(annotations)
        self.remote = Munch(entity_dicts=None, dag=None)
        self.dag = None
        self._build_remote_entity_dag()



    def _initialize_project_info(self, ):
        pass

    def _process_config_tree(self, config_tree):
        """Process configuration values."""
        if config_tree is None:
            return Munch()
        else:
            if isinstance(config_tree, Munch):
                return config_tree
            else:
                return munchify(config_tree)

    def _process_annotations(self, annotations):
        """Process annotation values."""
        if annotations is None:
            return Munch()
        else:
            if isinstance(annotations, Munch):
                return annotations
            else:
                return munchify(annotations)

    def _get_remote_entity_dicts(self):
        """Query Synapse for all entity information related to this Project ID."""
        pid = self.project['id'][3:]
        q = 'SELECT * FROM entity WHERE projectId=="{pid}"'.format(pid=pid)

        self.remote.entity_dicts = self.syn.query(q)['results']

    def _build_remote_entity_dag(self):
        """Build a DAG of the remote project structure."""
        self._get_remote_entity_dicts()

        dag = nx.DiGraph()
        dag.node = munchify(dag.node)


        nodes = {ent['entity.id']: SynNode(entity_dict=ent, synapse_session=self.syn) for ent in self.remote.entity_dicts}
        for node in nodes.values():
            try:
                dag.add_node(n=node.id, attr_dict=node)
                dag.add_edge(u=nodes[node['parentId']].id, v=node.id)
            except KeyError as exc:
                if exc.args[0] == self._parent_id:
                    parent = SynNode(entity_dict={'entity.id': self._parent_id}, is_root=True)
                    dag.add_node(n=node.id, attr_dict=node)
                    dag.add_node(n=parent.id, attr_dict=parent)
                    dag.add_edge(u=parent.id, v=node.id)

        # for n in dag.node.keys():
        #     dag.node[n] = Munch(dag.node[n])


        if nx.dag.is_directed_acyclic_graph(dag):
            self.dag = dag
        else:
            raise e.ValidationError('networkx.dag.is_directed_acyclic_graph() returned `False` suggesting a cyclic relationship between entities.')


    def _get_project_entity(self):
        """Set self.project after retrieving the synapse object by name, create the Project if it does not exist."""
        try:
            self.project = self.syn.get(syn.Project(name=self.name))
        except TypeError:
            self.project = self.syn.store(syn.Project(name=self.name))
