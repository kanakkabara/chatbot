import io
import json
from snips_nlu import SnipsNLUEngine, load_resources
from snips_nlu.default_configs import CONFIG_EN
dataset_path = "snip\\dataset.json"

def parse(string):
    load_resources(u"en")
    engine = SnipsNLUEngine(config=CONFIG_EN)
    with io.open(dataset_path) as f:
        data_set = json.load(f)

    engine.fit(data_set)
    return engine.parse(string)


if __name__ == '__main__':
    dataset_path = 'dataset.json'
    print(json.dumps(parse("can i get the account balance in JYP for account number 12345"), indent=2))