
"""
This file is part of Morpho.

    Morpho is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Morpho is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Morpho.  If not, see <http://www.gnu.org/licenses/>.

------------------------------------------------------
Author: Michael Gasser <gasser@cs.indiana.edu>

All functions specific to Tigrinya morphology are here (or imported
from geez.py).
"""

from . import language
from .geez import *

### Various functions that will be values of attributes of Tigrinya Morphology
### and POSMorphology objects.

def vb_get_citation(root, fs, simplified=False, guess=False, vc_as=False):
    '''Return the canonical (prf, 3sm) form for the root and language.FeatStructs
    in language.FeatStruct set fss.

    If vc_as is True, preserve the voice and aspect of the original word.
    '''
    if root == 'al_e':
        return "'alo"
    # Return root if no citation is found
    result = root
    # Unfreeze the feature structure
    fs = fs.unfreeze()
    # Update the feature structure to incorporate default (with or without vc and as)
    fs.update(TI.morphology['v'].citationFS if vc_as else TI.morphology['v'].defaultFS)
    # Refreeze the feature structure
    fs.freeze()
    # Find the first citation form compatible with the updated feature structure
    citation = TI.morphology['v'].gen(root, fs, from_dict=False,
                                       simplified=simplified, guess=guess)
    if citation:
        result = citation[0][0]
    elif not vc_as:
        # Verb may not occur in simplex form; try passive
        fs = fs.unfreeze()
        fs.update({'vc': 'ps'})
        fs.freeze()
        citation = TI.morphology['v'].gen(root, fs, from_dict=False,
                                           simplified=simplified, guess=guess)
        if citation:
            result = citation[0][0]
    return result

def simplify(word):
    """Simplify Tigrinya orthography."""
    word = word.replace("`", "'").replace('H', 'h').replace('^', '').replace('_', '')
    return word

def orthographize(word):
    '''Convert phonological romanization to orthographic.'''
    word = word.replace('_', '').replace('I', '')
    return word

def cop_anal2string(anal):
    '''Convert a copula analysis to a string.

    anal is ("cop", "Iyyu", "Iyyu", gramFS)
    '''
    s = 'POS: copula'
    if anal[1]:
        s += ', root: <' + anal[1] + '>'
    s += '\n'
    fs = anal[3]
    if fs:
        sb = fs['sb']
        s += ' subject:'
        s += arg2string(sb)
        anygram = False
        if fs.get('neg'):
            s += ' grammar: negative'
            anygram = True
        if fs.get('yn'):
            if anygram:
                s += ','
            else:
                s += ' grammar:'
            s += ' yes/no'
            anygram = True
        if anygram:
            s += '\n'
        cj = fs.get('cj2')
        if cj:
            s += ' conjunctive suffix: ' + cj + '\n'
    return s

def vb_anal2string(anal):
    '''Convert a verb analysis to a string.

    anal is ("(*)v", root, citation, gramFS)
    '''
    pos = 'verb'
    root = anal[1]
    citation = anal[2]
    fs = anal[3]
    POS = '?POS: ' if '?' in anal[0] else 'POS: '
    s = POS + pos
    if root:
        s += ', root: <' + root + '>'
    if citation:
        s += ', citation: ' + citation
    s += '\n'
    if fs:
        sb = fs['sb']
        s += ' subject:'
        s += arg2string(sb)
        ob = fs.get('ob')
        if ob and ob.get('xpl'):
            s += ' object:'
            s += arg2string(ob, True)
        s += ' grammar:'
        tm = fs.get('tm')
        if tm == 'prf':
            s += ' perfective'
        elif tm == 'imf':
            s += ' imperfective'
        elif tm == 'j_i':
            s += ' jussive/imperative'
        elif tm == 'ger':
            s += ' gerundive'
        else:
            s += ' present'
        asp = fs.get('as')
        if asp == 'it':
            s += ', iterative'
        elif asp == 'rc':
            s += ', reciprocal'
        vc = fs.get('vc')
        if vc == 'ps':
            s += ', passive'
        elif vc == 'tr':
            s += ', transitive'
        if fs.get('yn'):
            s += ', yes/no'
        if fs.get('rel') or fs.get('neg'):
            if fs.get('rel'):
                s += ', relative'
            if fs.get('neg'):
                s += ', negative'
        s += '\n'
        cj1 = fs.get('cj1')
        cj2 = fs.get('cj2')
        prep = fs.get('pp')
        if cj1 or cj2 or prep:
            any_affix = False
            if prep:
                any_affix = True
                s += ' preposition: ' + prep
            if cj1:
                if any_affix: s += ','
                s += ' conjunctive prefix: ' + cj1
            if cj2:
                if any_affix: s += ','
                s += ' conjunctive suffix: ' + cj2
            s += '\n'
    return s

def arg2string(fs, obj=False):
    '''Convert an argument Feature Structure to a string.'''
    s = ''
    if fs.get('p1'):
        s += ' 1'
    elif fs.get('p2'):
        s += ' 2'
    else:
        s += ' 3'
    if fs.get('plr'):
        s += ', plur'
    else:
        s += ', sing'
    if not fs.get('p1'):
        if fs.get('fem'):
            s += ', fem'
        else:
            s += ', masc'
    if obj:
        if fs.get('prp'):
            s += ', prep'
    s += '\n'
    return s

def ti_preproc(form):
    form = form.replace("'", " !")
    return eth2sera(ETH_SERA['ti'][0], form, lang='ti'),

def agr_to_list(agr, cat):
    '''Category, then person, then number, then gender, then prepositional.'''
    gram = [cat]

    if agr.get('p1'):
        gram.append('1')
    elif agr.get('p2'):
        gram.append('2')
    else:
        gram.append('3')

    if agr.get('plr'):
        gram.append('plural')
    else:
        gram.append('singular')

    if not agr.get('p1'):
        # Gender only for 2nd and 3rd person
        if agr.get('fem'):
            gram.append('feminine')
        else:
            gram.append('masculine')
    else:
        gram.append('')

    if agr.get('prp'):
        gram.append('yes')
    elif cat == 'object':
        gram.append('no')

    return gram

def vb_anal_to_dict(root, fs):
    args = []
    # List of features that are true
    bools = []
    strings = {}

    gram = {}

    gram['root'] = root

    sbj = fs['sb']
    obj = fs.get('ob', None)
    vc = fs['vc']
    asp = fs['as']
    tm = fs['tm']
    cj1 = fs.get('cj1', None)
    cj2 = fs.get('cj2', None)
    prp = fs.get('pp', None)

    # Arguments
    # The first item in args is a list of category labels
    labels = ['person', 'number', 'gender']
    if obj.get('xpl'):
        labels.append('prepositional')
    args.append(labels)
    # The second item in args is a list of argument category lists
    args1 = []
    args1.append(agr_to_list(sbj, 'subject'))
    if obj.get('xpl'):
        args1.append(agr_to_list(obj, 'object'))
    args.append(args1)

    # TAM
    if tm == 'imf':
        strings['tense/mood'] = 'imperfective'
    elif tm == 'prf':
        strings['tense/mood'] = 'perfective'
    elif tm == 'ger':
        strings['tense/mood'] = 'gerundive'
    else:
        strings['tense/mood'] = 'jussive/imperative'

    # DERIVATIONAL STUFF
    if vc == 'ps':
        strings['voice'] = 'passive'
    elif vc == 'tr':
        strings['voice'] = 'transitive'

    if asp == 'it':
        strings['aspect'] = 'iterative'
    elif asp == 'rc':
        strings['aspect'] = 'reciprocal'

    # NEGATION
    if fs.get('neg'):
        bools.append('negative')
    # RELATIVIZATION
    if fs.get('rel'):
        bools.append('relative')
    # CONJUNCTIONS AND PREPOSITIONS
    if cj1 and cj1 != 'nil':
        strings['prefix conjunction'] = cj1
    if cj2 and cj2 != 'nil':
        strings['suffix conjunction'] = cj2
    if prp and prp != 'nil':
        strings['preposition'] = prp

    gram['args'] = args
    gram['strings'] = strings
    gram['bools'] = bools

    return gram

def list_to_arg(dct, prefix):
    '''Person, number, gender, (formality), (prepositional).'''
    arg = language.FeatStruct()
    person = dct.get(prefix + '_pers')
    number = dct.get(prefix + '_num')
    gender = dct.get(prefix + '_gen')
    arg['xpl'] = True

    # Person
    if person == '1':
        arg['p1'] = True
        arg['p2'] = False
    elif person == '2':
        arg['p2'] = True
        arg['p1'] = False
    else:
        # 3rd person the default
        arg['p1'] = False
        arg['p2'] = False
    # Number
    if number == 'plur':
        arg['plr'] = True
    else:
        # Singular the default
        arg['plr'] = False
    # Gender
    if person != '1':
        if gender == 'fem':
            arg['fem'] = True
        else:
            arg['fem'] = False

    # Prepositional (object only)
    if prefix == 'obj':
        if dct.get(prefix + '_prep_ti'):
            arg['prp'] = True
        else:
            arg['prp'] = False

    return arg

def vb_dict_to_anal(root, dct, freeze=True):
    fs = language.FeatStruct()
    root = root or dct['root']

    # Arguments
    sbj = list_to_arg(dct, 'sbj')
    if dct.get('obj'):
        obj = list_to_arg(dct, 'obj')
    else:
        obj = language.FeatStruct()
        obj['xpl'] = False
    fs['sb'] = sbj
    fs['ob'] = obj
    
    # TAM: labels are the same as FS values
    fs['tm'] = dct.get('tam', 'prf')

    # DERIVATIONAL STUFF
    fs['as'] = dct.get('asp', 'smp')
    fs['vc'] = dct.get('voice_ti', 'smp')

    # OTHER GRAMMAR
    fs['neg'] = dct.get('neg', False)
    fs['rel'] = dct.get('rel', False)

    # PREPOSITIONS and CONJUNCTIONS
    fs['pp'] = dct.get('prep_ti', 'nil')
    if fs['pp'] != 'nil':
        fs['sub'] = True

    fs['cj1'] = dct.get('preconj_ti', 'nil')
    if fs['cj1'] != 'nil':
        fs['sub'] = True

    fs['cj2'] = dct.get('sufconj_ti', 'nil')

    return [root, FSSet(fs)]

def list_to_arg_old(arg_list, obj=False):
    '''Person, number, gender, prepositional.'''
    arg = language.FeatStruct()
    person = arg_list[0]
    number = arg_list[1]
    gender = arg_list[2]

    # Person
    if person == '3':
        arg['p1'] = False
        arg['p2'] = False
    elif person == '2':
        arg['p2'] = True
        arg['p1'] = False
    else:
        arg['p1'] = True
        arg['p2'] = False
    # Number
    if number == 'plural':
        arg['plr'] = True
    else:
        arg['plr'] = False
    # Gender
    if gender == 'feminine':
        arg['fem'] = True
    elif gender == 'masculine':
        arg['fem'] = False
    # Object-specific stuff
    if obj:
        arg['xpl'] = True
        prep = arg_list[3]
        if prep == 'yes':
            arg['prp'] = True
        else:
            arg['prp'] = False

    return arg

def dict_to_anal_old(root, dct, freeze=True):
    fs = language.FeatStruct()
    root = root or dct['root']
    strings = dct.get('strings', {})
    bools = dct.get('bools', [])

    # Arguments
    # A list: args[0] a list of feature categories, args[1] a list of args,
    #  each a list of features
    args = dct.get('args', [['person', 'number', 'gender'], [['subject', '3', 'singular', 'masculine']]])
    arg_cats = args[0]
    for arg_list in args[1]:
        typ = arg_list[0]
        fs['sb' if (typ == 'subject') else 'ob'] = list_to_arg(arg_list[1:], typ == 'object')
    if len(args[1]) < 2:
        # No explicit object
        fs['ob'] = language.FeatStruct()
        fs['ob']['xpl'] = False

    # TAM
    tm = strings.get('tense/mood')
    if tm == 'jussive/imperative':
        fs['tm'] = 'j_i'
    elif tm == 'imperfective':
        fs['tm'] = 'imf'
    elif tm == 'gerundive':
        fs['tm'] = 'ger'
    else:
        fs['tm'] = 'prf'

    # DERIVATIONAL STUFF
    vc = strings.get('voice')
    if vc == 'passive':
        fs['vc'] = 'ps'
    elif vc == 'transitive':
        fs['vc'] = 'tr'
    else:
        fs['vc'] = 'smp'

    asp = strings.get('aspect')

    if asp == 'iterative':
        fs['as'] = 'it'
    elif asp == 'reciprocal':
        fs['as'] = 'rc'
    else:
        fs['as'] = 'smp'

    # NEGATION
    if 'negative' in bools:
        fs['neg'] = True
    else:
        fs['neg'] = False
    # RELATIVIZATION
    if 'relative' in bools:
        fs['rel'] = True
        fs['sub'] = True
    else:
        fs['rel'] = False
        # Could be overridding by cj1
        fs['sub'] = False

    # CONJUNCTIONS AND PREPOSITIONS
    cj1 = strings.get('prefix conjunction')
    cj2 = strings.get('suffix conjunction')
    prp = strings.get('preposition')

    fs['cj1'] = cj1 if cj1 else 'nil'
    fs['cj2'] = cj2 if cj2 else 'nil'
    fs['pp'] = prp if prp else 'nil'
    if cj1:
        fs['sub'] = True

    return [root, FSSet(fs)]

## Create Language object for Tigrinya, including preprocessing, postprocessing,
## and segmentation units (phones).
TI = language.Language("Tigrinya", 'Ti',
                       postproc=lambda form: sera2geez(GEEZ_SERA['ti'][1], form, lang='ti'),
                       preproc=lambda form: geez2sera(GEEZ_SERA['ti'][0], form, lang='ti'),
                       seg_units=[["a", "e", "E", "i", "I", "o", "u", "@", "A", "w", "y", "'", "`", "|", "_"],
                                  {"b": ["b", "bW"], "c": ["c", "cW"], "C": ["C", "CW"],
                                   "d": ["d", "dW"], "f": ["f", "fW"], "g": ["g", "gW"],
                                   "h": ["h", "hW"], "H": ["H", "HW"], "j": ["j", "jW"], "k": ["k", "kW"], "K": ["K", "KW"],
                                   "l": ["l", "lW"], "m": ["m", "mW"], "n": ["n", "nW"],
                                   "p": ["p", "pW"], "P": ["P", "PW"],
                                   "N": ["N", "NW"], "q": ["q", "qW"], "Q": ["Q", "QW"], "r": ["r", "rW"],
                                   "s": ["s", "sW"], "S": ["S", "SW"], "t": ["t", "tW"],
                                   "T": ["T", "TW"], "v": ["v", "vW"], "x": ["x", "xW"],
                                   "z": ["z", "zW"], "Z": ["Z", "ZW"]}])

## Create Morphology object and noun, verb, and copula POSMorphology objects for Tigrinya,
## including punctuation and ASCII characters that are part of the romanization.
TI.set_morphology(language.Morphology((),
                                      pos_morphs=[('cop', [], [], []), ('v', [], [], [])],
                                      # Exclude ^ and - (because it can be used in compounds)
                                      punctuation=r'[“‘”’–—:;/,<>?.!%$()[\]{}|#@&*\_+=\"፡።፣፤፥፦፧፨]',
                                      # Include digits?
                                      characters=r'[a-zA-Zሀ-ፚ\'`^]'))

### Assign various attributes to Morphology and POSMorphology objects

# Functions that simplifies Tigrinya orthography
TI.morphology.simplify = lambda word: simplify(word)
TI.morphology.orthographize = lambda word: orthographize(word)

# Function that performs trivial analysis on forms that don't require romanization
TI.morphology.triv_anal = lambda form: no_convert(form)

## Functions converting between feature structures and simple dicts
TI.morphology['v'].anal_to_dict = lambda root, anal: vb_anal_to_dict(root, anal)
TI.morphology['v'].dict_to_anal = lambda root, anal: vb_dict_to_anal(root, anal)

## Default feature structures for POSMorphology objects
## Used in generation and production of citation form
TI.morphology['v'].defaultFS = \
    language.FeatStruct("[pos=v,tm=prf,as=smp,vc=smp,sb=[-p1,-p2,-plr,-fem],ob=[-xpl,-p1,-p2,-plr,-fem,-prp],cj1=None,cj2=None,pp=None,-neg,-yn,-rel,-sub]")
TI.morphology['v'].FS_implic = {'rel': ['sub'], 'cj1': ['sub'], 'pp': ['rel', 'sub'], 'ob': [['xpl']]}
# defaultFS with voice and aspect unspecified
TI.morphology['v'].citationFS = \
    language.FeatStruct("[pos=v,tm=prf,sb=[-p1,-p2,-plr,-fem],ob=[-xpl],cj1=None,cj2=None,pp=None,-neg,-yn,-rel,-sub]")
TI.morphology['cop'].defaultFS = \
    language.FeatStruct("[cj2=None,-neg,ob=[-xpl],-rel,sb=[-fem,-p1,-p2,-plr,-frm],-sub,-yn,tm=prs]")

## Functions that return the citation forms for words
TI.morphology['v'].citation = lambda root, fss, simplified, guess, vc_as: vb_get_citation(root, fss, simplified, guess, vc_as)

## Functions that convert analyses to strings
TI.morphology['v'].anal2string = lambda fss: vb_anal2string(fss)
TI.morphology['cop'].anal2string = lambda fss: cop_anal2string(fss)

## "Interesting" features
# Stem
TI.morphology['v'].sig_features = ['as', 'vc']
# Valency
# TI.morphology['v'].sig_features2 = ['sb', 'ob']
# Defective roots
TI.morphology['v'].defective = ['al_o']

VOWEL_RULES = [
    # A: transitive, negative
    "'amS'o", "yemS'o", "'ayfeleTen", "zeyfeleTe", "keyfeleTe", "'ayedeqesen", "'ayemS'on",
    "zemS'o", "zEfeleTe", "kEfeleTe",
    # stem-internal changes
    "sete", "seteye", "seteKa", "fetewe", "fetoKa", "'fetu", "'deli", "'fetweki", "'delyeki",
    "gWeyeye", "ygWeyi", "tegWayeye",
    "'axeTet", "yexiTu", "'axiTom", "'axiT"
    ]
