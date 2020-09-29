#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


"""
CoreNLPXMLParser.py

(C) 2017 by Damir Cavar <damir@cavar.me>

In LingData use SentenceData to store properties of sentences and all tokens

The output of the CoreNLP parser is a sequence of sentences, plus correference of elements across sentences

TODO:
Make sure that we generate the token list first and fill the token list in LingData, then process the sentence level token list.


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
__revision__ = " $Id: CoreNLPXMLParserOld.py 2 2017-07-25 14:32:00Z damir $ "
__docformat__ = 'reStructuredText'
__author__ = 'Damir Cavar <damir@cavar.me>, Atreyee M., Hai Hu, Nandini Goswami, Sarita Bhateja'
__version__ = '0.2'


import sys, os.path, re, datetime, configparser, argparse, logging, logging.handlers
import xml.etree.ElementTree as ET
from corenlp_pywrap import pywrap
from LingData import Sentence, Clause, LingData, Token, tokenfeatures
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from SemDiscUtils import encodeReturn, decodeReturn
from PSTreeMapper import getPCFGData, Tree, Node


# Defaults
annotators = ['tokenize', 'cleanxml', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'dcoref']
cport = "9000"
chost = "localhost"
language = "en"

# CoreNLPXMLParser Server parameters
port = 9007
host = "localhost"
logfile = "CoreNLP.log"
logger = None

# keep global the port to the CoreNLP server
cn = None
myLingData = None


conffile = "config.ini"


def test():
    """
    Test the functionalities.
    """
    #global chost, cport, host, port, annotators, language, cn

    # myParser = CoreNLPXMLParserOld()
    # print(annotators)
    #print("Establishing connection to CoreNLP server: host " + chost + " port " + str(cport))
    #if not cn:
    #    cn = connect('http://' + chost + ':' + str(cport))
    #logging.debug("Establishing connection to CoreNLP server: host " + chost + " port " + str(cport))
    x = """Tim Cook will sell Apple. He bought Bill Gates a Porsche. A Porsche is a car. Once, I drove backwards """
    # x = "Tim Cook is the CEO of Apple."
    print(x)
    res = decodeReturn(parse(x))
    print("NLP ID:", res.NLPID)
    print("Timestamp:", datetime.date.fromtimestamp(res.parseTime))
    print("-" * 30)
    for s in res.tokenList:
        print(s.word)
        # print(s.c_commandees)
        # print(s.maxProject)
        #with open("LINGDATA.pkl","wb") as templd:
    #    pickle.dump(result, templd)
    #
    #print(result)
    # print("Root:", myParser.myDoc.sentences[0].getDependencyRoot())

    # result = myParser.getConcepts()
    # for x in result:
    #    print(" ".join( x ) )
    # print(result)


def parseConfiguration(conff=conffile):
    """
    Parse the config.ini and set the parameters.
    """

    global chost, cport, host, port, annotators, logfile, language

    config = configparser.ConfigParser()
    config.read(conff)
    if "corenlp" in config.sections():
        if "host" in config["corenlp"]:
            chost = config["corenlp"]["host"]
        if "port" in config["corenlp"]:
            cport = config["corenlp"]["port"]  # this is a string!
        if "annotators" in config["corenlp"]:
            annotators = config["corenlp"]["annotators"].split()
        if "language" in config["corenlp"]:
            language = config["corenlp"]["language"]

    if "corenlpxml" in config.sections():
        if "host" in config["corenlpxml"]:
            host = config["corenlpxml"]["host"]
        if "port" in config["corenlpxml"]:
            port = int(config["corenlpxml"]["port"])  # this is a string!
        if "logfile" in config["corenlpxml"]:
            logfile = config["corenlpxml"]["logfile"]


def parse(text):
    """
    This is the main access function exposed to the world over XML-RPC.
    """
    global chost, cport, annotators, cn
    logging.debug("Received text to parse:\n{}".format(text))
    #if not cn:
    #    cn = connect('http://{}:{}'.format(chost, cport))
    if not cn:
        try:
            cn = connect('http://{}:{}'.format(chost, cport))
        except xmlrpc.client.Fault as err:
            logging.error("Calling: http://{}:{} failed!".format(chost, cport))
            logging.error("Fault code: {}".format(err.faultCode))
            logging.error("Fault string: {}".format(err.faultString))
            return None
    logging.info("Establishing connection to CoreNLP server: host {} port {}".format(chost, cport))
    res = getParseFromConnection(cn, text)
    logging.debug("Returned from CoreNLP server and processed result.")
    #
    # TODO remove this later
    # Printing out the token
    #logging.debug("Token list:")
    #for sent in res.sentences:
    #    for token in sent.tokenList:
    #        logging.debug("Token: " + token.word + " " + token.lemma)
    return encodeReturn(res)


def setAnnotators(a):
    """
    Sets the annotators for the Stanford CoreNLP parser.
    """
    global annotators
    logging.debug("Setting annotator list to: {}".format(repr(a)))
    annotators = a


def connect(cnlpurl):
    """
    Establish a remote connection to a CoreNLP server.
    :param url:
    :return:
    """
    global annotators, cn, chost, cport
    logging.info("Establishing connection to CoreNLP server: host {} port {}".format(chost, cport))
    return pywrap.CoreNLP(url=cnlpurl, annotator_list=list(annotators))


def getParse(root):
    """
    Get the parse information for some text. If there is a remote connection, use it, otherwise assume
    that text contains a file name to read and process.
    :param root:
    :return:
    """
    myLingData = LingData()
    myLingData.NLPID = "CoreNLP"
    data = None
    pat = re.compile('.*-([0-9]{1,3})$') # for c_commander
    for child in root.findall(".//document/*"):
        if child.tag == "sentences":
            # does sentence have a subject?
            varHasNSubj = True


            for sentence in child.findall("*"):
                mySent = Sentence()
                mySent.id = int(sentence.attrib['id'])
                # const parse

                numTokens = len(sentence.findall('.//tokens/*'))
                # --------------------------------
                # get the tree
                data = sentence.find('parse').text
                if data:
                    pcfgDict, numTokens = getPCFGData(data, verbose=False)
                    # print(len(pcfgDict.keys()))
                    tree = Tree()
                    tree.pcfgDict = pcfgDict
                    for n in pcfgDict.keys():  # e.g. n=year-29
                        node = Node()

                        node.ccommandees = pcfgDict[n]['ccommandees']
                        node.ccommanders = pcfgDict[n]['ccommanders']
                        node.children = pcfgDict[n]['allchildren']
                        node.sisters = pcfgDict[n]['sisters']
                        node.label = n

                        node.index = int(n.split('-')[-1])
                        if node.index <= numTokens:  # terminal, lexical category
                            node.word = ''.join(n.split('-')[0:-1])
                            tree.Terminals[node.index] = node
                        else:  # non terminal
                            node.tag = ''.join(n.split('-')[0:-1])

                        # append to tree
                        tree.Nodes[node.index] = node
                        tree.startEnumNodes = numTokens + 1
                # --------------------------------

                # parsing the sentence
                for i in sentence.findall('.//tokens/*'):
                    td = Token(id=i.get('id'),
                               word=i.find('word').text,
                               lemma=i.find('lemma').text,
                               POS=i.find('POS').text,
                               NE=i.find('NER').text)
                    # logging.debug("Token in: " + td.word + " " + td.lemma)

                    td.maxProject = tree.getMaximalProjection(tree.getNodeByIndex(td.id))
                    
                    # add c_commandee, c_commander
                    c_commandees_str_list = pcfgDict[td.word + '-' + str(td.id)]['ccommandees']
                    c_commanders_str_list = pcfgDict[td.word + '-' + str(td.id)]['ccommanders']
                    c_commandees_ids = set() # a set of Token ids
                    c_commanders_ids = set() # a set of Token ids

                    for commandee in c_commandees_str_list:
                        m = pat.match(commandee)
                        if m and (int(m.group(1)) <= numTokens) and (int(m.group(1) != td.id)):
                            c_commandees_ids.add(int(m.group(1)))
                    td.c_commandees = c_commandees_ids


                    for commander in c_commanders_str_list:
                        m = pat.match(commander)
                        if m and (int(m.group(1)) <= numTokens) and (int(m.group(1) != td.id)):
                            c_commanders_ids.add(int(m.group(1)))
                    td.c_commanders = c_commanders_ids

                    myLingData.addToken(td)
                    mySent.tokenList.append(td)


                for i in sentence.findall('.//dependencies[@type="basic-dependencies"]/*'):
                    # parent and its dependent
                    depID = myLingData.getDepID(i.attrib["type"])
                    governor = int(i.find('governor').attrib['idx'])
                    dependent = int(i.find('dependent').attrib['idx'])
                    val = mySent.governor_k.get(governor, [])
                    val.append((dependent, depID))
                    mySent.governor_k[governor] = val
                    val = mySent.dependent_k.get(dependent, [])
                    val.append((governor, depID))
                    mySent.dependent_k[dependent] = val
                    # append the tuple with governor dependent for the dependency as key
                    mySent.depRelDict[depID] = mySent.depRelDict.get(depID, []) + [(governor, dependent)]
                    mySent.govRelation[(governor, depID)] = mySent.govRelation.get((governor, depID), []) + [
                        dependent]
                # self.govOfDeprel(mySent,"dobj")
                # print("depRelDict",mySent.depRelDict)
                # call generateDeps
                #data = sentence.find('parse').text
                # data = getFlatTree(data)
                #data = re.sub('\s\s+', ' ', data) # get flat tree

                # TODO constituent parse tree conversion is broken
                #lexRules, gramRules = getPCFG( CFGTreeAssignIndex(data) )
                #pcfgDict = getDict(lexRules, gramRules)

                myLingData.addSentence(mySent)

        elif child.tag == "coreference":
            logging.debug("Processing coreferences...")
            for x in child.findall('*'):
                antecedent = None
                anaphora = []
                for z in x.findall('.mention'):
                    sentence = int(z.find('sentence').text)
                    start = int(z.find('start').text)
                    end = int(z.find('end').text)
                    head = int(z.find('head').text)
                    text = z.find('text').text
                    if 'representative' in z.attrib:
                        antecedent = (sentence, start, end, head, text)
                    else:
                        anaphora.append((sentence, start, end, head, text))
                # process reference and corefs
                for z in anaphora:
                    # store the anaphora for all antecedent
                    myLingData.addReference(z, antecedent)
    return myLingData



def translationRulesRel(mySent):
    """

    :param mySent:
    :return:
    """
    return


def hasDeprelType(mySent, deprel, myLingData):
    """
    checks if a sentence has a particular type of deprel using the depreldict [key = depID, val is list of tuples (governor, dependent)]
    :param mySent: sentence object
    :param deprel: dependency relation
    :return:
    """
    for i in mySent.depRelDict:
        if (myLingData.getDepLabel(i) == deprel):
            return True


def govOfDeprel(mySent, deprel, myLingData):
    """

    :param mySent:
    :param deprel:
    :param myLingData:
    :return:
    """
    # print(mySent.depRelDict)
    # for i in mySent.depRelDict:
    #    if (myLingData.getDepLabel(i) == deprel):
    #        return mySent.tokens[i[0][0]][labels.id]  # id of the parent
    return ""


def getParseFromConnection(cn, text):
    """
    Uses the CoreNLP TCP/IP connection to fetch the resulting XML file from the parser
    :param text:
    :return:
    """
    if cn:
        if text:
            # parse by talking to remote server
            logging.debug("Connection to Stanford CoreNLP server established.")
            return getParse(ET.fromstring( cn.basic(text, out_format='xml').text ))
        else:
            logging.info("No text to process.")
    else:
        logging.error("No connection to a Stanford CoreNLP server established.")
    return None


def getParseFromFile(filename):
    """
    Reads the XML output file from CoreNLP
    :param filename:
    :return:
    """
    if not os.path.exists(filename):
        logging.error("File {} does not exist.".format(filename))
        return None

    # process file content
    content = ""
    try:
        ifp = open(filename, mode='r', encoding='utf8')
        content = ifp.read()
        ifp.close()
    except IOError:
        logging.error("Cannot read from file: {}".format(filename))
        return None
    if content:
        root = ET.fromstring(cn.basic(content, out_format='xml').text)
        return getParse(root)
    logging.error("No content in file: {}".format(filename))
    return None


def setLogging(logfile):
    """Set a logger"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=10240, backupCount=5)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


if __name__ == "__main__":

    # command line arguments overwrite config.ini settings
    parser = argparse.ArgumentParser(prog="CoreNLP", description='Command line arguments.', epilog='')
    parser.add_argument('-c', '--config', dest="conffile", default=conffile, help="Alternative config.ini file name")
    parser.add_argument('-t', '--test', action='store_true', help="Run in test mode") # just a flag
    args = parser.parse_args()

    # parse the config first
    if args.conffile != conffile:
        parseConfiguration(args.conffile)
    else:
        parseConfiguration()

    # start logging
    print("Logfile:", logfile)
    logging.basicConfig(filename=logfile, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    if args.test:
        test()
    else:
        # establish a connection
        cn = connect('http://{}:{}'.format(chost, cport))
        server = SimpleXMLRPCServer((host, port), allow_none=True)
        server.register_introspection_functions()
        server.register_function(parse)
        server.register_function(setAnnotators)
        logging.info('Serving XML-RPC on {} port {}'.format(host, port))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("Interrupt received, exiting.")
            sys.exit(0)
