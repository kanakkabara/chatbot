import json
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

with open(dir_path + '/intents.json') as json_data:
    intents = json.load(json_data)


def get_intents():
    return intents['intents']


def get_intent(tag):
    return list(filter(lambda x: x['tag'] == tag, get_intents()))[0]


def get_intents_by_tag(tag):
    return list(filter(lambda x: x['tag'] == tag, get_intents()))


def get_clarification_for_field(field, tag):
    for intent in get_intents_by_tag(tag):
        if 'clarification' in intent['context_set'].keys():
            if 'field' in intent['context_set']['clarification'].keys():
                if intent['context_set']['clarification']['field'] == field:
                    return intent

