#!/usr/bin/env python
"""Provide code devoted to retrieving and building the most up-to-date metadata database info from Synapse."""

# Imports
from logzero import logger as log

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



class SubjectDatabase(object):

    """Base class for managing interactions with Synapse concerning accessing, downloading, and combining subject database files from member-sites."""

    def __init__(self, main_confs, syn):
        """Initialize and validate basic information.

        Extra information section

        Args:
            main_confs (dict-like): refernce to main configuration tree.
            syn (Synapse): an active synapse connection object.

        """
        self.main_confs = main_confs
        self.local_sub_db = main_confs.SITE.LOCAL_PATHS.SUBJECT_DATABASE_DIR
        self.syn = syn
        self.data = Munch()

    # def __repr__(self):
    #     return "%s(main_confs=%r, syn=%r)" % (self.__class__, self.main_confs, self.syn)

class ProjectSubjectDatabase(SubjectDatabase):

    """Manage interactions with Synapse concerning accessing, downloading, and combining subject database files from a single Synapse Project."""

    def __init__(self, main_confs, syn, project_id):
        """Initialize and validate basic information.

        Args:
            main_confs (dict-like): refernce to main configuration tree.
            syn (Synapse): an active synapse connection object.
            project_id (str): Synapse ID for a project.

        """
        super(ProjectSubjectDatabase, self).__init__(main_confs, syn)

        # Ensure that project_id conforms to what synapse client expects.
        if isinstance(project_id, int):
            pass
        elif isinstance(project_id, str):
            try:
                project_id = int(project_id)
            except ValueError:
                if not project_id.startswith('syn'):
                    raise ValueError('Invalid `project_id` value: {v}'.format(v=project_id))
                else:
                    pass

        self.project = self.syn.get(project_id)
        self.data = Munch()
        self.db_files = Munch()

        self.retrieve_db_file_ids()
        self.get_db_files()


    def retrieve_db_file_ids(self):
        """Perform SQL query and return list of ``file.id`` values that are tagged with ``is_db=='true'`` for this project."""
        log.debug('Beginning to retrieve DB file IDs.')

        sql_query = 'SELECT id FROM file WHERE file.is_db == "true" AND file.projectId == "{proj_id}"'

        results = self.syn.query(sql_query.format(proj_id=self.project.id))['results']
        self.data.db_file_ids = [x['file.id'] for x in results]
        log.debug('Retrieved DB file IDs.')

    def get_db_files(self):
        """Iterate through DB file IDs preforming ``sns.get(db_file_id)`` and storing in ``self.db_files``."""
        log.debug('Beginning to download {num} DB files.'.format(num=len(self.data.db_file_ids)))
        for fid in self.data.db_file_ids:
            file_entity = self.syn.get(fid)
            self.db_files[file_entity.properties.name.replace('.','__')] = file_entity

        log.debug('Downloaded {num} DB files.'.format(num=len(self.data.db_file_ids)))

class TeamSubjectDatabase(SubjectDatabase):

    """Manage interactions with Synapse concerning accessing, downloading, and combining subject database files from all member-sites in a Team."""

    def __init__(self, main_confs, syn, team_name):
        """Initialize and validate basic information.

        Args:
            main_confs (dict-like): refernce to main configuration tree.
            syn (Synapse): an active synapse connection object.
            team_name (str): the name of a Synapse Team.

        """
        super(TeamSubjectDatabase, self).__init__(main_confs, syn)
        self.team = self.syn.getTeam(team_name)
        self.project_ids = None
        self.project_dbs = Munch()

        self.retrieve_team_project_ids()
        self.build_project_dbs()
        self.combine_project_dbs()

    def combine_project_dbs(self):
        """This has not yet been implemented.

        Extra information section

        Args:
            param1 (type): The first parameter.
            param2 (type): The second parameter.

        Returns:
            type: The return value. True for success, False otherwise.
        """
        raise NotImplementedError()

    def retrieve_team_project_ids(self):
        """Retrieve info for all projects shared with ``self.team.id``.

        Uses the REST API and results are a multilevel dict-like object with two keys:
            - results (list of info dicts)
            - totalNumberOfResults (int)

        Returns:
            None
        """
        team_id = self.team.id
        team_projects = self.syn.restGET('/projects/TEAM_PROJECTS/team/{team_id}'.format(team_id=team_id))

        proj_ids = []
        for proj in team_projects['results']:
            proj_ids.append(proj['id'])

        self.project_ids = proj_ids

    def build_project_dbs(self):
        """Iterate through project IDs building DB tables from each, storing the restults.

        Stored as ``ProjectSubjectDatabase`` objects
        """
        for project_id in self.project_ids:
            project_db = ProjectSubjectDatabase(main_confs=self.main_confs, syn=self.syn, project_id=project_id)
            self.project_dbs[project_db.project.id] = project_db




def main(ctx, user, team_name):
    """"""
    main_confs = ctx.obj.CONFIG
