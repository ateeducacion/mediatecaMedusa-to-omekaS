# Set Primary Thumbnail Media Script

## Descripción

Este script actualiza el medio principal de los items en Omeka S para usar el primer medio que contenga 'thumb' en su campo `source`. Esto es útil cuando los items tienen medios thumbnail pero Omeka está mostrando un medio diferente como vista previa.

## Funcionalidad

El script:
1. Busca todos los items (o solo los de un site específico si se indica)
2. Para cada item, busca el primer medio cuyo campo `source` contenga 'thumb' (case-insensitive)
3. Si encuentra un medio thumbnail y no es ya el medio principal, actualiza el item para establecerlo como medio principal
4. Muestra estadísticas del proceso al finalizar

## Uso

### Sintaxis básica

```bash
php scripts/set_primary_thumbnail_media.php [--site-id <site_id>] [--omeka-path <path>]
```

### Parámetros

- `--site-id` (Opcional): ID del site del cual procesar los items. Si no se proporciona, procesa items de todos los sites.
- `--omeka-path` (Opcional): Ruta a la instalación de Omeka S. Por defecto: `/var/www/html`

### Ejemplos

#### Procesar todos los items de todos los sites

```bash
php scripts/set_primary_thumbnail_media.php
```

#### Procesar solo los items del site con ID 5

```bash
php scripts/set_primary_thumbnail_media.php --site-id 5
```

#### Especificar una ruta personalizada de Omeka

```bash
php scripts/set_primary_thumbnail_media.php --omeka-path /home/user/omeka-s
```

#### Combinar parámetros

```bash
php scripts/set_primary_thumbnail_media.php --site-id 10 --omeka-path /var/www/omeka
```

## Salida

El script muestra:

- Información de inicialización
- Progreso de procesamiento de cada item
- Acciones realizadas (actualizado, omitido, error)
- Estadísticas finales:
  - Total de items procesados
  - Items actualizados
  - Items omitidos (sin medios, sin thumbnail, o ya configurado correctamente)
  - Errores encontrados

### Ejemplo de salida

```
===========================================
Set Primary Thumbnail Media Script
Version: 1.0.0
===========================================
Processing items from site ID: 5
Omeka path: /var/www/html
-------------------------------------------
Initializing Omeka S application...
Using admin user for API operations
-------------------------------------------
Total items to process: 150
-------------------------------------------
[1/150] Item ID 1234: Updated primary media to thumbnail (Media ID 5678)
[2/150] Item ID 1235: Thumbnail media (ID 5679) is already primary, skipping
[3/150] Item ID 1236: No thumbnail media found, skipping
...
===========================================
Process completed!
-------------------------------------------
Total items processed: 150
Items updated: 45
Items skipped: 105
Errors: 0
===========================================
```

## Requisitos

- PHP CLI
- Acceso a la instalación de Omeka S
- Usuario administrador en Omeka S (ID 1)
- Permisos de lectura/escritura en la base de datos de Omeka

## Notas

- El script procesa items en lotes de 100 para evitar problemas de memoria
- Solo actualiza items que tengan medios con 'thumb' en el source
- No modifica items que ya tengan el thumbnail como medio principal
- Usa la API de Omeka con permisos de administrador
- El campo `source` se busca con coincidencia parcial case-insensitive (ej: 'thumb', 'Thumb', 'thumbnail', etc.)

## Autor

ATE - Área de Tecnología Educativa

## Fecha

2026-02-13
