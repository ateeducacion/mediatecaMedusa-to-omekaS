# Make sure CAS_login.py is in the same directory or in your Python path
from .common.CAS_login import cas_login

# Ejemplo de cómo se usaría la función
if __name__ == "__main__":
    target_url = "https://www3.gobiernodecanarias.org/medusa/mediateca/pruebas/wp-admin/export.php"
    username = "USERNAME"
    password = "PASSWORD"
    session = cas_login(target_url, username, password)

    params = {
        'download': 'true',
        'content': 'all'  # opciones: all, posts, pages, attachment
    }

    # Ahora puedes usar 'session' para realizar otras solicitudes autenticadas
    # Por ejemplo: response = session.get(otra_url)
    response = session.get(target_url,params=params)
    # Guarda el resultado como archivo XML
    with open('export.xml', 'wb') as f:
        f.write(response.content)
    
    print(response.text)
