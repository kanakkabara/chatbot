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


    def get_asset_allocation(self):
        return [f'you asset allocation is ...']

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
            return self.get_asset_allocation(), None
        else:
            remaining_field = self.get_remaining_fields()[0]
            responses = get_clarification_for_field(remaining_field, 'asset_allocation')
            self.state = remaining_field
            return responses, self

