from abc import ABC, abstractmethod, ABCMeta


class Handler(metaclass=ABCMeta):

    required_fields = None
    fields = None

    def __init__(self, _dict=None):
        self.fields = dict() if _dict is None else _dict
        self.state = None

    @abstractmethod
    def handle(self, sentence):
        pass

    def has_all_required_fields(self):
        if self.fields is None:
            return False
        if sorted(self.fields.keys()) == sorted(self.required_fields):
            return True
        else:
            return False

    def get_remaining_fields(self):

        return list((set(self.required_fields)).difference(set(self.fields.keys())))

