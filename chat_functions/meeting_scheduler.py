import json
import random

from chat_functions.handler import Handler
from intent.intent_manager import get_clarification_for_field
from snip.snip_handler import SnipHandler


class MeetingScheduler(Handler):
    required_fields = ['location', 'time']
    tag = 'schedule_meeting'

    def __init__(self, _dict=None):
        super()
        super().__init__(_dict)

    def schedule_meeting(self):
        return ['Your meeting has been confirmed.', 'I have set up the appointment.']

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
                    if field in self.required_fields:
                        self.fields[field] = value
            else:
                return [random.choice(["I'm sorry, I don't understand. Could you rephrase that?"])], None
        if self.has_all_required_fields():
            return self.schedule_meeting(), None
        else:
            remaining_field = self.get_remaining_fields()[0]
            self.state = remaining_field
            return get_clarification_for_field(remaining_field, 'schedule_meeting'), self

