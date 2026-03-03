# Instrucciones para el servidor de producción (Azure)

Documento para la persona que administra el servidor donde se despliega SCA-EMPX. El despliegue se hace desde GitLab CI por SSH; el servidor solo debe estar preparado una vez.

---

## 1. Requisitos en la VM de Azure

- Sistema operativo: Linux (Ubuntu 22.04 LTS recomendado).
- Usuario SSH con el que se conectará el pipeline: el mismo que está configurado en GitLab como `PRODUCTION_USER` (por ejemplo `azureuser`).

---

## 2. Instalar Docker y Docker Compose

En el servidor, como usuario con permisos de administrador:

```bash
# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar para que el grupo docker aplique

# Docker Compose (plugin)
sudo apt-get update && sudo apt-get install -y docker-compose-plugin
```

Comprobar:

```bash
docker --version
docker compose version
```

---

## 3. Crear el directorio de la aplicación

```bash
sudo mkdir -p /opt/sca-empx
sudo chown $USER:$USER /opt/sca-empx
cd /opt/sca-empx
```

---

## 4. Tener el archivo `docker-compose.prod.yml` en el servidor

O bien **clonar el repositorio** en `/opt/sca-empx` (y hacer `git pull` cuando se actualice), o bien **copiar solo** el archivo `docker-compose.prod.yml` del repo a `/opt/sca-empx`.

Ejemplo clonando (si tienen acceso al repo):

```bash
cd /opt
sudo rm -rf sca-empx   # solo si ya existía y quieren reemplazar
sudo git clone <URL_DEL_REPOSITORIO> sca-empx
sudo chown -R $USER:$USER sca-empx
cd sca-empx
```

Comprobar que existe:

```bash
ls -la /opt/sca-empx/docker-compose.prod.yml
```

---

## 5. Configurar SSH para que acepte el deploy desde GitLab

El pipeline usa una clave privada guardada en GitLab (`SSH_PRIVATE_KEY`). La **clave pública** correspondiente debe estar en el servidor.

- Quien configure GitLab debe generar un par de claves (o usar una existente) y:
  - Guardar la **clave privada** en GitLab CI/CD → Variables como `SSH_PRIVATE_KEY`.
  - Pasar la **clave pública** al administrador del servidor.

En el servidor, para el usuario con el que se conecta el pipeline (ej. `azureuser`):

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# Pegar la clave pública en authorized_keys (una línea, sin espacios extra)
echo "LA_CLAVE_PUBLICA_QUE_TE_PASARON" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

No debe haber restricciones en `~/.ssh` que impidan el acceso (por ejemplo, que el dueño no sea ese usuario).

---

## 6. Abrir puertos en el servidor / Azure

Asegurar que estén accesibles desde internet (o desde donde deban usar la app):

- **Puerto 80** (HTTP) – frontend.
- **Puerto 8000** (TCP) – backend API (si se expone directamente; si todo va por un proxy, ajustar según corresponda).

En Azure: en el recurso de la VM, abrir en **Networking** (o en el NSG asociado) reglas de entrada para TCP 80 y, si aplica, 8000.

---

## 7. (Opcional) Variables de entorno en producción

Si quieren fijar `SECRET_KEY` u otras variables en el servidor (recomendado para producción), crear en `/opt/sca-empx` un archivo `.env` con el contenido que les indiquen, por ejemplo:

```bash
# /opt/sca-empx/.env
SECRET_KEY=una-clave-secreta-muy-larga-y-aleatoria
DEBUG=false
```

El pipeline ya exporta `DOCKER_REGISTRY`, `DOCKER_USERNAME` y `APP_VERSION`; no hace falta ponerlas en `.env` a menos que quieran valores fijos.

---

## 8. Comprobar que el usuario puede usar Docker sin sudo

Con el usuario con el que se hace el deploy:

```bash
docker ps
docker compose version
```

Si pide contraseña o falla, revisar que el usuario esté en el grupo `docker` (`groups`) y que haya cerrado sesión y vuelto a entrar después de `usermod -aG docker`.

---

## 9. Qué hace el pipeline (solo informativo)

Cuando en GitLab se ejecuta el job de deploy a producción:

1. Se conecta por SSH a este servidor con el usuario configurado.
2. Ejecuta en `/opt/sca-empx`:
   - `docker compose -f docker-compose.prod.yml pull` (descarga las imágenes).
   - `docker compose -f docker-compose.prod.yml up -d` (levanta los contenedores).
   - `docker compose -f docker-compose.prod.yml ps` (lista el estado).

No es necesario que nadie ejecute nada a mano en cada despliegue; solo hay que tener el servidor preparado como en los pasos anteriores.

---

## Resumen rápido para el administrador

1. VM Linux (ej. Ubuntu 22.04) con usuario SSH (ej. `azureuser`).
2. Instalar Docker y Docker Compose plugin.
3. Crear `/opt/sca-empx` y poner ahí `docker-compose.prod.yml` (clonando el repo o copiando el archivo).
4. Añadir la clave pública SSH del deploy en `~/.ssh/authorized_keys` del usuario.
5. Abrir puertos 80 (y 8000 si aplica) en Azure.
6. (Opcional) Crear `.env` en `/opt/sca-empx` con `SECRET_KEY` y demás variables que les indiquen.

Después de esto, los despliegues se hacen desde GitLab; el administrador no tiene que correr comandos en cada release.
