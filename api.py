import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
import json
import re
import pickle

# Load model and feature extraction
count_vect = pickle.load(open("static/feature_New.sav", "rb"))
nn_model = pickle.load(open("static/model_NN.sav", "rb"))

#NN model prediction
def neural_network_predict(text):
    # Data preprocessing
    text = count_vect.transform([cleansing(text)])
    prediction = nn_model.predict(text)[0]
    return prediction

# Load model LSTM
tokenizer = pickle.load(open("static/feature_New_lstm.sav", "rb"))
lstm_model =  pickle.load(open("static/model_lstm.sav", "rb"))

#LSTM prediction
def lstm_predict(text):
    # Data preprocessing
    text = [cleansing(text)]
    
    tokenized_text = tokenizer.texts_to_sequences(text)
    padded_text = pad_sequences(tokenized_text, maxlen=100)
    prediction = lstm_model.predict(padded_text)[0]
    sentiment = get_sentiment_label(prediction)
    return sentiment

def get_sentiment_label(prediction):
    labels = ['negative', 'neutral', 'positive']
    sentiment = labels[prediction.argmax()]
    return sentiment

#Cleansing
def cleansing(sent):
    # Mengubah kata menjadi huruf kecil semua dengan menggunakan fungsi lower()
    string = sent.lower()
    # Menghapus emoticon dan tanda baca menggunakan "RegEx" dengan script di bawah
    string = re.sub(r'[^a-zA-Z0-9]', ' ', string)
    return string
