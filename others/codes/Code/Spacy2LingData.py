#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
Spacy2LingData.py

(C) 2017 by Jay Kaiser <jayckaiser.github.io
Updated Oct 15 by Jay Kaiser

In LingData use SentenceData to store properties of sentences and all tokens

The output of the Spacy pipeline is a sequence of sentences, plus correference of elements across sentences.

This code represents a means to translate the output of SpaCy to LingData

\copyright Copyright 2017 by Jay Kaiser

\license{Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.}
"""


import sys, spacy, glob
from spacy.symbols import *  # get the enumerated symbols
# removed feature detection for now
# from tagtrans import translate #: get the tag parsing method using foma
from LingData import LingData, Token, Sentence, Clause
import datetime



def translateToLingData(nlp, text):
    """
    Testing function
    """

    doc = nlp(text)

    # for debugging
    '''
    for word in doc:
        print(word.text + " : " + word.dep_, end="\t Subtree: ")
        for x in word.subtree:
            print(x.text, end="\t")
        print()
    print("--------------")
    '''

    ld = spacy2Document(doc)

    # test lingData
    print([(x.word, x.POS) for x in ld.tokenList])

    return ld

    # print(ld)
    ''' hide clause testing
    for sent in ld.sentences:
        for clause in sent.getClauses():
            print(clause)
    '''


def spacy2Document(spacy_output):
    """
    Converts a spaCy-parsed document into a LingData document

    :param spacy_output:
    :return LingData object:
    """

    d = LingData()
    d.setNLPID("spacy")

    # generate the flat list of tokens in the document
    for token in spacy_output:
        t = toLingDataToken(token)
        d.addToken(t)

    fromTok = 0
    for sentence in spacy_output.sents:
        s = Sentence()
        # set to token
        toTok = fromTok + (len(sentence) - 1)
        d.addSentence(s)
        s.addTokens(fromTok, toTok, d.tokenList)

        # resest from token
        fromTok = fromTok + len(sentence)

        ### POPULATE THE SENTENCE ###

        # spaCy does not have coreferencing...
        # spaCy does not have constituency parsing...

        '''
        Temporarily removed clause detection

        for token in sentence:
            # first populate sentence
            # ind root and create clauses from that root

            if token.dep_ == "ROOT":
                createClauses(token, s)
                break
        '''

    return d


def createClauses(root, sent):
    """
    Find the clauses recursively from the given root token object

    root: spacy token object to search from (the root of the clause in spacy is usually the verb)
    sent: a Lingdata sentence object which contains the list of clauses and clause embeddings
    return: void (modifies the inputs in place)
    """
    CLAUSE_SIGNALS = ["xcomp", "ccomp", "relcl"]

    clauseFound = False
    for token in root.subtree:
        if token.dep_ in CLAUSE_SIGNALS and token.i != root.i:
            clauseFound = True
            createClauses(token, sent)
            # break

    if not clauseFound:
        # if no clause is found, we are at the deepest subclause and the recursive structure terminates

        c = LD.LingData.Clause()
        # for now, only add to flat list of clauses
        sent.addClause(c)

        for token in root.subtree:
            if token.dep_ == "ROOT":
                # flag this as matrix clause
                c.setMatrixClause(True)

            c.addToken(token.i)
    else:
        # we are currently in a clause that has a subclause already
        c = LD.LingData.Clause()
        sent.addClause(c)

        for token in root.subtree:
            # make sure this token isn't already a part of the sentence (i.e. in another clause)
            if token.i not in sent.tokenIDs:
                if token.dep_ == "ROOT":
                    # flag this as matrix clause
                    c.setMatrixClause(True)

                c.addClauseToken(token.i)


def toLingDataToken(token):
    """
    Converts a token as parsed by SpaCy into a LingData Token

    :param token:
    :return LingData.Token:
    """

    t = Token()

    t.set(
        id=token.i,
        word=token.orth_,
        lemma=token.lemma_,
        POS=token.tag_,
        SPOS=token.pos_,
        depID=token.dep,
        depStr=token.dep_,
        NE=token.ent_type_,
        foreign=token.is_oov
    )

    # setting features
    '''
    t.features = {}
    #print(t.POS)
    featureStr = translate(t.POS)
    # save string form of feature translation
    t.features['str'] = featureStr

    featureArr = featureStr.split("+")
    #print(featureArr)
    # find the first feature
    i = 0
    while len(featureArr[i]) < 1:
        i += 1

    t.features['type'] = featureArr[i]
    if t.features['type'] in ["N"]:
        # look for number
        i += 1
        while i < len(featureArr):
            # this means it's probably a number declaration
            if len(featureArr[i]) < 4:
                t.features['number'] = featureArr[i]
                # and next feature could be type of noun
                if i + 1 < len(featureArr):
                    t.features['isProper'] = featureArr[i + 1]
                break
            i += 1

    if t.features['type'] in ["V"]:
        # look for person and number
        i += 1
        while i < len(featureArr):
            # this means it's probably a person declaration
            if len(featureArr[i]) < 4:
                t.features['person'] = featureArr[i]
                # and next feature could be number
                if i + 1 < len(featureArr):
                    t.features['number'] = featureArr[i + 1]
                break
            else:
                # probably a tense
                t.features['tense'] = featureArr[i]
                t.features['isParticiple'] = ("Part" in featureArr[i])

            i += 1
    #print(t.features)
    '''

    # setting wordType
    if token.tag_ == "BES":  # copula
        t.set(wordType=4)
    elif token.pos_ == "VERB":
        t.set(wordType=1)
    elif token.pos_ == "NOUN" or token.pos_ == "PROPN":
        t.set(wordType=2)
    elif token.pos_ == "PRON":
        t.set(wordType=3)
    else:
        t.set(wordType=5)

    # spaCy does not have coreferencing...

    return t


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = "I like green eggs and ham."
    translateToLingData(text)
