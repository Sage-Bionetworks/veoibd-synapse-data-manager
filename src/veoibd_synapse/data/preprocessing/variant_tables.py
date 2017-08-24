#!/usr/bin/env python
"""Provide code to generate Metadata tables concerning summaries of variants per subject."""

# Imports
from logzero import logger as log

import veoibd_synapse.errors as e
from veoibd_synapse.data import loaders
import veoibd_synapse.data.extract_subids as extract_subids

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"


# Functions
def make_snpeff_gene_table(vcf_path, ignore_variants=None, genome_version=None, sample_name_converter=None):
    vcf_dict = loaders.vcf.load_vcf(path=vcf_path, ignore_variants=ignore_variants)

    zygosity = loaders.vcf.vcf_to_zygosity_table(vcf_dict=vcf_dict,
                                                 genome_version=genome_version,
                                                 extra_index_cols=['SNPEFF_GENE'],
                                                 sample_name_converter=sample_name_converter)
    return zygosity
