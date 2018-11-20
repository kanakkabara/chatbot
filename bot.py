import pickle
import numpy as np
import nltk
from nltk.stem.lancaster import LancasterStemmer
import random

from chat_functions import AccountBalance
from chat_functions.advisory import Advisory
from chat_functions.asset_allocation import AssetAllocation
from intent import get_intents
from training import get_model

data = pickle.load(open("./model/training_data", "rb"))
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# Define model and setup tensorboard
model = get_model(train_x, train_y)
model.load('./model/model.tflearn')

context = {}
ERROR_THRESHOLD = 0.25


def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    stemmer = LancasterStemmer()
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)

    return np.array(bag)


def classify(sentence):
    # generate probabilities from the model
    results = model.predict([bow(sentence, words)])[0]
    # filter out predictions below a threshold
    results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability
    print(return_list)
    return return_list


def get_query_obj(tag):
    objs = {
        'account_balance': AccountBalance,
        'asset_allocation': AssetAllocation,
        Advisory.tag: Advisory
    }
    return None if tag not in objs else objs[tag]()


def response(sentence, obj, user_id='123', show_details=False):
    intents = get_intents()

    results = [[obj.tag]] if obj is not None else classify(sentence)
    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:

                    obj = get_query_obj(i['tag']) if obj is None else obj
                    if obj is not None:
                        responses, state = obj.handle(sentence)
                        return random.choice(responses), state
                    responses = i['responses']
                    '''
                    context_info = None
                    if i['tag'] == "account_balance" or i['tag'] == 'account_balance_clarification':
                        responses, context_info = AccountBalance().account_balance_handler(sentence)

                    # set context for this intent if necessary
                    if 'context_set' in i:
                        context[user_id] = i['context_set'] if context_info is None else context_info
                        if show_details:
                            print('context:', context[user_id])
                    '''
                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or (
                            user_id in context and 'context_filter' in i and i['context_filter'] == context[user_id]):
                        if show_details:
                            print('tag:', i['tag'])
                        # a random response from the intent
                        return random.choice(responses), None
            results.pop(0)


if __name__ == "__main__":
    print("Welcome!")
    obj = None
    while True:
        try:
            chat = input()
            res, _obj = response(chat, obj, show_details=True)
            obj = _obj
            print(res)
            if obj is None:
                print('What else can I help you with?')
        except(KeyboardInterrupt, EOFError, SystemExit):
            break

