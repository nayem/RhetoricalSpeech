# A Guide to the LingData Data Structure
## **From the view of a linguist to assist non-linguists...**
### By Jay Kaiser (and naturally all credit goes to Damir for its content)

This is meant to be a guide to LingData.py found in the Code folder of our BitBucket. Not only does this describe the code and the methods in a more easily accessible manner, but it also explains some linguistic concepts that might be unknown to a majority of the class. Hopefully it will provide some value in translating the outputs from NLTK, CoreNLP, SpaCy, and OpenNLP to LingData objects. (I do not claim this is complete, and a lot of this information came directly from the code. Again, it will hopefully assist those groups who will be translating content into the LingData class to be parsed later on by the graph database groups.)

The LingData data structure subdivides into four levels of description: Document, Clause, Sentence, and Token.

## Document

A *Document* is just that, and can be seen as a collection of sentences to be further parsed. A *Document* constructor consists of the following variables:

- sentences (list): the raw list of sentences
- sIDs (dictionary): each sentence's unique ID is the key and its count in the document is the value
- index (integer): "helping variable for iterations" ???
- dep2id (dictionary): dependencies as strings are the keys, and IDs as integers are the values
- id2dep (dictionary): dependency IDs as integers are the keys and their string representations are the values
- corefs (dictionary): key is tuples in the form of (token_from, token_to) and value is tuples as (sentence_ID, from, to); this returns all coreference relationships between entities in the document
- refs (dictionary) key is a tuple of indices over tokens and the value is a reference; this returns ???

There are also a vast array of functions available for objects of the *Document* class, each of which has been outlined below:

- addSentence(sentenceObject): adds a new sentence to this document's index
- getSentenceByID(sentenceID): returns the text sentence for a given ID
- addReference(anaphora, antecedent): adds a coreference between the two given variables that is stored internally and can be recalled again later
- getTokens(s, f, to): returns the tokens in sentence **s** from the span of tokens from **f** to **to**, as lemmas (strings)
- getString4TokID(s, tokID): returns the string for a given token ID **tokID** as its lemma form
- getTokenType(s, tokID): returns whether a token ID **tokID** is a noun or a verb (or unknown)
- getConcepts(): returns context tuples from the text of the document (this is high level stuff like subjects, relations, etc)
- getDepID(label): returns the unique ID for a given dependency label
- getDepLabel(idn): returns the label for a given unique dependency ID


## Clause

A *Clause* is any complete sentence or subsentence. Clauses that can stand alone as a complete sentence are **independent clauses**, and sentences that cannot are **dependent clauses**. In the sentence below:

"If I had a million dollars, I would leave here and I would just move to Australia, assuming the spiders don't get me first."

there are four clauses:

- If I had a million dollars...
- I would leave here...
- ... and I would just move to Australia...
- ... assuming the spiders don't get me first.

In English, each clause must have both a subject and a verb.

Each *Clause* object has the following constructor variables:

- transitive (integer): see *Enumerators*
- fromToken (integer): index of the first clausal token of the full sentence
- toToken (integer): index of the last clausal token of the full sentence, exclusive
- root (integer): index of the "root" of the clause (the main verb)
- clause (boolean): **True** if this clause is the main clause of the complete sentence
- negated (boolean): **True** if the clause contains a negation
- aspect (integer): see *Enumerators*
- tense (integer): see *Enumerators*
- voice (integer): see *Enumerators*
- mood (integer): see *Enumerators*

There are also a number of unimplemented classes that will need to be added in detail to ensure full linguistic information is found. Most of these will be very easy to add given the above information exists.

- getSubject(): returns the subject terminal/token of the clause (in minimal detail)
- getSubjectPhrase(): returns the full subject phrase of the clause
- getObject(): returns the object terminal/token of the clause (in minimal detail)
- getObjectPhrase(): returns the full object phrase of the clause
- isNegated(): returns **self.negated**
- isFinite(): returns **True** if **self.tense** != 4 (infinitive)
- isMatrixClause(): returns **self.clause**
- getRoot(): returns the root terminal/token of the clause
- isTransitive(): returns **True** if **self.transitive** == 2
- isDitransitive(): returns **True** if **self.transitive** == 3
- isPassive(): returns **True** if **self.voice** == 2
- isPastTense(): returns **True** if **self.tense** == 2
- isPresentTense(): returns **True** if **self.tense** == 1
- set(): sets values as necessary into the Clause

e.g.) Let's apply these values to "If I had a million dollars..."
- transitive: 2 (there is both a subject and an object, so it is transitive)
- fromToken: 0
- toToken: 5
- root: 2 ("had" is the main verb of the sentence)
- clause: **False** (this cannot stand alone as a sentence so it is not the main clause)
- negated: **False** (there is no negation here)
- aspect: 1 (simple aspect)
- tense: 1 (present tense)
- voice: 1 (active voice)
- mood: 1 (conditional mood)

## Sentence

A sentence is any combination of clauses together in one complete sentence. A sentence consisting of a single clause is a **simple sentence**. One consisting of more than one dependent clauses is a **compound sentence**. One consisting of at least one dependent clause and one independent clause is a **complex sentence**. One consisting of at least two independent clauses and one dependent clause is a **compound-complex sentence**.

Each *Sentence* object has the following constructor values. Any values below in **italics** are currently unimplemented:

- tokens (list of dictionaries): the meta-linguistic information for each token in the sentence
- clauses (list): a list of Clause objects
- *mood (integer): see *Enumerators* *
- id (string): a unique ID value for representing this sentence
- text (string): the raw text of the sentence
- clauseEmbeddings (dictionary): ???
- *interrogative (boolean): **True** if the sentence is a question*
- token_dict (list of dictionaries): the Token object information for each token in the sentence
- *dependencies (list of dictionaries): the dependencies of the sentence, as found by a dependency parse*
- constituents (list of dictionaries): the "phrases" in the sentence that can stand alone (e.g. "the green cat" but not "the green", and "kick the ball" but not "kick the")
- depRelDict (dictionary): holds all dependency labels from a dependency parse of the sentence, with key as the dependency's ID and the value as a list of tuples of the form (governor, dependent)
- governor_k (dictionary): same structure as above, but ???
- dependent_k (dictionary): same structure as above, but ???
- govRelation (dictionary): same structure as above, but ???
- antecedent (dictionary): stores antecedent/dependent pairs, with indexes of each as the key and value
- mw (dictionary): stores multi-word tokens (soy sauce, New York) with key as token ID and value as the span of words in the multi-word token

There are also a number of classes that uses the above information:

- isComplex(): returns **True** if len(**self.clauses**) > 1
- getDependencyRoot(): returns governor_k[0][0] (the root token ID for the sentence's dependency parse)
- getTokens(fromt, to): returns the tokens in a given span of the sentence (from **fromt** to **to**) as their unique IDs
- getLemmas(fromt, to): returns the lemmata (as strings or unique IDs?) for a given span of tokens in the sentence
- hasScopeOver(x, y): returns **True** if **x** has scope over **y** in the phrase structure (unimplemented); based on two tokens in a syntactic parse tree for the sentence, this will determine whether one token is higher up than the other

## Token

A *Token* is any word-like element found in a sentence. These do not have to be single words (they can be phrases, punctuation marks, etc.), but each can be represented as a series of features from which greater linguistic analysis can be found. Below are listed the constructor variables for a *Token* object. Again, unimplemented variables are found in **italics**:

- id (integer): the unique ID of the given token (to be found in some master dictionary)
- word (string): the raw string of the token
- lemma (string): the lemma of the token (a lemma is an uninflected word; the lemma of "dogs" is "dog" and the lemma of "caught" is "catch")
- POS (string): the part-of-speech tag of the token (e.g. proper noun, adjective, past-tense verb, preposition, etc.)
- SPOS (string): the simplified part-of-speech tag of the token (e.g. proper noun == noun, past-tense verb == verb, etc.)
- wordType (integer): see *Enumerators*
- NE (string?): if the token is a named entity (location, organization, time, person), which one is it
- foreign (boolean): is the token from a foreign language than that of the main text?
- isReferent (boolean): is the token a referent for an anaphor? (e.g. "He gave **himself** a prize.")
- hasAntecedent (boolean): is the token the anaphora itself? (e.g. "**He** gave himself a prize.")
- *RefText (???): *
- *RefS (???): *
- *RefFrom (???): *
- *RefTo (???): *
- *RefHead (???): *

The only currently defined method for a *Token* is **set()**, which takes in a list of optional arguments and sets these variables with them for the given *Token* object.

In this manner, a *Document* object can be described as a list of *Sentence* objects, each of which consists of a list of *Clause* objects, each of which is a list of *Token* objects.


## Enumerators

There a number of enumerators for various features describing clauses, sentences, and tokens. They have been explicitly described below, in full linguistic detail as well.

**tokenfeatures**
- 1 - *id*
- 2 - *word*
- 3 - *lemma*
- 4 - *POS*
- 5 - *SPOS*
- 6 - *NER*
- 7 - *foreign*
- 8 - *isReferent*
- 9 - *hasAntecedent*
- 10 - *RefText*
- 11 - *RefS*
- 12 - *RefFrom*
- 13 - *RefTo*
- 14 - *RefHead*

**wtypes**
- 1 - *verb*	
- 2 - *noun*	
- 3 - *pronoun*	
- 4 - *copula*: the verb "to be" in a connecting sense (e.g. "He **is** a man.")
- 5 - *unknown*	

**mood** (you will definitely not use a majority of these)
- 1 - *conditional*: expresses probability, possibility, wonder, or conjecture (e.g. "He **could** go tomorrow.")
- 2 - *deontic*: expresses permission or obligation with regard to some system of rules (e.g. "The murderer **must** be stopped.")
- 3 - *epistemic*: expresses possibility and necessity with regard to knowledge (e.g. "The butler **must** be the murderer!")
- 4 - *hypothetical*: expresses a situation that has not actually happened (e.g. "If I **won"" the lottery, ...")
- 5 - *indicative*: expresses normal facts (most used of all of them for our purposes)
- 6 - *inferential*: expresses a nonwitnessed event without confirmation (very rare in languages)
- 7 - *interrogative*: expresses a question (e.g. "Is he having any fun?")
- 8 - *imperative*: expresses a command (e.g. "Do it right now!")
- 9 - *irrealis*: expresses that a situation is not known to have happened yet (conflates with several other moods)
- 10 - *jussive*: expresses an order or a command (encompasses a greater number of examples than just **imperative**)
- 11 - *optative*: expresses a wish or a hope ("If only I were a real boy...")
- 12 - *potential*; expresses that an action is likely to occur
- 13 - *subjunctive*: expresses a condition that is doubtful or unfactual (e.g. If he would have just arrived earlier, then I **could have** gone home.")

**tense**
- 1 - *present*
- 2 - *past*
- 3 - *future*
- 4 - *infinitive*: an uninflected form of the verb (e.g. "He likes to **run** in the summer.")

**aspect**
- 1 - *simple*
- 2 - *progressive*: a verb that is currently being undergone; represented by <BE VERB+ing> in English
- 3 - *imperfect*
- 4 - *perfect*: a verb that has been completed; represented by <HAVE VERB+ed> in English
- 5 - *perfectprogressive*: a verb that is currently being completed; represented by <HAVE been VERB+ing> in English

**voice**
- 1 - *active*: an agent acts upon a patient; in most cases, a subject does something to a verb (The man broke the window.)
- 2 - *passive*: a patient is acted upon with or without an agent (The window was broken by the man.)
- 3 - *middle*: neither active nor passive, as the subject contains elements of each (The window broke.)
- 4 - *other*

**clause**
- 1 - *matrix*: the main clause of the sentence (can stand alone if all other clauses were removed)
- 2 - *complement*: a clause introduced by words like "that" or "whether" (e.g. "The news **that she had won the lottery** surprised me.")
- 3 - *adjunct*: an optional clause that can be fully removed from the sentence without a loss of grammaticality

**transitive**
- 1 - *intransitive*: a verb that takes only one argument (e.g. "He **sleeps**.")
- 2 - *transitive*: a verb that takes exactly two arguments (e.g. "He **slapped** the fish.")
- 3 - *ditransitive*: a verb that takes exactly three arguments (e.g. "He **gave** Sally a book.")