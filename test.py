import json
import numpy as np
import os

def testing():
    random_value = np.random.random()

    log_dir = 'log'
    log_file = os.path.join(log_dir, 'log.json')

    os.makedirs(log_dir, exist_ok=True)

    if not os.path.exists(log_file):
        with open(log_file, 'w') as file:
            json.dump([], file)

    with open(log_file, 'r') as file:
        data = json.load(file)

    data.append(random_value)

    with open(log_file, 'w') as file:
        json.dump(data, file)

    print("Valeur ajoutée au fichier log :", random_value)
