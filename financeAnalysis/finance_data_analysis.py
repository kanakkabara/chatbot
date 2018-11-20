import pandas as pd
import json
import re
from sklearn import preprocessing
import nltk


# "financeScraper/data/reu_AAPL-Nov-20-2018.jl"

def readJson(filename):
    contents = open(filename, "r").read()
    data = [json.loads(str(item)) for item in contents.strip().split('\n')]
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.drop_duplicates(subset=['text'])
    df = df.sort_values(by=['date'])
    return df


def cleanText(text):
    """
    removes punctuation, stopwords and returns lowercase text in a list of single words
    """
    text = text.lower()

    from bs4 import BeautifulSoup
    text = BeautifulSoup(text).get_text()

    from nltk.tokenize import RegexpTokenizer
    tokenizer = RegexpTokenizer(r'\w+')
    text = tokenizer.tokenize(text)
    from nltk.corpus import stopwords
    clean = [word for word in text if word not in stopwords.words('english')]
    return clean


def loadPositive():
    myfile = open('LoughranMcDonald_Positive.csv', "r")
    positives = myfile.readlines()
    positive = [pos.strip().lower().split(",")[0] for pos in positives]
    return positive


def loadNegative():
    myfile = open('LoughranMcDonald_Negative.csv', "r")
    negatives = myfile.readlines()
    negative = [neg.strip().lower().split(",")[0] for neg in negatives]
    return negative


def countNeg(cleantext, negative):
    negs = [word for word in cleantext if word in negative]
    return len(negs)


def countPos(cleantext, positive):
    pos = [word for word in cleantext if word in positive]
    return len(pos)


def getSentiment(cleantext, negative, positive):
    return (countPos(cleantext, positive) - countNeg(cleantext, negative))


def updateSentimentDataFrame(df):
    positive = loadPositive()
    negative = loadNegative()
    df['text'] = df['text'].apply(cleanText)
    df['score'] = df['text'].apply(lambda x: getSentiment(x, negative, positive))
    print(df['score'])


def prepareToConcat(filename):
    df = pd.read_csv(filename, parse_dates=['date'])
    df = df.drop('text', 1)
    df = df.dropna()
    df = df.groupby(['date']).mean()
    name = re.search(r'/(\w+).csv', filename)
    df.columns.values[0] = name.group(1)
    return df


def mergeSentimentToStocks(stocks):
    df = pd.read_csv('/home/sentiment.csv', index_col='date')
    final = stocks.join(df, how='left')
    return final


def createSentimentDataset(sentimentdata):
    df = sentimentdata[0].join(sentimentdata[1:], how='outer')

    df = df.fillna(method='bfill')
    df = df.fillna(method='ffill')

    i = df.index
    c = df.columns

    print(df.shape[0] * df.shape[1] - df.count().sum())
    return pd.DataFrame(preprocessing.scale(df), index=i, columns=c)

def performSentimentAnalysis(ticker)

print('reading jl files')
df = readJson("financeScraper/data/reu_AAPL-Nov-20-2018.jl")
print('performing sentiment analysis')
updateSentimentDataFrame(df)
