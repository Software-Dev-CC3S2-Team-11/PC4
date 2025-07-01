import subprocess
import os
import sys
import time
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COMPOSE_ENVIRONMENTS = {
    "db-env": "docker-compose.base.yaml",
    "todo-env": "docker-compose.dev.yaml",
    "auth-env": "docker-compose.dev.yaml"
}

MINIKUBE_ENVIRONMENTS = {
    "db-env": os.path.join(BASE_DIR, "k8s", "db.yaml"),
    "todo-env": os.path.join(BASE_DIR, "k8s", "todo_service.yaml"),
    "auth-env": os.path.join(BASE_DIR, "k8s", "auth_service.yaml")
}

TARGET_SERVICES = {
  "auth-env": ["db", "auth_service"],
  "todo-env": ["db", "todo_service"],
  "db-env":   ["db"],
}


def wait_for_pod_ready(label, retries=10, delay=3):
    if (label == "db-env"):
        label = "db"

    if (label == "todo-env"):
        label = "todo-service"

    if (label == "auth-env"):
        label = "auth-service"

    for _ in range(retries):
        result = subprocess.run(
            ["kubectl", "get", "pods", "-l", f"app={label}",
             "-o", "jsonpath={.items[0].status.containerStatuses[0].ready}"],
            capture_output=True, text=True
        )
        if result.stdout.strip() == "true":
            return True
        time.sleep(delay)
    return False


def start_env(env_name):
    if env_name not in COMPOSE_ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    print(f"Iniciando entorno '{env_name}'")
    if env_name == "db-env":
        subprocess.run(["docker-compose", "-f", COMPOSE_ENVIRONMENTS[env_name], "up", "-d"])
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


def status_env(env_name):
    """
    Realiza un healthcheck de los contenedores en un entorno Docker Compose.
    Imprime el healthcheck del contenedor (healthy/unhealthy) y el tiempo que lleva en ejecución.
    """
    if env_name not in COMPOSE_ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return

    compose_file = os.path.join(BASE_DIR, os.pardir, COMPOSE_ENVIRONMENTS[env_name])
    compose_file = os.path.abspath(compose_file)
    print(f"\nHealthcheck para '{env_name}' (Docker Compose '{compose_file}')")

    try:
        ps = subprocess.run(
            ["docker-compose", "-f", compose_file, "ps", "-q"],
            capture_output=True, text=True, check=True
        )
        lines = ps.stdout.splitlines()
        ids = []
        for c in lines:
            clean_line = c.strip()
            if clean_line != "":
                ids.append(c)
    except subprocess.CalledProcessError:
        ids = []
    if not ids:
        print("  (no hay contenedores en ejecución o falló 'ps')")
        return

    all_healthy = True
    for cid in ids:
        info = subprocess.run(
            ["docker", "inspect", cid, "--format", "{{json .State}}"],
            capture_output=True, text=True, check=True
        )
        state = __import__('json').loads(info.stdout)
        # health status or fallback
        health = state.get("Health", {}).get("Status", "no-healthcheck")
        started = state.get("StartedAt")

        dt = datetime.fromisoformat(started.replace("Z","+00:00"))
        uptime = datetime.now(timezone.utc) - dt

        ok = (health == "healthy")
        if not ok:
            all_healthy = False
        status = "healthy" if ok else f"{health}"

        short_id = cid[:12]
        uptime_text = str(uptime)
        parts = uptime_text.split(".")
        uptime_format = parts[0]

        message = " - " + short_id + " → " + status + ", uptime " + uptime_format
        print(message)

    summary = "Todos healthy" if all_healthy else "Algunos contenedores unhealthy"
    print("→", summary, "\n")

    total = len(TARGET_SERVICES[env_name])
    completed = len(ids)
    remaining = total - completed
    print(f"Tareas restantes: {remaining} de {total}")

    # Registrar métrica para Burn-up/Burn-down
    metrics_path = os.path.abspath(os.path.join(BASE_DIR, os.pardir, "burn_metrics.csv"))
    header = "timestamp,environment,completed,remaining,total\n"
    now = datetime.now(timezone.utc).isoformat()
    entry = f"{now},{env_name},{completed},{remaining},{total}\n"
    write_header = not os.path.exists(metrics_path)
    with open(metrics_path, "a") as mf:
        if write_header:
            mf.write(header)
        mf.write(entry)
    print(f"📊 Burn metrics añadidas a {metrics_path}\n")


def status_k8s(env_name):
    """
    Comprueba readiness de los Pods en Kubernetes y su uptime.
    """
    if env_name not in MINIKUBE_ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido para K8s.")
        return
    
    label = {
        "db-env":   "db",
        "todo-env": "todo-service",
        "auth-env": "auth-service"
    }[env_name]
    print(f"\nEstado K8s para '{env_name}' (app={label})")

    # Obtener pods JSON
    out = subprocess.run(
        ["kubectl", "get", "pods", "-l", f"app={label}", "-o", "json"],
        capture_output=True, text=True, check=True
    ).stdout

    pods = __import__('json').loads(out).get("items", [])
    if not pods:
        print("  (no se encontraron Pods para esa etiqueta)")
        return

    all_ready = True
    
    for pod in pods:
        name = pod["metadata"]["name"]

        created = pod["metadata"]["creationTimestamp"]
        ts = datetime.fromisoformat(created.replace("Z","+00:00"))
        up = datetime.now(timezone.utc) - ts

        conds = pod["status"].get("conditions", [])
        ready = next((c["status"] for c in conds if c["type"]=="Ready"), "Unknown")
        ok = (ready == "True")
        if not ok: 
            all_ready = False
        status = "READY" if ok else f"{ready}"
        
        up_text = str(up)
        parts = up_text.split(".")
        uptime_trimmed = parts[0]
        message = " - " + name + " → " + status + ", uptime " + uptime_trimmed
        print(message)

    summary = "Todos READY" if all_ready else "Algunos Pods no están listos"
    print("→", summary, "\n")


def list_envs():
    print("Entornos disponibles:")
    for env in COMPOSE_ENVIRONMENTS:
        print("\t-  " + env)


def deploy_service(env_name):
    if env_name not in MINIKUBE_ENVIRONMENTS:
        print(f"El entorno '{env_name}' no está definido.")
        return
    print(f"Desplegando servicio en el entorno '{env_name}'")

    # Recoge hora del último commit para Lead Time
    try:
        git_ts = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        commit_dt = datetime.fromtimestamp(int(git_ts), timezone.utc)
    except Exception:
        # si falla, usamos ahora como commit_dt (lead time cero)
        commit_dt = datetime.now(timezone.utc)

    # Recoge hora de inicio del despliegue para Cycle Time
    deploy_start = datetime.now(timezone.utc)

    if env_name == "db-env":
        subprocess.run(["kubectl", "apply", "-f", MINIKUBE_ENVIRONMENTS[env_name]])
        if (wait_for_pod_ready(env_name)):
            subprocess.run(["minikube", "service", "db","--url"])
    elif env_name == "auth-env":
        subprocess.run(["kubectl", "apply", "-f", MINIKUBE_ENVIRONMENTS[env_name]])
        if (wait_for_pod_ready(env_name)):
            subprocess.run(["minikube", "service", "auth-service", "--url"])
    elif env_name == "todo-env":
        subprocess.run(["kubectl", "apply", "-f", MINIKUBE_ENVIRONMENTS[env_name]])
        if (wait_for_pod_ready(env_name)):
            subprocess.run(["minikube", "service", "todo-service", "--url"])

    # Hora en que el servicio está listo
    ready_dt = datetime.now(timezone.utc)

    print(f"Servicio en '{env_name}' desplegado correctamente.")
    subprocess.run(["minikube", "service", "list"])

    # Calculo de métricas
    lead_time_sec = int((ready_dt - commit_dt).total_seconds())
    cycle_time_sec = int((ready_dt - deploy_start).total_seconds())

    # Escribimos en metrics.csv en el root del proyecto
    metrics_file = os.path.abspath(os.path.join(BASE_DIR, os.pardir, "metrics.csv"))
    is_new = not os.path.exists(metrics_file)
    with open(metrics_file, "a") as m:
        if is_new:
            m.write("environment,commit_time,deploy_start,ready_time,lead_time_s,cycle_time_s\n")
        m.write(
            f"{env_name},"
            f"{commit_dt.isoformat()},"
            f"{deploy_start.isoformat()},"
            f"{ready_dt.isoformat()},"
            f"{lead_time_sec},"
            f"{cycle_time_sec}\n"
        )
    print(f"📊 Métricas registradas en {metrics_file}: lead_time={lead_time_sec}s, cycle_time={cycle_time_sec}s")


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
        print("\tstatus_env <env_name> \t Comprueba healthchecks y uptime de los contenedores")
        print("\tstatus_k8s <env_name>\tChequea readiness y uptime de Pods en Kubernetes")
        print("\tdeploy_service <env_name> \t Despliega en Kubernetes y muestra service URL")
        print("\tdelete_service <env_name> \t Elimina recursos de Kubernetes")
    command = sys.argv[1]
    env_name = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "start_env":
        start_env(env_name)
    elif command == "stop_env":
        stop_env(env_name)
    elif command == "status_env":
        status_env(env_name)
    elif command == "status_k8s":
        status_k8s(env_name)
    elif command == "list_envs":
        list_envs()
    elif command == "deploy_service":
        deploy_service(env_name)
    elif command == "delete_service":
        delete_service(env_name)
    else:
        print(f"Comando '{command}' no reconocido")
        sys.exit(1)
