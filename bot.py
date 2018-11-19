import pickle
from collections import defaultdict

import numpy as np
import nltk
from nltk.stem.lancaster import LancasterStemmer
import random

from chat_functions import account_balance_handler
from intent import get_intents, get_intent
from training import get_model

data = pickle.load(open("./model/training_data", "rb"))
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# Define model and setup tensorboard
model = get_model(train_x, train_y)
model.load('./model/model.tflearn')

ERROR_THRESHOLD = 0.5


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


tag_under_processing = defaultdict(dict)
state = defaultdict(dict)
context = {}


def response(sentence, user_id='123', show_details=False):
    intents = get_intents()

    if tag_under_processing[user_id]:
        intent = get_intent(tag_under_processing[user_id])
        requirements = intent['requirements']
        for requirement in requirements:
            if not state[user_id][requirement]:
                # TODO check if current sentence fulfils this req
                # if not ask clarification
                # if yes populate the state
                state[user_id][requirement] = sentence
                break

        for requirement in requirements:
            if not state[user_id][requirement]:
                return random.choice(intent['clarifications'][requirement])
        results = [[tag_under_processing[user_id]]]
        # all reqs are satisfied now, use tag under processing and proceed normally
    else:
        results = classify(sentence)

    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    responses = i['responses']
                    context_info = None
                    if i['tag'] == "account_balance":
                        responses, completed, user_state = account_balance_handler(sentence, state[user_id])
                        if not completed:
                            state[user_id] = user_state
                            tag_under_processing[user_id] = i['tag']
                        else:
                            state[user_id] = {}
                            tag_under_processing[user_id] = None

                    # set context for this intent if necessary
                    if 'context_set' in i:
                        context[user_id] = i['context_set'] if context_info is None else context_info
                        if show_details:
                            print('context:', context[user_id])

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or (
                            user_id in context and 'context_filter' in i and i['context_filter'] == context[user_id]):
                        if show_details:
                            print('tag:', i['tag'])
                        # a random response from the intent
                        return random.choice(responses)

            results.pop(0)
    else:
        return "I'm sorry, I don't understand what you mean.."


if __name__ == "__main__":
    print("Welcome!")
    while True:
        try:
            chat = input()
            print(response(chat, show_details=True))
        except(KeyboardInterrupt, EOFError, SystemExit):
            break
