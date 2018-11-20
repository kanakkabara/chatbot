import io
import json
from snips_nlu import SnipsNLUEngine, load_resources
from snips_nlu.default_configs import CONFIG_EN

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
dataset_path = dir_path + "/dataset/advisory_dataset.json"

class SnipAdvisory:

    __instance__ = None

    @staticmethod
    def get_instance():
        if SnipAdvisory.__instance__ is None:
            SnipAdvisory()
        return SnipAdvisory.__instance__

    def __init__(self):
        load_resources(u"en")
        engine = SnipsNLUEngine(config=CONFIG_EN)
        with io.open(dataset_path) as f:
            data_set = json.load(f)

        self.engine = engine.fit(data_set)

        SnipAdvisory.__instance__ = self

    def parse(self, string):
        return self.engine.parse(string)
