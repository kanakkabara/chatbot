import nltk
import re

from intent import get_intent

is_noun = lambda pos: pos[:2] == 'NNP' or pos[:2] == 'NN'


def account_balance_handler(sentence, existing_state):
    state = existing_state
    token_words = nltk.word_tokenize(sentence)
    tagged_tokens = nltk.pos_tag(token_words)
    nouns = [word for (word, pos) in tagged_tokens if is_noun(pos)]
    print(nltk.ne_chunk(tagged_tokens))

    r = re.compile("^S[0-9]{6}$")
    account_number = list(filter(r.match, nouns))

    intent = get_intent('account_balance')
    if account_number:
        state["account"] = account_number[0]
    elif "account" in state:
        account_number = [state["account"]]
    else:
        state["account"] = None
        return intent['clarifications']["account"], False, state

    response = intent['responses'][0]
    response = response % (account_number[0], get_account_balance(account_number[0]))
    return [response], True, state


def get_account_balance(account_number):
    # TODO fetch data
    print("perform transaction %s" % account_number)
    return 1000
