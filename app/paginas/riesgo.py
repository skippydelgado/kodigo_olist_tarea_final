import json

import pandas as pd
import streamlit as st

from comun import leer_csv, llamar_api

st.title("Riesgo de mala reseña")
st.caption("Elija un pedido de ejemplo, cambie lo que quiera y pregunte a la API desplegada en Render.")

ENTRADAS = ["order_id", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
            "order_delivered_customer_date", "order_estimated_delivery_date", "estado_cliente", "n_items",
            "n_vendedores", "precio_total", "flete_total", "peso_total_g", "fotos_promedio", "categoria",
            "estado_vendedor", "tipo_pago", "cuotas_max"]
ENTEROS = {"n_items", "n_vendedores"}
NUMEROS = {"precio_total", "flete_total", "peso_total_g", "fotos_promedio", "cuotas_max"}

ejemplos = leer_csv("ejemplos_pedidos.csv", dtype=str)
if ejemplos is None:
    st.error("No se encontró `datos/ejemplos_pedidos.csv`. Genérelo con el notebook (Parte 5).")
    st.stop()

etiqueta = st.selectbox("Pedido de ejemplo", ejemplos["etiqueta"])
fila = ejemplos.loc[ejemplos["etiqueta"] == etiqueta].iloc[0]

tabla = pd.DataFrame({"variable": ENTRADAS, "valor": [fila[c] if pd.notna(fila[c]) else "" for c in ENTRADAS]})
editada = st.data_editor(tabla, hide_index=True, width="stretch", disabled=["variable"],
                         height=35 * len(ENTRADAS) + 40, key=f"editor_{etiqueta}")


def a_json(df):
    """Convierte la tabla editada al JSON del contrato (vacío -> null; números como número)."""
    pedido, errores = {}, []
    for var, val in zip(df["variable"], df["valor"]):
        val = "" if val is None else str(val).strip()
        if val in ("", "nan", "None"):
            pedido[var] = None
        elif var in ENTEROS or var in NUMEROS:
            try:
                num = float(val)
                pedido[var] = int(num) if var in ENTEROS and num.is_integer() else num
            except ValueError:
                errores.append(f"`{var}` debe ser un número")
        else:
            pedido[var] = val
    return pedido, errores


col_boton, col_real = st.columns([1, 3])
calcular = col_boton.button("Calcular riesgo", type="primary")
if "mala_resena" in fila and pd.notna(fila["mala_resena"]):
    col_real.caption("Resultado real de este pedido (no se envía a la API): "
                     + ("**mala reseña (1–2★)**" if str(fila["mala_resena"]) == "1" else "reseña de 3–5★"))

if calcular:
    pedido, errores = a_json(editada)
    if errores:
        st.error("Corrija los datos: " + "; ".join(errores))
        st.stop()
    with st.spinner("Consultando la API… (si estaba dormida, puede tardar hasta un minuto)"):
        respuesta, error = llamar_api("POST", "/riesgo", json=pedido)
    if error:
        st.error(error)
    else:
        c1, c2 = st.columns(2)
        c1.metric("Probabilidad de 1–2 estrellas", f"{respuesta['probabilidad'] * 100:.0f}%")
        c2.metric("Umbral de riesgo alto (10% más riesgoso)", f"{respuesta['umbral'] * 100:.0f}%")
        if respuesta["riesgo_alto"]:
            st.error("**Riesgo alto:** contactar al cliente.")
        else:
            st.success("Riesgo normal: no está en el 10% más riesgoso.")
        with st.expander("Respuesta completa de la API"):
            st.json(respuesta)
        with st.expander("JSON enviado a la API"):
            st.code(json.dumps(pedido, indent=2, ensure_ascii=False), language="json")

with st.expander("¿La API está despierta?"):
    if st.button("Probar GET /"):
        with st.spinner("Llamando a la API…"):
            datos, error = llamar_api("GET", "/")
        st.error(error) if error else st.json(datos)
