import subprocess
import os
import sys

ENVIRONMENTS = {
    "db-env": "docker-compose.base.yaml",
    "auth-env": "docker-compose.dev.yaml",
}


def start_env(env_name):
    if env_name not in ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    docker_compose_file = ENVIRONMENTS[env_name]
    print(f"Iniciando entorno '{env_name}'")
    subprocess.run(["docker compose", "-f", docker_compose_file, "up", "-d"])
    subprocess.run(["docker", "ps"])


def stop_env(env_name):
    if env_name not in ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    docker_compose_file = ENVIRONMENTS[env_name]
    print(f"Deteniendo entorno '{env_name}'")
    subprocess.run(["docker compose", "-f", docker_compose_file, "down"])
    subprocess.run(["docker", "ps"])


def list_envs():
    print("Entornos disponibles:")
    for env in ENVIRONMENTS:
        print("\t-  " + env)


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Comandos:")
        print("\tstart_env <env_name> \t Inicia un conjunto de servicios Docker Compose")
        print("\tstop_env <env_name> \t Detiene y elimina los servicios de Docker Compose")
    command = sys.argv[1]
    env_name = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "start_env":
        start_env(env_name)
    elif command == "stop_env":
        stop_env(env_name)
    elif command == "list_envs":
        list_envs()
    else:
        print(f"Comando '{command}' no reconocido")
        sys.exit(1)
