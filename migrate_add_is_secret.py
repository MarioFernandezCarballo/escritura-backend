"""
Script de migración para agregar el campo is_secret a la tabla blog_post
Este script debe ejecutarse UNA SOLA VEZ después de actualizar el modelo
"""

import sqlite3
import os

def migrate_database():
    # Buscar el archivo de base de datos
    db_paths = [
        'instance/app.db',
        'app.db',
        '../instance/app.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("No se encontró el archivo de base de datos. Posibles ubicaciones:")
        for path in db_paths:
            print(f"  - {path}")
        return False
    
    print(f"Usando base de datos: {db_path}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(blog_post)")
        columns = [column[1] for column in cursor.fetchall()]
        
        changes_made = False
        
        if 'is_secret' not in columns:
            # Agregar la columna is_secret con valor por defecto False
            cursor.execute("ALTER TABLE blog_post ADD COLUMN is_secret BOOLEAN DEFAULT 0 NOT NULL")
            print("Columna 'is_secret' agregada exitosamente")
            changes_made = True
        else:
            print("La columna 'is_secret' ya existe")
        
        if 'secret_token' not in columns:
            # Agregar la columna secret_token
            cursor.execute("ALTER TABLE blog_post ADD COLUMN secret_token VARCHAR(32) UNIQUE")
            print("Columna 'secret_token' agregada exitosamente")
            changes_made = True
        else:
            print("La columna 'secret_token' ya existe")
        
        if not changes_made:
            print("Todas las columnas ya existen en la tabla blog_post")
            conn.close()
            return True
        
        # Verificar cuántos posts existen
        cursor.execute("SELECT COUNT(*) FROM blog_post")
        post_count = cursor.fetchone()[0]
        
        print(f"Se actualizaron {post_count} posts existentes")
        print("Todos los posts existentes mantienen is_secret = False y secret_token = NULL")
        
        # Confirmar los cambios
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("Iniciando migración para agregar campo is_secret...")
    success = migrate_database()
    
    if success:
        print("✅ Migración completada exitosamente")
        print("Ahora puedes reiniciar tu aplicación Flask")
    else:
        print("❌ La migración falló")
        print("Por favor, revisa los errores y vuelve a intentar")
