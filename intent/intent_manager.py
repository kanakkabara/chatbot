import json
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

with open(dir_path + '/intents.json') as json_data:
    intents = json.load(json_data)


def get_intents():
    return intents['intents']


def get_intent(tag):
    return list(filter(lambda x: x['tag'] == tag, get_intents()))[0]
