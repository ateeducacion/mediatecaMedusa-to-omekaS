# Update Site Settings Script

## Descripción

Este script aplica una configuración común (tema, ajustes de sitio y ajustes de tema) a uno o varios sitios de Omeka S. Puede actuar sobre un conjunto de sitios especificado mediante un CSV o sobre la totalidad de sitios de la instalación. Opcionalmente configura la navegación por defecto con una página de redirección como portada.

## Uso

```bash
php scripts/update_site_settings.php --config-file <config.json> (--sites-file <sites.csv> | --all) [--default-nav] [--base-url <url>] [--omeka-path <path>]
```

### Parámetros

| Parámetro | Requerido | Descripción |
|---|---|---|
| `--config-file` | Sí | Ruta al JSON con la configuración a aplicar |
| `--sites-file` | Sí\* | Ruta al CSV con los sitios a procesar (columna `site_id`) |
| `--all` | Sí\* | Aplicar la configuración a **todos** los sitios (requiere confirmación) |
| `--default-nav` | No | Configurar la navegación por defecto en cada sitio |
| `--base-url` | No | URL base de la instalación de Omeka (necesaria con `--default-nav`, por defecto: `http://localhost:8888`) |
| `--omeka-path` | No | Ruta a la instalación de Omeka S (por defecto: `/var/www/html`) |

\* Se debe indicar exactamente uno de los dos: `--sites-file` o `--all`. Usar ambos a la vez produce un error.

### Ejemplos

#### Aplicar configuración a un conjunto de sitios desde CSV

```bash
php scripts/update_site_settings.php \
  --config-file scripts/default_site_conf.json \
  --sites-file sites.csv
```

#### Aplicar configuración a todos los sitios

```bash
php scripts/update_site_settings.php \
  --config-file scripts/default_site_conf.json \
  --all
```

El script pedirá escribir `CHANGE ALL` para confirmar antes de modificar todos los sitios.

#### Aplicar configuración y configurar navegación por defecto

```bash
php scripts/update_site_settings.php \
  --config-file scripts/default_site_conf.json \
  --sites-file sites.csv \
  --default-nav \
  --base-url http://omeka.example.org
```

#### Con Docker

```bash
docker exec -it omeka-s-docker-omekas-1 php scripts/update_site_settings.php \
  --config-file /path/to/default_site_conf.json \
  --all \
  --default-nav \
  --base-url http://localhost:8888
```

## Formato del archivo de configuración (`--config-file`)

El fichero debe tener la clave raíz `site_data`. El script ignora el resto de claves del JSON (como `site_id`, `timestamp` u otras presentes en ficheros exportados).

```json
{
  "site_data": {
    "site": {
      "theme": "freedom-ate"
    },
    "site_settings": {
      "show_user_bar": "1",
      "search_type": "sitewide",
      "locale": ""
    },
    "theme_settings_freedom-ate": {
      "primary_color": "#464646",
      "browse_layout": "grid",
      "footer_copyright": "<div>© Gobierno de Canarias</div>"
    }
  }
}
```

### Claves reconocidas dentro de `site_data`

| Clave | Descripción |
|---|---|
| `site.theme` | Nombre del tema a activar (`o:theme`) |
| `site_settings` | Objeto con pares clave/valor que se escriben con `Omeka\Settings\Site` |
| `theme_settings_<nombre-tema>` | Objeto con los ajustes del tema; se almacena bajo la clave `theme_settings_<nombre-tema>` en los site settings |

El tema se aplica **antes** que los settings para asegurar que los ajustes de tema se persisten contra el tema correcto.

El fichero `default_site_conf.json` incluido en el repositorio contiene la configuración de referencia del proyecto.

## Formato del CSV de sitios (`--sites-file`)

El CSV debe incluir al menos la columna `site_id`. Las demás columnas se ignoran.

```csv
site_id,name,slug
10,CEIP Ejemplo,ceipejemplo
11,CEIP Otro,ceipotro
```

## Navegación por defecto (`--default-nav`)

Cuando se pasa `--default-nav`, el script realiza las siguientes acciones en cada sitio:

1. Crea (o actualiza) una página con slug `item` y título `Inicio` que contiene un bloque `redirectToUrl` apuntando a `<base-url>/s/<slug-del-sitio>/item`.
2. Establece esa página como portada del sitio (`o:homepage`).
3. Configura la navegación del sitio con dos entradas:
   - La página de redirección (sin etiqueta, usada como portada)
   - Un enlace de tipo `browseItemSets` con etiqueta `Colecciones`

> Si no se proporciona `--base-url` junto con `--default-nav`, se usará `http://localhost:8888` y se mostrará un aviso.

## Salida de ejemplo

```
Reading config file: scripts/default_site_conf.json
Reading sites file: sites.csv
Found 3 site(s) to process
Initializing Omeka S application...
Using admin user for API operations

Processing 3 site(s)...
========================================

[1/3] Processing site ID: 10
  Site: CEIP Ejemplo (slug: ceipejemplo)
    Applying site configuration to site (ID: 10)...
    Setting theme: freedom-ate
    Theme updated and changes persisted
    Applying 3 site settings...
      - Set show_user_bar
      - Set search_type
      - Set locale
    Applying theme settings for theme: freedom-ate
      - Setting: primary_color = "#464646"
      - Setting: browse_layout = "grid"
    Applied 1 theme settings
    Site configuration applied successfully
  ✓ Site updated successfully

...

========================================
SUMMARY
========================================
Total sites processed: 3
Successful: 3
Failed: 0

Script completed.
```

## Requisitos

- PHP CLI
- Acceso a la instalación de Omeka S
- Usuario administrador en Omeka S (ID 1)
- Permisos de lectura/escritura en la base de datos de Omeka

## Notas

- El script usa el usuario administrador (ID 1) para todas las operaciones de API.
- Si un sitio no existe, se registra el error y se continúa con el siguiente.
- Los fallos en la configuración de navegación no interrumpen el proceso: el sitio se cuenta como exitoso si la configuración principal se aplicó correctamente.
- El código de salida siempre es `0`; los errores se registran en la consola con detalle.

## Autor

ATE - Área de Tecnología Educativa

## Fecha

2025-12-16
