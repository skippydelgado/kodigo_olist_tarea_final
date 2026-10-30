import streamlit as st

from comun import CARPETA

ruta = CARPETA / "ficha_modelo.md"
if ruta.exists():
    st.markdown(ruta.read_text(encoding="utf-8"))
else:
    st.error("No se encontró `ficha_modelo.md` en la carpeta de la app. Genérelo con el notebook (Parte 6).")
