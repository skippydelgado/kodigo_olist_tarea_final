import streamlit as st

from comun import leer_csv

st.title("Segmentos de vendedores")
st.caption("Pregunta abierta (opción 3B): K-Means con k = 4 sobre vendedores con al menos 10 pedidos entregados.")

vendedores = leer_csv("segmentos_vendedores.csv")
perfil = leer_csv("perfil_segmentos.csv")
if vendedores is None or perfil is None:
    st.error("No se encontraron los archivos de segmentos. Genérelos con el notebook (Parte 3).")
    st.stop()

cols = st.columns(len(perfil))
for col, (_, r) in zip(cols, perfil.iterrows()):
    col.metric(r["nombre"], int(r["n_vendedores"]), f"{r['ventas_del_grupo_%']:.1f}% de las ventas",
               delta_color="off", delta_arrow="off", help="Número de vendedores del segmento")

st.subheader("Perfil de cada grupo (medianas)")
tabla = perfil[["nombre", "n_vendedores", "n_pedidos", "ventas_total", "precio_promedio", "flete_relativo",
                "tasa_retraso", "tasa_mala_resena", "n_categorias"]].rename(columns={
    "nombre": "segmento", "n_vendedores": "vendedores", "n_pedidos": "pedidos", "ventas_total": "ventas (R$)",
    "precio_promedio": "ticket (R$)", "flete_relativo": "flete / precio", "tasa_retraso": "tasa de retraso",
    "tasa_mala_resena": "tasa de mala reseña", "n_categorias": "categorías"})
st.dataframe(tabla, hide_index=True, width="stretch")

st.subheader("Acción para cada segmento")
for _, r in perfil.iterrows():
    st.markdown(f"**{r['nombre']}** — {r['accion']}")

st.subheader("Mapa de los grupos (PCA)")
st.scatter_chart(vendedores, x="pca1", y="pca2", color="segmento_nombre", size=20, height=450)
st.caption("Cada punto es un vendedor, proyectado en los 2 componentes principales de las 6 variables escaladas.")

with st.expander("Buscar un vendedor"):
    sid = st.text_input("seller_id (o los primeros caracteres)")
    if sid:
        st.dataframe(vendedores[vendedores["seller_id"].str.startswith(sid.strip())], hide_index=True)
