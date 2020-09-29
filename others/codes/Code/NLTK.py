#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Concepts.py
(C) 2017 by Damir Cavar <damir@cavar.me>


"""


MODULENAME = "NLTK"
FILENAME = "NLTK.py"


__revision__ = "$Id: " + FILENAME + " 2 2017-09-26 17:00:00 damir$"
__docformat__ = "reStructuredText"
__author__ = "Damir Cavar <damir@cavar.me>"
__version__ = "0.1"


import sys, argparse, configparser, logging, xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from LingData import LingData, Sentence, Clause, Token
from SemDiscUtils import encodeReturn, decodeReturn
from defaults import NLPs, MODULES, CONFFILE
import datetime

from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import words, wordnet
from nltk import ne_chunk
import nltk.tree


port = 9010
host = "localhost"

MODULENAME = "NLTK"
FILENAME = "NLTK.py"


def parse(data):
    named_entities = []

    d = LingData()
    d.setNLPID("nltk")

    tokens = word_tokenize(data)

    pos = pos_tag(tokens)
    spos = pos_tag(tokens, tagset='universal')

    lemmatizer = WordNetLemmatizer()

    # creating list of tuples of tokens with their respective named entity labels
    chunks = ne_chunk(pos)
    for chunk in chunks:
        if hasattr(chunk, 'label') and chunk.label:
            if len(chunk) > 1:
                traverse(chunk, chunk.label(), named_entities)
            else:
                named_entities.append((chunk[0][0], chunk.label()))
        else:
            named_entities.append((chunk[0], ''))

    # create LingData Token
    for i in range(len(pos)):
        t = Token()

        lemma_ = lemmatizer.lemmatize(pos[i][0], getWordNetPos(pos[i][1]))

        # is this the right way to check if a word is foreign?
        if pos[i][0] in words.words() or pos[i][0].lower() in words.words():
            is_oov = False
        else:
            is_oov = True

        t.set(
            id=i,
            word=pos[i][0],
            lemma=lemma_,
            POS=pos[i][1],
            SPOS=spos[i][1],
            NE=named_entities[i][1],
            foreign=is_oov
        )

        # setting wordType
        if pos[i][1] == "BES":  # copula
            t.set(wordType=4)
        elif spos[i][1] == "VERB":
            t.set(wordType=1)
        elif spos[i][1] == "NOUN" or spos[i][1] == "PROPN":
            t.set(wordType=2)
        elif spos[i][1] == "PRON":
            t.set(wordType=3)
        else:
            t.set(wordType=5)

        # creating flat lists of all hypernyms and hyponyms for a token as some tokens have multiple hypernyms. Should
        # hypernyms of those hypernyms be added to this list? It would not be an ordered list , should another data structure
        # be used?
        synset_list = wordnet.synsets(pos[i][0], getWordNetPos(pos[i][1]))
        hypernyms = []
        hyponyms = []
        lemmas = []
        for ss in synset_list:
            hypernyms += ss.hypernyms()
            hyponyms += ss.hyponyms()
            lemmas += ss.lemmas()
        '''
        t.set(
            hypernyms=hypernyms,
            hyponyms=hyponyms,
            synonyms=synset_list,
            wn_lemmas=lemmas
        )
        '''
        # TODO
        # This does not get added to the LingData object!
        d.addToken(t)

    # extracting sentences from the text
    fromTok = 0
    for sentence in sent_tokenize(data):
        s = Sentence()
        token_list = word_tokenize(sentence)
        toTok = fromTok + (len(token_list) - 1)
        d.addSentence(s)
        s.addTokens(fromTok, toTok, d.tokenList)
        # reset from token
        fromTok = fromTok + len(token_list)

    return encodeReturn(d)


def traverse(tree, label, named_entities):
    """
    Traverses nltk tree object to generate flattened list of named entities

    :param tree:
    :param label:
    :param named_entities:
    """
    for subtree in tree:
        named_entities.append((subtree[0], label))
        if type(subtree) == nltk.tree.Tree:
            traverse(subtree)


def getWordNetPos(treebank_tag):
    """
    Maps Treebank tags to WordNet tags for lemmatization

    :param treebank_tag:
    :return wordnet_tag:
    """
    if treebank_tag.startswith('V'):
        return 'v'
    elif treebank_tag.startswith('J'):
        return 'a'
    elif treebank_tag.startswith('R'):
        return 'r'
    else:
        return 'n'


def test():
    global port, host
    try:
        s = xmlrpc.client.ServerProxy("http://{}:{}".format(host, port), allow_none=True)
        res = decodeReturn(s.parse("Twitter is based in San Francisco. DeepMind has an office in London. Tim Cook sold Apple Inc. He bought Google Inc."))
        # prints in client
        print("NLP ID:", res.NLPID)
        """
        print("Timestamp:", datetime.date.fromtimestamp(res.parseTime))
        print("-" * 30)
        print('id\t word\t lemma\t pos\t spos\t ne\t foreign')
        for s in res.tokenList:
            print(s.id, s.word, s.lemma, s.POS, s.SPOS, s.NE, s.foreign)
        """
    except xmlrpc.client.Fault as err:
        logging.error("Calling NLTK: http://{}:{} failed!".format(host, port))
        logging.error("Fault code: {}".format(err.faultCode))
        logging.error("Fault string: {}".format(err.faultString))


def mainServer(port, host):
    """Start the Dispatcher in Server mode."""

    # start the XML-RPC server
    server = SimpleXMLRPCServer((host, int(port)), allow_none=True)
    server.register_introspection_functions()
    server.register_function(parse)

    logging.info('Serving XML-RPC on {} port {}'.format(host, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Interrupt received, exiting.")
        sys.exit(0)


def parseConfiguration(conff=CONFFILE):
    """Parse the config.ini and set the parameters."""
    global NLPs

    # read configuration
    config = configparser.ConfigParser()
    config.read(conff)

    for l in (MODULENAME, ):
        inilabel = NLPs[l].inilabel
        if inilabel in config.sections():
            if "host" in config[inilabel]:
                NLPs[l].host = config[inilabel]["host"]
            if "port" in config[inilabel]:
                NLPs[l].port = config[inilabel]["port"]
            if "logfile" in config[inilabel]:
                NLPs[l].logfile = config[inilabel]["logfile"]


if __name__ == "__main__":
    # command line arguments overwrite config-file parameters
    parser = argparse.ArgumentParser(prog=MODULENAME, description='Command line arguments.', epilog='')
    parser.add_argument('-c', '--config', dest="conffile", default=CONFFILE, help="Alternative " + CONFFILE + " file name")
    parser.add_argument('-t', '--test', dest='test', action='store_true', help="Run in test mode")  # just a flag
    args = parser.parse_args()

    if args.conffile != CONFFILE:
        parseConfiguration(args.conffile)
    else:
        parseConfiguration()

    # start logging
    logging.basicConfig(filename=NLPs[MODULENAME].logfile, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    if args.test:
        test()
    else:
        mainServer(NLPs[MODULENAME].port, NLPs[MODULENAME].host)
