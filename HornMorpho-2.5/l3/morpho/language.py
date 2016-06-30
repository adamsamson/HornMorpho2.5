"""
This file is part of L3Morpho.

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
--------------------------------------------------------------------

Author: Michael Gasser <gasser@cs.indiana.edu>

Language objects, with support mainly for morphology (separate
Morphology objects defined in morphology.py).

-- 2011-07-18
   Languages now created from data in language file:
   Language.make(abbrev)
"""

import os, sys, re

LANGUAGE_DIR = os.path.join(os.path.dirname(__file__),
                            os.path.pardir,
                            'languages')

from .morphology import *
# from Graphics.graphics import *
from .anal import *

# class LLL:
#     version = 3.0

## Regexes for parsing language data
# Language name
LG_NAME_RE = re.compile(r'\s*n.*?:\s*(.*)')
# Backup language abbreviation
# l...: 
BACKUP_RE = re.compile(r'\s*l.*?:\s*(.*)')
# Segments (characters)
# seg...: 
SEG_RE = re.compile(r'\s*seg.*?:\s*(.*)')
# Punctuation
# pun...: 
PUNC_RE = re.compile(r'\s*pun.*?:\s*(.*)')
# Part of speech categories
# pos:
POS_RE = re.compile(r'\s*pos:\s*(.*)')
# Feature abbreviations
# ab...:
ABBREV_RE = re.compile(r'\s*ab.*?:\s*(.*)')
# Term translations
# tr...:
TRANS_RE = re.compile(r'\s*tr.*?:\s*(.*)')
# Beginning of feature-value list
FEATS_RE = re.compile(r'\s*feat.*?:\s*(.*)')
# Feature-value pair
FV_RE = re.compile(r'\s*(.*?)\s*=\s*(.*)')
# FV combinations, could be preceded by ! (= priority)
FVS_RE = re.compile(r'([!]*)\s*([^!]*)')
# Abbrev, with prefixes, and full name
ABBREV_NAME_RE = re.compile(r'([*%]*?)([^*%()]*?)\s*\((.*)\)\s*(\[.*\])?')
NAME_RE = re.compile(r'([*%]*)([^*%\[\]]*)\s*(\[.*\])?')
#re.compile(r'([*%]*)([^*%]*)')

## Regex for checking for non-ascii characters
ASCII_RE = re.compile(r'[a-zA-Z]')

class Language:
    '''A single Language, currently only handling morphology.'''

    T = TDict()

    def __init__(self, label='', abbrev='', backup='',
                 preproc=None, postproc=None,
                 # There may be a further function for post-processing
                 postpostproc=None,
                 seg_units=None,
                 # list of grammatical features to be combined with roots for statistics,
                 # e.g., voice and aspect for Amharic verb roots (assume there's only
                 # list)
                 stat_root_feats=None,
                 # list of lists of grammatical features for statistics, e.g.,
                 # [poss, expl] for Amharic (whether is explicitly possessive)
                 stat_feats=None,
                 citation_separate=True):
#                 msgs=None, trans=None):
        """
        Set some basic language-specific attributes.

        @param preproc            Whether to pre-process input to analysis, for example,
                                  to convert non-roman to roman characters
        @param postproc           Whether to post-process output of generation, for
                                  example, to convert roman to non-roman characters
        @param seg_units          Segmentation units (graphemes)
        @param citation_separate  Whether citation form of words is separate from roots
#        @param msgs               Messages in the languages (or some other)
#        @param trans              Translations of terms from english to this language
        """
        self.label = label
        self.abbrev = abbrev or label[:3]
        # Backup language for term translation, etc.
        self.backup = backup
        self.morphology = None
        self.preproc = preproc
        self.postproc = postproc
        self.postpostproc = postpostproc
        self.seg_units = seg_units or []
        self.stat_root_feats = stat_root_feats or []
        self.stat_feats = stat_feats or []
        self.citation_separate = citation_separate
#        self.msgs = msgs or {}
#        self.trans = trans or {}
        self.directory = self.get_dir()
        self.tlanguages = [abbrev]
        if self.backup:
            self.tlanguages.append(self.backup)
        # Whether the language data and FSTs have been loaded
        self.load_attempted = False

    def __str__(self):
        return self.label or self.abbrev

    def get_dir(self):
        """Where data for this language is kept."""
        return os.path.join(LANGUAGE_DIR, self.abbrev)

    def get_data_file(self):
        """Data file for language."""
        return os.path.join(self.get_dir(), self.abbrev + '.lg')

    @staticmethod
    def make(name, abbrev, load_morph=False, segment=False, phon=False,
             verbose=False):
        """Create a language using data in the language data file."""
        lang = Language(abbrev=abbrev)
        # Load data from language file
        lang.load_data(load_morph=load_morph, segment=segment, phon=phon,
                       verbose=verbose)
#        if load_morph:
#            lang.load_morpho(verbose=verbose)
        return lang

    def load_data(self, load_morph=False, segment=False, phon=False,
                  verbose=False):
        if self.load_attempted:
            return
        self.load_attempted = True
        filename = self.get_data_file()
        if not os.path.exists(filename):
#            print(Language.T.tformat('No language data file for {}', [self], self.tlanguages))
            pass
        else:
            if verbose:
                print(Language.T.tformat('Loading language data from {}', [filename], self.tlanguages))
            with open(filename, encoding='utf-8') as stream:
                data = stream.read()
                self.parse(data, verbose=verbose)
        if load_morph:
            self.load_morpho(segment=segment, ortho=True, phon=phon, verbose=verbose)
        # Create a default FS for each POS
        for posmorph in self.morphology.values():
            if not posmorph.defaultFS:
                posmorph.defaultFS = posmorph.make_default_fs()

    def parse(self, data, verbose=False):

        """Read in language data from a file."""
#        if verbose:
        print('Parsing data for', self)

        lines = data.split('\n')[::-1]

        seg = []
        punc = []
        abbrev = {}
        fv_abbrev = {}
        trans = {}
        fv_dependencies = {}
        fv_priorities = {}

        excl = {}
        feats = {}
        lex_feats = {}

        chars = ''

        current = None

        current_pos = ''
        current_feats = []
        current_lex_feats = []
        current_excl = []
        current_abbrevs = {}
        current_fv_abbrev = []
        current_fv_priority = []

        complex_feat = False
        current_feat = None
        current_value_string = ''
        complex_fvs = []

        while lines:

            line = lines.pop().split('#')[0].strip() # strip comments

            # Ignore empty lines
            if not line: continue

            # Beginning of segmentation units
            m = SEG_RE.match(line)
            if m:
                current = 'seg'
                seg = m.group(1).split()
                continue

            m = LG_NAME_RE.match(line)
            if m:
                label = m.group(1).strip()
                self.label = label
                continue

            m = BACKUP_RE.match(line)
            if m:
                lang = m.group(1).strip()
                self.backup = lang
                self.tlanguages.append(lang)
                continue

            m = PUNC_RE.match(line)
            if m:
                current = 'punc'
                punc = m.group(1).split()
                continue

            m = ABBREV_RE.match(line)
            if m:
                current = 'abbrev'
                abb_sig = m.group(1).split()
                if '=' in abb_sig:
                    abb, sig = abb_sig.split('=')
                    abbrev[abb.strip()] = sig.strip()
                continue

            m = TRANS_RE.match(line)
            if m:
                current = 'trans'
                w_g = m.group(1).split()
                if '=' in w_g:
                    w, g = w_g.split('=')
                    # Add to the global TDict
                    Language.T.add(w.strip(), g.strip(), self.abbrev)
#                    self.trans[w.strip()] = g.strip()
                continue

            m = FEATS_RE.match(line)
            if m:
                current = 'feats'
                continue

            if current == 'feats':
                m = POS_RE.match(line)
                if m:
                    # Start a set of features for a new part-of-speech category
                    pos = m.group(1).strip()
                    current_feats = []
                    current_lex_feats = []
                    current_excl = []
                    current_abbrev = {}
                    current_fv_abbrev = []
                    current_fv_dependencies = {}
                    current_fv_priority = []
                    lex_feats[pos] = current_lex_feats
                    feats[pos] = current_feats
                    excl[pos] = current_excl
                    abbrev[pos] = current_abbrev
                    fv_abbrev[pos] = current_fv_abbrev
                    fv_dependencies[pos] = current_fv_dependencies
                    fv_priorities[pos] = current_fv_priority
                    continue

                m = FV_RE.match(line)
                if m:
                    # A feature and value specification
                    feat, val = m.groups()
                    if '+' in feat or '-' in feat:
                        # Expansion for a set of boolean feature values
                        # See if there's a ! (=priority) prefix
                        m2 = FVS_RE.match(feat)
                        priority, fvs = m2.groups()
                        # An abbreviation for one or more boolean features with values
                        fvs = fvs.split(',')
                        fvs = [s.strip() for s in fvs]
                        fvs = [s.split('=') if '=' in s else [s[1:], (True if s[0] == '+' else False)] for s in fvs]
                        current_fv_abbrev.append((fvs, val))
                        if priority:
                            current_fv_priority.append(fvs)
                    elif '=' in val:
                        # Complex feature (with nesting)
                        complex_feat = self.proc_feat_string(feat, current_abbrev, current_excl, current_lex_feats,
                                                             current_fv_dependencies)
                        vals = val.split(';')
                        for fv2 in vals:
                            fv2 = fv2.strip()
                            if fv2:
                                m2 = FV_RE.match(fv2)
                                if m2:
                                    feat2, val2 = m2.groups()
                                    f = self.proc_feat_string(feat2, current_abbrev, current_excl, current_lex_feats,
                                                              current_fv_dependencies)
                                    v = self.proc_value_string(val2, f, current_abbrev, current_excl,
                                                               current_fv_dependencies)
                                    complex_fvs.append((f, v))
                        if len(vals) == 1:
                            current_feats.append((complex_feat, complex_fvs))
                            complex_feat = None
                            complex_fvs = []
                    else:
                        fvs = line.split(';')
                        if len(fvs) > 1:
                            # More than one feature-value pair (or continuation)
                            if not complex_feat:
                                complex_feat = current_feat
                            for fv2 in fvs:
                                fv2 = fv2.strip()
                                if fv2:
                                    m2 = FV_RE.match(fv2)
                                    if m2:
                                        # A single feature-value pair
                                        feat2, val2 = m2.groups()
                                        f = self.proc_feat_string(feat2, current_abbrev, current_excl, current_lex_feats,
                                                                  current_fv_dependencies)
                                        v = self.proc_value_string(val2, f, current_abbrev, current_excl,
                                                                   current_fv_dependencies)
                                        complex_fvs.append((f, v))
                        elif complex_feat:
                            # A single feature-value pair
                            f = self.proc_feat_string(feat, current_abbrev, current_excl, current_lex_feats,
                                                      current_fv_dependencies)
                            v = self.proc_value_string(val, f, current_abbrev, current_excl,
                                                       current_fv_dependencies)
                            complex_fvs.append((f, v))
                            current_feats.append((complex_feat, complex_fvs))
                            complex_feat = None
                            complex_fvs = []
                        else:
                            # Not a complex feature
                            current_feat = self.proc_feat_string(feat, current_abbrev, current_excl, current_lex_feats,
                                                                 current_fv_dependencies)
                            current_value_string = ''
                            val = val.strip()
                            if val:
                                # The value is on this line
                                # Split the value by |
                                vals = val.split('|')
                                vals_end = vals[-1].strip()
                                if not vals_end:
                                    # The line ends with | so the value continues
                                    current_value_string = val
                                else:
                                    v = self.proc_value_string(val, current_feat, current_abbrev, current_excl,
                                                               current_fv_dependencies)
                                    current_feats.append((current_feat, v))

                else:
                    # Just a value
                    val = line.strip()
                    current_value_string += val
                    # Split the value by | to see if it continues
                    vals = val.split('|')
                    if vals[-1].strip():
                        v = self.proc_value_string(current_value_string, current_feat, current_abbrev, current_excl,
                                                   current_fv_dependencies)
                        current_feats.append((current_feat, v))
                        current_value_string = ''

            elif current == 'seg':
                seg.extend(line.strip().split())

            elif current == 'punc':
                punc.extend(line.strip().split())

            elif current == 'pos':
                pos.extend(line.strip().split())

            elif current == 'trans':
                wd, gls = line.strip().split('=')
                # Add to the global TDict
                Language.T.add(wd.strip(), gls.strip(), self.abbrev)
#                self.trans[wd] = gls.strip()

            else:
                raise ValueError("bad line: {}".format(line))

        if punc:
            # Make punc list into a string
            punc = ''.join(punc)

        if seg:
            # Make a bracketed string of character ranges and other characters
            # to use for re
            chars = ''.join(set(''.join(seg)))
            chars = self.make_char_string(chars)
            # Make the seg_units list, [chars, char_dict], expected for transduction,
            # composition, etc.
            self.seg_units = self.make_seg_units(seg)

        if feats and not self.morphology:
            pos_args = []
            for pos in feats:
                pos_args.append((pos, feats[pos], lex_feats[pos], excl[pos],
                                 abbrev[pos], fv_abbrev[pos], fv_dependencies[pos],
                                 fv_priorities[pos]))
            morph = Morphology((), pos_morphs=pos_args,
                               punctuation=punc, characters=chars)
            self.set_morphology(morph)

    def proc_feat_string(self, feat, abbrev_dict, excl_values, lex_feats, fv_dependencies):
        prefix = ''
        depend = None
        m = ABBREV_NAME_RE.match(feat)

        if m:
            prefix, feat, name, depend = m.groups()
            abbrev_dict[feat] = name
        else:
            m = NAME_RE.match(feat)
            prefix, feat, depend = m.groups()

#        print('Prefix {}, feat {}, depend {}'.format(prefix, feat, depend))

        if '*' in prefix:
            excl_values.append(feat)
        if '%' in prefix:
            lex_feats.append(feat)

        if depend:
            # Feature and value that this feature value depends on
            # Get rid of the []
            depend = depend[1:-1]
            # Can be a comma-separated list of features
            depends = depend.split(',')
            for index, dep in enumerate(depends):
                dep_fvs = [fvs.strip() for fvs in dep.split()]
                if dep_fvs[-1] == 'False':
                    dep_fvs[-1] = False
                elif dep_fvs[-1] == 'True':
                    dep_fvs[-1] = True
                elif dep_fvs[-1] == 'None':
                    dep_fvs[-1] = None
                depends[index] = dep_fvs
            fv_dependencies[feat] = depends

        return feat

    def proc_value_string(self, value_string, feat, abbrev_dict, excl_values, fv_dependencies):
        '''value_string is a string containing values separated by |.'''
        values = [v.strip() for v in value_string.split('|')]
        res = []
        prefix = ''
        for value in values:
            if not value:
                continue
            if value == '+-':
                res.extend([True, False])
            else:
                m = ABBREV_NAME_RE.match(value)
                if m:
                    prefix, value, name, depend = m.groups()
                    abbrev_dict[value] = name
                else:
                    m = NAME_RE.match(value)
                    prefix, value, depend = m.groups()

                value = value.strip()

                if value == 'False':
                    value = False
                elif value == 'True':
                    value = True
                elif value == 'None':
                    value = None

                if '*' in prefix:
                    excl_values.append((feat, value))

                if depend:
                    # Feature and value that this feature value depends on
                    depend = depend[1:-1]
                    dep_fvs = [fvs.strip() for fvs in depend.split()]
                    if dep_fvs[-1] == 'False':
                        dep_fvs[-1] = False
                    elif dep_fvs[-1] == 'True':
                        dep_fvs[-1] = True
                    elif dep_fvs[-1] == 'None':
                        dep_fvs[-1] = None
                    fv_dependencies[(feat, value)] = dep_fvs

                res.append(value)
        return tuple(res)

    def make_char_string(self, chars):
        non_ascii = []
        for char in chars:
            if not ASCII_RE.match(char):
                non_ascii.append(char)
        non_ascii.sort()
        non_ascii_s = ''.join(non_ascii)
        return r'[a-zA-Z' + non_ascii_s + r']'

    def make_seg_units(self, segs):
        """Convert a list of segments to a seg_units list + dict."""
        singletons = []
        dct = {}
        for seg in segs:
            c0 = seg[0]
            if c0 in dct:
                dct[c0].append(seg)
            else:
                dct[c0] = [seg]
        for c0, segs in dct.items():
            if len(segs) == 1 and len(segs[0]) == 1:
                singletons.append(c0)
        for seg in singletons:
            del dct[seg]
        singletons.sort()
        return [singletons, dct]

#    def get_trans(self, word):
#        return self.trans.get(word, word)

    def preprocess(self, form):
        '''Preprocess a form.'''
        if self.preproc:
            return self.preproc(form)
        return form

    def postprocess(self, form):
        '''Postprocess a form.'''
        if self.postproc:
            return self.postproc(form)
        return form

    def postpostprocess(self, form):
        '''Postprocess a form that has already been postprocessed.'''
        if self.postpostproc:
            return self.postpostproc(form)
        return form

    def preprocess_file(self, filein, fileout):
        '''Preprocess forms in filein, writing them to fileout.'''
#        fin = codecs.open(filein, 'r', 'utf-8')
#        fout = codecs.open(fileout, 'w', 'utf-8')
        fin = open(filein, 'r', encoding='utf-8')
        fout = open(fileout, 'w', encoding='utf-8')
        for line in fin:
            fout.write(str(self.preproc(line), 'utf-8'))
        fin.close()
        fout.close()

    def set_morphology(self, morphology, verbosity=0):
        '''Assign the Morphology object for this Language.'''
        self.morphology = morphology
        morphology.language = self
        for pos in morphology.values():
            pos.language = self
        morphology.directory = self.directory
        morphology.seg_units = self.seg_units
        morphology.phon_fst = morphology.restore_fst('phon', create_networks=False)

    def load_morpho(self, fsts=None, simplified=False, ortho=True, phon=False,
                    segment=False, recreate=False, verbose=False):
        """Load words and FSTs for morphological analysis and generation."""
        fsts = fsts or self.morphology.pos
        opt_string = ''
        if segment:
            opt_string = 'segmentation'
        elif phon:
            opt_string = 'phonetic'
        if not self.has_cas(generate=phon, simplified=simplified, guess=False,
                            phon=phon, segment=segment):
            print('No {} FST available for {}!'.format(opt_string, self))
            return False
        msg_string = Language.T.tformat('Loading morphological data for {0}{1} ...',
                                        [self, ' (' + opt_string + ')' if opt_string else ''],
                                        self.tlanguages)
        print(msg_string)
        print()
#        print(msg_string.format(self, opt_string))
        # In any case, assume the root frequencies will be needed?
        self.morphology.set_root_freqs()
        self.morphology.set_feat_freqs()
        if ortho:
            # Load unanalyzed words
            self.morphology.set_words(simplify=simplified, ortho=True)
            # Load pre-analyzed words
            self.morphology.set_analyzed(ortho=True)
        if phon:
            # Load unanalyzed words
            self.morphology.set_words(simplify=simplified, ortho=False)
            # Load pre-analyzed words
            self.morphology.set_analyzed(ortho=False)
        for pos in fsts:
            # Load pre-analyzed words if any
            if ortho:
                self.morphology[pos].set_analyzed(ortho=True)
            if phon:
                self.morphology[pos].set_analyzed(ortho=False)
            # Load lexical anal and gen FSTs (no gen if segmenting)
            if ortho:
                self.morphology[pos].load_fst(gen=not segment,
                                              create_casc=False,
                                              simplified=simplified, phon=False, segment=segment,
                                              recreate=recreate, verbose=verbose)
            if phon:
                self.morphology[pos].load_fst(gen=True,
                                              create_casc=False,
                                              simplified=simplified, phon=True, segment=segment,
                                              recreate=recreate, verbose=verbose)
            # Load guesser anal and gen FSTs
            if not segment:
                if ortho:
                    self.morphology[pos].load_fst(gen=True, guess=True, phon=False, segment=segment,
                                                  create_casc=False,
                                                  recreate=recreate, verbose=verbose)
                if phon:
                    self.morphology[pos].load_fst(gen=True, guess=True, phon=True, segment=segment,
                                                  create_casc=False,
                                                  recreate=recreate, verbose=verbose)
        return True

    def get_fsts(self, generate=False, phon=False, segment=False):
        '''Return all analysis FSTs (for different POSs) satisfying phon and segment contraints.'''
        fsts = []
        for pos in self.morphology.pos:
            if phon:
                fst = self.morphology[pos].get_fst(generate=True, phon=True)
            else:
                fst = self.morphology[pos].get_fst(generate=generate, segment=segment)
            if fst:
                fsts.append(fst)
        return fsts

    def has_cas(self, generate=False, simplified=False, guess=False,
                phon=False, segment=False):
        """Is there at least one cascde file for the given FST features?"""
        for pos in self.morphology.pos:
            if self.morphology[pos].has_cas(generate=generate, simplified=simplified,
                                            guess=guess, phon=phon, segment=segment):
                return True
        return False

    ### Analyze words or sentences

    def anal_file(self, pathin, pathout=None, preproc=True, postproc=True, pos=None,
                  root=True, citation=True, segment=False, gram=True,
                  knowndict=None, guessdict=None, saved=None,
                  phon=False, only_guess=False, guess=True, raw=False,
                  rank=True, report_freq=True, nbest=100,
                  nlines=0, start=0):
        """Analyze words in file, either writing results to pathout, storing in
        knowndict or guessdict, or printing out.
        saved is a dict of saved analyses, to save analysis time for words occurring
        more than once.
        """
        preproc = preproc and self.preproc
        postproc = postproc and self.postproc
        citation = citation and self.citation_separate
        storedict = True if knowndict != None else False
        try:
            filein = open(pathin, 'r', encoding='utf-8')
            # If there's no output file and no outdict, write analyses to terminal
            out = sys.stdout
            if segment:
                print('Segmenting words in', pathin)
            else:
                print('Analyzing words in', pathin)
            if pathout:
                # Where the analyses are to be written
                fileout = open(pathout, 'w', encoding='utf-8')
                print('Writing to', pathout)
                out = fileout
            fsts = pos or self.morphology.pos
            n = 0
            # Save words already analyzed to avoid repetition
            saved = saved or {}
            # If nlines is not 0, keep track of lines read
            lines = filein.readlines()
            if start or nlines:
                lines = lines[start:start+nlines]
            for line in lines:
                # Separate punctuation from words
                line = self.morphology.sep_punc(line)
                # Segment into words
                for word in line.split():
                    if word in saved:
                        # Don't bother to analyze saved words
                        analysis = saved[word]
                    else:
                        # If there's no point in analyzing the word (because it contains
                        # the wrong kind of characters or whatever), don't bother.
                        # (But only do this if preprocessing.)
                        analysis = preproc and self.morphology.trivial_anal(word)
                        if analysis:
                            if raw:
                                analysis = (word, [])
                            else:
#                                analysis = self.get_trans('word') + ': ' + analysis + '\n'
                                analysis = 'word: ' + analysis + '\n'
                        else:
                            # Attempt to analyze the word
                            form = word
                            if preproc:
                                form = self.preproc(form)
                            analyses = self.anal_word(form, fsts=fsts, guess=guess, simplified=False,
                                                      phon=phon, only_guess=only_guess,
                                                      segment=segment,
                                                      root=root, stem=True,
                                                      citation=citation and not raw, gram=gram, 
                                                      preproc=False, postproc=postproc and not raw,
                                                      rank=rank, report_freq=report_freq, nbest=nbest,
                                                      string=not raw, print_out=False,
                                                      only_anal=storedict)
                            if raw:
                                analyses = (form, [(anal[0], anal[1], anal[2]) if len(anal) > 2 else (anal[0],) for anal in analyses])
                            # If we're storing the analyses in a dict, don't convert them to a string
                            if storedict or raw:
                                analysis = analyses
                            # Otherwise (for file or terminal), convert to a string
                            else:
                                if analyses:
                                    # Convert the analyses to a string
                                    analysis = self.analyses2string(word, analyses,
                                                                    form_only=segment and not gram)
                                else:
#                                    analysis = '?' + self.get_trans('word') + ': ' + word + '\n'
                                    analysis = '?word: ' + word + '\n'
                        # Store the analyses (or lack thereof)
                        saved[word] = analysis
                    # Either store the analyses in the dict or write them to the terminal or the file
                    if storedict:
                        if analysis:
                            add_anals_to_dict(self, analysis, knowndict, guessdict)
                    elif raw:
                        print(self.pretty_analyses(analysis), file=out)
                    else:
                        print(analysis, file=out)
            filein.close()
            if pathout:
                fileout.close()
        except IOError:
            print('No such file or path; try another one.')

    def pretty_analyses(self, analyses):
        form = analyses[0]
        anals = analyses[1]
        s = '- ' + form + '\n'
        if anals:
            for anal in anals:
                if len(anal) == 1:
                    s += '  {}\n'.format(anal[0])
                else:
                    # root, features, frequency
                    s += '  {} {} {}\n'.format(anal[0], anal[1].__repr__(), anal[2])
        return s

    def analyses2string(self, word, analyses, form_only=False):
        '''Convert a list of analyses to a string.'''
        if form_only:
            return word + ': ' + ', '.join(analyses) + '\n'
        s = ''
        if not analyses:
            s += '?'
        s += Language.T.tformat('{}: {}\n', ['word', word], self.tlanguages)
#        s += self.get_trans('word') + ': ' + word + '\n'
# self.msgs.get('Word', 'Word') + ': ' + word + '\n'
        for analysis in analyses:
            pos = analysis[0]
            if pos:
                pos = pos.replace('?', '')
                if pos in self.morphology:
                    if self.morphology[pos].anal2string:
                        s += self.morphology[pos].anal2string(analysis)
                    else:
                        s += self.morphology[pos].pretty_anal(analysis)
                elif self.morphology.anal2string:
                    s += self.morphology.anal2string(analysis)
        return s

    def analysis2dict(self, analysis, record_none=False, ignore=[]):
        """Convert an analysis (a FeatStruct) to a dict."""
        dct = {}
        for k, v in analysis.items():
            if isinstance(v, FeatStruct):
                v_dict = self.analysis2dict(v, record_none=record_none, ignore=ignore)
                if v_dict:
                    # Could be {}
                    dct[k] = v_dict
            elif not v:
                # v is None, False, '', or 0
                if record_none:
                    dct[k] = None
            elif k not in ignore:
                dct[k] = v
        return dct

    def anal_word(self, word, fsts=None, guess=True, only_guess=False, simplified=False,
                  phon=False, segment=False,
                  root=True, stem=True, citation=True, gram=True,
                  to_dict=False, preproc=False, postproc=False,
                  string=False, print_out=False,
                  rank=True, report_freq=True, nbest=100,
                  only_anal=False):
        '''Analyze a single word, trying all existing POSs, both lexical and guesser FSTs.

        [ [POS, {root|citation}, FSSet] ... ]
        '''
        preproc = preproc and self.preproc
        postproc = postproc and self.postproc
        citation = citation and self.citation_separate
        analyses = []
        fsts = fsts or self.morphology.pos
        if preproc:
            # Convert to roman
            form = self.preproc(word)
        else:
            form = word
        # See if the word is unanalyzable ...
        unal_word = self.morphology.is_word(form, simple=simplified)
        if unal_word:
            if only_anal:
                return []
            analyses.append(self.simp_anal([unal_word], postproc=postproc, segment=segment))
        # ... or is already analyzed
        elif form in self.morphology.analyzed:
            if only_anal:
                return []
            analyses.extend(self.proc_anal_noroot(form, self.morphology.get_analyzed(form)))
        if not analyses:
            if not only_guess:
                for pos in fsts:
                    #... or already analyzed within a particular POS
                    preanal = self.morphology[pos].get_analyzed(form, simple=simplified)
                    if preanal:
                        analyses.extend(self.proc_anal(form, [preanal], pos,
                                                       show_root=root, citation=citation, stem=stem,
                                                       segment=segment,
                                                       simplified=False, guess=False,
                                                       postproc=postproc, gram=gram,
                                                       freq=rank or report_freq))
            if not analyses:
                if not only_guess:
                    # We have to really analyze it; first try lexical FSTs for each POS
                    for pos in fsts:
                        analysis = self.morphology[pos].anal(form, simplified=simplified,
                                                             phon=phon, segment=segment,
                                                             to_dict=to_dict)
                        if analysis:
                            # Keep trying if an analysis is found
                            analyses.extend(self.proc_anal(form, analysis, pos,
                                                           show_root=root, citation=citation and not segment,
                                                           segment=segment,
                                                           stem=stem, simplified=simplified,
                                                           guess=False, postproc=postproc, gram=gram,
                                                           freq=rank or report_freq))
                # If nothing has been found, try guesser FSTs for each POS
                if not analyses and guess:
                    # Accumulate results from all guessers
                    for pos in fsts:
                        analysis = self.morphology[pos].anal(form, guess=True,
                                                             phon=phon, segment=segment,
                                                             to_dict=to_dict)
                        if analysis:
                            analyses.extend(self.proc_anal(form, analysis, pos,
                                                           show_root=root,
                                                           citation=citation and not segment,
                                                           segment=segment,
                                                           simplified=False, guess=True, gram=gram,
                                                           postproc=postproc,
                                                           freq=rank or report_freq))
        if rank and len(analyses) > 1 and not segment:
            analyses.sort(key=lambda x: -x[-1])
        # Select the n best analyses
        analyses = analyses[:nbest]
        if print_out:
            # Print out stringified version
            print(self.analyses2string(word, analyses, form_only=segment and not gram))
#        print('Analyses', analyses)
        elif not string:
            analyses =  [(anal[1], anal[-2], anal[-1]) if len(anal) > 2 else (anal[1],) for anal in analyses]
        
        return analyses

    def simp_anal(self, analysis, postproc=False, segment=False):
        '''Process analysis for unanalyzed cases.'''
        if postproc:
            # Convert the word to Geez.
            analysis[0] = self.postproc(analysis[0])
        if segment:
            return analysis[0]
        return [None, analysis[0]]

    def proc_anal_noroot(self, form, analyses):
        '''Process analyses with no roots/stems.'''
        return [(analysis.get('pos'), None, None, analysis, None, 0) for analysis in analyses]

    def proc_anal(self, form, analyses, pos, show_root=True, citation=True,
                  segment=False, stem=True, simplified=False, guess=False,
                  postproc=False, gram=True, string=False,
                  freq=True):
        '''Process analyses according to various options, returning a list of analysis tuples.
        If freq, include measure of root and morpheme frequency.'''
        cat = '?' + pos if guess else pos
        results = set()
        if segment and not gram:
            return [analysis[0] for analysis in analyses]
        for analysis in analyses:
            root = analysis[0]
            grammar = analysis[1]
            if not show_root and not segment:
                analysis[0] = None
            if postproc and self.morphology[pos].postproc:
                self.morphology[pos].postproc(analysis)
#            proc_root = analysis[0]
            root_freq = 0
            for g in grammar:
                if freq:
                    # The freq score is the count for the root-feature combination
                    # times the product of the relative frequencies of the grammatical features
                    root_freq = self.morphology.get_root_freq(root, g)
                    feat_freq = self.morphology.get_feat_freq(g)
                    root_freq *= feat_freq
                # Find the citation form of the root if required
                if citation and self.morphology[pos].citation:
                    cite = self.morphology[pos].citation(root, g, simplified, guess, stem)
                    if postproc:
                        cite = self.postprocess(cite)
                else:
                    cite = None
                    # Prevent analyses with same citation form and FS (results is a set)
                    # Include the grammatical information at the end in case it's needed
                results.add((cat, root, cite, g if gram else None, g, round(root_freq)))
        return list(results)

    def ortho2phon(self, word, gram=False, raw=False, return_string=False,
                   gram_pre='-- ', postpostproc=False,
                   rank=True, nbest=100, report_freq=True):
        '''Convert a form in non-roman to roman, making explicit features that are missing in orthography.
        @param word:     word to be analyzed
        @type  word:     string or unicode
        @param gram:     whether a grammatical analysis is to be included
        @type  gram:     boolean
        @param return_string: whether to return string analyses (needed for phon_file)
        @type  return_string: boolean
        @param gram_pre: prefix to put before form when grammatical analyses are included
        @type  gram_pre: string
        @param postpostproc: whether to call postpostprocess on output form
        @type  postpostproc: boolean
        @param rank: whether to rank the analyses by the frequency of their roots
        @type  rank: boolean
        @param nbest: return or report only this many analyses
        @type  nbest: int
        @param report_freq: whether to report the frequency of the root
        @type  report_freq: boolean
        @return:         a list of analyses
        @rtype:          list of (root, feature structure) pairs
        '''
        preproc = self.preprocess(word)
        # An output form to count, analysis dictionary
        results = {}
        # Is the word in the word or analyzed lists?
        analyzed = self.morphology.ortho2phon(preproc)
        if analyzed:
            # Just add each form with no analysis to the dict
            if postpostproc:
                analyzed = [self.postpostprocess(a) for a in analyzed]
            results = dict([(a, '') for a in analyzed])
        else:
            # Try to analyze it with FSTs
            for posmorph in self.morphology.values():
                output = posmorph.ortho2phon(preproc, rank=rank)
                if output:
                    # Analyses found for posmorph; add each to the dict
                    for form, anal in output.items():
#                        root_count = count_anal[0]
#                        anal = count_anal[1:]
                        if gram:
                            if not raw:
                                anal = [(a[0], posmorph.anal2string(a[1:])) for a in anal]
                            else:
                                anal = [(a[0], a[2], a[4]) for a in anal]
                        else:
                            anal = [(a[0], a[1:]) for a in anal]
                        if postpostproc:
                            form = self.postpostprocess(form)
                        results[form] = results.get(form, []) + anal
            if not results:
                # No analysis
                # First phoneticize the form and mark as unknown ('?')
                form = '?' + self.morphology.phonetic(preproc)
                if postpostproc:
                    form = self.postpostprocess(form)
                # Then add it to the dict
                results = {form: ''}
        # Now do something with the results
        # Convert the result dict to a list (ranked if rank=True)
        result_list = []
        for f, anals in results.items():
            count = 0
            anal_list = []
            if anals:
                for a in anals:
                    count += a[0]
                    anal_list.append(a[1:])
            result_list.append((f, count, anal_list))
        if rank:
            result_list.sort(key=lambda x: -x[1])
        result_list = result_list[:nbest]
        if gram:
            # Include grammatical analyses
            if not raw:
                if return_string:
                    # Return the results as a string
                    return [(r[0], r[1:]) for r in result_list]
                # Print out the results
                for f, c, anals in result_list:
                    print(gram_pre + f)
                    for anal in anals:
                        print(anal[0], end='')
            else:
                # Return the raw results
                return result_list
        elif raw or return_string:
            # Return only the forms and frequencies
            if rank and report_freq:
                return [(r[0], r[1]) for r in result_list]
            else:
                return [r[0] for r in result_list]
        else:
            # Print out only the forms
            for anal, count in [(r[0], r[1]) for r in result_list]:
                if rank and report_freq:
                    print('{} ({})'.format(anal, count), end=' ')
                else:
                    print('{}'.format(anal), end=' ')
            print()

    def ortho2phon_file(self, infile, outfile=None, gram=False,
                        word_sep='\n', anal_sep=' ', print_ortho=True,
                        postpostproc=False,
                        rank=True, report_freq=True, nbest=100,
                        start=0, nlines=0):
        '''Convert non-roman forms in file to roman, making explicit features that are missing in the orthography.
        @param infile:   path to a file to read the words from
        @type  infile:   string
        @param outfile:  path to a file where analyses are to be written
        @type  outfile:  string
        @param gram:     whether a grammatical analysis is to be included
        @type  gram:     boolean
        @param word_sep:  word separator (only when gram=False)
        @type  word_sep:  string
        @param anal_sep:  analysis separator (only when gram=False)
        @type  anal_sep:  string
        @param print_ortho: whether to print the orthographic form first
        @type  print_ortho: boolean
        @param postpostproc: whether to call postpostprocess on output form
        @type  postpostproc: boolean
        @param rank: whether to rank the analyses by the frequency of their roots
        @type  rank: boolean
        @param report_freq: whether to report the frequency of the root
        @type  report_freq: boolean
        @param start:    line to start analyzing from
        @type  start:    int
        @param nlines:   number of lines to analyze (if not 0)
        @type  nlines:   int
        '''
        try:
#            filein = codecs.open(infile, 'r', 'utf-8')
            filein = open(infile, 'r', encoding='utf-8')
            # Whether to write analyses to terminal
            out = sys.stdout
            # Dictionary to store analyzed words in
            saved_dct = {}
            print('Analyzing words in', infile)
            if outfile:
                # Where the analyses are to be written
#                out = codecs.open(outfile, 'w', 'utf-8')
                out = open(outfile, 'w', encoding='utf-8')
                print('Writing analysis to', outfile)
            lines = filein.readlines()
            if start or nlines:
                lines = lines[start:start+nlines]
            begun = False
            for line in lines:
                # Separate punctuation from words
                line = self.morphology.sep_punc(line)
                # Segment into words
                for word in line.split():
                    if word in saved_dct:
                        # Don't bother to analyze saved words
                        analysis = saved_dct[word]
                    else:
                        # Analyze the word
                        analysis = self.ortho2phon(word, gram=gram,
                                                   postpostproc=postpostproc,
                                                   raw=False, return_string=True,
                                                   rank=rank, report_freq=report_freq, nbest=nbest)
                        saved_dct[word] = analysis
                    # Write the analysis to file or stdout
                    if gram:
                        print("{0}".format(word), file=out)
                        for form, anal in analysis:
                            print("-- {0}".format(form), file=out)
                            for a in anal[1:]:
                                for a1 in a:
                                    print("{0}".format(a1[0]), end='', file=out)
                        print(file=out)
                    else:
                        # Start with the word_sep string
                        if begun:
                            print(file=out, end=word_sep)
                        if print_ortho:
                            # Print the orthographic form
                            print("{0} ".format(word), end='', file=out)
                        for anal in analysis[:-1]:
                            # Print an analysis followed by the analysis separator
                            print("{0} ({1})".format(anal[0], anal[1]), end=anal_sep, file=out)
                        # Print the last analysis with no analysis separator
                        if analysis:
                            print("{0} ({1})".format(analysis[-1][0], analysis[-1][1]), end='', file=out)
                    begun=True
            if not gram:
                # Final newline
                print(file=out)
            filein.close()
            if outfile:
                out.close()
        except IOError:
            print('No such file or path; try another one.')

##class Multiling(dict):
##
##    def __init__(self, *lang_pos):
##        """Constructor takes one or more pairs: (language, pos)."""
##        dict.__init__(self, [(lang.abbrev, lang.morphology[pos]) for lang, pos in lang_pos])
##
##    def trans_word(self, form, source, dest, trace=False):
##        pass
##
##    def graphics(self):
##        start_graphics(self.values())
##
##    def load_fst(self):
##        for pos in self.values():
##            pos.load_fst()
##
##    def set_transfer_fs(self, fss):
##        '''Set the transfer FSs.'''
##        self.transfer_fss = fss
##
##    def transfer1(self, source, source_fs, target):
##        source_trans = FeatStruct()
##        source_trans[source] = source_fs
##        target_morphpos = self[target]
##        for fs in self.transfer_fss:
##            unify_fs = unify(source_trans, fs)
##            if unify_fs:
##                target_morphpos.assign_defaults(unify_fs[target])
##                return unify_fs
##
##    def transfer(self, source_lang, source_fss, target_lang):
##        """Root, FS pairs for generating target word(s)."""
##        target = []
##        for fs_set in source_fss:
##            for fs in fs_set:
##                target_fs = self.transfer1(source_lang, fs, target_lang)
##                if target_fs:
##                    # The source FS unifies with some transfer FS
##                    if target_lang in target_fs:
##                        target_glosses = target_fs[target_lang]['g'], split[',']
##                        for gloss in target_gloses:
##                            target.append((gloss, target_fs))
##        return target
                    
