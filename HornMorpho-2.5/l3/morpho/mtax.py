import re, os
from .utils import segment
from .semiring import FSSet, UNIFICATION_SR, TOPFSS
from .fs import FeatStructParser

# Default name for final state
DFLT_FINAL = 'fin'
# Signifies no input or output characters associated with an FSS
NO_INPUT = '--'

# new state; capture the state only
STATE_RE = re.compile(r'\s*\$\s+(\S+)$')
# Feature structure for subsequent paths; capture the FS string
# and indentation
FS_RE = re.compile(r'(\s*)(\[.+?\])$')
# Path: input string to match ... Feature Structure Set; capture
# indentation, input string and FSSet
PATH_RE = re.compile(r'(\s*?)(\S+)\s+(\[.*?\])$')
# Path with no FSS
PATH_NO_FS_RE = re.compile(r'(\s*?)(\S+)$')
# A lex file and a Feature Structure Set; capture indentation,
# file name, and FSSet
LEX_RE = re.compile(r'(\s*?)\+(.*?)\+\s+(\[.*?\])$')
# Specify a state other than the next one and a FSS; capture both.
SHORTCUT_FS_RE = re.compile(r'\s*->\s*(\S+)\s*(\[.+?\])$')
# Specify a state other than the next one and a lex file; capture both.
SHORTCUT_LEX_RE = re.compile(r'\s*->\s*(\S+)\s*\+(.*?)\+$')

class MTax:

    def __init__(self, fst, directory=''):
        self.fst = fst
        self.cascade = fst.cascade
        self.seg_units = self.cascade.seg_units
        self.directory = directory
        self.weighting = UNIFICATION_SR
        self.states = []

    def parse(self, label, s, verbose=False):
        """
        Parse a morphotactic FST from a string consisting of multiple lines from a file.
        """
        # Feature structures
        FSs = []

        # Current state
        current_state = None

        # Current FS
        current_fs = None

        # Join lines ending in ';'
        pending_line = ''

        # Current indentation within a state
        current_indent = 0

        lines = s.split('\n')[::-1]

        while lines:
            line = lines.pop().split('#')[0].rstrip() # strip comments

            if not line: continue

            if line[-1] == ';':
                # Continue on to next line
                pending_line += line
                continue

            if pending_line:
                # Add this line onto pending line before parsing
                line = pending_line + line
                pending_line = ''

            # New state
            m = STATE_RE.match(line)
            if m:
                label = m.group(1)
                # Create the state
                self.fst.add_state(label)
                if not current_state:
                    # This must be the first state, so make it initial
                    self.fst._set_initial_state(label)
                # Use this for all paths and lex files until the next state                
                current_state = [label, {'paths': [], 'shortcuts': []}]
                current_fs = None
                current_indent = 0
                self.states.append(current_state)
                continue

            # Lex file to be converted to a letter tree, then to an FST and concatenated in
            # Destination FST not in file, to be used for all entries.
            # +file+
            m = LEX_RE.match(line)
            if m:
                indentation, label, fss = m.groups()
#                print('Lex', label)
                weight = self.weighting.parse(fss)
                filename = label + '.lex'
                if len(indentation) > current_indent and current_fs:
                    # Update FSS with current FS
                    weight = weight.update(weight, current_fs)
                current_state[1]['paths'].append((filename, weight))
                continue

            # Feature structure for subsequent paths
            m = FS_RE.match(line)
            if m:
                indentation, fs = m.groups()
                # a FeatStruct, not a FSSet
                weight = FeatStructParser().parse(fs)
                current_fs = weight
                current_indent = len(indentation)
                continue

            # Path: input string and FSSet
            m = PATH_RE.match(line)
            if m:
                indentation, in_string, fss = m.groups()
                weight = self.weighting.parse(fss)
                if len(indentation) > current_indent and current_fs:
                    # Update FSS with current FS
                    weight = weight.update(weight, current_fs)
                current_state[1]['paths'].append((in_string, weight))
                continue

            # Shortcut to another state with the associated FSS
            m = SHORTCUT_FS_RE.match(line)
            if m:
                next_state, fss = m.groups()
                current_state[1]['shortcuts'].append((next_state, fss))
                continue

            # Shortcut to another state via a lex file
            m = SHORTCUT_LEX_RE.match(line)
            if m:
                next_state, label = m.groups()
                filename = label + '.lex'
                current_state[1]['shortcuts'].append((next_state, filename))
                continue

            # Path: input string but no FSSet
            m = PATH_NO_FS_RE.match(line)
            if m:
                indentation, in_string = m.groups()
                weight = ''
                if len(indentation) > current_indent and current_fs:
                    weight = FSSet(current_fs)
                current_state[1]['paths'].append((in_string, weight))
                continue
            
            raise ValueError("bad line: %r" % line)

    def compile(self, verbose=False):

        # Create a final state
        final_label = DFLT_FINAL
        self.states.append([final_label, {'paths': [], 'shortcuts': []}])
        self.fst.add_state(final_label)
        self.fst.set_final(final_label)

        # Now make the paths between the successive states
        for index, state in enumerate(self.states[:-1]):
            src = state[0]
            paths = state[1].get('paths')
            dest = self.states[index+1][0]
            # Do the normal paths
            for in_string, weight in paths:
                if '.lex' in in_string:
                    # in_string is a lex filename
                    label = in_string.split('.')[0]
                    fst1 = self.cascade.get(label) if self.cascade else None
                    if not fst1:
                        if verbose:
                            print('Creating FST from lex file', in_string)
                        fst1 = self.fst.load(os.path.join(self.cascade.get_lex_dir(), in_string),
# os.path.join(self.directory, in_string),
                                             weighting=self.weighting, cascade=self.cascade,
                                             seg_units=self.seg_units,
                                             lex_features=True, dest_lex=False)
                    if verbose:
                        print('Inserting', fst1.label, 'between', src, 'and', dest)
                    self.fst.insert(fst1, src, dest, weight=weight, mult_dsts=False)
                elif in_string == NO_INPUT:
                    self.fst.add_arc(src, dest, '', '', weight=weight)
                else:
                    self.fst._make_mult_arcs(in_string, '', src, dest, weight, self.seg_units)
            # Do the shortcuts
            shortcuts = state[1].get('shortcuts')
            for dest, wt_file in shortcuts:
                if '.lex' in wt_file:
#                    if verbose:
#                        print('lex shortcut', wt_file)
                    label = wt_file.split('.')[0]
                    fst1 = self.cascade.get(label) if self.cascade else None
                    if not fst1:
                        fst1 = self.fst.load(os.path.join(self.cascade.get_lex_dir(), wt_file),
# os.path.join(self.directory, wt_file),
                                             weighting=self.weighting, cascade=self.cascade,
                                             seg_units=self.seg_units,
                                             lex_features=True, dest_lex=False)
                    if verbose:
                        print('Inserting', fst1.label, 'between', src, 'and', dest)
                    self.fst.insert(fst1, src, dest, weight=TOPFSS, mult_dsts=False)
                else:
                    self.fst.add_arc(src, dest, '', '', weight=wt_file)

