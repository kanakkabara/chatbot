from chat_functions.handler import Handler
from intent.intent_manager import *
from snip.snip_handler import SnipHandler

is_noun = lambda pos: pos[:2] == 'NN'

required_fields = ['BU', 'CIF', 'allocationGroup']
permitted_fields = ['currency', 'portfolioId']


class AssetAllocation(Handler):
    tag = 'asset_allocation'

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

    def get_account_balance(self):

        return [f'you asset allocation is ...']

    def handle(self, sentence):
        snip = SnipHandler.get_instance()
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
            return self.get_account_balance(), None
        else:
            remaining_field = self.get_remaining_fields()[0]
            responses = get_clarification_for_field(remaining_field, 'asset_allocation')
            self.state = remaining_field
            return responses, self

