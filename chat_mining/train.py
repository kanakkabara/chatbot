
import io
import json
from snips_nlu import SnipsNLUEngine, load_resources
from snips_nlu.default_configs import CONFIG_EN
import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class SnipHandler:
    dataset_path = DIR_PATH + "/question_dataset.json"
    __instance__ = None

    @staticmethod
    def get_instance():
        if SnipHandler.__instance__ is None:
            SnipHandler()
        return SnipHandler.__instance__

    def __init__(self):
        load_resources(u"en")
        engine = SnipsNLUEngine(config=CONFIG_EN)
        with io.open(SnipHandler.dataset_path) as f:
            data_set = json.load(f)

        self.engine = engine.fit(data_set)

        SnipHandler.__instance__ = self

    def parse(self, string):
        return self.engine.parse(string)

print(SnipHandler.get_instance().parse('what is your stuff'))
