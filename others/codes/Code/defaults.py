#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
defaults.py

(C) 2017 by Damir Cavar <dcavar@me.com>

Stores default configuration parameters. To include these parameters in the server components, use:

from defaults import NLPs, MODULES, CONFFILE

"""


class ServerConfig:
    def __init__(self, port=9000, host="localhost", logfile="", annotators=tuple(), inilabel=""):
        self.host = host
        self.port = port
        self.logfile = logfile
        self.annotators = annotators
        self.inilabel = inilabel


NLPs = {"CoreNLP": ServerConfig(port=9007, logfile="CoreNLP.log", inilabel="corenlpxml",
                                annotators=(
                                'tokenize', 'cleanxml', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse',
                                'dcoref')),
        "spaCy": ServerConfig(port=9001, logfile="spaCy.log", inilabel="spacy"),
        "FLE": ServerConfig(port=9006, logfile="fle.log", inilabel="fle"),
        "morphotagger": ServerConfig(port=9002, logfile="morphtagger.log", inilabel="morphotagger"),
        "OpenNLP": ServerConfig(port=9004, logfile="opennlp.log", inilabel="opennlp"),
        "NLTK": ServerConfig(port=9010, logfile="NLTK.log", inilabel="nltk"),
        "ClauseDetector": ServerConfig(port=2013, logfile="ClauseDetector.log", inilabel="clausedetect")
        }

MODULES = {"GraphMapper": ServerConfig(port=9008, logfile="GraphMapper.log", inilabel="graphmapper"),
           "ConcExtract": ServerConfig(port=9009, logfile="ConcExtractor.log", inilabel="concExtract"),
           "Concepts": ServerConfig(port=9011, logfile="Concepts.log", inilabel="concepts"),
           "Neo4J": ServerConfig(port=7687, logfile="", inilabel="neo4j"),
           "StarDog": ServerConfig(port=8180, logfile="", inilabel="stardog"),
           "Dispatcher": ServerConfig(port=9007, logfile="Dispatcher.log", inilabel="dispatcher"),
           "QAMatchingServer": ServerConfig(port=9012, logfile="QAMatching.log", inilabel="qamatching")}

CONFFILE = "config.ini"

if __name__ == "__main__":
    print("Running in batch mode.")
