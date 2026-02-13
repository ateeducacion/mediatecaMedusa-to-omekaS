# Hoja de Ruta - Migración Mediateca Medusa a Omeka S

## 1. Configuración Inicial

### Módulos Requeridos

| Módulo | Versión | Fuente | Notas |
|--------|---------|--------|-------|
| Advanced Resource Template | - | Repositorio oficial Omeka | |
| Bulk Import | 3.4.59 | Repositorio oficial Omeka | **Debe ser esta versión exacta** (versiones superiores presentan problemas) |
| CAS | 0.6.3 | [GitHub ATE](https://github.com/ateeducacion/omeka-s-CAS) | Incluye modificación de `cas_logout`, solicitada por CAUCE |
| Common | - | Repositorio oficial Omeka | |
| Custom Vocab | - | Repositorio oficial Omeka | |
| Disk Quota | - | Repositorio oficial Omeka | |
| Easy Admin | - | Repositorio oficial Omeka | |
| GlobalLandingPage | - | Repositorio oficial Omeka | |
| Impersonate | - | Repositorio oficial Omeka | |
| Isolated Sites | - | Repositorio oficial Omeka | |
| ThreeDViewer | 1.0.5 | Repositorio oficial Omeka | |
| HelpAssistant | - | Repositorio oficial Omeka | |
| Block Plus | - | Repositorio oficial Omeka | |

### Tema

- **Freedom ATE**: [https://github.com/ateeducacion/omeka-s-theme-freedom-ate](https://github.com/ateeducacion/omeka-s-theme-freedom-ate)

### Requisitos del Servidor

### Modulos php
   xml, xmlreader, xsl

#### Políticas de ImageMagick

Configurar en el archivo de políticas de ImageMagick:

```xml
<!-- Denegar ZIP -->
<policy domain="coder" rights="none" pattern="ZIP" />

<!-- Permitir EPS -->
<policy domain="coder" rights="read|write" pattern="EPS" />

<!-- Permitir MP4 y MOV -->
<policy domain="coder" rights="read|write" pattern="MP4" />
<policy domain="coder" rights="read|write" pattern="MOV" />
```

#### Software adicional

- **ffmpeg** instalado

---

## 2. Pasos para la Migración de Información

### 2.1. Fuera del servidor

1. **Preparar CSV de traspaso** con el formato:
   ```
   name,url,slug,editor
   ```

2. **Preparar API Keys** del servidor Omeka-S

3. **Ejecutar comando de migración**:

   Configurar entorno virtual:
   ```bash
   # PowerShell (Windows)
   setup_venv.ps1

   # macOS/Linux
   source setup_venv.sh
   ```

   Ejecutar migración:
   ```bash
   python main.py \
       --config migration_config.json \
       --omeka-url [host]/api \
       --key-identity hX2u9b3JvlztF5fh0sibuJk8evWTe6MV \
       --key-credential YdXCg8Ca0iS77puYEaMo5U8Qj4riPfgV \
       --wp-username admincauce \
       --csv example_channels.csv \
       --output-file migracion_XXX.json
   ```

4. **Ejecutar limpieza de ficheros XML**:
   - `limpieza_xml.sh` (Linux/macOS)
   - `limpieza_xml.ps1` (Windows)

### 2.2. En el servidor Omeka-S

1. **Comprobar** trabajos de Bulk Import

2. **Comprobar** sitios y usuarios

3. **Ejecutar script de preparación del servidor**:
   ```bash
   wget https://github.com/ateeducacion/mediatecaMedusa-to-omekaS/raw/refs/heads/main/scripts/setup_host.sh
   bash setup_host.sh
   ```

4. **Transferir al servidor**:
   - Archivos XML de canales descargados
   - Archivo `migracion_XXX.json`

5. **Ejecutar migración** (en directorio `scripts`):
   ```bash
   php run_migration_tasks.php \
       --input-file ../files/import/pruebas_cauce.json \
       --output-file ./scripts/output.json \
       --delete-tasks \
       --config-site-file default_site_conf.json \
       --default-nav \
       --base-url https://www.gobiernodecanarias.org/medusa/mediateca
   ```

---

## 3. Ajuste Inicial de Datos

### Política de Item-Sets

- Solo se migran los item-sets que contienen algún item (los vacíos se eliminan).

---

## 4. Configuración de Portada

- [ ] Indicar sitios destacados
- [ ] Preparar páginas de condiciones de uso y/o términos de servicio

---

## 5. Permisos de Usuario

- [ ] Obtener lista de directores para el alta de usuarios

---

## 6. Comunicación

- [ ] Preparar correo a centros para informar del cambio de plataforma
  - Incluir posibilidad de rescindir el servicio

---

## 7. Tareas Pendientes

- [ ] Refinar plantilla de recurso creada

