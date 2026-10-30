"""App de Streamlit · Proyecto final Olist (punto de entrada).

Páginas: Riesgo de un pedido (consulta la API) · Comentarios · Segmentos de vendedores · Ficha del modelo.
La URL de la API se lee de st.secrets["API_URL"] (en Streamlit Cloud: Settings › Secrets).
"""
import streamlit as st

from comun import url_api

st.set_page_config(page_title="Olist · Riesgo de mala reseña", page_icon="📦", layout="wide")

paginas = st.navigation([
    st.Page("paginas/riesgo.py", title="Riesgo de un pedido", icon="⚠️", default=True),
    st.Page("paginas/comentarios.py", title="Comentarios", icon="💬"),
    st.Page("paginas/segmentos.py", title="Segmentos de vendedores", icon="🏪"),
    st.Page("paginas/ficha.py", title="Ficha del modelo", icon="📄"),
])

with st.sidebar:
    st.caption("URL de la API")
    st.code(url_api() or "(sin configurar)", language=None)
    st.caption("Proyecto final AIMLF1 · Ruiz Melissa, Rodrigo y Cesar")

paginas.run()
