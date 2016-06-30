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

Author: Michael Gasser <gasser@cs.indiana.edu>
"""

_version = '3.0'
_para_version = '1.0'
_horn_version = '2.5'

from . import morpho

print('\n>>>>> This is L3Morpho, version {} <<<<<'.format(_version))
# print(  '>>>>>   and ParaMorfo, version', _para_version, ' <<<<<\n')
print('>>>>>  and HornMorpho, version {}  <<<<<'.format(_horn_version))

def load_lang(language, phon=False, segment=False, load_morph=True, verbose=False):
    """Load a language's morphology.

    @param language: a language label
    @type  language: string
    """
    morpho.load_lang(language, phon=phon, segment=segment, load_morph=load_morph,
                     verbose=verbose)

def seg_word(language, word, root=False, citation=False, gram=False,
             roman=False, raw=False):
    '''Segment a single word and print out the results.
    
    @param language: abbreviation for a language
    @type  language: string
    @param word:     word to be analyzed
    @type  word:     string or unicode
    @param root:     whether a root is to be included in the analyses
    @type  root:     boolean
    @param citation: whether a citation form is to be included in the analyses
    @type  citation: boolean
    @param gram:     whether a grammatical analysis is to be included
    @type  gram:     boolean
    @param roman:    whether the language is written in roman script
    @type  roman:    boolean
    @param raw:      whether the analyses should be returned in "raw" form
    @type  raw:      boolean
    @return:         a list of analyses (only if raw is True)
    @rtype:          list of (root, feature structure) pairs
    '''
    language = morpho.get_language(language, phon=False, segment=True)
    if language:
        analysis = language.anal_word(word, preproc=not roman,
                                      postproc=not roman and not raw,
                                      root=root, citation=citation, gram=gram,
                                      segment=True, only_guess=False,
                                      print_out=not raw,
                                      string=not raw)
        if raw:
            print('Analysis', analysis)
            if gram:
                return [(anal[1], anal[-1]) for anal in analysis]
            else:
                return analysis

seg = seg_word

def seg_file(language, infile, outfile=None, root=False, citation=False, gram=False,
             preproc=True, postproc=True, start=0, nlines=0):
    '''Analyze the words in a file, writing the analyses to outfile.

    @param infile:   path to a file to read the words from
    @type  infile:   string
    @param outfile:  path to a file where analyses are to be written
    @type  outfile:  string
    @param root:     whether a root is to be included in the analyses
    @type  root:     boolean
    @param citation: whether a citation form is to be included in the analyses
    @type  citation: boolean
    @param gram:     whether a grammatical analysis is to be included
    @type  gram:     boolean
    @param preproc:  whether to preprocess inputs
    @type  preproc:  boolean
    @param postproc: whether to postprocess outputs
    @type  postproc: boolean
    @param start:    line to start analyzing from
    @type  start:    int
    @param nlines:   number of lines to analyze (if not 0)
    @type  nlines:   int
    '''
    language = morpho.get_language(language, phon=False, segment=True)
    if language:
        language.anal_file(infile, outfile, root=root, citation=citation, gram=gram,
                           pos=None, preproc=preproc, postproc=postproc,
                           segment=True, only_guess=False, guess=False,
                           start=start, nlines=nlines)

def anal_word(language, word, root=True, citation=True, gram=True,
              non_roman=True, roman=False, segment=False, guess=False,
              dont_guess=False,
              rank=True, freq=True, nbest=100,
              raw=False):
    '''Analyze a single word, trying all available analyzers, and print out
    the analyses.
    
    @param language: abbreviation for a language
    @type  language: string
    @param word:     word to be analyzed
    @type  word:     string or unicode
    @param root:     whether a root is to be included in the analyses
    @type  root:     boolean
    @param citation: whether a citation form is to be included in the analyses
    @type  citation: boolean
    @param gram:     whether a grammatical analysis is to be included
    @type  gram:     boolean
    @param non_roman: whether the language is written in non-roman script
                      (included for backwards compatibility)
    @type  non_roman: boolean
    @param roman:    whether the language is written in roman script
    @type  roman:    boolean
    @param segment:  whether to return the segmented input string rather than
                     the root/stem
    @type  segment:  boolean
    @param guess:    try only guesser analyzer
    @type guess:     boolean
    @param dont_guess:    try only lexical analyzer
    @type dont_guess:     boolean
    @param rank:     whether to rank the analyses by the frequency of their roots
    @type  rank:     boolean
    @param freq:     whether to report frequencies of roots
    @type  freq:     boolean
    @param nbest:    maximum number of analyses to return or print out
    @type  nbest:    int
    @param raw:      whether the analyses should be returned in "raw" form
    @type  raw:      boolean
    @return:         a list of analyses (only if raw is True)
    @rtype:          list of (root, feature structure) pairs
    '''
    language = morpho.get_language(language, phon=False, segment=segment)
    if language:
        analysis = language.anal_word(word, preproc=non_roman and not roman,
                                      postproc=(non_roman and not roman) and not raw,
                                      root=root, citation=citation, gram=gram,
                                      segment=segment, only_guess=guess,
                                      guess=not dont_guess,
                                      nbest=nbest,
                                      string=not raw, print_out=not raw)
        if raw:
            return analysis
#        if raw:
#            return [(anal[1], anal[-2], anal[-1]) if len(anal) > 2 else (anal[1],) for anal in analysis]

anal = anal_word

def anal_files(language, infiles, outsuff='.out',
               root=True, citation=True, gram=True,
               preproc=True, postproc=True, guess=False, raw=False,
               dont_guess=False, rank=True, freq=True, nbest=100):
    """Analyze the words in a set of files, writing the analyses to
    files whose names are the infile names with outpre prefixed to them.
    See anal_file for description of parameters."""
    language = morpho.get_language(language)
    if language:
        # Dict for saving analyses
        saved = {}
        for infile in infiles:
            outfile = infile + outsuff
            language.anal_file(infile, outfile, root=root, citation=citation, gram=gram,
                               pos=None, preproc=preproc, postproc=postproc,
                               nbest=nbest,
                               only_guess=guess, guess=not dont_guess,
                               raw=raw, saved=saved)

def anal_file(language, infile, outfile=None,
              root=True, citation=True, gram=True,
              preproc=True, postproc=True, guess=False, raw=False,
              dont_guess=False,
              rank=True, freq=True, nbest=100,
              start=0, nlines=0):
    '''Analyze the words in a file, writing the analyses to outfile.

    @param infile:   path to a file to read the words from
    @type  infile:   string
    @param outfile:  path to a file where analyses are to be written
    @type  outfile:  string
    @param root:     whether a root is to be included in the analyses
    @type  root:     boolean
    @param citation: whether a citation form is to be included in the analyses
    @type  citation: boolean
    @param gram:     whether a grammatical analysis is to be included
    @type  gram:     boolean
    @param preproc:  whether to preprocess inputs
    @type  preproc:  boolean
    @param postproc: whether to postprocess outputs
    @type  postproc: boolean
    @param guess:    try only guesser analyzer
    @type guess:     boolean
    @param dont_guess: try only lexical analyzer
    @type dont_guess: boolean
    @param rank:     whether to rank the analyses by the frequency of their roots
    @type  rank:     boolean
    @param freq:     whether to report frequencies of roots
    @type  freq:     boolean
    @param raw:      whether the analyses should be printed in "raw" form
    @type  raw:      boolean
    @param start:    line to start analyzing from
    @type  start:    int
    @param nlines:   number of lines to analyze (if not 0)
    @type  nlines:   int
    '''
    language = morpho.get_language(language)
    if language:
        language.anal_file(infile, outfile, root=root, citation=citation, gram=gram,
                           pos=None, preproc=preproc, postproc=postproc,
                           only_guess=guess, guess=not dont_guess,
                           raw=raw,
                           nbest=nbest,
                           start=start, nlines=nlines)

##def anal_gui(language, infile, outfile=None):
##    '''Open a window for reading in a file where words can be clicked for analysis.'''
##    language = morpho.get_language(language)
##    if language:
##        app = morpho.anal_gui.App(language, fname=infile)
##        app.MainLoop()

def gen(language, root, features=[], pos=None, guess=False, phon=False,
        roman=False, non_roman=True):
    '''Generate a word, given stem/root and features (replacing those in default).
    If pos is specified, check only that POS; otherwise, try all in order until one succeeeds.

    @param root:     root or stem of a word
    @type  root:     string (roman)
    @param features: grammatical features to be added to default
    @type  features: string containing bracketed expression, e.g., '[sb=[+p1,+plr]]'
    @param pos:      part-of-speech: use only the generator for this POS
    @type  pos:      string
    @param guess:    whether to use guess generator if lexical generator fails
    @type  guess:    boolean
    @param roman:    whether the languages uses a roman script
    @type roman:      boolean
    @param non_roman: whether the language uses a non-roman script
    @type  non_roman: boolean
    '''
    language = morpho.get_language(language, segment=False, phon=phon)
    if language:
        is_not_roman = not roman and non_roman
        morf = language.morphology
        if pos:
            posmorph = morf[pos]
            output = posmorph.gen(root, update_feats=features,
                                  postproc=is_not_roman, guess=guess)
            if output:
                print(output[0][0])
                return
        else:
            for posmorph in list(morf.values()):
                output = posmorph.gen(root, update_feats=features,
                                      postproc=is_not_roman, guess=guess)
                if output:
                    print(output[0][0])
                    return
        print("This word can't be generated!")

def phon_word(lang_abbrev, word, gram=False, raw=False,
              postproc=False, rank=True, nbest=100, freq=True):
    '''Convert a form in non-roman to roman, making explicit features that are missing in the orthography.
    @param lang_abbrev: abbreviation for a language
    @type  lang_abbrev: string
    @param word:     word to be analyzed
    @type  word:     string or unicode
    @param gram:     whether a grammatical analysis is to be included
    @type  gram:     boolean
    @param postproc: whether to run postpostprocess on the form
    @type  postproc: boolean
    @param rank:     whether to rank the analyses by the frequency of their roots
    @type  rank:     boolean
    @param nbest:    maximum number of analyses to return or print out
    @type  nbest:    int
    @param freq:     whether to report frequencies of roots
    @type  freq:     boolean
    @return:         a list of analyses
    @rtype:          list of (root, feature structure) pairs
    '''
    language = morpho.get_language(lang_abbrev, phon=True, segment=False)
    if language:
        return language.ortho2phon(word, gram=gram, raw=raw, return_string=False,
                                   report_freq=freq, nbest=nbest,
                                   postpostproc=postproc, rank=rank)

phon = phon_word

def phon_file(lang_abbrev, infile, outfile=None, gram=False,
              word_sep='\n', anal_sep=' ', print_ortho=True,
              postproc=False, rank=True, freq=True, nbest=100,
              start=0, nlines=0):
    '''Convert non-roman forms in file to roman, making explicit features that are missing in the orthography.
    @param lang_abbrev: abbreviation for a language
    @type  lang_abbrev: string
    @param infile:   path to a file to read the words from
    @type  infile:   string
    @param outfile:  path to a file where analyses are to be written
    @type  outfile:  string
    @param gram:     whether a grammatical analysis is to be included
    @type  gram:     boolean
    @param word_sep: separator between words (when gram=False)
    @type  word_sep: string
    @param anal_sep: separator between analyses (when gram=False)
    @type  anal_sep: string
    @param print_ortho: whether to print out orthographic form (when gram=False)
    @type  print_ortho: boolean
    @param postproc: whether to run postpostprocess on the form
    @type  postproc: boolean
    @param rank:     whether to rank the analyses by the frequency of their roots
    @type  rank:     boolean
    @param freq:     whether to report frequencies of roots
    @type  freq:     boolean
    @param nbest:    maximum number of analyses to return or print out for each word
    @type  nbest:    int
    @param start:    line to start analyzing from
    @type  start:    int
    @param nlines:   number of lines to analyze (if not 0)
    @type  nlines:   int
    '''
    language = morpho.get_language(lang_abbrev, phon=True, segment=False)
    if language:
        language.ortho2phon_file(infile, outfile=outfile, gram=gram,
                                 word_sep=word_sep, anal_sep=anal_sep, print_ortho=print_ortho,
                                 postpostproc=postproc, rank=rank, nbest=nbest,
                                 report_freq=freq,
                                 start=start, nlines=nlines)

def get_features(language, pos=None):
    '''Return a dict of features and their possible values for each pos.

    @param language:  abbreviation for a language
    @type  language:  string
    @param pos:       part-of-speech; if provided, return only
                      features for this POS
    @type  pos:       string
    @return:          dictionary of features and possible values; if
                      there is more than one POS, list of such
                      dictionaries.
    @rtype:           dictionary of feature (string): possible values (list)
                      pairs or list of (pos, dictionary) pairs
    '''
    language = morpho.get_language(language)
    if language:
        morf = language.morphology
        if pos:
            return morf[pos].get_features()
        elif len(morf) == 1:
            return list(morf.values())[0].get_features()
        else:
            feats = []
            for pos, posmorph in list(morf.items()):
                feats.append((pos, posmorph.get_features()))
            return feats

### Functions for debugging and creating FSTs

def cascade(language, pos, gen=False, phon=False, segment=False, 
            verbose=False):
    '''Returns a cascade for the language and part-of-speech.
    @param language: abbreviation for a language, for example, 'gn'
    @type  language: string
    @param pos:    part-of-speech for the cascade, for example, 'v'
    @type  pos:    string
    @param phon:   whether the cascade is for phonology
    @type  phon:   boolean
    @param segment: whether the cascade is for segmentation
    @type  segment: boolean
    @param invert: whether to return the inverted cascade (for generation).
    @type  invert: boolean
    @param verbose: whether to print out various messages
    @type  verbose: boolean
    @return:       cascade for the the language and POS: a list of FSTs
    @rtype:        instance of the FSTCascade class (subclass of list)
    '''
    pos = get_pos(language, pos, phon=phon, segment=segment, load_morph=False, verbose=verbose)
    if not gen and pos.casc:
        return pos.casc
    if gen:
        if pos.casc_inv:
            return pos.casc_inv
        if pos.casc:
            casc_inv = pos.casc.inverted()
            pos.casc_inv = casc_inv
            return casc_inv
    pos.load_fst(True, create_fst=False, generate=gen, invert=gen, gen=gen,
                 segment=segment, verbose=verbose)
    if gen:
        return pos.casc_inv
    return pos.casc

def recompile(language, pos, phon=False, segment=False, gen=False, backwards=False,
              save=True, verbose=True):
    '''Recompiles the cascade FST for the language and part-of-speech.
    @param language: abbreviation for a language, for example, 'gn'
    @type  language: string
    @param pos:    part-of-speech for the cascade, for example, 'v'
    @type  pos:    string
    @param phon:   whether the cascade is for phonology
    @type  phon:   boolean
    @param segment: whether the cascade is for segmentation
    @type  segment: boolean
    @param gen:    whether to compile the cascade for generation (rather than analysis)
    @type  gen:    boolean
    @param backwards: whether to compile the FST from top (lexical) to bottom (surface)
                      for efficiency's sakd
    @type  backwards: boolean
    @param save:   whether to save the compiled cascade as an FST file
    @type  save:   boolean
    @param verbose: whether to print out various messages
    @type  verbose: boolean
    @return:       the POS morphology object
    @rtype:        instance of the POSMorphology class
    '''
    pos_morph = get_pos(language, pos, phon=phon, segment=segment, load_morph=False, verbose=verbose)
    fst = pos_morph.load_fst(True, segment=segment, generate=gen, invert=gen,
                             compose_backwards=backwards,
                             phon=phon, verbose=verbose)
    if not fst and gen == True:
        # Load analysis FST
        pos_morph.load_fst(True, verbose=True)
        # ... and invert it for generation FST
        pos_morph.load_fst(generate=True, invert=True, gen=True, verbose=verbose)
    if save:
        pos_morph.save_fst(generate=gen, segment=segment, phon=phon)
    return pos_morph

def test_fst(language, pos, string, gen=False, phon=False, segment=False,
             fst_label='', fst_index=0):
    """Test a individual FST within a cascade, identified by its label or its index,
    on the transduction of a string.
    @param language: abbreviation for a language, for example, 'gn'
    @type  language: string
    @param pos:    part-of-speech for the cascade, for example, 'v'
    @type  pos:    string
    @param phon:   whether the cascade is for phonology
    @type  phon:   boolean
    @param segment: whether the cascade is for segmentation
    @type  segment: boolean
    @param gen:     whether to use the inverted cascade (for generation).
    @type  gen:     boolean
    @param verbose: whether to print out various messages
    @type  verbose: boolean
    @return:       a list of analyses, each a list consisting of a root and a feature-structure set
    @rtype:        list of lists, each of the form [str, FSSet]
    """
    casc = cascade(language, pos, gen=gen, phon=phon, segment=segment)
    if not casc:
        print('No cascade found')
        return
    return casc.transduce1(string, fst_label=fst_label, fst_index=fst_index)

def get_pos(abbrev, pos, phon=False, segment=False, load_morph=False, verbose=False):
    """Just a handy function for working with the POS objects when re-compiling
    and debugging FSTs.
    @param abbrev: abbreviation for a language, for example, 'am'
    @type  abbrev: string
    @param pos:    part-of-speech for the FST, for example, 'v'
    @type  pos:    string
    @param phon:   whether the FST is for phonology
    @type  phon:   boolean
    @param segment: whether the FST is for segmentation
    @type  segment: boolean
    @param verbose: whether to print out various messages
    @type  verbose: boolean
    @return:       POS object for the the language and POS
    @rtype:        instance of the POSMorphology class

    """
    load_lang(abbrev, segment=segment, phon=phon, load_morph=load_morph, verbose=verbose)
    lang = morpho.get_language(abbrev, phon=phon, segment=segment, load=load_morph,
                               verbose=verbose)
    if lang:
        return lang.morphology[pos]

