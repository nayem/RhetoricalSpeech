# !/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
*LingData.py*

(C) 2017 by Damir Cavar <damir@cavar.me>, Atreyee M., Jay Kaiser <jayckaiser.github.io>, Mac Vogelsang

Provides classes for linguistic data coming from parsers

**Date Created on:**
Tue Jun 20 16:30:00 2016

**Copyright:**
Copyright 2016-2017 by Damir Cavar, Jay Kaiser

**Note:**
This needs some more specification specification and optimization.


**Bug:** None (we never code bugs!)

"""

__license__ = """Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""
__revision__ = " $Id: LingData.py 2 2017-07-25 14:32:00Z damir $ "
__docformat__ = 'reStructuredText'
__author__ = 'Damir Cavar <damir@cavar.me>, Jay Kaiser, Mac Vogelsang'
__version__ = '0.2'


from enum import Enum
from datetime import datetime
import time


wtypes = Enum('wtypes', 'verb noun pronoun copula unknown')

mood = Enum('mood',
            'conditional deontic epistemic hypothetical indicative inferential interrogative imperative irrealis jussive optative potential subjunctive')

tense = Enum('tense', 'present past future infinitive')

aspect = Enum('aspect', 'simple progressive imperfect perfect perfectprogressive')

voice = Enum('voice', 'active passive middle other')

clause = Enum('clause', 'matrix complement adjunct')


tokenfeatures = Enum('tokenfeatures',
                     'id word lemma POS SPOS NER foreign isNegated isReferent hasAntecedent RefText RefS RefFrom RefTo RefHead')



def main():
    tok = Token()
    tok.set(POS="ads", word="test")


class LingData():
    """The Ling data class"""


    def __init__(self):
        self.NLPID = None  #: one of the NLP pipelines

        self.parseTime = time.time()  #: timestamp of parse run

        # ADD TOKENS TO LINGDATA FIRST, THEN USE THIS LIST TO ADD TOKENS TO SENTENCES AND CLAUSES
        self.tokenList = []  #: the list of all tokens for the entire document

        self.documentCreationTime = time.time()  #: timestamp of document creation

        self.sentences = []  #: list of sentence objects
        self.index = 0  #: helping variable for iterations

        # these are populated when tokens with dependencies are added by the translators
        self.dep2id = {}  #: dictionary with dependencies as strings (keys) and int IDs as values
        self.id2dep = {}  #: dictionary with int IDs as keys and dependencies as strings

        # coreference relations
        # key tuple(token_from, token_to); value is tuple(sentence_ID, from, to)
        self.corefs = {}  #: coreference relations coded in keys and values, keys are tuple(token_from, token_to), value is tuple(sentence_ID, from, to)
        # list of references for a token sequence
        self.refs = {}  #: key is a tuple of indices over tokens, the value is a reference

    def setNLPID(self, nlpid):
        """Setter for the NLP ID"""
        self.NLPID = nlpid

    def getNLPID(self):
        return self.NLPID

    def setParseTime(self, timestamp):
        self.parseTime = timestamp

    def getParseTime(self):
        return self.parseTime

    def setDocumentCreationTime(self, timestamp):
        self.documentCreationTime = timestamp

    def getDocumentCreationTime(self):
        return self.documentCreationTime

    def addToken(self, tokenObject):
        # tokens should be appended in order for now so that they'll have the same index as their id
        # later we could make a mapping dict of token id's from the parser to their position in this list
        self.tokenList.append(tokenObject)

    def getTokens(self, tokenIDs=None):
        """
        Returns the tokens for a tokenList or for the whole doc if sentence isn't specified

        """
        if tokenIDs is not None:
            return [token for ID, token in enumerate(self.tokenList) if ID in tokenIDs]

        else:
            return self.tokenList

    def addSentence(self, sentenceObject):
        """Adds a sentence object to the list of sentences"""

        # add a pointer to the doc's tokenlist
        # sentenceObject.tokenList = self.tokenList
        # append the sentence
        self.sentences.append(sentenceObject)

    def getSentenceByID(self, sentenceID):
        """Returns the sentence for an ID. This is the enumeration in NLP comoponents - 1"""
        return self.sentences[sentenceID - 1]

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        if self.index >= len(self.sentences) - 1:
            raise StopIteration
        self.index = self.index + 1
        return self.sentences[self.index]

    def addReference(self, anaphora, antecedent):
        """Add coreferences.
           Note: the sentence IDs are 1 for the first sentence, etc.; the sentences are stored in a Python list
           with indexes starting at 0. See the comment in getStentenceByID how the real sentence ID is reduced by
           1 to access the sentence from the storage list.
        """
        anaphora = tuple(anaphora)
        antecedent = tuple(antecedent)
        #print("Anaphora:", anaphora)
        #print("Antecedent:", antecedent)
        #print("Sentences:", self.sentences)
        self.refs[antecedent] = self.refs.get(antecedent, []) + [anaphora]

        # store the antecedent for the anaphora
        self.corefs[anaphora] = antecedent

        # store facts in tokens
        anaphoraSentence = self.getSentenceByID(anaphora[0])

        # this generates Tim Cook from he or from CEO
        mw = (anaphora[2] - anaphora[1]) > 1
        for i in range(anaphora[1], anaphora[2]):
            anaphoraSentence.antecedent[i] = antecedent
            if mw:
                anaphoraSentence.mw[i] = anaphora
        antecedentSentence = self.getSentenceByID(antecedent[0])

        # store the antecedent as refering to itself (this generates Tim Cook from Cook)
        for i in range(antecedent[1], antecedent[2]):
            antecedentSentence.antecedent[i] = antecedent

    def getString4TokID(self, tokID):
        """Return the correct string for a token ID"""
        return self.tokenList[tokID].word  #: word refers to token text

    def getTokenType(self, tokID):
        """Return the type of the token."""
        return self.tokenList[tokID].getTokenType()

    # TODO vvvvv BELOW FUNCTIONS ARE CORENLP SPECIFIC vvvvv
    # TODO No, they are not

    def getDepID(self, label):
        """return the ID for a dependency label"""

        if label in self.dep2id:
            return self.dep2id[label]
        newid = len(self.dep2id) + 1
        self.dep2id[label] = newid
        self.id2dep[newid] = label
        return newid

    def getDepLabel(self, idn):
        """return the label for a dependency ID"""

        if idn in self.id2dep:
            return self.id2dep[idn]
        return 0





class Token():
    """The Token class contains all lexical properties and syntactic relations of a token."""

    def __init__(self, id=None, word=None, lemma=None, POS=None, SPOS=None, 
        wordType=None, NE=None, foreign=None, maxProject = None):
        self.id = id  #: ID is the running index in the list
        self.word = word  #: string of token
        self.lemma = lemma  #: string of lemma
        self.POS = POS  #: string Part-of-Speech tag
        self.SPOS = SPOS  #: string simplified Part-of-Speech tag
        self.wordType = wordType  #: enum word type

        # dependency parse
        self.depID = None  #: id of dependency
        self.depStr = None  #: string of dependency

        # constituency parse
        self.parent = None
        self.children = None
        self.c_commandees = None # a set of ids of all c_commandees of the Token
        self.c_commanders = None # a set of ids of all c_commandees of the Token
        self.maxProject = None # a string: maxProject of Tim will be Tim Cook 

        # optional labels
        self.NE = NE  #: Named Entity property
        self.foreign = foreign  #: boolean is token a foreign word or not
        self.isReferent = None  #: boolean is token a referent for some anaphora
        self.isNegated = None  #: boolean is the head of a phrase negated for neation scope
        self.hasAntecedent = None  #: ist token an anaphora itself
        self.vector = None  #:   1-dimensional numpy array of 32-bit floats from word2vec

        self.features = {}  #: features dictionary that defines word specific features such as tense, voice, negations

        # wordnet
        self.synonyms = []
        self.hypernyms = []
        self.hyponyms = []
        self.wn_lemmas = []


    def getTokenType(self):
        """Return the type of the token."""
        if self.POS[0] == 'N':
            return wtypes.noun
        elif self.POS[0] == 'V':
            return wtypes.verb
        return wtypes.unknown

    def set(self, **args):
        # set the token parameters from NLP processor output
        for x in args:
            if x == "id":
                self.id = args[x]
            elif x == "word":
                self.word = args[x]
            elif x == "lemma":
                self.lemma = args[x]
            elif x == "POS":
                self.POS = args[x]
            elif x == "SPOS":
                self.SPOS = args[x]
            elif x == "depID":
                self.depID = args[x]
            elif x == "depStr":
                self.depStr = args[x]
            elif x == "parent":
                self.parent = args[x]
            elif x == "children":
                self.children = args[x]
            elif x == "c_commands":
                self.c_commands = args[x]
            elif x == "wordType":
                self.wordType = args[x]
            elif x == "NE":
                self.NE = args[x]
            elif x == "foreign":
                self.foreign = args[x]
            elif x == "isReferent":
                self.isReferent = args[x]
            elif x == "isNegated":
                self.isNegated = args[x]
            elif x == "hasAntecendent":
                self.hasAntecedent = args[x]
            elif x == "features":
                self.features = args[x]
            elif x == "hypernyms":
                self.hypernyms = args[x]
            elif x == "hyponyms":
                self.hyponyms = args[x]
            elif x == "synonyms":
                self.synonyms = args[x]
            elif x == "wn_lemmas":
                self.wn_lemmas = args[x]
            else:
                raise NameError


class Clause():
    """
    Clause class
    """

    def __init__(self):
        self.transitive = False  #: is token transitive 2, intransitive 1, ditransitive 3

        # from and to should be changed to list of indices of tokens
        # e.g.: 'What did John say that Mary read?'
        # self.fromToken = -1 #: index of first clausal token
        # self.toToken   = -1 #: index of last clausal token, exclusive

        self.mainVerb = None
        self.root = None

        self.tokenList = []  #: list of tokens that belong to this particular clause
        self.parentSentence = None  #: sentence object this clause belongs to. Set when clause is added to a sentence
        self.clauseID = None  #: should be set when clause is added to a sentence in translator scripts
        self.matrixclause = True  #: boolean is clause matrix clause
        self.negated = False  #: boolean clause negated
        self.aspect = None  #: int aspect
        self.tense = None  #: int tense
        self.voice = None  #: int voice
        self.mood = None  #: int mood

        self.subject = []
        self.subjectPhrase = None
        self.object = []
        self.objectPhrase = None

    def __str__(self):
        outstr = "["
        outstr = " ".join(list(self.getTokens()))
        outstr = outstr + "]"
        return outstr

    def addTokens(self, tokenIndexes, tokenList):
        """
        Adds tokens ID to clause.tokenList. The tokenIndexes are relative to the sentence tokenList.
        """
        for i in tokenIndexes:
            self.tokenList.append(tokenList[i])

    def getTokens(self):
        return self.tokenList

    def getParentSentence(self):
        return self.parentSentence

    def getSubject(self):
        """Returns the subject terminal/token."""
        return self.subject

    def getSubjectPhrase(self):
        """Returns the subject phrase."""
        return self.subjectPhrase

    def getObject(self):
        return self.object

    def getObjectPhrase(self):
        return self.objectPhrase

    def isNegated(self):
        return self.negated

    def isFinite(self):
        return (self.tense != 4)

    def setMatrixClause(self, bool):
        self.matrixclause = bool

    def isMatrixClause(self):
        return self.matrixclause

    def getPredicate(self):
        """Return the predicate head Verb, Noun, Adjective..."""
        # TODO explanartion....
        return None

    def getMainVerb(self):
        """If there is a main verb, return it, else return None"""
        return self.mainVerb

    def getMainFeatures(self):
        # TODO no idea, Mac needs to do this...
        return self.mainVerb # ].features

    def isTransitive(self):
        return (self.transitive == 2)

    def isDitransitive(self):
        return (self.transitive == 3)

    def isPassive(self):
        return (self.voice == 2)

    def isPastTense(self):
        return (self.tense == 2)

    def isPresentTense(self):
        return (self.tense == 1)

    def set(self, **args):
        for x in args:
            if x == "transitive":
                self.transitive = args[x]
            elif x == "fromToken":
                self.fromToken = args[x]
            elif x == "toToken":
                self.toToken = args[x]
            elif x == "root":
                self.root = args[x]
            elif x == "clause":
                self.clause = args[x]
            elif x == "negated":
                self.negated = args[x]
            elif x == "aspect":
                self.aspect = args[x]
            elif x == "tense":
                self.tense = args[x]
            elif x == "voice":
                self.voice = args[x]
            elif x == "mood":
                self.mood = args[x]
            elif x == "subject":
                self.subject = args[x]
            elif x == "subjectPhrase":
                self.subjectPhrase = args[x]
            elif x == "object":
                self.object = args[x]
            elif x == "objectPhrase":
                self.objectPhrase = args[x]
            else:
                raise NameError

        print(args)


class Sentence():
    """
    This is the main class that holds sentence data.
    """

    def __init__(self):

        self.tokenList = []
        self.clauses = []
        self.interrogative = False

        # List of dictionaries
        self.token_dict = {}
        # self.dependencies = {}
        self.constituents = []

        # table to hold mapping of internal to our dep labels, int to int
        # key = depID, val is list of tuples (governor, dependent)
        self.depRelDict = {}
        # key = tokenID of governor, val = list of tuples of tokenID of dependent and dependencyID
        self.governor_k = {}
        # key = tokenID of depdendent, val = list of tuples of tokenID of governor and dependencyID
        self.dependent_k = {}
        # key = tuple of tokenID of governor and dependencyID, val = list of dependenceIDs

        self.govRelation = {}

        # Antecedent lookup table, key index of token, val
        self.antecedent = {}  #:
        # store multi word expressions, key = tokenID, val = span of mw
        self.mw = {}

    def __str__(self):
        return " ".join(self.getTokens()) # This does not work?!

    def addTokens(self, fromTok, toTok, tokenList):
        self.tokenList += tokenList[fromTok:toTok]

    def getTokens(self):
        return self.tokenList

    def addClause(self, clause):
        # append clause
        self.clauses.append(clause)
        # set clauseID to its index in the clause list
        clause.clauseID = len(self.clauses) - 1

    def getClauses(self):
        return self.clauses

    def isComplex(self):
        if len(self.clauses) > 1:
            return True
        return False

    def getDependencyRoot(self):
        """Returns the root token ID for the dependency parse."""
        return self.governor_k[0][0]

    def getLemmas(self):
        """Get a span of lemmata from the sentence."""

    def hasScopeOver(self, x, y):
        """Returns True, if X has scope over Y in the phrase structure."""
        pass

    def isInterrogative(self):
        # find matrix clause and get if matrix clause is interrogative
        pass



if __name__ == "__main__":
    main()
