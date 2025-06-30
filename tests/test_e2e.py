import requests
import pytest
import time
import subprocess

SERVICES = ["db-env", "auth-env", "todo-env"]

LABELS = {
    "db-env": "db",
    "auth-env": "auth-service",
    "todo-env": "todo-service"
}


@pytest.fixture(scope="session", autouse=True)
def deploy_all_services():
    """Crea configmaps y secretos y despliega 
    los servicios al inicio y luego los elimina"""

    # Crea los configmaps y secretos antes del despliegue
    for env in ["db-env", "auth-env", "todo-env"]:
        result = subprocess.run(
            ["python", "src/env_secrets_configmaps.py", env],
            capture_output=True, text=True
        )
        assert result.returncode == 0

    # Despliega los servicios
    for service in SERVICES:
        deploy = subprocess.run(
            ["python", "src/env_orchestrator.py", "deploy_service", service],
            capture_output=True, text=True
        )
        assert deploy.returncode == 0

    # Espera a que los servicios esten listos
    for service in SERVICES:
        label = LABELS[service]
        for i in range(20):
            result = subprocess.run(
                ["kubectl", "get", "pods", "-l", f"app={label}",
                 "-o", "jsonpath={.items[0].status.containerStatuses[0].ready}"],
                capture_output=True, text=True
            )
            if result.stdout.strip() == "true":
                break
            time.sleep(3)
        else:
            subprocess.run(["kubectl", "get", "pods", "-l", f"app={label}"])
            subprocess.run(
                ["kubectl", "describe", "pods", "-l", f"app={label}"])

    yield  # Ejecuta los tests

    # Eliminan los servicios
    for service in SERVICES:
        subprocess.run(
            ["python", "src/env_orchestrator.py", "delete_service", service],
            capture_output=True, text=True
        )


def get_service_url(service_name: str) -> str:
    try:
        result = subprocess.run(
            ["minikube", "service", service_name, "--url"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        pytest.fail(
            f"No se pudo obtener la url para {service_name}")


@pytest.fixture(scope="session")
def auth_token():
    """Registra y loguea al usuario
        devuelve el token
    """
    auth_url = get_service_url("auth-service")

    register_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword"
    }
    requests.post(auth_url + "/auth/register", data=register_data)

    login_data = {
        "username": "testuser",
        "password": "securepassword"
    }
    r = requests.post(auth_url + "/auth/login", data=login_data)
    assert r.status_code == 200
    token = r.json().get("token")
    assert token
    return token


@pytest.mark.order(1)
def test_create_task(auth_token):
    """Crea una tarea"""
    todo_url = get_service_url("todo-service")
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_data = {
        "title": "Mi",
        "description": "Descripción de prueba"
    }

    r = requests.post(todo_url + "/tasks", json=task_data, headers=headers)
    assert r.status_code == 200
    assert r.json().get("message") == "Tarea registrada"


@pytest.mark.order(2)
def test_get_tasks(auth_token):
    """Obtiene las tareas del usuario"""
    todo_url = get_service_url("todo-service")
    headers = {"Authorization": f"Bearer {auth_token}"}

    r = requests.get(todo_url + "/tasks", headers=headers)
    assert r.status_code == 200
    tasks = r.json()
    assert isinstance(tasks, list)
    assert len(tasks) > 0
    assert "title" in tasks[0]
    assert "description" in tasks[0]

    # Guarda la id para las siguientes pruebas
    test_get_tasks.task_id = tasks[0]["id"]


@pytest.mark.order(3)
def test_update_task(auth_token):
    """Actualiza una tarea"""

    todo_url = get_service_url("todo-service")
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Usamos el ID de la prueba anterior
    task_id = getattr(test_get_tasks, "task_id", None)
    assert task_id is not None

    updated_data = {
        "title": "tare actualizada",
        "description": "descripcion"
    }

    r = requests.put(f"{todo_url}/tasks/{task_id}",
                     json=updated_data, headers=headers)
    assert r.status_code == 200
    assert r.json().get("message") == "Tarea actualizada"


@pytest.mark.order(4)
def test_delete_task(auth_token):
    """Elimina una tarea"""
    todo_url = get_service_url("todo-service")
    headers = {"Authorization": f"Bearer {auth_token}"}

    task_id = getattr(test_get_tasks, "task_id", None)
    assert task_id is not None

    r = requests.delete(f"{todo_url}/tasks/{task_id}", headers=headers)
    assert r.status_code == 200
    assert r.json().get("message") == "Tarea eliminada"
