import random

from intent.intent_manager import *
from chat_functions.handler import Handler
from snip.snip_handler import SnipHandler

is_noun = lambda pos: pos[:2] == 'NN'

required_fields = ['currency', 'accountNumber']


class AccountBalance(Handler):
    tag = 'account_balance'

    def __init__(self, _dict=None):
        super().__init__(_dict)
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

    def get_account_balance(self):
        return ['you account balance is 100']

    def handle(self, sentence):
        snip = SnipHandler.get_instance()
        parsed = snip.parse(sentence)
        if self.state is not None:
            self.fields[self.state] = sentence
            self.state = None
        else:
            if parsed['slots'] is not None:
                fields = list(map(lambda x: (x['entity'], x['value']['value']), parsed['slots']))
                for field, value in fields:
                    if field in required_fields:
                        self.fields[field] = value
            else:
                return [random.choice(["I'm sorry, I don't understand. Could you rephrase that?"])], None
        if self.has_all_required_fields():
            return self.get_account_balance(), None
        else:
            remaining_field = self.get_remaining_fields()[0]
            self.state = remaining_field
            return get_clarification_for_field(remaining_field, 'account_balance'), self

