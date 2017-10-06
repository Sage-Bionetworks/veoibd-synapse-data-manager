#!/usr/bin/env python
"""Provide helper utilities to extract_subids specific to BCH."""

# Imports
import logging
from logzero import logger as log

import pandas as pd

from munch import Munch


def process_r1(file_names):
    """Return the extracted and recoded subject_names from file_names."""
    if not isinstance(file_names, pd.Series):
        file_names = pd.Series(data=file_names)

    subject_names = extract_subject_names(file_names=file_names)
    masks = make_class_masks(subject_names=subject_names)

    subject_names = recode_subject_names(subject_names=subject_names, masks=masks)

    return subject_names


def recode_subject_names(subject_names, masks):
    """Return the fully recoded subject_names."""
    subject_names = recode_dashed_alphas(subject_names, masks)
    subject_names = recode_dashed_dots(subject_names, masks)
    subject_names = recode_fam_letters(subject_names, masks)

    return subject_names


def extract_subject_names(file_names):
    """Extract subject names from file_names and return subject_names."""
    return file_names.apply(lambda name: name.split('_')[1])


def make_class_masks(subject_names):
    """Define masks and store in self._class_masks."""
    masks = Munch()

    masks.has_dash = subject_names.apply(test_dash_in)
    masks.first_alpha = subject_names.apply(test_starts_letter)
    masks.last_alpha = subject_names.apply(test_ends_letter)

    return masks


def recode_dashed_alphas(subject_names, masks):
    """Recode appropriate indices of self._subject_names."""
    subject_names = subject_names.copy()
    subject_names[masks.first_alpha &
                  masks.has_dash] = subject_names[masks.first_alpha &
                                                  masks.has_dash].apply(lambda x: x.replace('-', ''))

    return subject_names


def recode_dashed_dots(subject_names, masks):
    """Recode appropriate indices of self._subject_names."""
    subject_names = subject_names.copy()
    subject_names[~masks.first_alpha &
                  masks.has_dash] = subject_names[~masks.first_alpha &
                                                  masks.has_dash].apply(lambda x: x.replace('-', '.'))

    return subject_names


def recode_fam_letters(subject_names, masks):
    """Recode appropriate indices of self._subject_names."""
    subject_names = subject_names.copy()
    subject_names[masks.last_alpha] = subject_names[masks.last_alpha].apply(translate_fam_letter)

    return subject_names


def translate_fam_letter(string):
    """Return string after translating the suffix correctly."""
    letter_map = {"M": ".2",
                  "MM": ".2",
                  "P": ".0",
                  "S": ".4", # this is dangerous (there may be more than one sibling)
                  "B": ".4", # this is dangerous (there may be more than one sibling)
                  "F": ".3"}
    string = string.upper()

    if string.endswith("MM"):
        i = -2
    else:
        i = -1

    string = "{prefix}{suffix}".format(prefix=string[:i],
                                       suffix=letter_map[string[i:]])

    return string


def test_dash_in(x):
    """Return True if x contains a dash."""
    return '-' in x


def test_starts_letter(x):
    """Return True if x starts with a letter."""
    return x[0].isalpha()


def test_ends_letter(x):
    """Return True if x ends with a letter."""
    return x[-1].isalpha()
