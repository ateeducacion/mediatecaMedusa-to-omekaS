# Update Users CAS Settings Script

## Descripción

Este script configura los usuarios de Omeka S para que puedan acceder correctamente al panel de administración mediante CAS (Central Authentication Service). Realiza dos acciones por usuario:

1. **Registra al usuario en la tabla `cas_user`** con la tupla `(user_name, user_id)`, asumiendo que el nombre de usuario de Omeka coincide con el nombre de usuario de CAS.
2. **Establece el ajuste de usuario `default_resource_template`** al valor indicado mediante `--resource-template-id`.

## Uso

### Sintaxis básica

```bash
php scripts/update_users_cas_settings.php --resource-template-id <id> [--user-id <id>] [--omeka-path <path>]
```

### Parámetros

| Parámetro | Requerido | Descripción |
|---|---|---|
| `--resource-template-id` | Sí | ID de la plantilla de recurso a establecer como predeterminada para los usuarios |
| `--user-id` | No | ID del usuario a procesar. Si no se indica, se procesan **todos** los usuarios |
| `--omeka-path` | No | Ruta a la instalación de Omeka S. Por defecto: `/var/www/html` |

### Ejemplos

#### Configurar un usuario concreto

```bash
php scripts/update_users_cas_settings.php --resource-template-id 3 --user-id 42
```

#### Configurar todos los usuarios (requiere confirmación interactiva)

```bash
php scripts/update_users_cas_settings.php --resource-template-id 3
```

El script pedirá escribir `CHANGE ALL` para confirmar antes de modificar todos los usuarios.

#### Especificar una ruta personalizada de Omeka

```bash
php scripts/update_users_cas_settings.php --resource-template-id 3 --user-id 42 --omeka-path /home/user/omeka-s
```

## Comportamiento detallado

### Tabla `cas_user`

- Si el usuario **no tiene** entrada en `cas_user`, se crea un nuevo registro `(user_name, user_id)`.
- Si el usuario **ya tiene** entrada pero con un `user_name` diferente, se actualiza al nombre de usuario actual de Omeka.
- Si el usuario ya tiene la entrada correcta, no se realiza ningún cambio.

### Ajuste `default_resource_template`

- Se establece (o sobreescribe) el ajuste de usuario `default_resource_template` con el ID de plantilla indicado.
- Usa el servicio `Omeka\Settings\User` para garantizar la persistencia correcta.

## Salida de ejemplo

```
===========================================
Update Users CAS Settings Script
Version: 1.0.0
===========================================
Resource template ID : 3
Target user ID       : ALL
Omeka path           : /var/www/html
-------------------------------------------

========================================
WARNING: You are about to update ALL users!
========================================
Type 'CHANGE ALL' to confirm (case sensitive): CHANGE ALL
Confirmation received. Proceeding with all users...

Initializing Omeka S application...
Using admin user for API operations
-------------------------------------------
Validating resource template ID 3...
Resource template ID 3 found.
-------------------------------------------
Retrieving all users from database...
Found 5 user(s) to process.
-------------------------------------------

[1/5] Processing user ID: 1 (name: admin)
  [CAS] Checking cas_user entry for user ID 1 (username: admin)...
  [CAS] Created cas_user entry: user_name='admin', user_id=1.
  [Settings] Setting default_resource_template=3 for user 1...
  [Settings] default_resource_template set to 3.
  ✓ User 1 updated successfully

[2/5] Processing user ID: 2 (name: ceipejemplo)
  [CAS] Checking cas_user entry for user ID 2 (username: ceipejemplo)...
  [CAS] Entry already exists with correct username. No update needed.
  [Settings] Setting default_resource_template=3 for user 2...
  [Settings] default_resource_template set to 3.
  ✓ User 2 updated successfully

...

==========================================
SUMMARY
==========================================
Total users processed : 5
Successful            : 5
Failed                : 0

Script completed.
```

## Requisitos

- PHP CLI
- Acceso a la instalación de Omeka S
- Usuario administrador en Omeka S (ID 1)
- Módulo CAS instalado en Omeka S (tabla `cas_user` existente en la base de datos)
- Permisos de lectura/escritura en la base de datos de Omeka

## Notas

- El script asume que el `name` del usuario en Omeka coincide exactamente con el nombre de usuario en CAS.
- El código de salida es `0` si todos los usuarios se procesaron sin errores, `1` si alguno falló.
- El usuario administrador (ID 1) se usa internamente para las operaciones de API pero también es procesado como cualquier otro usuario.

## Autor

ATE - Área de Tecnología Educativa

## Fecha

2026-03-17
