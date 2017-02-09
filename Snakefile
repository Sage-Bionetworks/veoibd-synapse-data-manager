"""Snakemake file."""
import os
import inspect

from pathlib import Path

import yaml

import pandas as pd
import numpy as np

from matplotlib import pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

import munch




def pathify_by_key_ends(dictionary):
    """Return a dict that has had all values with keys marked as '*_PATH' or '*_DIR' converted to Path() instances."""
    for key, value in dictionary.items():
        if isinstance(value, dict):
            pathify_by_key_ends(value)
        elif key.endswith("_PATH") or key.endswith("_DIR"):
            dictionary[key] = Path(value)

    return dictionary


class MyRun(object):

    """Initialize and manage information common to the whole run."""

    def __init__(self, cfg):
        """Initialize common information for a run."""
        assert isinstance(cfg, dict)

        common = cfg["COMMON"]

        self.snakefile = Path(inspect.getfile(inspect.currentframe()))
        self.globals = munch.Munch()
        self.cfg = cfg
        self.name = common["RUN_NAME"]
        self.d = common["SHARED"]
        self.out_dir = Path("{base_dir}/{run_name}".format(base_dir=common["OUT_DIR"],
                                                           run_name=self.name
                                                           )
                            )
        self.pretty_names = {}
        self.log_dir = self.out_dir / "logs"

class MyRule(object):

    """Manage the initialization and deployment of rule-specific information."""

    def __init__(self, run, name, pretty_name=None):
        """Initialize logs, inputs, outputs, params, etc for a single rule."""
        assert isinstance(run, MyRun)

        if pretty_name is None:
            pretty_name = name

        self.run = run
        self.name = name.lower()
        self.pretty_name = pretty_name

        self.run.pretty_names[self.name] = pretty_name

        self.log_dir = run.log_dir / self.name
        self.log = self.log_dir / "{name}.log".format(name=self.name)
        self.out_dir = run.out_dir / self.name
        self.i = munch.Munch() # inputs
        self.o = munch.Munch() # outputs
        self.p = munch.Munch() # params

        self._import_config_dict()

    def _import_config_dict(self):
        """Inport configuration values set for this rule so they are directly accessable as attributes."""
        try:
            for key, val in self.run.cfg[self.name.upper()].items():
                self.__setattr__(key, val)
            self.cfg = True
        except KeyError:
            self.cfg = False



#### COMMON RUN STUFF ####
ORIGINAL_CONFIG_AS_STRING = yaml.dump(config, default_flow_style=False)
config = pathify_by_key_ends(config)
config = munch.munchify(config)

RUN = MyRun(cfg=config)

PRE = []
ALL = []

# add specific useful stuff to RUN
# RUN.globals.fam_names = [vcf.stem for vcf in config.VALIDATE_INPUT_VCFS.IN.VCF_DIR.glob("*.vcf")]



############ BEGIN PIPELINE RULES ############
# ------------------------- #
#### SAVE_RUN_CONFIG ####
SAVE_RUN_CONFIG = MyRule(run=RUN, name="SAVE_RUN_CONFIG")
SAVE_RUN_CONFIG.o.file = RUN.out_dir / "{NAME}.yaml".format(NAME=RUN.name)



rule save_run_config:
    input:
    output:
        file=str(SAVE_RUN_CONFIG.o.file)

    run:
        with open(output.file, 'w') as cnf_out:
            cnf_out.write(ORIGINAL_CONFIG_AS_STRING)

PRE.append(rules.save_run_config.output)
ALL.append(rules.save_run_config.output)



############ BEGIN PIPELINE RULES ############


#### SAVE_RUN_CONFIG ####
SAVE_RUN_CONFIG_OUT = OUT_DIR+"/{RUN_NAME}.yaml".format(RUN_NAME=RUN_NAME)

rule save_run_config:
    input:
    output:
        file=SAVE_RUN_CONFIG_OUT

    run:
        with open(output.file, 'w') as cnf_out:
            cnf_out.write(ORIGINAL_CONFIG_AS_STRING)

ALL.append(rules.save_run_config.output)




# ------------------------- #
#### RECORD_GENES_WITH_VARIANTS ####
RECORD_GENES_WITH_VARIANTS = MyRule(run=RUN, name="RECORD_GENES_WITH_VARIANTS")

# params
RECORD_GENES_WITH_VARIANTS.p.param_1 = RECORD_GENES_WITH_VARIANTS.PARAMS.param_1

# input
RECORD_GENES_WITH_VARIANTS.i.input_1 = str(RECORD_GENES_WITH_VARIANTS.IN.input_1 / "{something}.ext")

# output
RECORD_GENES_WITH_VARIANTS.o.output_1 = str(RECORD_GENES_WITH_VARIANTS.out_dir / "{something}.ext")

# ---
rule RECORD_GENES_WITH_VARIANTS:
    log:
        path=str(RECORD_GENES_WITH_VARIANTS.log)

    params:
        param_1=RECORD_GENES_WITH_VARIANTS.p.param_1,

    input:
        input_1=RECORD_GENES_WITH_VARIANTS.i.input_1,

    output:
        output_1=RECORD_GENES_WITH_VARIANTS.o.output_1,

    script:
        "python/scripts/RECORD_GENES_WITH_VARIANTS.py"

PRE.append(rules.RECORD_GENES_WITH_VARIANTS.output)



# ------------------------- #


#### ALL ####
# ---
rule all:
    input: ALL


# ------------------------- #
#### DRAW_RULE_GRAPH ####
DRAW_RULE_GRAPH = MyRule(run=RUN, name="DRAW_RULE_GRAPH")

# params
DRAW_RULE_GRAPH.p.pretty_names = RUN.pretty_names

# input

# output
DRAW_RULE_GRAPH.o.rule_graph_dot = str(DRAW_RULE_GRAPH.out_dir / "rule_graph.dot")
DRAW_RULE_GRAPH.o.recoded_rule_graph_dot = str(DRAW_RULE_GRAPH.out_dir / "recoded_rule_graph.dot")
DRAW_RULE_GRAPH.o.recoded_rule_graph_svg = str(DRAW_RULE_GRAPH.out_dir / "recoded_rule_graph.svg")

# ---
rule draw_rule_graph:
    log:
        path=str(DRAW_RULE_GRAPH.log)

    params:
        pretty_names=DRAW_RULE_GRAPH.p.pretty_names,

    input:
        Snakefile=str(RUN.snakefile.absolute()),
        config=rules.save_run_config.output,

    output:
        rule_graph_dot=DRAW_RULE_GRAPH.o.rule_graph_dot,
        recoded_rule_graph_dot=DRAW_RULE_GRAPH.o.recoded_rule_graph_dot,
        recoded_rule_graph_svg=DRAW_RULE_GRAPH.o.recoded_rule_graph_svg,

    run:
        rule_name = RUN.globals.draw_rule
        shell("snakemake -p -s {input.Snakefile}  --configfile {input.config} "+rule_name+" --rulegraph > {output.rule_graph_dot}")

        dag.recode_graph(dot=output.rule_graph_dot,
                         new_dot=output.recoded_rule_graph_dot,
                         pretty_names=RUN.pretty_names,
                         rules_to_drop=['save_run_config',rule_name],
                         color="#50D0FF",
                         use_pretty_names=False)

        shell("dot -Tsvg {output.recoded_rule_graph_dot} -o {output.recoded_rule_graph_svg} -v ; echo ''")


# ------------------------- #
#### DRAW_DAG_GRAPH ####
DRAW_DAG_GRAPH = MyRule(run=RUN, name="DRAW_DAG_GRAPH")

# params
DRAW_DAG_GRAPH.p.pretty_names = RUN.pretty_names

# input

# output
DRAW_DAG_GRAPH.o.dag_graph_dot = str(DRAW_DAG_GRAPH.out_dir / "dag_graph.dot")
DRAW_DAG_GRAPH.o.recoded_dag_graph_dot = str(DRAW_DAG_GRAPH.out_dir / "recoded_dag_graph.dot")
DRAW_DAG_GRAPH.o.recoded_dag_graph_svg = str(DRAW_DAG_GRAPH.out_dir / "recoded_dag_graph.svg")

# ---
rule draw_dag_graph:
    log:
        path=str(DRAW_DAG_GRAPH.log)

    params:
        pretty_names=DRAW_DAG_GRAPH.p.pretty_names,

    input:
        Snakefile=str(RUN.snakefile.absolute()),
        config=rules.save_run_config.output,

    output:
        dag_graph_dot=DRAW_DAG_GRAPH.o.dag_graph_dot,
        recoded_dag_graph_dot=DRAW_DAG_GRAPH.o.recoded_dag_graph_dot,
        recoded_dag_graph_svg=DRAW_DAG_GRAPH.o.recoded_dag_graph_svg,

    run:
        rule_name = RUN.globals.draw_rule
        shell("snakemake -p -s {input.Snakefile}  --configfile {input.config} "+rule_name+" --dag > {output.dag_graph_dot}")

        dag.recode_graph(dot=output.dag_graph_dot,
                         new_dot=output.recoded_dag_graph_dot,
                         pretty_names=RUN.pretty_names,
                         rules_to_drop=['save_run_config',rule_name],
                         color="#50D0FF",
                         use_pretty_names=False)

        shell("dot -Tsvg {output.recoded_dag_graph_dot} -o {output.recoded_dag_graph_svg} -v ; echo ''")