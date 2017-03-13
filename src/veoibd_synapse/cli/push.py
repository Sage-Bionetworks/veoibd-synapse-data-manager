#!/usr/bin/env python
"""Provide code devoted to uploading data to Synapse."""

# Imports
import logging
log = logging.getLogger(__name__)

from pathlib import Path
import datetime as dt
import glob
from collections import deque

import networkx as nx
import synapseclient as synapse

from click.utils import echo

from munch import Munch, munchify

import veoibd_synapse.errors as e
from veoibd_synapse.misc import process_config, chunk_md5
import veoibd_synapse.dag_tools as dtools


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"



# Functions
class Push(object):

    """Manage interactions with Synapse concerning adding/changing information on the Synapse servers."""

    def __init__(self, main_confs, user, push_config,):
        """Initialize and validate basic information for a Push."""
        log.debug("Initializing Push obj.")
        
        self.main_confs = main_confs
        self.user = self._process_user(user=user, users=self.main_confs.USERS)
        self.push_id = None
        self.push_time = None
        self.push_config_path = push_config
        self.push_config = self._process_push_config(push_config=push_config)

        log.info("Initializing Synapse client.")
        self.syn = synapse.Synapse()
        self.dag = None

        log.info("Creating interaction instances.")
        self._create_interactions()


    def _process_user(self, user, users):
        """Validate the value for 'user'."""
        if user is None:
            raise e.ValidationError('A value for USER must be provided.')

        try:
            return users[user]
        except KeyError:
            raise e.ValidationError('User "{user}" not found in "users.yaml".'.format(user=user))

    def _process_push_config(self, push_config):
        """Validate the value for 'push_config' and set 'push_id' and 'push_time'."""
        if push_config is None:
            raise e.ValidationError('A value for PUSH_CONFIG must be provided.')

        pconf = process_config(config=push_config)

        try:
            itype = pconf.INTERACTION_TYPE.lower()
            if itype == 'push':

                self.push_id = chunk_md5(push_config, size=1024000)
                self.push_time = dt.datetime.now(tz=dt.timezone.utc).isoformat()
                return pconf
            else:
                msg = """The "INTERACTION_TYPE" of a push-config file must be "push", not "{itype}".""".format(itype=itype)
                raise e.ValidationError(msg)

        except AttributeError:
            msg = """The push-config file must have "INTERACTION_TYPE" set in the top level."""
            raise e.ValidationError(msg)

    def login(self):
        """Log in to Synapse and acquire the project entity."""
        log.info("Initiating log in to Synapse and acquiring the project entity.")
        
        self.syn.login(email=self.user.SYN_USERNAME, apiKey=self.user.API_KEY)

        project_name = self.push_config.PROJECT_NAME
        log.info("""Acquiring Synapse project instance for "{name}".""".format(name=project_name))
        
        try:
            self.project = self.syn.get(synapse.Project(name=project_name))
        except TypeError:
            self.project = self.syn.store(synapse.Project(name=project_name))

        self._build_remote_entity_dag()


    def execute(self):
        """Execute the configured interactions."""
        log.info("Executing configured push interations.")
        
        for interaction in self.interactions:
            interaction.execute()

    def _create_interactions(self):
        """Create and store interaction objects based on the push_config."""
        self.interactions = []

        manual_updates = set(["ANNOTATIONS"])

        for interaction in self.push_config.INTERACTIONS:
            info = self.__base_info()

            # Manual updates
            info.ANNOTATIONS.update(interaction.ANNOTATIONS)

            # Standard updates
            keys = set(interaction.keys()) - manual_updates

            for key in keys:
                info[key] = interaction[key]

            # create and store the PushInteraction
            self.interactions.append(PushInteraction(info=info, push_obj=self))

        # create special interaction to push the config file to the project
        record_info = Munch()
        record_info.REMOTE_DESTINATION_DIR = "push_history"
        record_info.CREATE_DIR = True
        record_info.ANNOTATIONS = Munch()
        record_info.ANNOTATIONS.file_type = 'yaml'
        record_info.LOCAL_PATHS = [self.push_config_path]

        self.interactions.append(PushInteraction(info=record_info, push_obj=self))


    def __base_info(self):
        """Return a fresh basic info tree for a new interaction to update."""
        base_info = Munch({'ANNOTATIONS': Munch()})
        base_info.ANNOTATIONS.deposited_by = self.user.SYN_USERNAME
        base_info.ANNOTATIONS.consortium_site = self.main_confs.SITE.SITE_NAME

        try:
            base_info.ANNOTATIONS.update(self.push_config.COMMON_ANNOTATIONS)
        except AttributeError:
            pass

        base_info.PROJECT_ID = self.push_config.PROJECT_ID

        return base_info

    def _get_remote_entity_dicts(self):
        """Query Synapse for all entity information related to this Project ID."""
        pid = self.project['id'][3:]
        q = 'SELECT * FROM entity WHERE projectId=="{pid}"'.format(pid=pid)

        ent_dicts = {ent['entity.id']: ent for ent in self.syn.query(q)['results']}

        # get rid of the 'entity.' prefixes
        ent_dicts_ = {}
        for name, d in ent_dicts.items():
            d_ = {key.replace('entity.', ''): val for key, val in d.items()}
            ent_dicts_[name] = d_

        self.entity_dicts = ent_dicts_

    def _build_remote_entity_dag(self):
        """Build a DAG of the remote project structure."""
        log.info("Building the project's DAG.")
        self._get_remote_entity_dicts()

        dag = dtools.ProjectDAG(project_id=self.project['id'], synapse_session=self.syn)

        # add nodes and edges with nodes being simple id names for now
        for n_id,node in self.entity_dicts.items():
            dag.add_edge(u=node['parentId'], v=n_id)

        # remove Project's parent from the dag bc it is useless to us.
        # we want our project as root.
        dag.remove_node(self.project['parentId'])

        # SynNode objects as values of each node
        for name in dag.nodes():
            dag.node[name] = dtools.SynNode(entity_dict=self.entity_dicts[name], synapse_session=self.syn)


        # label our project as root
        dag.node[self.project['id']].is_root = True


        if nx.dag.is_directed_acyclic_graph(dag):
            self.dag = dag
        else:
            raise e.ValidationError('networkx.dag.is_directed_acyclic_graph() returned `False` suggesting a cyclic relationship between entities.')



class BaseInteraction(object):

    """Base class to manage information and execution for a single interaction with Synapse."""

    def __init__(self, info):
        """Initialize an Interaction.

        More docs...
        """
        self.info = info


class PushInteraction(BaseInteraction):

    """Manage information and execution for a single "push" interaction with Synapse."""

    def __init__(self, info, push_obj):
        """Initialize a PushInteraction.

        Args:
            info (dict-like): Basic information tree.
            push_obj (Push): Pointer the host ``Push`` object.
        """
        # self.info = None
        super().__init__(info)
        self.push = self._process_push_obj(push_obj)
        self.syn = self.push.syn
        self.info.LOCAL_PATHS = self._process_local_paths()

    def prepare_destination(self):
        """Get or create remote destination."""
        log.info("""Preparing destination "{path}".""".format(path=self.info.REMOTE_DESTINATION_DIR))
        # does our destination exist?
        # If not, create Synapse Objects for them and add to the DAG if appropriate.
        path = deque(self.info.REMOTE_DESTINATION_DIR.split('/'))
        destination = self.push.dag.follow_path_to_folder(path=path, origin=None, create=self.info.CREATE_DIR)

        self.destination = destination

    def add_file(self, loc_file):
        """Create and add Synapse File object to DAG and upload to Synapse."""
        log.info("""File: "{name}".""".format(name=loc_file.name))

        # Create and add file to Synapse
        parent_obj = self.push.dag.node[self.destination]
        annotations = self.info.ANNOTATIONS
        new_file = synapse.File(path=str(loc_file),
                                parent=parent_obj,
                                annotations=annotations)
        new_file = self.syn.store(new_file)
        new_file_id = new_file['id']

        # add file to DAG
        self.push.dag.add_edge(u=self.destination, v=new_file_id, attr_dict=None)
        entity_dict = {k:v  for k,v in new_file.items()}
        self.push.dag.node[new_file_id] = dtools.SynNode(entity_dict=entity_dict,
                                                         synapse_session=self.syn,
                                                         is_root=False)

    def execute(self):
        """Execute the push interaction."""
        self.prepare_destination()

        for loc_file in self.info.LOCAL_PATHS:
            self.add_file(loc_file=loc_file)

    def _process_push_obj(self, push_obj):
        """Make sure we have what we think we have."""
        if not isinstance(push_obj, Push):
            msg = """Expected object of type: "Push", but got one of type: {got}.""".format(got=push_obj.__class__)
            raise e.ValidationError(msg)

        return push_obj

    def _process_local_paths(self):
        """Make sure that all local paths exist and convert them to Path()s."""
        local_paths = []

        for p in self.info.LOCAL_PATHS:
            globbed = glob.glob(p)

            if len(globbed) == 0:
                msg = """LOCAL_PATH value: {p} did not resolve to any files.""".format(p=p)
                raise e.ValidationError(msg)

            for gp in globbed:
                local_paths.append(Path(gp))

        return local_paths







def main(ctx, user, push_config):
    """Consume a push-config file, execute described transactions, save record of transactions."""
    main_confs = ctx.obj.CONFIG

    push = Push(main_confs=main_confs,
                user=user,
                push_config=push_config)
    
    


    push.login()
    push.execute()
