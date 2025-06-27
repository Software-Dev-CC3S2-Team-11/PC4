import subprocess
import os
import sys

ENVIRONMENTS = {
    "db-env": "docker-compose.base.yaml",
    "todo-env": "docker-compose.dev.yaml",
    "auth-env": "docker-compose.dev.yaml"
}


def start_env(env_name):
    if env_name not in ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    print(f"Iniciando entorno '{env_name}'")
    if env_name == "db-env":
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "up", "-d", "db"])
    elif env_name == "auth-env":
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "up", "-d", "auth_service"])
    elif env_name == "todo-env":
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "up", "-d", "todo_service"])
    subprocess.run(["docker", "ps"])


def stop_env(env_name):
    if env_name not in ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    print(f"Deteniendo entorno '{env_name}'")
    if env_name == "db-env":
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "stop", "db"])
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "rm", "-f", "db"])
    if env_name == "auth-env":
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "stop", "auth_service"])
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "rm", "-f", "auth_service"])
    elif env_name == "todo-env":
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "stop", "todo_service"])
        subprocess.run(["docker-compose", "-f", ENVIRONMENTS[env_name], "rm", "-f", "todo_service"])

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
