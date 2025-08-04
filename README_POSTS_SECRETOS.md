# Implementación de Posts Secretos

Esta funcionalidad permite crear posts que solo son accesibles mediante enlaces únicos y no aparecen en la lista pública del blog.

## Cambios Realizados

### Backend

1. **Modelo de Base de Datos** (`src/models.py`)
   - Agregado campo `is_secret` a la tabla `BlogPost` (valor por defecto: `False`)
   - Agregado campo `secret_token` a la tabla `BlogPost` (token único para posts secretos)

2. **Schemas** (`src/schemas.py`)
   - Agregado campo `is_secret` a `BlogPostBase`, `BlogPostCreate` y `BlogPost`
   - Agregado campo `secret_token` a `BlogPost`

3. **Rutas** (`src/routes.py`)
   - Nueva ruta `/blog/posts/admin` para obtener TODOS los posts (incluyendo secretos) para administradores
   - Nueva ruta `/secret/<token>` para acceder a posts secretos mediante token único

4. **Lógica de Negocio** (`src/utils.py`)
   - `Post.getAll()`: Filtra posts secretos (solo muestra públicos)
   - `Post.getAllAdmin()`: Muestra TODOS los posts para administradores
   - `Post.get()`: Permite acceso directo a posts por ID (mantiene compatibilidad)
   - `Post.getByToken()`: Obtiene posts secretos mediante token único
   - `Post.generateSecretToken()`: Genera tokens únicos para posts secretos
   - `Post.post()` y `Post.edit()`: Manejan campos `is_secret` y `secret_token`

### Frontend

1. **API** (`util/api.ts`)
   - Agregado campos `is_secret` y `secret_token` a la interfaz `BlogPost`
   - Nuevo hook `useAllBlogPosts()` para administradores
   - Nuevo hook `useSecretPost()` para obtener posts por token

2. **Gestión de Posts** (`app/manage-posts/page.tsx`)
   - Usa `useAllBlogPosts()` para mostrar todos los posts
   - Indicadores visuales para posts secretos
   - Nueva columna "Type" con badges
   - Botón "Copiar enlace" para posts secretos

3. **Creación de Posts** (`app/create-post/page.tsx`)
   - Checkbox para marcar posts como secretos
   - Explicación de la funcionalidad

4. **Edición de Posts** (`app/edit-post/[id]/page.tsx`)
   - Checkbox para cambiar el estado secreto/público
   - Mantiene el estado actual del post

5. **Vista de Posts Secretos** (`app/secret/[token]/page.tsx`)
   - Página dedicada para mostrar posts secretos
   - Banner de contenido exclusivo con enlaces a Telegram y Newsletter
   - Diseño especial para contenido premium

## Migración de Base de Datos

**IMPORTANTE**: Antes de usar esta funcionalidad, ejecuta el script de migración:

```bash
cd mariocarballo-backend
python migrate_add_is_secret.py
```

Este script:
- Agrega la columna `is_secret` a la tabla `blog_post`
- Establece `is_secret = False` para todos los posts existentes
- Es seguro ejecutarlo múltiples veces

## Funcionamiento

### Posts Públicos
- Aparecen en `/blog` (lista pública)
- Aparecen en `/manage-posts` (administración)
- Accesibles por link directo `/blog/[id]`

### Posts Secretos
- **NO** aparecen en `/blog` (lista pública)
- **SÍ** aparecen en `/manage-posts` (administración) con indicador visual
- **SÍ** son accesibles por link directo `/blog/[id]` (mantiene compatibilidad)
- **NUEVA URL SECRETA**: `/secret/[token]` con token único generado automáticamente

### URLs de Acceso

- **Posts Públicos**: `https://tudominio.com/blog/123`
- **Posts Secretos**: `https://tudominio.com/secret/AbC123XyZ456` (token único)

### Indicadores Visuales

En la vista de administración:
- **Posts Públicos**: Badge verde con icono de globo
- **Posts Secretos**: Badge amarillo con icono de candado
- Icono de ojo tachado junto al título de posts secretos
- Botón "Copiar enlace" para obtener la URL secreta

### Banner de Contenido Exclusivo

Los posts secretos muestran un banner especial que incluye:
- Mensaje de contenido exclusivo para miembros de Telegram y suscriptores
- Enlaces directos a Telegram y Newsletter
- Diseño premium con iconos y colores distintivos
- Mensaje de agradecimiento al final del post

## Casos de Uso

1. **Contenido Exclusivo**: Compartir posts solo con personas específicas
2. **Borradores Avanzados**: Posts casi listos pero no públicos
3. **Contenido Premium**: Acceso mediante enlaces especiales
4. **Pruebas**: Probar contenido sin hacerlo público

## Seguridad

- Los posts secretos NO están protegidos por contraseña
- Cualquiera con el link directo puede acceder
- Para mayor seguridad, considera implementar autenticación adicional
