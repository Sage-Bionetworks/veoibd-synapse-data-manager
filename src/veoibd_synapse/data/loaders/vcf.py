#!/usr/bin/env python
"""Provide code needed to load VCF files."""

# Imports
from collections import namedtuple, OrderedDict
from logzero import logger as log

import numpy as np
import pandas as pd

from munch import Munch

from veoibd_synapse.misc import nan_to_str
import veoibd_synapse.errors as e

import cyvcf2

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


def extract_snpeff_gene_from_cyvcf2_variant(variant):
    """Return the 4th value in the ANN data: "GENE".

    Args:
        variant (cyvcf2.Variant): A single ``cyvcf2.Variant`` object.
    """
    try:
        return variant.INFO.get("ANN").split('|')[3]
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

def identity(x):
    return x

def add_parsed_info_col(df, col_name, func=None):
    if func is None:
        func = identity

    t = df.copy()
    t.loc[:, col_name] = t.loc[:, 'INFO'].apply(func)

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
        sample_name_converter = identity

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


def cyvcf2_to_zygosity_table(vcf_path, genome_version=None, extract_from_info=None, sample_name_converter=None):
    """Take cyvcf2 VCF, return pd.DataFrame."""
    if genome_version is None:
        genome_version = "Not Provided"

    if extract_from_info is None:
        extract_from_info = {}
    else:
        if not isinstance(extract_from_info, OrderedDict):
            log.warn("To guarantee the order of your output MultiIndex, use an `OrderedDict` for `extract_from_info`.")

    if sample_name_converter is None:
        sample_name_converter = identity

    vcf = cyvcf2.VCF(str(vcf_path))

    gt_type_map = {vcf.HOM_REF: "HOM_REF",
                   vcf.HET: "HET",
                   vcf.HOM_ALT: "HOM_ALT",
                   vcf.UNKNOWN: "UNKNOWN"}

    zyg_ = Munch()

    ROW_IDX = namedtuple("CYVCF2_TO_ZYGOSITY_TABLE_INDEX",
                         ["CHROM", "POS", "ID", "REF", "ALT", "FORMAT"] + list(extract_from_info.keys()))

    process_row_idx_fields = OrderedDict(CHROM=lambda variant: variant.CHROM,
                                         POS=lambda variant: variant.POS,
                                         ID=lambda variant: nan_to_str(x=variant.ID,
                                                                       replacement="."),
                                         REF=lambda variant: variant.REF,
                                         ALT=lambda variant: ",".join(variant.ALT),
                                         FORMAT=lambda variant: ":".join(variant.FORMAT))

    process_row_idx_fields.update(extract_from_info)

    for variant in vcf:
        fields = dict()
        for f in ROW_IDX._fields:
            fields[f] = process_row_idx_fields[f](variant)

        row_idx = ROW_IDX(**fields)

        row_data = pd.Series(tuple(variant.gt_types), index=vcf.samples)

        zyg_[row_idx] = row_data

    zyg = pd.DataFrame(zyg_).T
    zyg.index.names = ROW_IDX._fields
    zyg = zyg.applymap(lambda x: gt_type_map[x])
    zyg = zyg.rename(columns=sample_name_converter)

    return zyg



def frac_hom_alt(variant):
    return variant.num_hom_alt / variant.num_called

def frac_hom_ref(variant):
    return variant.num_hom_ref / variant.num_called

def frac_het(variant):
    return variant.num_het / variant.num_called

def num_called(variant):
    return variant.num_called
