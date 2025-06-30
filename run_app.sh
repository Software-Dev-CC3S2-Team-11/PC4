#!/usr/bin/env bash
set -e


minikube start --driver=docker

echo "Cambiando entorno Docker a Minikube"
eval "$(minikube docker-env)"


echo "Construyendo y cargando imágenes en Minikube"
docker build -t auth-service src/auth_service/
docker build -t todo-service src/todo_service/


echo "Configurando secrets/configmaps"
for ENV in db-env auth-env todo-env; do
    echo "Ejecutando configuración para $ENV"
    python3 src/env_secrets_configmaps.py "$ENV"
done


for SERVICE in db-env auth-env todo-env; do
    echo "Desplegando $SERVICE"
    python3 src/env_orchestrator.py deploy_service "$SERVICE"
done

echo "Todos los servicios han sido desplegados correctamente"
