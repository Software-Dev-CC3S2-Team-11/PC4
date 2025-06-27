import os


def load_env(ENV_PATH):
    """
    Carga el contenido un archivo .env a partir de su ruta.
    Lee el formato diccionario y mapea su contenido
    """
    ENV_ARRAY = {}

    with open(ENV_PATH) as ENV_FILE:
        for line in ENV_FILE:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue

            KEY, VALUE = line.split("=",1)
            ENV_ARRAY[KEY.strip()] = VALUE.strip()
    return ENV_ARRAY
