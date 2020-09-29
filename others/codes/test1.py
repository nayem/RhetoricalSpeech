from nltk.corpus import brown
import nltk

ifile = open("text_file.txt",mode="r",encoding='utf-8')
text = ifile.read()
ifile.close()
print(text)

tokens = nltk.word_tokenize(text)

myFD=nltk.FreqDist(text)

for x in myFD:
    print(x,myFD)

FreqDist = nltk.ngrams(tokens,2)
myBigramsFP = nltk.FreqDistrams(FreqDist)

for x in myBigramsFP:
    print(x,myBigramsFP[x])

tokens, tags = zip(*brown.tagged_words())
print(tokens,tags)

for i in range(0,10):
    print(tokens[i],tags[i])