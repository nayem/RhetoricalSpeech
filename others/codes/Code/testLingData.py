#!/usr/bin/env python3


"""
Damir Cavar
Just testing lists and pointers to elements in lists.
"""

import pickle


class LingData():

    def __init__(self):
        self.tokenList = []
        self.sentenceList = []


class Token():

    def __init__(self):
        self.token = ""
        self.lemma = ""


class Sentence():

    def __init__(self):
        self.tokenList = []


def main():
    myLD = LingData()
    myToken = Token()
    myToken.token = "is"
    myToken.lemma = "be"
    myLD.tokenList.append(myToken)
    myToken = Token()
    myToken.token = "this"
    myToken.lemma = "this"
    myLD.tokenList.append(myToken)
    print([ x.token for x in myLD.tokenList ] )
    myS = Sentence()
    myS.tokenList = myLD.tokenList[0:2]
    print([x.token for x in myS.tokenList])
    myS.tokenList[0].token = "are"
    print([ x.token for x in myS.tokenList ])
    print([ x.token for x in myLD.tokenList ] )
    print("See: The list is handling pointers not values.")

    myLD.sentenceList.append(myS)
    encodedLD = pickle.dumps(myLD, 0).decode()
    newLD = pickle.loads(encodedLD.encode())
    newS = newLD.sentenceList[0]
    newS.tokenList[0].token = "is"
    print([ x.token for x in newS.tokenList ])
    print([ x.token for x in newLD.tokenList ] )
    print([ x.token for x in myS.tokenList ])
    print([ x.token for x in myLD.tokenList ] )


if __name__=="__main__":
    main()

