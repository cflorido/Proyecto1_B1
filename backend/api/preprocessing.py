# preprocessing.py
import pandas as pd
import contractions
import nltk
from pathlib import Path
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer, PorterStemmer, SnowballStemmer
from nltk import word_tokenize, sent_tokenize
import string
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
import re
import joblib

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
vectorizer = joblib.load(ARTIFACTS_DIR / "vectorizer.joblib")

def vectorization_function_transform(x):
    return vectorizer.transform(x).toarray()

def aMinusculas(palabras):
    return [palabra.lower() for palabra in palabras]


def eliminarNumeros(palabras):
    return [re.sub(r'\d+', '', palabra) for palabra in palabras]

def eliminarPuntuacion(palabras):
    return [palabra for palabra in palabras if palabra not in string.punctuation]

def removerNoAscii(palabras):
    return [palabra for palabra in palabras if palabra.isascii()]

def eliminarStopwords(palabras):
    sw = set(stopwords.words('spanish'))
    return [palabra for palabra in palabras if palabra not in sw]

def aplicarStemmingYLematizacion(palabras):

    stemmer = SnowballStemmer('spanish')
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(stemmer.stem(palabra)) for palabra in palabras]

def preprocesar(palabras):
    palabras = aMinusculas(palabras)
    palabras = eliminarNumeros(palabras)
    palabras = eliminarPuntuacion(palabras)
    palabras = removerNoAscii(palabras)
    palabras = eliminarStopwords(palabras)
    return palabras

def procesar(texto):
    texto = contractions.fix(texto)
    palabras = word_tokenize(texto)
    palabras = preprocesar(palabras)
    palabras = aplicarStemmingYLematizacion(palabras)
    return ' '.join(palabras)

def dropna_and_combine_text(df):
    df_clean = df.dropna(subset=['Titulo', 'Descripcion']).copy()
    df_clean['Texto'] = df_clean['Titulo'] + ' ' + df_clean['Descripcion']
    return df_clean['Texto']

def text_preprocessing_function(x):
    return x.apply(procesar) 

def vectorization_function(x, vectorizer):
    return vectorizer.transform(x).toarray()
