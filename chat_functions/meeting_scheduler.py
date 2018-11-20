import json
import random

import parsedatetime
from datetime import datetime
from chat_functions.handler import Handler
from intent.intent_manager import get_clarification_for_field
from snip.snip_handler import SnipHandler


class MeetingScheduler(Handler):
    required_fields = ['location', 'time', 'attendee']
    tag = 'schedule_meeting'

    def __init__(self, _dict=None):
        super()
        super().__init__(_dict)

    def schedule_meeting(self):
        time = self.fields['time'].strftime('%Y-%m-%d %H:%M:%S')
        return [f'Your meeting has been confirmed at {time}.', f'I have set up the appointment at {time}.']

    def handle(self, sentence):
        snip = SnipHandler.get_instance()
        parsed = snip.parse(sentence)
        if self.state is not None:

            self.fields[self.state] = parse_time(sentence) if self.state == 'time' else sentence
            self.state = None
        else:
            if parsed['slots'] is not None:

                fields = list(map(lambda x: (x['entity'], x['value']['value']), parsed['slots']))
                for field, value in fields:
                    if field in self.required_fields:
                        self.fields[field] = parse_time(value) if field == 'time' else value
                    elif field =='snips/datetime':
                        self.fields['time'] = datetime.strptime(value[:19], '%Y-%m-%d %H:%M:%S')

            else:
                return [random.choice(["I'm sorry, I don't understand. Could you rephrase that?"])], None
        if self.has_all_required_fields():
            return self.schedule_meeting(), None
        else:
            remaining_field = self.get_remaining_fields()[0]
            self.state = remaining_field
            return get_clarification_for_field(remaining_field, 'schedule_meeting'), self


def parse_time(time_str):
    cal = parsedatetime.Calendar()
    time_struct, _ = cal.parse(time_str)
    return datetime(*time_struct[:6])

