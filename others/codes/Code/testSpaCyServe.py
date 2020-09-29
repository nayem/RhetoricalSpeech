#!/usr/bin/env python3

"""
Running a test server on port 8999

"""

sport = 8999
sstyle = 'ent' # 'dep' or 'ent'

import spacy
from spacy import displacy


nlp = spacy.load('en')
doc1 = nlp(u'John Smith works for IBM.')
doc2 = nlp(u'This is another sentence.')

displacy.serve([doc1, doc2], style=sstyle, port=sport)

