#!/usr/bin/env python
"""Provide code to build pyparsing objects that deal with GTF lines."""

# Imports
from collections import namedtuple
import pyparsing as p

from munch import Munch, munchify

# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"



class GTFLine(object):
    __slots__ = ["seqname","source","feature","start","end","score","strand","frame","attributes","line_number"]
    def __init__(self, seqname, source, feature, start, end, score, strand, frame, attributes, line_number=None):
        
        self.seqname = seqname
        self.source = source
        self.feature = feature
        self.start = start
        self.end = end
        self.score = score
        self.strand = strand
        self.frame = frame
        self.attributes = attributes
        self.line_number = line_number
        
    def __repr__(self):
       return """GTFLine(seqname="{seqname}", source="{source}", feature="{feature}", start="{start}", end="{end}", score="{score}", strand="{strand}", frame="{frame}", attributes={attributes}, line_number={line_number})""".format(seqname=self.seqname,
                                                source=self.source,
                                                feature=self.feature,
                                                start=self.start,
                                                end=self.end,
                                                score=self.score,
                                                strand=self.strand,
                                                frame=self.frame,
                                                attributes=self.attributes,
                                                line_number=self.line_number)


## Helper parts
semcol = p.Literal(";").suppress()
tab = p.Literal("\t").suppress()
space = p.Literal(" ").suppress()
dquot = p.Literal('"').suppress()
squot = p.Literal("'").suppress()
quote = dquot | squot


# Keywords allowed in Attrs
# NOTE: this is probably why the parser is GLACIALY slow
kws = ["ccdsid",
       "exon_id",
       "exon_number",
       "gene_biotype",
       "gene_id",
       "gene_name",
       "gene_source",
       "gene_status",
       "gene_type",
       "gene_version",
       "havana_gene",
       "havana_transcript",
       "level",
       "ont",
       "protein_id",
       "tag",
       "transcript_id",
       "transcript_name",
       "transcript_status",
       "transcript_support_level",
       "transcript_type",]

## Actual parser pieces
attr_kws = p.Or([p.Keyword(kw) for kw in kws])
attr_item = attr_kws + p.QuotedString('"')


def parse_gtf_file(path):
    """Parse full GTF file by yielding parsed GTF lines.
    
    Commented text is ignored.
    
    Args:
        path (Path): Path obj pointing to GTF file.
    
    Yields:
        GTFLine: representing a parsed GTP line.
    """
    with path.open('r') as gtf:
        line_in_file = 0
        for line in gtf:
            line_in_file += 1
            # discard text to the right of comments
            line = line.strip('\n').split('#')[0]

            if line:
                gtf_line = parse_gtf_line(line, line_number=line_in_file)
                yield gtf_line
             


# def parse_gtf_line1(line, line_number=None):
#     """Parse a single line of GTF file into it's columns, converting the attributes into a dict.
#
#     Args:
#         line (str): One line of GTF formatted information.
#         line_number (int|None): Optional: number of the line this comes from in the file (starting from 1).
#
#     Returns:
#         GTFLine:
#     """
#     cols = line.strip('\n').split('\t')
#     cols[-1] = Munch({x[0][0]:x[0][1] for x in attr_item.scanString(cols[-1])})
#
#     return GTFLine(*cols,line_number=line_number)
    
    
def parse_gtf_line(line, line_number=None):
    """Parse a single line of GTF file into it's columns, converting the attributes into a dict.
    
    Args:
        line (str): One line of GTF formatted information.
        line_number (int|None): Optional: number of the line this comes from in the file (starting from 1).
    
    Returns:
        dict-like
    """
    columns = line.strip('\n').split('\t')
    required_cols = columns[:-1]
    attrs_col = columns[-1]

    attr_strings = (item.strip() for item in attrs_col.strip(';').replace('"','').split(';'))
    kvs = (attr_string.split() for attr_string in attr_strings)

    attr_lib = Munch({k:v for k,v in kvs})
    attr_lib
    
    return GTFLine(*required_cols, attr_lib, line_number=line_number)