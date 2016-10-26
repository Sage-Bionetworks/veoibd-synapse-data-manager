# Target Functionality
- create new project
- add files to the new project
- update metadata annotations for files in project
- amend permissions on project with list of synapse users

# Current Coding
- Design/write/subclass classes to structure a project and its contained entities.
    - use networkx to map relationshop tree from `entities = syn.query('SELECT id, name, concreteType FROM entity WHERE projectId=="7416980"')`
    - navigate tree to populate self.entities.extant
