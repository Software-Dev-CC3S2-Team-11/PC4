#!/usr/bin/env bash
# One-time setup: reubicar git hooks hacia .githooks/ and configure Git
set -e

HOOK_DIR=".githooks"

echo "Convirtiendo hooks en ejecutables..."
chmod +x "$HOOK_DIR"/pre-commit "$HOOK_DIR"/pre-push

echo "Configurando Git para usar '$HOOK_DIR' como ruta de hooks..."
git config core.hooksPath "$HOOK_DIR"

echo "!Setup completado! Directoria de Git hooks actualizado: '$HOOK_DIR'."
