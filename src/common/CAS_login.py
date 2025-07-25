#!/usr/bin/env python3

"""
CAS Login

Este script realiza el proceso de inicio de sesión CAS para la URLs proporcionadas y devuelve un objeto requests.Session con la sesión iniciada

Autor: Ernesto Serrano <esercol@gobiernodecanarias.org>
Fecha: 13-13-2023
"""
import requests
import re

def cas_login(target_url, username, password):
    """
    Realiza el proceso de inicio de sesión CAS para la URL proporcionada y devuelve un objeto requests.Session con la sesión iniciada.
    
    Parámetros:
    cas_hostname: El hostname del servidor CAS.
    target_url: La URL del recurso que se desea acceder después del login.
    username: Nombre de usuario para el login.
    password: Contraseña para el login.
    """

    cas_hostname = "www3.gobiernodecanarias.org/educacion/cau_ce"

    session = requests.Session()
    cas_login_url = f"https://{cas_hostname}/cas/login?service={target_url}"
    response = session.get(cas_login_url)

    # Extrae el ticket de CAS
    cas_id = re.search(r'name="execution" value="([^"]*)"', response.text)
    if not cas_id:
        raise Exception("No se pudo obtener el ticket de CAS.")

    cas_id = cas_id.group(1)
    data = {
        "username": username,
        "password": password,
        "execution": cas_id,
        "_eventId": "submit"
    }

    # Realiza el POST para el login
    response = session.post(cas_login_url, data=data, allow_redirects=False)
    if response.status_code != 302:
        raise Exception("Error en el login. Revisa las credenciales y la URL.")

    # Redirige a la URL después del login
    session.get(response.headers.get('Location'), allow_redirects=False)
    return session

