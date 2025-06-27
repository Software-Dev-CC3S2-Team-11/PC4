import subprocess
import os
import sys

COMPOSE_ENVIRONMENTS = {
    "db-env": "docker-compose.base.yaml",
    "todo-env": "docker-compose.dev.yaml",
    "auth-env": "docker-compose.dev.yaml"
}

MINIKUBE_ENVIRONMENTS = {
    "db-env": "k8s/db_service.yaml",
    "todo-env": "k8s/todo_service.yaml",
    "auth-env": "k8s/auth_service.yaml"
}


def start_env(env_name):
    if env_name not in COMPOSE_ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    print(f"Iniciando entorno '{env_name}'")
    if env_name == "db-env":
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "up", "-d", "db"])
    elif env_name == "auth-env":
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "up", "-d", "auth_service"])
    elif env_name == "todo-env":
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "up", "-d", "todo_service"])
    subprocess.run(["docker", "ps"])


def stop_env(env_name):
    if env_name not in COMPOSE_ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    print(f"Deteniendo entorno '{env_name}'")
    if env_name == "db-env":
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "stop", "db"])
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "rm", "-f", "db"])
    if env_name == "auth-env":
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "stop", "auth_service"])
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "rm", "-f", "auth_service"])
    elif env_name == "todo-env":
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "stop", "todo_service"])
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "rm", "-f", "todo_service"])

    subprocess.run(["docker", "ps"])


def list_envs():
    print("Entornos disponibles:")
    for env in COMPOSE_ENVIRONMENTS:
        print("\t-  " + env)


def deploy_service(env_name):
    if env_name not in MINIKUBE_ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    print(f"Desplegando servicio en el entorno '{env_name}'")

    if env_name == "db-env":
        subprocess.run(["kubectl", "apply", "-f", MINIKUBE_ENVIRONMENTS[env_name]])
        subprocess.run(["minikube", "service", "db","--url"])
    elif env_name == "auth-env":
        subprocess.run(["kubectl", "apply", "-f", MINIKUBE_ENVIRONMENTS[env_name]])
        subprocess.run(["minikube", "service", "auth-service", "--url"])
    elif env_name == "todo-env":
        subprocess.run(["kubectl", "apply", "-f", MINIKUBE_ENVIRONMENTS[env_name]])
        subprocess.run(["minikube", "service", "todo-service", "--url"])

    print(f"Servicio en '{env_name}' desplegado correctamente.")
    subprocess.run(["minikube", "service", "list"])


def delete_service(env_name):
    if env_name not in MINIKUBE_ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    
    print(f"Eliminando servicio en el entorno '{env_name}'")
    subprocess.run(["kubectl", "delete", "-f", MINIKUBE_ENVIRONMENTS[env_name]])

    print(f"Servicio en '{env_name}' eliminado correctamente.")        
    subprocess.run(["minikube", "service", "list"])



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
    elif command == "deploy_service":
        deploy_service(env_name)
    elif command == "delete_service":
        delete_service(env_name)
    else:
        print(f"Comando '{command}' no reconocido")
        sys.exit(1)
