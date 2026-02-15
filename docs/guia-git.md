# Guía de Uso de Git - SCA-EMPX

## Descripción

Esta guía describe cómo usar **Git** en el proyecto **Sistema de Control de Acceso Físico (SCA-EMPX)** para STI S.A.S.: flujo de trabajo diario, ramas, commits, sincronización con el remoto, **manejo de ambientes (dev, UAT, producción)** y buenas prácticas.

**Audiencia**: Desarrolladores, líder de proyecto, cualquier persona que contribuya al repositorio.

---

## Requisitos previos

- **Git** instalado en tu máquina.  
  - Windows: [git-scm.com](https://git-scm.com/) o `winget install Git.Git`  
  - Verificar: `git --version`
- Acceso al repositorio (clone con HTTPS o SSH según lo definido por el equipo).

---

## 1. Configuración inicial (una vez)

### Identidad

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@sti.com.co"
```

### Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO> SCA-EMPX
cd SCA-EMPX
```

Si ya tienes el repo clonado, solo asegúrate de estar en la raíz del proyecto al ejecutar los comandos.

---

## 2. Flujo de trabajo diario

### Ver estado

```bash
git status
```

Muestra archivos modificados, nuevos o eliminados y en qué rama estás.

### Ver diferencias

```bash
# Cambios en archivos aún no añadidos
git diff

# Cambios ya preparados (staged)
git diff --staged
```

### Añadir cambios al área de preparación (staging)

```bash
# Un archivo concreto
git add docs/guia-git.md

# Todos los archivos modificados
git add .

# Por patrón (ej. solo .md en docs)
git add docs/*.md
```

### Hacer commit

```bash
git commit -m "Descripción breve y clara del cambio"
```

Ejemplos de mensajes:

- `docs: añadir guía de uso de Git`
- `fix: corregir validación de ingreso en torniquete`
- `feat(api): endpoint de listado de visitantes`

### Enviar cambios al remoto

```bash
# Primera vez en la rama (crear rama remota con el mismo nombre)
git push -u origin <nombre-rama>

# Siguientes veces en la misma rama
git push
```

### Traer cambios del remoto

```bash
# Actualizar la rama actual con los cambios del remoto
git pull
```

Equivale a `git fetch` + `git merge`. Si trabajas con ramas propias, a menudo querrás:

```bash
git fetch origin
git merge origin/main
```

(o `origin/master` según el nombre de la rama principal en tu repo).

---

## 3. Ramas

### Ver ramas

```bash
# Locales
git branch

# Locales y remotas
git branch -a
```

### Crear y cambiar de rama

```bash
# Crear y cambiar en un paso
git checkout -b feature/nombre-descriptivo

# Solo cambiar a una rama existente
git checkout main
```

En Git reciente también puedes usar:

```bash
git switch -c feature/nombre-descriptivo   # crear y cambiar
git switch main                            # cambiar a main
```

### Buenas prácticas con ramas

- **main** (o **master**): rama principal estable; no hacer commits directos si el equipo usa flujo con merge/PR.
- **feature/xxx**: nueva funcionalidad (ej. `feature/registro-visitantes`).
- **fix/xxx**: corrección de un bug (ej. `fix/validacion-facial`).
- **docs/xxx**: solo documentación (ej. `docs/guia-git`).

Convención recomendada: nombres en minúsculas, separados por guiones, sin espacios.

### Integrar una rama en main

Desde la rama que quieres integrar (por ejemplo `feature/mi-feature`):

1. Asegurarte de que está al día con `main`:
   ```bash
   git checkout main
   git pull
   git checkout feature/mi-feature
   git merge main
   ```
2. Resolver conflictos si los hay, luego:
   ```bash
   git add .
   git commit -m "merge main en feature/mi-feature"
   ```
3. Subir la rama y, si el equipo lo usa, abrir un **Pull Request** o **Merge Request** hacia `main` en Azure DevOps / GitHub / GitLab.

---

## 4. Manejo de ambientes (dev, UAT, producción)

En el proyecto se distinguen tres ambientes. Cada uno suele asociarse a una rama (o a un despliegue automático desde esa rama):

| Ambiente      | Rama típica | Uso                                                                                      |
|---------------|-------------|------------------------------------------------------------------------------------------|
| **Desarrollo**| `develop`   | Donde se integran las ramas `feature/` y `fix/`. Pruebas locales e integración continua. |
| **UAT**       | `uat`       | Entorno de pruebas de aceptación (usuarios/QA). Estable antes de producción.             |
| **Producción**| `main`      | Código en vivo. Solo lo que pasó UAT y está aprobado.                                    |

### Flujo entre ambientes

El código avanza en un solo sentido:

```
feature/xxx  →  develop  →  uat  →  main (producción)
```

1. **Desarrollo**: Las ramas `feature/` y `fix/` se fusionan en `develop` (vía PR o merge). El ambiente **dev** se despliega desde `develop`.
2. **UAT**: Cuando `develop` está listo para pruebas de aceptación, se lleva a `uat` (merge o PR de `develop` → `uat`). El ambiente **UAT** se despliega desde `uat`.
3. **Producción**: Cuando UAT está aprobado, se lleva a `main` (merge o PR de `uat` → `main`). El ambiente **producción** se despliega desde `main`.

### Comandos útiles por ambiente

**Actualizar tu rama local con el ambiente de desarrollo:**

```bash
git fetch origin
git checkout develop
git pull origin develop
```

**Preparar UAT (fusionar develop en uat):**

```bash
git checkout uat
git pull origin uat
git merge develop
# Resolver conflictos si los hay
git push origin uat
```

**Preparar producción (fusionar uat en main):**

```bash
git checkout main
git pull origin main
git merge uat
# Resolver conflictos si los hay
git push origin main
```

Quién ejecuta estos merges (desarrollador, líder, DevOps) y si se usa solo PR depende de cómo lo defina el equipo.

### Crear las ramas de ambiente (solo una vez)

Si el repositorio es nuevo y aún no existen `develop` ni `uat`:

```bash
# Crear develop desde main
git checkout main
git pull origin main
git checkout -b develop
git push -u origin develop

# Crear uat desde main (o desde develop)
git checkout main
git checkout -b uat
git push -u origin uat
```

A partir de ahí, `develop` y `uat` se actualizan según el flujo anterior.

### Configuración por ambiente

- **No** versionar archivos con secretos ni datos reales (`.env`, `appsettings.Production.json` con conexiones, etc.).
- Usar `.env.example` o plantillas (por ejemplo `config.dev.json.example`) con variables sin valores sensibles.
- Cada ambiente (dev, UAT, producción) tiene su propia configuración en el servidor o en variables de entorno (Azure, pipeline, etc.), no en el repo.

Así se evita mezclar credenciales de producción con desarrollo y se mantiene el mismo código con distinta configuración por ambiente.

---

## 5. Deshacer cambios

### Descartar cambios en un archivo (sin commit)

```bash
git checkout -- nombre-archivo
# o
git restore nombre-archivo
```

### Quitar un archivo del staging (sin borrar cambios en disco)

```bash
git reset HEAD nombre-archivo
# o
git restore --staged nombre-archivo
```

### Deshacer el último commit (manteniendo los cambios)

```bash
git reset --soft HEAD~1
```

Los cambios quedan en staging; puedes editarlos y hacer un nuevo commit.

### Deshacer el último commit (descartando cambios)

```bash
git reset --hard HEAD~1
```

**Cuidado**: los cambios se pierden. Usar solo si estás seguro.

---

## 6. Sincronización con el remoto

### Ver remotos

```bash
git remote -v
```

### Descargar cambios sin fusionar

```bash
git fetch origin
```

Luego puedes inspeccionar con `git branch -a`, `git log origin/main`, etc., y fusionar cuando quieras.

### Actualizar rama local con la remota

En la rama que quieras actualizar (por ejemplo `main`):

```bash
git pull origin main
```

### Subir una rama nueva al remoto

```bash
git push -u origin nombre-rama
```

---

## 7. Historial y referencias

### Ver historial de commits

```bash
# Resumido
git log --oneline

# Con gráfico de ramas
git log --oneline --graph --all

# Últimos N commits
git log -5 --oneline
```

### Ver un archivo en una versión anterior

```bash
git show <commit-hash>:ruta/al/archivo
```

---

## 8. Archivos ignorados (.gitignore)

El proyecto usa un `.gitignore` para no versionar:

- Entornos virtuales (`venv/`, `.venv/`)
- Archivos de IDE y sistema
- Binarios, cachés, etc.

Para no trackear un archivo que ya estaba en el repo:

```bash
git rm --cached nombre-archivo
git commit -m "Dejar de trackear nombre-archivo"
```

Añade ese archivo o patrón a `.gitignore` para que no vuelva a aparecer.

---

## 9. Resumen de comandos frecuentes

| Acción              | Comando |
|---------------------|--------|
| Ver estado          | `git status` |
| Añadir archivos     | `git add .` o `git add archivo` |
| Commit              | `git commit -m "mensaje"` |
| Subir cambios       | `git push` |
| Traer cambios       | `git pull` |
| Crear rama          | `git checkout -b feature/nombre` |
| Cambiar rama        | `git checkout main` |
| Ver ramas           | `git branch -a` |
| Ver historial       | `git log --oneline` |
| Descartar cambios   | `git restore archivo` |
| Ambientes           | `develop` → dev, `uat` → UAT, `main` → producción |

---

## 10. Integración con Azure DevOps

Si el repositorio está en **Azure DevOps**:

- La URL de clone suele ser: `https://dev.azure.com/<org>/<proyecto>/_git/<repo>` o con SSH.
- Las **Pull Requests** se abren desde la web: *Repos → Branches → Create pull request*.
- Es recomendable que `main` esté protegida y que los cambios entren vía PR y revisión de código.

Para más detalle sobre documentación y backlog en Azure DevOps, consultar la documentación interna del equipo o las guías específicas si están disponibles en el repositorio.

---

## 11. Buenas prácticas en el proyecto

1. **Commits atómicos**: Un commit = un cambio lógico (una corrección, una feature pequeña, una doc).
2. **Mensajes claros**: Empezar con verbo en imperativo y, si se usa, prefijo (`docs:`, `fix:`, `feat:`).
3. **Trabajar por ramas**: No desarrollar directamente en `main`; usar `feature/` o `fix/`.
4. **Actualizar antes de push**: Hacer `git pull` (o `fetch` + `merge`) antes de `git push` para evitar rechazos.
5. **No subir secretos**: Nunca commitear contraseñas, API keys o archivos de entorno con datos reales; usar variables de entorno o gestores de secretos.

---

**Documento**: Guía de Uso de Git  
**Versión**: 1.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
