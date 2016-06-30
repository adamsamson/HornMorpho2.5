# HornMorpho 2.5 

HORNMORPHO is a Python program that analyzes Amharic, Oromo, and Tigrinya words into their constituent morphemes (meaningful parts) and generates words, given a root or stem and a representation of the word’s grammatical structure. It is part of the L3 project at Indiana University <http://www.cs.indiana.edu/~gasser/Research/projects.html>, which is dedicated to developing computational tools for under-resourced languages.

Natural language applications, such as question-answering, speech recognition, information retrieval, and machine translation, rely on a lexicon of possible forms in the relevant language. Morphological analysis is important for morphologically complex languages like Amharic, Oromo, and Tigrinya because it is practically impossible to store all possible words in a lexicon, and many words have close to 0 probability of occurrence in any given corpus. This becomes obvious in the context of machine translation to a morphologically simple language such as English, where the correspondence between words in Amharic, Oromo, or Tigrinya and the other language will often be many-to-one. The Amharic word ባይከፈትላቸውም, for example (which incidentally does occur in an online corpus), could be translated as ‘even if it isn’t opened for them’. While a system for processing English could include all of the English words in the translation (even, if, it, isn’t, opened, for, them) in its lexicon, an Amharic system that includes all words such as ባይከፈትላቸውም is clearly impractical. For translation into Amharic, Oromo, or Tigrinya and sophisticated question-answering, morphological generation is also desirable because it is probably impossible to store all of the words that the system will output. Finally, for Semitic languages such as Amharic and Tigrinya, morphological analysis can make explicit some of the phonological features of the languages that are not reflected in the orthography; these features may be important for text-to-speech applications. For example, the Tigrinya word ዚፍለጥ ‘which (it) is known’ is correctly pronounced with gemination (lengthening) of the third consonant: zifIlleT. The gemination in this case is grammatical, and a morphological analyzer can infer it based on its knowledge of Tigrinya verb roots and the particular templates that they occur with (see Section 5 for more on this aspect of Amharic and Tigrinya grammar).

# Installation

To install HORNMORPHO, you will need to open a shell (often called “command prompt window” in Windows). In the shell, go to the HornMorpho2.5 directory (folder), and enter the following if you are on a Unix or Unix-like system, making sure that you are running Python 3.0 or 3.1.
     python setup.py install
If you are using Windows, it will probably suffice to enter:
     setup.py install
To test whether the installation succeeded, start up the Python interpreter, again making sure that you are running at least Python 3.0 (see Section 8.a in the horn2.5.pdf file if you don’t know how to do this), and type
import l3
If you don’t want to install the program, you can still use it. Just move the whole directory to a con- venient place in your file system, and then make sure you run the Python interpreter from the HornMorpho-2.5 directory, wherever that is.  

# Functions

Options for each function are shown with their default values.

```
anal(language, word)
 Options: roman=False, root=True, gram=True, citation=True, raw=False, nbest=100 [Amharic only]
 Performs morphological analysis of the word. For ambiguous words returns the first nbest
 analyses. For Amharic only, analyses are ordered by their estimated frequency.
```

```
>>> l3.anal('ti', 'ናብ')
 word: ናብ
>>> l3.anal('ti', 'ፔፕሲ')
 ?word: ፔፕሲ
>>> l3.anal('am', 'የማያስፈልጋትስ')
 word: የማያስፈልጋትስ
```

