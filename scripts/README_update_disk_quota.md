# Update Disk Quota Script

## Descripción

Este script establece la cuota de disco (`diskquota_user_quota` para usuarios, `diskquota_site_quota` para sites) en Omeka S a partir de uno o dos ficheros CSV. Cada fila del CSV lleva su propio valor de cuota, por lo que usuarios o sites distintos pueden recibir cuotas distintas en la misma ejecución. Antes de aplicar ningún cambio, el script muestra cuántos usuarios y/o sites se van a actualizar y pide confirmación explícita.

## Uso

```bash
php scripts/update_disk_quota.php [--users-file <users.csv>] [--sites-file <sites.csv>] [--omeka-path <path>]
```

### Parámetros

| Parámetro | Requerido | Descripción |
|---|---|---|
| `--users-file` | Sí\* | Ruta al CSV con los usuarios a actualizar (columnas `user_id,diskquota_user_quota`) |
| `--sites-file` | Sí\* | Ruta al CSV con los sites a actualizar (columnas `site_id,diskquota_site_quota`) |
| `--omeka-path` | No | Ruta a la instalación de Omeka S (por defecto: `/var/www/html`) |

\* Se debe indicar al menos uno de los dos. Se pueden usar ambos a la vez en la misma ejecución.

### Ejemplos

#### Actualizar cuota de usuarios

```bash
php scripts/update_disk_quota.php --users-file users_quota.csv
```

#### Actualizar cuota de sites

```bash
php scripts/update_disk_quota.php --sites-file sites_quota.csv
```

#### Actualizar usuarios y sites en la misma ejecución

```bash
php scripts/update_disk_quota.php \
  --users-file users_quota.csv \
  --sites-file sites_quota.csv
```

#### Con Docker

```bash
docker exec -it omeka-s-docker-omekas-1 php scripts/update_disk_quota.php \
  --users-file /path/to/users_quota.csv \
  --sites-file /path/to/sites_quota.csv
```

## Formato del CSV de usuarios (`--users-file`)

Debe incluir las columnas `user_id` y `diskquota_user_quota`. El resto de columnas se ignoran.

```csv
user_id,diskquota_user_quota
2,500
3,1000
```

## Formato del CSV de sites (`--sites-file`)

Debe incluir las columnas `site_id` y `diskquota_site_quota`. El resto de columnas se ignoran.

```csv
site_id,diskquota_site_quota
10,1000
11,2000
```

Las filas con valores no numéricos en `user_id`/`diskquota_user_quota` o `site_id`/`diskquota_site_quota` se descartan con un aviso y no se procesan.

## Confirmación

Antes de aplicar cualquier cambio, el script imprime cuántos usuarios y/o sites se van a actualizar y pide escribir `yes` para continuar:

```
-------------------------------------------
SUMMARY OF CHANGES TO APPLY
-------------------------------------------
2 user(s) will have 'diskquota_user_quota' updated
2 site(s) will have 'diskquota_site_quota' updated
-------------------------------------------
Type 'yes' to proceed: yes
Confirmation received. Proceeding...
```

Cualquier otra respuesta cancela la operación sin realizar cambios.

## Salida de ejemplo

```
===========================================
Update Disk Quota Script
Version: 1.0.0
===========================================
Reading users file: users_quota.csv
Reading sites file: sites_quota.csv
-------------------------------------------
SUMMARY OF CHANGES TO APPLY
-------------------------------------------
2 user(s) will have 'diskquota_user_quota' updated
2 site(s) will have 'diskquota_site_quota' updated
-------------------------------------------
Type 'yes' to proceed: yes
Confirmation received. Proceeding...

Initializing Omeka S application...
Using admin user for API operations

Processing 2 user(s)...
========================================

[1/2] Processing user ID: 2 (diskquota_user_quota: 500)
  ✓ User 2 updated successfully

[2/2] Processing user ID: 3 (diskquota_user_quota: 1000)
  ✓ User 3 updated successfully

Processing 2 site(s)...
========================================

[1/2] Processing site ID: 10 (diskquota_site_quota: 1000)
  ✓ Site 10 updated successfully

[2/2] Processing site ID: 11 (diskquota_site_quota: 2000)
  ✓ Site 11 updated successfully

===========================================
SUMMARY
===========================================
Users  - processed: 2, successful: 2, failed: 0
Sites  - processed: 2, successful: 2, failed: 0

Script completed.
```

## Requisitos

- PHP CLI
- Acceso a la instalación de Omeka S
- Usuario administrador en Omeka S (ID 1)
- Permisos de lectura/escritura en la base de datos de Omeka

## Notas

- El identificador de usuario es el `user_id` numérico de Omeka S (no el email), igual que `site_id` se usa para sites en el resto de scripts de este directorio.
- Si un usuario o site no existe, el error se registra y se continúa con el siguiente; el código de salida final es `1` si hubo algún fallo, `0` si todo se procesó correctamente.
- El usuario administrador (ID 1) se usa internamente para las operaciones de API.

## Autor

ATE - Área de Tecnología Educativa

## Fecha

2026-08-27
