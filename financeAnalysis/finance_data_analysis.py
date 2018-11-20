import pandas as pd
import json
import os
import re
from sklearn import preprocessing
import nltk
from financeScraper.crawlers import crawl


# "financeScraper/data/reu_AAPL-Nov-20-2018.jl"

def readJL(filename):
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
    myfile = open('financeAnalysis/LoughranMcDonald_Positive.csv', "r")
    positives = myfile.readlines()
    positive = [pos.strip().lower().split(",")[0] for pos in positives]
    return positive


def loadNegative():
    myfile = open('financeAnalysis/LoughranMcDonald_Negative.csv', "r")
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


def do_sentiment_analysis(tickers):
    crawl(tickers)
    files= os.listdir("financeScraper/data")
    for i in range(len(files) - 1, -1, -1):
        file_name = files[i]
        if (not file_name.endswith(".jl")) or file_name.startswith('blo') or (tickers[0] not in file_name):
            del files[i]
    dframes = []
    for file_name in files:
        print(file_name)
        file_to_read = "financeScraper/data/" + file_name
        dframes.append(readJL(file_to_read))
    updatedDframes = []
    print(dframes)
    for dframe in dframes:
        updatedDframes.append(updateSentimentDataFrame(dframe))
    concat_dframe = pd.concat(updatedDframes)
    return(concat_dframe['score'].sum())

def main():
    do_sentiment_analysis(["MSFT"])

if __name__ == '__main__':
    main()