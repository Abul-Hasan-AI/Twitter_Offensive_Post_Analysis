# -*- coding: utf-8 -*-
"""NLP_Part_D

"""


!pip install demoji
!pip install emoji
!pip install "python-crfsuite"

"""**Note: For POS tagging to work the "crfpostagger" file present in the folder of part D needs to be uploaded to colab or other needs to beplaced in the path of execution along with other input data files bold text**"""

import keras
import numpy as np
from keras.layers import Lambda, GlobalAveragePooling1D, GlobalMaxPooling1D,Dense, Embedding, Dropout, LSTM,Conv1D
from keras import backend as K
from keras.models import Sequential
import nltk
from nltk.stem import WordNetLemmatizer
import pandas
lemmatizer = WordNetLemmatizer()
import emoji
import string as str
#demoji.download_codes()
np.random.seed(500)

"""# 1. Loading the Data"""

def remove_PunctuationAndNum(Word):
  import string as str

  # define punctuation
  punctuation = """@:#'’!'!"#$%&()”+,-./:;<=>?@[\\]“^_`{|}~\t\n'"""
  output_word = ''
  for char in Word:
    if char not in punctuation and not char.isnumeric():
      output_word = output_word + char
  return output_word

import keras
nltk.download('wordnet')
import numpy as np
from keras.layers import Lambda, GlobalAveragePooling1D, Dense, Embedding, Dropout, LSTM
from keras import backend as K
from keras.models import Sequential
import nltk
from nltk.stem import WordNetLemmatizer
import pandas
from nltk.tag import CRFTagger
from nltk import pos_tag
import pycrfsuite
from collections import defaultdict
from nltk.corpus import wordnet as wn

lemmatizer = WordNetLemmatizer()
import emoji
import string as str
#demoji.download_codes()
np.random.seed(500)



train_df = pandas.read_csv('olid-training-v1.0.tsv',delimiter='\t',encoding='utf-8')



X_train = train_df['tweet']
Y_train_a = train_df['subtask_a']



# t = keras.preprocessing.text.Tokenizer()
# t.fit_on_texts(X_train)
# l1 = t.word_index
# l2 = list(l1.keys())
# print(l1[l2[-1]])

tokenizer = nltk.tokenize.TreebankWordTokenizer()
TAGGER_PATH = "crfpostagger"
POS_tagger = CRFTagger()  # initialize tagger
POS_tagger.set_model_file(TAGGER_PATH)

#Dictionary for apostrophe characters
apost_Dict = {
	"m" :"am",
	"n't" : "not",
	"'s" : "is",
	"re" : "are",
	"ve" : "have",
	"ll" : "will",
	"d" : "did",
	"cause" : "because",
	"c'mon" : "come on",
  "nt" :"not",
  "s" : "is",
  "t" : "not"
	}


# dictionary defination for POS tag
tag_map = defaultdict(lambda : wn.NOUN)
tag_map['J'] = wn.ADJ
tag_map['V'] = wn.VERB
tag_map['R'] = wn.ADV

X_train_preprocessed = []

for sent in X_train:
  sent_processed = []
  sent = sent.lower()
  sent = emoji.demojize(sent)
  words = tokenizer.tokenize(sent)
  for word,tag in POS_tagger.tag(words): 
    if word in apost_Dict:
      word = apost_Dict[word]
    word = remove_PunctuationAndNum(word)
    word = word.lower()
    if word != "" and word not in ['user','url']:
      word = lemmatizer.lemmatize(word,tag_map[tag[0]])
      sent_processed.append(word)
      
      
  X_train_preprocessed.append(sent_processed)

t = keras.preprocessing.text.Tokenizer()
t.fit_on_texts(X_train_preprocessed)
word2idx = t.word_index
word2idx = {k:(v+2) for k,v in word2idx.items()}
word2idx["<PAD>"] = 0
word2idx["<START>"] = 1
word2idx["<UNK>"] = 2
print(word2idx)
print(X_train_preprocessed)

"""# 2. Readying Inputs"""

from keras.preprocessing.sequence import pad_sequences
MAXIMUM_LENGTH = 200
print(Y_train_a)
Label_ENC_dict={
    'OFF' : 1,
    'NOT' : 0
}

# Encoding
X_train_encoded = []
for sent in X_train_preprocessed:
  sentENC =[]
  for word in sent:
    sentENC.append(word2idx[word])
  X_train_encoded.append(sentENC)

Y_train_a_ENC = []

for value in Y_train_a:
  #print(value)
  Y_train_a_ENC.append(Label_ENC_dict[value])



X_train_preprocessed_final = pad_sequences(X_train_encoded, maxlen=MAXIMUM_LENGTH)

print(X_train_preprocessed_final)
print(Y_train_a_ENC)

"""# Model"""

VOCAB_SIZE = len(word2idx)

EMBED_SIZE = 100
model = Sequential()
model.add(Embedding(input_dim=VOCAB_SIZE,output_dim=EMBED_SIZE,input_length=MAXIMUM_LENGTH,name ='Embedding_layer' ))
model.add(Dropout(rate = 0.2, noise_shape=None, seed=None))
model.add(LSTM(units = 100,activation='tanh',name ='LSTM_layer'))
model.add(Dropout(rate = 0.2, noise_shape=None, seed=None))
model.add(Dense(units =1, activation='sigmoid',name ='Output_layer'))
model.summary()

model.compile(
              loss='binary_crossentropy',optimizer='adam',
              metrics=['accuracy'])

"""# Train Validation split"""

X_val = np.array(X_train_preprocessed_final[:3000])
partial_X_train = np.array(X_train_preprocessed_final[3000:])

y_val_a = np.array(Y_train_a_ENC[:3000])
partial_y_train_a = np.array(Y_train_a_ENC[3000:])

"""# Training"""

history = model.fit(partial_X_train,
                    partial_y_train_a,
                    epochs=3,
                    batch_size=100,
                    validation_data=(X_val, y_val_a),
                    verbose=1)

"""# Testing part A"""

X_test_df_a = pandas.read_csv('testset-levela.tsv',delimiter='\t',encoding='utf-8',names=['ID','tweets'])
Y_test_df_a = pandas.read_csv('labels-levela.csv',delimiter=',',encoding='utf-8', names=['ID','labels'])

X_test_a = X_test_df_a['tweets']
Y_test_a = Y_test_df_a['labels']
X_test_a = X_test_a.drop(0)
print(X_test_a)
print(Y_test_a)
print(len(word2idx))

"""Preprocessing"""

X_test_preprocessed_a = []
for sent in X_test_a:
  sent_processed = []
  sent = sent.lower()
  sent = emoji.demojize(sent)
  words = tokenizer.tokenize(sent)
  #words = keras.preprocessing.text.text_to_word_sequence(sent, filters="""@:#'’!'!"#$%&()”+,-./:;<=>?@[\\]“^_`{|}~\t\n'""", lower=True, split=' ')
  for word,tag in POS_tagger.tag(words): 
    if word in apost_Dict:
      word = apost_Dict[word]
    word = remove_PunctuationAndNum(word)
    word = word.lower()
    if word != "" and word not in ['user','url']:
      word = lemmatizer.lemmatize(word,tag_map[tag[0]])
      sent_processed.append(word)
      
      
  X_test_preprocessed_a.append(sent_processed)

"""Padding and encoding test data"""

X_test_encoded_a = []
for sent in X_test_preprocessed_a:
  sentENC =[]
  for word in sent:
    if word not in word2idx:
      word = '<UNK>'
    sentENC.append(word2idx[word])
  X_test_encoded_a.append(sentENC)

Y_test_a_ENC = []

for value in Y_test_a:
  #print(value)
  Y_test_a_ENC.append(Label_ENC_dict[value])



X_test_preprocessed_final = pad_sequences(X_test_encoded_a, maxlen=MAXIMUM_LENGTH)
print(X_test_preprocessed_final)

"""Testing"""

results_a = model.evaluate(X_test_preprocessed_final, Y_test_a_ENC) 
print(results_a)

"""Plotting Training-Validation accuracy"""

import matplotlib.pyplot as plt

history_dict = history.history

acc = history_dict['acc']
val_acc = history_dict['val_acc']
loss = history_dict['loss']
val_loss = history_dict['val_loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.show()

"""# Part A B C

# Multi class train data preparartion
"""

Y_train_b = train_df['subtask_b']
Y_train_c = train_df['subtask_c']

Y_train_M = Y_train_a.copy()



for i, label in enumerate(Y_train_a):
  if label == 'OFF':
    Y_train_M[i] = Y_train_M[i] +"-"+ Y_train_b[i]
    if Y_train_b[i] == 'TIN':
      Y_train_M[i] = Y_train_M[i] +"-"+ Y_train_c[i]

#print(Y_train_M.unique())    

# One Hot encoding the labels
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

label_encoder = LabelEncoder()
integer_encoded = label_encoder.fit_transform(Y_train_M)

onehot_encoder = OneHotEncoder(sparse=False)
integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
onehot_train_Y = onehot_encoder.fit_transform(integer_encoded)

print(onehot_train_Y)

# Train val split

y_val_M = np.array(onehot_train_Y[:3000])
partial_y_train_M = np.array(onehot_train_Y[3000:])

"""# Multiclass Classifier Model"""

model2 = Sequential()
model2.add(Embedding(input_dim=VOCAB_SIZE,output_dim=EMBED_SIZE,input_length=MAXIMUM_LENGTH,name ='Embedding_layer' ))
model2.add(Dropout(rate = 0.5, noise_shape=None, seed=None))
model2.add(LSTM(units = 100,activation='tanh',name ='LSTM_layer'))
model2.add(Dropout(rate = 0.5, noise_shape=None, seed=None))
model2.add(Dense(units =5, activation='softmax',name ='Output_layer'))
model2.summary()

model2.compile(
              loss='categorical_crossentropy',optimizer='adam',
              metrics=['accuracy'])

"""# Training"""

history2 = model2.fit(partial_X_train,
                    partial_y_train_M,
                    epochs=3,
                    batch_size=100,
                    validation_data=(X_val, y_val_M),
                    verbose=1)

"""# Test Data"""

#X_test_df_b = pandas.read_csv('testset-levelb.tsv',delimiter='\t',encoding='utf-8',names=['ID','tweets'])
Y_test_df_b = pandas.read_csv('labels-levelb.csv',delimiter=',',encoding='utf-8', names=['ID','labels'])

#X_test_df_c = pandas.read_csv('testset-levelc.tsv',delimiter='\t',encoding='utf-8',names=['ID','tweets'])
Y_test_df_c = pandas.read_csv('labels-levelc.csv',delimiter=',',encoding='utf-8', names=['ID','labels'])

#X_test_df_c = X_test_df_c.drop(0).reset_index(drop= True)

j = 0
k = 0
Y_test_M = Y_test_a.copy()
# print(Y_test_df_b['ID'])
# print((Y_test_df_b['ID'][0] == Y_test_df_b['ID'][0]))
for i,ids in enumerate(Y_test_df_a['ID']):
  #print(ids)
  if ids in Y_test_df_b.values:
    
    Y_test_M[i] = Y_test_M[i] +"-"+ Y_test_df_b['labels'][j]
    j += 1

    if ids in Y_test_df_c.values:
      Y_test_M[i] = Y_test_M[i] +"-"+ Y_test_df_c['labels'][k]
      k += 1
print(Y_test_M) 


integer_encoded = label_encoder.fit_transform(Y_test_M)


integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
onehot_test_Y = onehot_encoder.fit_transform(integer_encoded)

print(onehot_test_Y)

"""# Testing"""

results_M = model2.evaluate(X_test_preprocessed_final, onehot_test_Y) 
print(results_M)

"""Plotting Training-Validation accuracy"""

import matplotlib.pyplot as plt

history_dict = history2.history

acc = history_dict['acc']
val_acc = history_dict['val_acc']
loss = history_dict['loss']
val_loss = history_dict['val_loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.show()

"""# Trying CNN model"""

model3 = Sequential()
model3.add(Embedding(input_dim=VOCAB_SIZE,output_dim=EMBED_SIZE,input_length=MAXIMUM_LENGTH,name ='Embedding_layer' ))
model3.add(Conv1D(128, kernel_size=7, activation='relu',padding='valid'))
model3.add(GlobalMaxPooling1D())
model3.add(Dense(200, activation='relu'))
model3.add(Dense(5, activation='sigmoid'))
model3.summary()

model3.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

history3 = model3.fit(partial_X_train,
                    partial_y_train_M,
                    epochs=3,
                    batch_size=100,
                    validation_data=(X_val, y_val_M),
                    verbose=1)

results_M_CNN = model3.evaluate(X_test_preprocessed_final, onehot_test_Y) 
print(results_M_CNN)

"""Plotting training Validation accuracy"""

import matplotlib.pyplot as plt

history_dict = history3.history

acc = history_dict['acc']
val_acc = history_dict['val_acc']
loss = history_dict['loss']
val_loss = history_dict['val_loss']

epochs = range(1, len(acc) + 1)

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.show()
