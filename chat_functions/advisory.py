import nltk
from intent.intent_manager import *
from snip.snip_advisory import SnipAdvisory

is_noun = lambda pos: pos[:2] == 'NN'

required_fields = ['stockName']


class Advisory:
    tag = 'advisory'

    def __init__(self, _dict=None):
        self.fields = dict() if _dict is None else _dict
        self.state = None

    def has_all_required_fields(self):
        if self.fields is None:
            return False
        if sorted(self.fields.keys()) == sorted(required_fields):
            return True
        else:
            return False

    def get_remaining_fields(self):

        return list((set(required_fields)).difference(set(self.fields.keys())))

    def get_advisory(self):
        return [f'This is my advice for %s' % self.fields]

    def handle(self, sentence):
        snip = SnipAdvisory.get_instance()
        parsed = snip.parse(sentence)
        if self.state is not None:
            self.fields[self.state] = sentence
            self.state = None
        else:
            fields = list(map(lambda x: (x['entity'], x['value']['value']), parsed['slots']))
            for field, value in fields:
                if field in required_fields:
                    self.fields[field] = value

        if self.has_all_required_fields():
            return self.get_advisory(), None
        else:
            remaining_field = self.get_remaining_fields()[0]
            # clarifications = get_clarification_for_field(remaining_field, self.tag)
            intent = get_intent(Advisory.tag)
            self.state = remaining_field
            return intent['clarifications'][remaining_field], self

