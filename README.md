# HornMorpho 2.5

[![Help Contribute to Open Source](https://www.codetriage.com/adamsamson/hornmorpho2.5/badges/users.svg)](https://www.codetriage.com/adamsamson/hornmorpho2.5)

HORNMORPHO is a Python program that analyzes Amharic, Oromo, and Tigrinya words into their constituent morphemes (meaningful parts) and generates words, given a root or stem and a representation of the word’s grammatical structure. It is part of the L3 project at Indiana University <http://www.cs.indiana.edu/~gasser/Research/projects.html>, which is dedicated to developing computational tools for under-resourced languages.

Natural language applications, such as question-answering, speech recognition, information retrieval, and machine translation, rely on a lexicon of possible forms in the relevant language. Morphological analysis is important for morphologically complex languages like Amharic, Oromo, and Tigrinya because it is practically impossible to store all possible words in a lexicon, and many words have close to 0 probability of occurrence in any given corpus. This becomes obvious in the context of machine translation to a morphologically simple language such as English, where the correspondence between words in Amharic, Oromo, or Tigrinya and the other language will often be many-to-one. The Amharic word ባይከፈትላቸውም, for example (which incidentally does occur in an online corpus), could be translated as ‘even if it isn’t opened for them’. While a system for processing English could include all of the English words in the translation (even, if, it, isn’t, opened, for, them) in its lexicon, an Amharic system that includes all words such as ባይከፈትላቸውም is clearly impractical. For translation into Amharic, Oromo, or Tigrinya and sophisticated question-answering, morphological generation is also desirable because it is probably impossible to store all of the words that the system will output. Finally, for Semitic languages such as Amharic and Tigrinya, morphological analysis can make explicit some of the phonological features of the languages that are not reflected in the orthography; these features may be important for text-to-speech applications. For example, the Tigrinya word ዚፍለጥ ‘which (it) is known’ is correctly pronounced with gemination (lengthening) of the third consonant: zifIlleT. The gemination in this case is grammatical, and a morphological analyzer can infer it based on its knowledge of Tigrinya verb roots and the particular templates that they occur with (see Section 5 for more on this aspect of Amharic and Tigrinya grammar).

# Installation

To install HORNMORPHO, you will need to open a shell (often called “command prompt window” in Windows). In the shell, go to the HornMorpho2.5 directory (folder), and enter the following if you are on a Unix or Unix-like system, making sure that you are running Python 3.0 or 3.1.
```
     python setup.py install
```
If you are using Windows, it will probably suffice to enter:
```
     setup.py install
```
To test whether the installation succeeded, start up the Python interpreter, again making sure that you are running at least Python 3.0 (see Section 8.a in the horn2.5.pdf file if you don’t know how to do this), and type
```
import l3
```
If you don’t want to install the program, you can still use it. Just move the whole directory to a con- venient place in your file system, and then make sure you run the Python interpreter from the HornMorpho-2.5 directory, wherever that is.

# Functions

Options for each function are shown with their default values.

```
anal(language, word)
 Options: roman=False, root=True, gram=True, citation=True, raw=False, nbest=100 [Amharic only]
 Performs morphological analysis of the word. For ambiguous words returns the first nbest
 analyses. For Amharic only, analyses are ordered by their estimated frequency.

>>> l3.anal('ti', 'ናብ')
 word: ናብ

>>> l3.anal('ti', 'ፔፕሲ')
 ?word: ፔፕሲ

>>> l3.anal('am', 'የማያስፈልጋትስ')
 word: የማያስፈልጋትስ
 POS: verb, root: <fl_g>, citation: አስፈለገ
  subject: 3, sing, masc
  object: 3, sing, fem
  grammar: imperfective, causative, relative, definite, negative
  conjunctive suffix: s

 >>> l3.anal('om', 'afeeramaniiru')
 word: afeeramaniiru
 POS: verb, root: <afeer>, citation: afeeramuu
  subject: 3, plur
  derivation: passive
  TAM: perfect

 >>> l3.anal('ti', 'ብዘጋጥመና')
 word: ብዘጋጥመና
 POS: verb, root: <gTm>, citation: ኣጋጠመ
  subject: 3, sing, masc
  object: 1, plur
  grammar: imperfective, reciprocal, transitive, relative
  preposition: bI

 >>> l3.anal('am', 'አይደለችም')
 word: አይደለችም
 POS: copula, root: <ne>
  subj: 3, sing, fem
  negative

 >>> l3.anal('ti', 'ዘየብለይ')
 word: ዘየብለይ
 POS: verb, root: <al_e>, citation: ኣሎ
  subject: 3, sing, masc
  object: 1, sing
  grammar: present, relative, negative

 >>> l3.anal('om', 'dubbanne')
 word: dubbanne
 POS: verb, root: <dubbadh>, citation: dubbachuu
  TAM: past, negative
 POS: verb, root: <dubbadh>, citation: dubbachuu
  subject: 1, plur
  TAM: past

 >>> l3.anal('am', 'lezemedocacnm', roman=True)
 word: lezemedocacnm
 POS: noun, stem: zemed
  possessor: 1, plur
  grammar: plural
  preposition: le, conjunctive suffix: m

 >>> l3.anal('am', 'ቢያስጨንቁአቸው', root=False, gram=False)
 word: ቢያስጨንቁአቸው
 POS: verb, citation: አስጨነቀ

 >>> l3.anal('am', 'ለዘመዶቻችንም', raw=True)
 [('zemed', [-acc, cnj='m', der=[-ass], -dis, +plr, pos='n',
 poss=[+expl, +p1, -p2, +plr], pp='le', rl=[-acc, +p], v=None])]

 >>> l3.anal('am', 'ይመጣሉ')
 word: ይመጣሉ
 POS: verb, root: <mT'>, citation: መጣ
  subject: 3, plur
  grammar: imperfective, aux:alle
 POS: verb, root: <mTT>, citation: መጠጠ
  subject: 3, plur
  grammar: imperfective, aux:alle
 POS: verb, root: <mT'>, citation: ተመጣ
  subject: 3, plur
  grammar: imperfective, aux:alle, passive

 >>> l3.anal('am', 'ይመጣሉ', nbest=1)
 word: ይመጣሉ
 POS: verb, root: <mT'>, citation: መጣ
  subject: 3, plur
  grammar: imperfective, aux:alle
```

```
 anal_file(language, input_file, output_file)
 Options: root=True, gram=True, citation=True, raw=False
 Runs anal on the words in a file.

 >>> l3.anal_file('am', 'l3/languages/am/data/ag.txt',
  'l3/languages/am/data/ag_out.txt')
 Analyzing words in l3/languages/am/data/ag.txt
 Writing to l3/languages/am/data/ag_out.txt
 ```


 ```
 seg(language, word) [Amharic and Oromo verbs and Oromo nouns only]
 Options: roman=False, gram=True, raw=False
 Performs morphological segmentation on the word. Morphemes are separated by ‘-’; stems/roots
 appear within ‘{}’.

 >>> l3.seg('am', 'ሲያጭበረብሩን')
 ሲያጭበረብሩን:
 s(cnj1)-y(sb=3sm|3p)-{Cbrbr+a12e3e4_5}(imprf,trans)-u(sb=2p|3p)-n(ob=1p)

 >>> l3.seg('om', 'afeeramaniiru', gram=True)
 word: afeeramaniiru
 POS: verb, segmentation: {afeer-am}-an-r-u
  subject: 3, plur
  derivation: passive
  TAM: perfect
 seg_file(language, input_file, output_file)
 Options: gram=True, raw=False
 Runs seg on the words in a file

 >>> l3.seg_file('am', 'l3/languages/am/data/ag.txt',
  'l3/languages/am/data/ag_out.txt')
 Segmenting words in l3/languages/am/data/ag.txt
 Writing to l3/languages/am/data/ag_out.txt
 ```

 ```
 phon(language, word) [Amharic only]
 Options: gram=True
 Converts an Amharic word written in Ge’ez characters to a romanized form that shows consonant
 gemination and the epenthetic vowel (represented by ‘I’). If multiple pronunciations are
 possible, they are ordered by estimated frequency.

 >>> l3.phon('am', "ይመታሉ")
 yImetal_u (132) yIm_et_al_u (61)

 >>> l3.phon('am', "ይመታሉ", gram=True)
 -- yImetal_u
 POS: verb, root: <mt'>
  subject: 3, plur
  grammar: imperfective, aux:alle
 -- yIm_et_al_u
 POS: verb, root: <mt'>
  subject: 3, plur
  grammar: imperfective, aux:alle, passive

 >>> l3.phon('am', 'እንድብር')
 ?IndIbIr (0)
 ```

 ```
 phon_file(language, input_file, output_file) [Amharic only]
 Options: gram=True, print_ortho=False, word_sep='\n', anal_sep=' '
 Runs phon on the words in a file.

 >>> l3.phon_file('am', 'l3/languages/am/data/ag.txt',
  'l3/languages/am/data/ag_phon.txt')
 Analyzing words in l3/languages/am/data/ag.txt
 Writing analysis to l3/languages/am/data/ag_phon.txt

 >>> l3.phon_file('am', 'l3/languages/am/data/ag.txt',
  print_ortho=False, word_sep=':')
 Analyzing words in l3/languages/am/data/ag.txt
 yIh:meShaf:yezarE:01:amet:gedema:bedenbu:mIrmera:alfo:tat_Imo:beweT_a:g
 izE:tal_aq_ tal_aq:cIg_Ir:feTrob_IN_:neb_er:.
 ```

 ```
 gen(language, root/stem, [grammatical_features])
 Options: roman=False, guess=False [Amharic, Tigrinya only]
 Generates the surface form of a word given a root or stem and optional grammatical features.
 With no features specified, a default form is output.

 >>> l3.gen('am', "mWl'")
 ሞላ

 >>> l3.gen('am', "mWl'", roman=True)
 mola

 >>> l3.gen('om', 'sirb')
 sirbe

 >>> l3.gen('ti', "gWyy")
 ጎየየ

 >>> l3.gen('am', "mWl'", '[sb=[+p2,+fem],ob=[+plr,+l]]')
 ሞላሽላቸው

 >>> l3.gen('am', "mengst", '[+plr,+def]')
 መንግስታቱ

 >>> l3.gen('am', 'sdb', '[pos=n,v=agt,vc=cs,as=rc]')
 አሳዳቢ

 >>> l3.gen('am', 'brkt', '[pos=n,v=ins,pp=ke,cnj=m,+def]')
 ከመበርከቻውም

 >>> l3.gen('am', 'ne', '[+neg, sb=[+p1,+plr]]')
 አይደለንም

 >>> l3.gen('am', 'kongo', '[pp=be]')
 This word can't be generated!

 >>> l3.gen('am', 'kongo', '[pp=be]', guess=True)
 በኮንጎ

 >>> l3.gen('am', 'wddr', '[+gen, poss=[+p1,+plr]]')
 This word can't be generated!

 >>> l3.gen('am', 'wdd_r', '[+gen, poss=[+p1,+plr]]')
 የውድድራችን

 >>> l3.gen('om', 'sirb', '[sb=[+fem],tm=prf]')
 sirbiteerti

 >>> l3.gen('om', 'barbaad', '[+inf,cnj=f]')
 barbaaduuf

 >>> l3.gen('om', 'sob', '[der=[+autoben],sb=[+p2],+neg,tm=prs]')
 sobattu

 >>> l3.gen('ti', 'HSb', '[sb=[+p2,+fem],ob=[+plr]]')
 ሐጸብክዮም

 >>> l3.gen('ti', 'n|qTqT', '[vc=ps,tm=imf,sb=[+p1,+plr]]')
 ንንቅጥቀጥ

 >>> l3.gen('ti','gdf','[tm=j_i,+neg,sb=[+p2],ob=[+plr],vc=ps,as=rc]')
 ኣይትጋደፎም
```
