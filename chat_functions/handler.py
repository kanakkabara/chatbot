from abc import ABC, abstractmethod, ABCMeta


class Handler(metaclass=ABCMeta):

    @abstractmethod
    def handle(self, sentence):
        pass