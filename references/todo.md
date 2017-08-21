# Target Functionality
- create new project
- add files to the new project
- update metadata annotations for files in project
- amend permissions on project with list of synapse users

# Current Coding
- [x] Design/write/subclass classes to structure a project and its contained entities.
    - [x] use networkx to map relationshop tree from `entities = syn.query('SELECT id, name, concreteType FROM entity WHERE projectId=="7416980"')`
    - [X] navigate tree to populate self.entities.extant

# General
- [x] make OSX-64 conda pkg
- [x] make manager default to loading factory_reset version of LOGGING config
- [_] there is an error in `dag_tools` at the end of `push` that needs to be figured out
- [_] create a way to automate sharing project with "team"