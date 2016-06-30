"""
This file is part of the L3Morpho package.

    L3Morpho is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    L3Morpho is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with L3Morpho.  If not, see <http://www.gnu.org/licenses/>.
-------------------------------------------------------

Cascades of weighted finite state transducers.

-- 2011-05-20
    Split off from fst.py.
"""

import re, os, time, functools
from .semiring import *
from .fst import FST

######################################################################
# CONTENTS
######################################################################
# 1. Finite State Transducer Cascade
# 2. Alternation Rules
# 3. Morphotactics
######################################################################

######################################################################
# Constants
######################################################################

FST_DIRECTORY = os.path.join(os.path.dirname(__file__),
                            os.path.pardir,
                            'FST')

## Regexs for parsing cascades
# string_set_label={chars1, chars1, chars2, ...}
SS_RE = re.compile('(\S+)\s*=\s*\{(.*)\}', re.U)
# weighting = UNIFICATION
WEIGHTING_RE = re.compile('weighting\s*=\s*(.*)')
# >fst<
CASC_FST_RE = re.compile(r'>(.*?)<')
# cascade name = {0, 1, 3, ...}
SUBCASC_RE = re.compile('cascade\s*(\S+)\s*=\s*\{(.*)\}')
# +lex+
CASC_LEX_RE = re.compile(r'\+(.*?)\+')


######################################################################
# Finite State Transducer Cascade
######################################################################

class FSTCascade(list):
    """
    A list of FSTs to be composed.
    """

    def __init__(self, label, *fsts):
        list.__init__(self, fsts)

        self.label = label

        # String sets, abbreviated in cascade file
        self._stringsets = {}

        # Semiring weighting for all FSTs; defaults to FSS with unification
        self._weighting = UNIFICATION_SR

        # Composition of FSTs
        self._composition = None

        # All FSTs, including those not in the composition
        self._fsts = {}

        # Language this cascade belongs to
        self.language = None

        # Initial weight to use during transduction
        self.init_weight = None

        # Dictionary of lists of FST indices, for particular purposes
        self._cascades = {}

    def __str__(self):
        """Print name for cascade."""
        return 'FST cascade ' + self.label

    def add(self, fst):
        """Add an FST to the dictionary with its label as key."""
        self._fsts[fst.label] = fst

    def inverted(self):
        """Return a list of inverted FSTs in the cascade."""
        fsts = [(fst.inverted() if isinstance(fst, FST) else fst) for fst in self]
        inv = FSTCascade(self.label + '_inv', *fsts)
        inv.init_weight = self.init_weight
        inv._weighting = self._weighting
        inv._stringsets = self._stringsets
        return inv

    def compose(self, begin=0, end=None, first=None, last=None, subcasc=None, backwards=False,
                relabel=True, trace=0):
        """Compose the FSTs that make up the cascade list or a sublist, including possible first and last FSTs."""
        if len(self) == 1:
            return self[0]
        else:
            fsts = []
            if subcasc:
                if subcasc not in self._cascades:
                    raise ValueError("%r is not a valid subscascade label" % subcasc)
                fsts = [self[i] for i in self._cascades[subcasc]]
            else:
                fsts = self[begin:(end if end != None else len(self))]  # end could be 0
                if first:
                    fsts = [first] + fsts
                if last:
                    fsts.append(last)
            return FST.compose(fsts, self.label + '@', relabel=relabel, trace=trace)

    def mult_compose(self, ends):
        begin = 0
        fsts = []
        for end in ends:
            fsts.append(self.compose(begin, end))
            begin = end
        fsts.append(self.compose(begin, len(self)))
        return fsts

    def rev_compose(self, split_index, begin=0, trace=0):
        """Compose the FSTs in the cascade in two steps."""
        # Compose from split_index to end
        c1 = self.compose(begin=split_index, trace=trace)
        # Compose from beginning to split_index
        return self.compose(begin=begin, end=split_index, last=c1, trace=trace)

    def compose_backwards(self, indices=[], subcasc=None, trace=0):
        if not indices:
            if subcasc:
                # Use a copy of the cascade indices because we're going to reverse them
                indices = list(self._cascades[subcasc])
            else:
                indices = range(len(self))
        indices.reverse()
        c = FST.compose([self[indices[1]], self[indices[0]]], trace=trace)
        for n in indices[2:]:
            c = FST.compose([self[n], c], trace=trace)
        return c

    def composition(self, begin=0, end=None):
        """The composed FSTs."""
        if not self._composition:
            self._composition = self.compose(begin=begin, end=end or len(self))
        return self._composition

    def transduce(self, inp_string, inp_weight, fsts, seg_units=[]):
        result = [[inp_string, inp_weight]]
        for fst in fsts:
            print(fst.label)
            result = reduce_lists([fst.transduce(x[0], x[1], seg_units=seg_units) for x in result])
            if not result:
                return False
        return result

    def stringset(self, label):
        """A labeled set of strings."""
        return self._stringsets.get(label, None)

    def stringset_label(self, stringset):
        """The label for a stringset if it's in the dict."""
        for label, sset in self._stringsets.items():
            if stringset == sset:
                return label

    def stringset_intersection(self, ss_label1=None, ss_label2=None, ss1=None, ss2=None):
        """Label for the intersection of two stringsets or element if only one.

        Either the labels or the stringsets or both are provided."""
        ss1 = ss1 or self.stringset(ss_label1)
        ss2 = ss2 or self.stringset(ss_label2)
        ss_label1 = ss_label1 or self.stringset_label(ss1)
        ss_label2 = ss_label2 or self.stringset_label(ss2)
        if ss1 and ss2:
            intersect = ss1 & ss2
            if intersect:                                    # could be empty
                if len(intersect) == 1:
                    # If there's only one element, don't create a new stringset
                    return list(intersect)[0]
                # Otherwise create a new stringset
                i_label = self.stringset_label(intersect)
                if i_label:
                    # The stringset intersection is already in the dict
                    return i_label
                # The stringset intersection is not in the dict
                # Add it and return its label
                new_label = FSTCascade.simplify_intersection_label(ss_label1, ss_label2)
                return new_label

    @staticmethod
    def simplify_intersection_label(label1, label2):
        """Simplify an intersection label by eliminating common elements."""
        if not '&' in label1 and not '&' in label2:
            # the two expressions between with the same stringset
            return FSTCascade.simplify_difference_intersection_labels(label1, label2)
        else:
            return '&'.join(set(label1.split('&')) | set(label2.split('&')))

    @staticmethod
    def simplify_difference_intersection_labels(label1, label2):
        """Simplify an intersection of differences if first elements are the same."""
        labels1 = label1.split('-')
        labels2 = label2.split('-')
        if labels1[0] == labels2[0]:
            set1 = set(labels1[1].split(',')) if len(labels1) > 1 else set()
            set2 = set(labels2[1].split(',')) if len(labels2) > 1 else set()
            subtracted = set1 | set2
            return labels1[0] + '-' + ','.join(subtracted)
        else:
            return label1 + '&' + label2

    def generate_stringset(self, label):
        """Make a stringset from a label.

        L: stored stringset
        L1-L2: difference of two stored stringsets
        L1-abc: difference of stringset L1 and the set of characters {abc}
        L1&L2: intersection of two stringsets (stored or generated)
        """
        ss = self.stringset(label)
        if ss:
            return ss
        if '-' in label or '&' in label:
            return self.intersect_stringsets(label.split('&'))

    def subtract_stringsets(self, label1, label2):
        """Difference between stringsets with labels or sets of characters."""
        ss1 = self.stringset(label1)
        if not ss1:
            ss1 = set([label1])
        ss2 = self.stringset(label2)
        if not ss2:
            ss2 = set([label2])    # set consisting of single phoneme/grapheme
        return ss1 - ss2

    def intersect_stringsets(self, labels):
        """Intersection of stringsets with given labels."""
        return functools.reduce(lambda x, y: x.intersection(y), [self.diff_stringset(label) for label in labels])

    def diff_stringset(self, label):
        """label is either a stored stringset or a stringset difference expression."""
        ss = self.stringset(label)
        if ss:
            return ss
        labels = label.split("-")
        # Assume there's only one -
        return self.subtract_strings(labels[0], labels[1])

    def subtract_strings(self, label1, label2):
        """Difference between stringsets with labels or sets of characters."""
        ss1 = self.stringset(label1)
        if not ss1:
            ss1 = set(label1.split(','))
        ss2 = self.stringset(label2)
        if not ss2:
            ss2 = set(label2.split(','))
        return ss1 - ss2

    def add_stringset(self, label, seq):
        """Add a labeled set of strings, updating sigma accordingly."""
        self._stringsets[label] = frozenset(seq)

    def weighting(self):
        """The weighting semiring for the cascade."""
        return self._weighting

    def set_weighting(self, label):
        """Set the weighting for the cascade."""
        label = label.lower()
        if 'uni' in label:
            self._weighting = UNIFICATION_SR
        elif 'prob' in label:
            self._weighting = PROBABILITY_SR
        elif 'trop' in label:
            self._weighting = TROPICAL_SR

    def get(self, label):
        """The FST with the given label."""
        return self._fsts.get(label)

    def set_init_weight(self, fs):
        self.init_weight = FSSet(fs)

    @staticmethod
    def load(filename, seg_units=[], create_networks=True, subcasc=None, language=None,
             weight_constraint=None, verbose=True):
        """
        Load an FST cascade from a file.

        If not create_networks, only create the weighting and string sets.
        """
        if verbose:
            print('Loading FST cascade from', filename)
        directory, fil = os.path.split(filename)
        label = del_suffix(fil, '.')

        return FSTCascade.parse(label, open(filename, encoding='utf-8').read(), directory=directory,
                                subcasc=subcasc, create_networks=create_networks, seg_units=seg_units,
                                language=language, weight_constraint=weight_constraint, verbose=verbose)
        
    @staticmethod
    def parse(label, s, directory='', create_networks=True, seg_units=[], subcasc=None, language=None,
              weight_constraint=None, verbose=False):
        """
        Parse an FST cascade from the contents of a file as a string.

        If not create_networks, only create the weighting and string sets.
        """

        cascade = FSTCascade(label)
        cascade.language = language
        cascade.seg_units = seg_units
        
        lines = s.split('\n')[::-1]
        subcasc_indices = []

        while lines:
            line = lines.pop().split('#')[0].strip() # strip comments

            if not line: continue

            # Weighting for all FSTs
            m = WEIGHTING_RE.match(line)
            if m:
                cascade.set_weighting(m.group(1))
                continue

            # Subcascade, specifying indices
            #   label = {i, j, ...}
            m = SUBCASC_RE.match(line)
            if m:
                label, indices = m.groups()
                indices = [int(i.strip()) for i in indices.split(',')]
                cascade._cascades[label] = indices
                # If we're only loading a certain subcascade and this is it, save its indices
                if label == subcasc:
                    subcasc_indices = indices
                continue

            # String set (a list, converted to a frozenset)
            m = SS_RE.match(line)

            if m:
                label, strings = m.groups()
                # Characters may contain unicode
#                strings = strings.decode('utf8')
                cascade.add_stringset(label, [s.strip() for s in strings.split(',')])
                continue

            # FST
            m = CASC_FST_RE.match(line)
            if m:
                if create_networks:
                    label = m.group(1)
                    filename = label + '.fst'
                    if not subcasc_indices or len(cascade) in subcasc_indices:
                        fst = FST.load(os.path.join(directory, filename),
                                       cascade=cascade, weighting=cascade.weighting(),
                                       seg_units=seg_units, weight_constraint=weight_constraint,
                                       verbose=verbose)
                    else:
                        fst = 'FST' + str(len(cascade))
                        if verbose:
                            print('Skipping FST', label)
                    cascade.append(fst)
                continue

            # FST in a lex file
            m = CASC_LEX_RE.match(line)
            if m:
                if create_networks:
                    label = m.group(1)
                    # handle specs
                    filename = label + '.lex'
                    if not subcasc_indices or len(cascade) in subcasc_indices:
                        fst = FST.load(os.path.join(directory, filename),
                                       cascade=cascade, weighting=cascade.weighting(),
                                       seg_units=seg_units, weight_constraint=weight_constraint,
                                       verbose=verbose, lex_features=True)
                        if verbose:
                            print('Adding lex FST', label, 'to cascade')
                    else:
                        fst = 'FST' + str(len(cascade))
                        if verbose:
                            print('Skipping lex FST', label)
                    cascade.append(fst)
                continue
            raise ValueError("bad line: %r" % line)

        return cascade

