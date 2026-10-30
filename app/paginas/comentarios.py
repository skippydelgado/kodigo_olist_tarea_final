import pandas as pd
import streamlit as st

from comun import leer_csv

st.title("¿Qué dicen los comentarios?")
st.caption("Sentimiento de 1,000 comentarios con el modelo preentrenado `cardiffnlp/twitter-xlm-roberta-base-sentiment`, "
           "comparado con las estrellas (1–2 negativo, 3 neutro, 4–5 positivo).")

muestra = leer_csv("sentimiento_muestra.csv")
if muestra is None:
    st.error("No se encontró `datos/sentimiento_muestra.csv`. Genérelo con el notebook (Parte 4).")
    st.stop()

ORDEN = ["negative", "neutral", "positive"]
NOMBRES = {"negative": "negativo", "neutral": "neutro", "positive": "positivo"}
coincide = (muestra["estrellas_grupo"] == muestra["sentimiento"])

c1, c2, c3 = st.columns(3)
c1.metric("Comentarios analizados", f"{len(muestra):,}")
c2.metric("Coincidencia con las estrellas", f"{coincide.mean() * 100:.1f}%")
c3.metric("Desacuerdos", f"{(~coincide).sum():,}")

tabla = pd.crosstab(muestra["estrellas_grupo"], muestra["sentimiento"]).reindex(index=ORDEN, columns=ORDEN, fill_value=0)
pct = (tabla.div(tabla.sum(axis=1), axis=0) * 100).round(1)
tabla.index = [f"estrellas: {NOMBRES[i]}" for i in tabla.index]
tabla.columns = [f"modelo: {NOMBRES[c]}" for c in tabla.columns]
pct.index, pct.columns = tabla.index, tabla.columns

st.subheader("Tabla cruzada")
izq, der = st.columns(2)
izq.caption("Número de comentarios")
izq.dataframe(tabla, width="stretch")
der.caption("% por fila (cómo lee el modelo cada grupo de estrellas)")
der.dataframe(pct.style.format("{:.1f}%").background_gradient(cmap="Blues", axis=None), width="stretch")

temas = leer_csv("temas_comentarios.csv", index_col=0)
if temas is not None:
    st.subheader("Temas que mencionan los clientes (% de comentarios)")
    temas.index = [f"estrellas: {NOMBRES.get(i, i)}" for i in temas.index]
    temas.index.name = None
    st.dataframe(temas.style.format("{:.1f}%").background_gradient(cmap="Oranges", axis=None), width="stretch")

clasificados = leer_csv("desacuerdos_clasificados.csv")
if clasificados is not None:
    st.subheader("Desacuerdos leídos y clasificados")
    st.dataframe(clasificados[["estrellas", "sentimiento_modelo", "confianza", "clasificacion", "comentario", "por_que"]],
                 hide_index=True, width="stretch")

st.subheader("Explorar desacuerdos")
f1, f2 = st.columns(2)
estrellas = f1.multiselect("Estrellas", [1, 2, 3, 4, 5], default=[1, 2, 4, 5])
sentim = f2.multiselect("Sentimiento del modelo", ORDEN, default=ORDEN, format_func=NOMBRES.get)
filtro = (~coincide) & muestra["review_score"].isin(estrellas) & muestra["sentimiento"].isin(sentim)
vista = muestra.loc[filtro, ["review_score", "sentimiento", "confianza", "review_comment_message"]]
st.caption(f"{len(vista)} comentarios")
st.dataframe(vista.rename(columns={"review_score": "estrellas", "review_comment_message": "comentario"}),
             hide_index=True, width="stretch")

st.info("**Qué agrega el texto:** las estrellas dicen *cuánto* molestó la compra; el comentario dice *por qué* "
        "(no llegó, llegó otro producto, defecto, retraso). Con eso cada queja puede ir al equipo responsable. "
        "El texto no se usa en el modelo de riesgo: existe solo después de la entrega.")
