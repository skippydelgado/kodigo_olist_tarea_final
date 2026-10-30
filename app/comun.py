"""Funciones compartidas por las páginas de la app."""
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

CARPETA = Path(__file__).resolve().parent
DATOS = CARPETA / "datos"


def url_api():
    """URL de la API desde st.secrets; si no hay secrets (por ejemplo, en local), usa la variable de entorno o nada."""
    try:
        url = st.secrets.get("API_URL", "")
    except Exception:  # no existe .streamlit/secrets.toml
        url = ""
    if not url:
        import os
        url = os.environ.get("API_URL", "")
    return url.rstrip("/")


@st.cache_data
def leer_csv(nombre, **kwargs):
    ruta = DATOS / nombre
    if not ruta.exists():
        return None
    return pd.read_csv(ruta, **kwargs)


def llamar_api(metodo, ruta, json=None, timeout=75):
    """Llama a la API y devuelve (datos, error). Nunca lanza excepciones a la interfaz."""
    base = url_api()
    if not base:
        return None, "La URL de la API no está configurada. Agréguela en los *secrets* de la app como `API_URL`."
    try:
        if metodo == "GET":
            r = requests.get(base + ruta, timeout=timeout)
        else:
            r = requests.post(base + ruta, json=json, timeout=timeout)
    except requests.exceptions.Timeout:
        return None, ("La API no respondió a tiempo. Render apaga los servicios gratuitos sin visitas y "
                      "la primera consulta puede tardar hasta un minuto: intente de nuevo en unos segundos.")
    except requests.exceptions.ConnectionError:
        return None, "No se pudo conectar con la API. Revise que el servicio de Render esté activo y que la URL sea correcta."
    except Exception as e:  # cualquier otro problema de red
        return None, f"No se pudo consultar la API ({type(e).__name__})."
    if r.status_code == 422:
        try:
            detalles = r.json().get("detail", [])
            campos = ", ".join(f"`{d['loc'][-1]}`: {d['msg']}" for d in detalles)
        except Exception:
            campos = r.text[:300]
        return None, f"La API rechazó los datos (422). Revise: {campos}"
    if r.status_code != 200:
        return None, f"La API respondió con un error ({r.status_code}). Intente de nuevo en unos segundos."
    try:
        return r.json(), None
    except ValueError:
        return None, "La API respondió algo que no es JSON. ¿La URL apunta a la API correcta?"
