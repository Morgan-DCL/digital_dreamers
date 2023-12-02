import asyncio
import os
import shutil

import nltk

from get_dataframes.api_tmdb import main as machine_learning
from get_dataframes.get_dataframes import GetDataframes
from utils.tools import import_config, logging

nltk.download("stopwords")
nltk.download("wordnet")
from datetime import datetime
config = import_config()

start = datetime.now()
def get_all(config: dict):
    logging.info("Start creating dataframe for Machine Learning...")
    asyncio.run(machine_learning(config))
    all_for_one = GetDataframes(config)
    all_for_one.get_all_dataframes()

get_all(config)
end = datetime.now()
print(f"Temps écoulé -> {end - start}")
