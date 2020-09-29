#!/usr/bin/env bash
#
# Runs Stanford CoreNLP.
# Simple uses for xml and plain text output to files are:
#    ./corenlp.sh -file filename
#    ./corenlp.sh -file filename -outputFormat text 
# Split into sentences, run POS tagger and NER, write CoNLL-style TSV file:
#    ./corenlp.sh -annotators tokenize,ssplit,pos,lemma,ner -outputFormat conll -file input.txt
# You can also start a simple shell where you can enter sentences to be processed:
#    ./corenlp.sh
#
# Note: (Damir Cavar)
# I increased the memory for this server instance to 10GB so that the Wikipedia instance linking could
# work. It might still run out of memory. You can change the value in the -mx10g parameter to some higher
# value, if you have the RAM in your machine.

PORT=9000

OS=`uname`
# Some machines (older OS X, BSD, Windows environments) don't support readlink -e
if hash readlink 2>/dev/null; then
  scriptdir=`dirname $0`
else
  scriptpath=$(readlink -e "$0") || scriptpath=$0
  scriptdir=$(dirname "$scriptpath")
fi

echo Running server on port $PORT
# Run the server using all jars in the current directory (e.g., the CoreNLP home directory)
java -mx5g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port $PORT -timeout 15000
