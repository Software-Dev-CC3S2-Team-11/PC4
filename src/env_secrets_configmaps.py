import os
import sys
import base64

# Diccionario con nombre del servicio como clave y ruta de la carpeta como valor
SERVICES = {
    "auth-env": "auth_service",
    "todo-env": "todo_service",
    "db-env": ""
}


def load_env(SERVICE_NAME):
    """
    Carga el contenido un archivo .env a partir de su ruta.
    Lee el formato diccionario y mapea su contenido
    """
    base_dir = os.path.dirname(__file__)
    service_dir = os.path.join(base_dir, SERVICES[SERVICE_NAME])
    
    env_path = None
    if os.path.isdir(service_dir):
        for fname in os.listdir(service_dir):
            if fname.endswith(".env"):
                env_path = os.path.join(service_dir, fname)
                break

    if not os.path.isfile(env_path):
        raise FileNotFoundError(f"No existe .env para '{SERVICE_NAME}' en {env_path}")
    env_data = {}

    with open(env_path) as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            env_data[key.strip()] = value.strip()
    return env_data


def render_secret(name, env_data):
    """
    Cargamos un archivo YAML listo para que la API de Kubernets pueda
    acceder a esta. Para ello, los valores de los secretos son pasados
    a b64 de acuerdo a su documentacion
    :param : 
    :return : YAML Secrets
    """
    lines = [
      "apiVersion: v1",
      "kind: Secret",
      "type: Opaque",
      f"metadata:\n  name: {name}",
      "data:"
    ]
    for key, value in env_data.items():
        if not key.startswith("SECRET_"):
            continue
        B64 = base64.b64encode(value.encode()).decode()
        lines.append(f"  {key}: \"{B64}\"")
    return "\n".join(lines)


def render_configmap(name, data):
    lines = [
      "apiVersion: v1",
      "kind: ConfigMap",
      f"metadata:\n  name: {name}",
      "data:"
    ]
    for k, v in data.items():
        if k.startswith("SECRET_"):
            continue
        lines.append(f"  {k}: \"{v}\"")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Uso: python env_secrets_configmaps.py <service_name>")
        print("Servicios disponibles:", ", ".join(SERVICES.keys()))
        sys.exit(1)
    SERVICE_NAME = sys.argv[1]
    if SERVICE_NAME not in SERVICES:
        print(f"Servicio no reconocido: '{SERVICE_NAME}'")
        print("Escoge uno de:", ", ".join(SERVICES.keys()))
        sys.exit(1)

    try:
        env_data = load_env(SERVICE_NAME)
    except FileNotFoundError as e:
        print("Error:", e)
        sys.exit(1)

    cm_yaml = render_configmap(f"{SERVICE_NAME}-config", env_data)
    sec_yaml = render_secret(f"{SERVICE_NAME}-secret", env_data)

    out_dir = os.path.join("configmaps", SERVICE_NAME)
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/configmap.yaml","w") as f:
        f.write(cm_yaml+"\n")
    with open(f"{out_dir}/secret.yaml","w") as f:
        f.write(sec_yaml+"\n")
    print("Manifiestos con secrets y configmaps generados en", out_dir)


if __name__ == "__main__":
    main()