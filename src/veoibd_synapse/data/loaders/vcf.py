#!/usr/bin/env python
"""Provide code needed to load VCF files."""

# Imports
from logzero import logger as log

import numpy as np
import pandas as pd

from munch import Munch, munchify

import veoibd_synapse.errors as e


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


# Functions
def extract_column_names(path):
    with path.open('r') as vcf:
        for line in vcf:
            if line.startswith("#CHROM"):
                return line.lstrip('#').rstrip("\n").split('\t')


def extract_snpeff_gene_from_info(x):
    """Return the 4th value in the ANN data: "GENE"

    Args:
        x (str): VCF data row.
    """
    try:
        return x.split(';ANN=')[1].split('|')[3]
    except IndexError:
        return np.NaN

def load_vcf(path, ignore_variants=None, extract_from_info=None):
    if ignore_variants is None:
        ignore_variants = []

    if extract_from_info is None:
        extract_from_info = {}

    m = Munch()
    column_names = extract_column_names(path)

    vcf = pd.read_csv(str(path), sep='\t', comment='#', header=None).rename(columns={old:new for old,new in enumerate(column_names)})

    # ignore variants that we think are suprious
    bad_vars = set(ignore_variants)

    vcf = vcf[~vcf.ID.isin(bad_vars)]


    meta_cols = vcf.columns.values[:9]
    sample_cols = vcf.columns.values[9:]

    meta = vcf[meta_cols]
    for col_name, func in extract_from_info.items():
        meta = add_parsed_info_col(df=meta, col_name=col_name, func=func)

    meta = meta.set_index(['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FORMAT'])

    sample = vcf[sample_cols]

    sample.index = vcf.set_index(['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FORMAT']).index


    m.full = vcf
    m.meta = meta
    m.sample = sample

    return m


def add_parsed_info_col(df, col_name, func=None):
    if func is None:
        func = lambda x: x

    t = df.copy()
    t.loc[:, col_name] = t.loc[:, 'INFO'].apply(lambda x: func(x))

    return t


def to_012_zygosity(x):
    try:
        return sum([int(a) for a in x.split('/')])
    except ValueError as exc:
        dot = "invalid literal for int() with base 10: '.'"
        if dot in exc.args[0]:
            return np.NaN
        else:
            raise exc


def vcf_to_zygosity_table(vcf_dict, genome_version=None, extra_index_cols=None, sample_name_converter=None):

    if genome_version is None:
        genome_version = "Not Provided"

    if extra_index_cols is None:
        extra_index_cols = []

    if sample_name_converter is None:
        sample_name_converter = lambda x: x

    meta = vcf_dict.meta
    sample = vcf_dict.sample

    new_index_cols = ['CHROM', 'POS', 'ID', 'REF', 'ALT'] + extra_index_cols
    zygosity_wide = meta.join(sample.applymap(lambda x: to_012_zygosity(x.split(':')[0]))).reset_index().drop(['FILTER', 'INFO', 'QUAL', 'FORMAT'], axis=1).set_index(new_index_cols)

    zygosity_melted = pd.melt(frame=zygosity_wide.reset_index(),
                              id_vars=new_index_cols,
                              value_vars=None,
                              var_name='subject',
                              value_name='zygosity',
                              col_level=None)

    # Remove NaN zygosities and recast as category
    zygosity_not_null = zygosity_melted.zygosity.notnull()
    zygosity_melted = zygosity_melted[zygosity_not_null].copy()
    zygosity_melted['zygosity'] = zygosity_melted.zygosity.astype(np.int64).astype('category')

    # Parse sample_names to subject_id
    zygosity_melted['subject'] = zygosity_melted.subject.apply(lambda i: sample_name_converter(i))

    zygosity_melted = zygosity_melted.rename(columns={'subject': 'subid'})

    return zygosity_melted.assign(genome_version=genome_version)
