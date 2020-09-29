# RhetoricalSpeech

## Automatic Question Detection in Speech using Deep Neural Network

In this project, we describe our efforts towards the automatic detection of questions in speech. 
We analyze the utility of various features for this task, Spectrogram and Mel-frequency cepstral coefficients (MFCC).
We have used IEEE corpus and self-prepared corpus of human-voice recorded audio files and trained the data on Recurrent Neural Networks (RNNs) and Convolutional Recurrent Neural Networks (CRNNs) and
compared their performances.
Our system, provides state-of-the-art results on the clean corpus and in noisy environments as well.

Dialogue Act Recognition is a challenging problem in dialogue interpretation which aims to attach semantic labels to utterance and characterize the speaker’s intention.
The most frequent DA types are are statements and opinions, questions, back-channels.
Our project focuses on detecting questions in the speech. 
Automatic Speech recognition is the versatile field of Computational Linguistics that develops methodologies and technologies that enables the recognition and translation of spoken language into text by computers. 
The system analyses the person’s specific voice and and use it to detect the person’s speech with better accuracy. 
Questions in human dialogues is an important first step to automatically processing and understanding the natural speech. 
It can be viewed as a subtask of speech act or dialogue act tagging, which aims to label functions of utterances in conversations. 
The various types of questions are Yes-No, wh, Declarative, Rhetoric, echo, etc. 
It is useful for meeting indexing and summarization. 
Examples-

**Yes-No:** *Have you looked at that?*

**Wh:** *What was the nature of the email?*

**Declarative:** *You are editing your slide?*

**Echo:** *He has undergone a surgery?*

**Rhetorical:** *Do you know that person?*

The main motivation behind this project is to develop a model that will consider intonation, stress and other speech attributes to classify the group questions. 
The current speech recognizer examples such as Google Home mini and Alexa can understand speech and respond accordingly. 
But these techniques are not smart enough to detect echo questions, rhetorical questions, etc. 
For an instance, questions like - *"What is your name?"* is easily recognizable by the current systems. 
But if the question is of echo type - *"Your name is abc?"*, then in this case the current systems will classify it as a normal sentence. 
But our model will classify these types also as *"Questions"* only unlike the current systems.

Full dataset is available on request. [[LINK]](https://drive.google.com/drive/folders/12PGLvr0aFcX1ou5k1b__lReLumkbrICa?usp=sharing)

&nbsp;

#### Authors:

**KHANDOKAR MD. NAYEM**, Indiana University Bloomington, USA

**TASLIMA AKTER**, Indiana University Bloomington, USA

HASIKA MAHTTA, Indiana University Bloomington, USA
