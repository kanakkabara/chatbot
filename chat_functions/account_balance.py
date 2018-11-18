import nltk
import re

from intent import get_intent

is_noun = lambda pos: pos[:2] == 'NN'


def account_balance_handler(sentence):
    words = nltk.word_tokenize(sentence)
    nouns = [word for (word, pos) in nltk.pos_tag(words) if is_noun(pos)]

    r = re.compile("^S[0-9]{6}$")
    account_number = list(filter(r.match, nouns))

    intent = get_intent('account_balance')
    if account_number:
        response = intent['responses'][0]
        response = response % (account_number[0], get_account_balance(account_number[0]))
        return [response], intent['context_set']['success'] % account_number[0]
    else:
        return intent['clarifications'], intent['context_set']['clarification']['context']


def get_account_balance(account_number):
    # TODO fetch data
    print("perform transaction %s" % account_number)
    return 1000
