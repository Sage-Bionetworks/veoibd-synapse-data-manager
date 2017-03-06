#!/usr/bin/env python
"""Provide code to help preprocess tasks for getting which genes a subject's SNPs are in."""

# Imports
from pathlib import Path

import numpy as np
import pandas as pd

from munch import Munch, munchify

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


# Functions
def extract_column_names(path):
    with path.open('r') as vcf:
        for line in vcf:
            if line.startswith("#CHROM"):
                return line.lstrip('#').rstrip("\n").split('\t')
            
def load_vcf(path):
    m = Munch()
    column_names = extract_column_names(path)
    
    vcf = pd.read_csv(str(path), sep='\t', comment='#', header=None).rename(columns={old:new for old,new in enumerate(column_names)})
    
    # remove variants that we think are suprious
    bad_vars = set(['rs56966114'])
    
    vcf = vcf[~vcf.ID.isin(bad_vars)]
    
    
    meta_cols = vcf.columns.values[:9]
    sample_cols = vcf.columns.values[9:]


    meta = add_snpeff_gene_col(vcf[meta_cols]).set_index(['CHROM', 'POS', 'ID', 'REF', 'ALT','QUAL','FORMAT'])
    
    sample = vcf[sample_cols]
    
    sample.index = vcf.set_index(['CHROM', 'POS', 'ID', 'REF', 'ALT','QUAL','FORMAT']).index
    
    
    m.full = vcf
    m.meta = meta
    m.sample = sample
    
    return m
        

def add_snpeff_gene_col(df):
    t = df.copy()
    t.loc[:,'snpeff_gene'.upper()] = t.loc[:,'INFO'].apply(lambda i: i.split(';ANN=')[1].split('|')[3])
    return t




def map_genes_to_samples(df, test=None):
    df = df.copy()
    genes = df.iloc[:,0].copy()
    samples = df.iloc[:,1:].copy()
    
    if test is None:
        mask = samples.applymap(lambda x: True if x is True else False)
    else:
        mask = samples.applymap(lambda x: test(x))
    
    for i in range(samples.shape[1]):
        yes_gene = genes[mask.iloc[:,i]]
        no_gene = genes[~mask.iloc[:,i]]
        no_gene = no_gene.apply(lambda x: np.NaN)
        samples.iloc[:,i] = pd.concat([no_gene,yes_gene]).sort_index()
        
    return samples


def to_012_zygosity(x):
    try:
        return sum([int(a) for a in x.split('/')])
    except ValueError as exc:
        dot = "invalid literal for int() with base 10: '.'"
        if dot in exc.args[0]:
            return np.NaN
        else:
            raise exc


def subject_from_regeneron1_fname(fname):
    """Parse a file name from the REGENERON1 data batch to as close to a subject_id as possible.
    
    Args:
        fname (``str``): a file name.
        
    Returns:
        ``str``
    """
    return fname.split('_')[1].rstrip('P').rstrip('M').rstrip('D').rstrip('F')