# Report Disk Usage Script

## Descripción

Este script genera dos CSV con el espacio en disco que ocupa actualmente cada usuario y cada site de Omeka S, junto con su cuota de disco vigente (`diskquota_user_quota` / `diskquota_site_quota`). Sirve como punto de partida para recalcular las cuotas en función del uso real: se editan los CSV y se aplican con [update_disk_quota.php](README_update_disk_quota.md).

El script es de solo lectura: no modifica ningún ajuste.

## Uso

```bash
php scripts/report_disk_usage.php [--users-output <users.csv>] [--sites-output <sites.csv>] [--omeka-path <path>]
```

### Parámetros

| Parámetro | Requerido | Descripción |
|---|---|---|
| `--users-output` | No | CSV de salida de usuarios (por defecto: `users_disk_usage.csv`) |
| `--sites-output` | No | CSV de salida de sites (por defecto: `sites_disk_usage.csv`) |
| `--omeka-path` | No | Ruta a la instalación de Omeka S (por defecto: `/var/www/html`) |

### Ejemplos

```bash
php scripts/report_disk_usage.php
```

#### Con Docker

```bash
docker exec -it omeka-s-docker-omekas-1 php scripts/report_disk_usage.php \
  --users-output /tmp/users_disk_usage.csv \
  --sites-output /tmp/sites_disk_usage.csv

docker cp omeka-s-docker-omekas-1:/tmp/users_disk_usage.csv .
docker cp omeka-s-docker-omekas-1:/tmp/sites_disk_usage.csv .
```

## Cálculo del espacio ocupado

Se replica exactamente el cálculo que hace el módulo DiskQuota (`DiskQuota\Service\DiskQuotaManager`) al comprobar las cuotas, sumando `media.size` de los medios con fichero original (`has_original = 1`):

- **Usuario**: medios cuyo propietario es el usuario.
- **Site**: medios de los ítems asignados al site (`item_site`) **más** medios de los ítems que pertenecen a colecciones asignadas al site (`site_item_set`). Un ítem accesible por ambas vías se cuenta dos veces, igual que hace el módulo.

## Cuota vigente

- Si el usuario/site tiene el ajuste propio, se usa ese valor (`quota_source` = `user` / `site`).
- Si no, se usa el valor global `diskquota_default_user_quota` / `diskquota_default_site_quota` (o 500 MB / 1000 MB si tampoco existe), con `quota_source` = `default`.
- Las cuotas están en **MB**. Un valor `<= 0` significa ilimitada (y `usage_percent` queda vacío).

## Formato del CSV de usuarios

```csv
user_id,email,name,role,is_active,used_bytes,used_mb,diskquota_user_quota,quota_source,usage_percent
2,profe@example.com,"Profe Ejemplo",editor,1,367001600,350,500,default,70
```

## Formato del CSV de sites

```csv
site_id,slug,title,owner_email,used_bytes,used_mb,diskquota_site_quota,quota_source,usage_percent
10,ceipejemplo,"CEIP Ejemplo",profe@example.com,1258291200,1200,1000,site,120
```

Las columnas `user_id`/`diskquota_user_quota` y `site_id`/`diskquota_site_quota` son las que espera `update_disk_quota.php`, así que basta con editar el valor de la cuota en los CSV y pasarlos con `--users-file` / `--sites-file` (el resto de columnas se ignoran).

## Requisitos

- PHP CLI
- Acceso a la instalación de Omeka S y a su base de datos

## Autor

ATE - Área de Tecnología Educativa

## Fecha

2026-09-21
