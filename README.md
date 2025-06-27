# PC4

## Prerrequisitos

Antes de empezar, asegúrate de tener instalado y en funcionamiento:
- **Docker** (daemon corriendo):  
  ```bash
  sudo systemctl start docker  # o abre Docker Desktop en macOS/Windows

## Desarrolladores

### Instalación de Git Hooks
En la raíz del proyecto encontrarás el script setup.sh, que debes ejecutar solo la primera vez para configurar los hooks:
```bash
# Desde la carpeta raíz del repo
bash setup.sh
```

Este script hará lo siguiente:

- Marcará los hooks como ejecutables
- Configurará Git para que use .githooks/ como ruta de hooks

### Workflow
#### **1.** Modificar o añadir código

#### **2.** Staging:

```bash
git add <archivo(s)>
```

#### **3.** Commits

 Al hacer git commit, se ejecutará el hook pre-commit que:

- Construye (docker build) los Dockerfiles modificados.

- Valida sintaxis de los docker-compose.*.yaml modificados.

Si alguna validación falla, el commit se detendrá y verás el error.

#### **4.** Pushes

Al hacer git push, el hook pre-push:

- Vuelve a validar todos los docker-compose.*.yaml.

- Intenta construir todos los Dockerfiles trackeados.

Si hay errores (p. ej. daemon detenido o sintaxis inválida), el push se bloquea.