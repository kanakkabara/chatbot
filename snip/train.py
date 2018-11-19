import io
import json
from snips_nlu import SnipsNLUEngine, load_resources
from snips_nlu.default_configs import CONFIG_EN


def parse(string):
    load_resources(u"en")
    engine = SnipsNLUEngine(config=CONFIG_EN)
    with io.open("dataset.json") as f:
        data_set = json.load(f)

    engine.fit(data_set)
    return engine.parse(string)