**********
Change Log
**********

v0.1.0 / 2017-10-06
===================

  * Successfully parse R1 file names
  * loaders.vcf: fixed imports
  * loaders.vcf.add_parsed_info_col: yank needless lambda
  * loaders.vcf: added cyvcf2 support and zygosity
  * multigene.snake: formatting
  * multigene.snake: added DEBUG metarule list
  * multigene.snake: rearranged imports
  * mulmultigene_LOF_search.snake: changed RUN.globals.input_vcfs
  * multigene.snake: added VCF_CHECK
  * added logging statements
  * added some metadata to multigene pipeline
  * set max mem in snpeff rules to 4g
  * multigene.snake: altered way config files treated
  * config.py: update replace_config
  * misc.py: yank DAG stuff, add load_csv/nan_to_str
  * errors.py remove logging
  * logging.yaml: use top_level_logs to store certain logs
  * update issue template
  * add vscode to ignore
  * switch to logzero
  * multigene: switch to ruamel.yaml
  * added explicit __all__ lists for imports in __init__.py files
  * data.loaders.vcf: defined single `identity` func
  * data.loaders.vcf: formatting and docstrings
  * switched to snaketools
  * removed extraneous `print`
  * Snakefile: switch to logzero
  * Snakefile: switch to ruamel.yaml
  * updated requirements for tools in pipeline
  * switched to snaketools
  * Makefile: corrected `install_python`
  * docs/conf.py is now responsible for sphinx-api call
  * amended module docs title to 'Source Code Documentation'
  * allow files from sphinx-apidoc to be version controled.
  * configs cmd now supports prefixes to group yamls
  * docs/usage.rst: drafted demo "Register New Data"
  * Preliminary switch to logzero logging - currently ignores logging.yaml config vals
  * reorganized docs
  * updated docs/requirements.txt
  * pip install -e . succeeds (hopefully RTD will too)
  * setup.py is now pypi-able
  * Update for RTD
  * Merged pypackage goodies and updated README
  * merged Makefile with updated cookiecutter-data-science
  * add multiple binary file types to ignored
  * committed all from feature/sync-db


v0.0.4 / 2017-03-29
===================

  * TeamSubjectDatabase(SubjectDatabase) is functional
  * ProjectSubjectDatabase(SubjectDatabase) is functional
  * added cli.sycdb skeleton

v0.0.3 / 2017-03-20
===================

  * added rule "SNPSIFT_ANNOTATE"
  * added basic logging boilerplate
  * removed un-needed instantiation of synapse object in cli.push
  * Merge branch 'feature/CD55-filter' into develop
  * Merge branch 'feature/multigene-filter' into develop
  * added src/veoibd_synapse/data/preprocessing/variant_tables.py
  * Merge branch 'feature/multigene-filter' into develop
  * added preprocessing package
  * reorganized
  * Merge branch 'develop' into feature/CD55-filter
  * removed certain existing xls files from tracking
  * Merge branch 'feature/CD55-filter' into develop
  * ignore xls type files and libreoffice lock files
  * Filter is functional.
  * Merge branch 'feature/count-gene-variants' into develop
  * Functional minimal gtf parser
  * Added graph drawing rules to snakefile
