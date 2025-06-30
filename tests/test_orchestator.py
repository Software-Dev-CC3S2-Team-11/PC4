import subprocess
import pytest
import time
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORCHESTRATOR_SCRIPT = os.path.join(BASE_DIR, "src", "env_orchestrator.py")

# Asocia los envs con sus respectivos servicios
ENV_LABEL_MAP = {
    "db-env": "db",
    "auth-env": "auth-service",
    "todo-env": "todo-service"
}


def run_command(cmd, timeout=None):
    """Ejecuta un comando y devuelve su salida estándar,
    error y el código de retorno.
    """
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode()
        return stdout.strip(), "TimeoutExpired", -1


def contains_url(text):
    """revisa si en la salida aparece una URL"""
    return bool(re.search(r"http[s]?://[^\s]+", text))


def is_pod_ready(label, retries=10, delay=3):
    """reintenta varias veces hasta que un pod con esa etiqueta esté ready."""
    for _ in range(retries):
        out, _, _ = run_command([
            "kubectl", "get", "pods", "-l", f"app={label}",
            "-o", "jsonpath={.items[0].status.containerStatuses[0].ready}"
        ])
        if out == "true":
            return True
        time.sleep(delay)
    return False


def is_exist_pod(label, retries=10, delay=3):
    """Verifica que ya no exista ningún pod con la etiqueta indicada."""
    for _ in range(retries):
        out, _, _ = run_command([
            "kubectl", "get", "pods", "-l", f"app={label}",
            "-o", "jsonpath={.items}"
        ])
        if out.strip() == "[]":
            return True
        time.sleep(delay)
    return False


@pytest.mark.order(1)
@pytest.mark.parametrize("env_name", ["db-env", "auth-env", "todo-env"])
def test_deploy_service(env_name):
    """
    Verifica que el script de despliegue muestre la URL al exponer el servicio
    """
    out, _, code = run_command(
        ["python3", ORCHESTRATOR_SCRIPT, "deploy_service", env_name],
        timeout=20
    )  # más tiempo por el minikube service para que muestra la url

    assert code in [0, -1]
    assert contains_url(
        out)


@pytest.mark.order(2)
@pytest.mark.parametrize("env_name", ["db-env", "auth-env", "todo-env"])
def test_pods_ready(env_name):
    """
    Verifica que el pod quede en estado ready tras desplegar
    """
    label = ENV_LABEL_MAP[env_name]
    assert is_pod_ready(
        label)


@pytest.mark.order(3)
@pytest.mark.parametrize("env_name", ["db-env", "auth-env", "todo-env"])
def test_delete_pods(env_name):
    """
    Verifica que se elimina el servicio y desaparecen los pods
    """
    out, err, code = run_command(
        ["python3", ORCHESTRATOR_SCRIPT, "delete_service", env_name]
    )
    assert code == 0
    label = ENV_LABEL_MAP[env_name]
    assert is_exist_pod(
        label)
