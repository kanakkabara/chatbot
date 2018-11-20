import io
import json
from snips_nlu import SnipsNLUEngine, load_resources
from snips_nlu.default_configs import CONFIG_EN

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
dataset_path = dir_path + "/dataset/account_balance_dataset.json"

class SnipAccountBalance:

    __instance__ = None

    @staticmethod
    def get_instance():
        if SnipAccountBalance.__instance__ is None:
            SnipAccountBalance()
        return SnipAccountBalance.__instance__

    def __init__(self):
        load_resources(u"en")
        engine = SnipsNLUEngine(config=CONFIG_EN)
        with io.open(dataset_path) as f:
            data_set = json.load(f)

        self.engine = engine.fit(data_set)

        SnipAccountBalance.__instance__ = self

    def parse(self, string):
        return self.engine.parse(string)


if __name__ == '__main__':
    dataset_path = 'account_balance_dataset.json'
    #print(json.dumps(parse("can i get the account balance in JYP for account number 12345"), indent=2))