"""
preparacion.py — Variables del modelo de riesgo de mala reseña (Proyecto final Olist).

Convierte las 17 columnas de entrada del contrato en las variables que usa el modelo.
El pipeline guardado en modelo_riesgo.joblib llama a `crear_variables` dentro de un
FunctionTransformer, por eso este archivo debe estar junto al .joblib (notebook y API).

Regla de oro (sin fuga de datos): solo se usa información conocida en el momento en que
el pedido se ENTREGA. Nada de la reseña (texto, largo, fechas de la reseña) entra aquí.
"""
import numpy as np
import pandas as pd

FECHAS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

NUMEROS_CONTRATO = ["n_items", "n_vendedores", "precio_total", "flete_total",
                    "peso_total_g", "fotos_promedio", "cuotas_max"]

NUMERICAS = [
    # Tiempos de la entrega (lo que más explica una mala reseña)
    "dias_retraso", "retrasado", "dias_entrega_total", "dias_aprobacion",
    "dias_hasta_transportista", "dias_transporte", "dias_prometidos",
    # Calendario (sin el mes: no generaliza a meses que el modelo no ha visto)
    "dia_semana_compra",
    # Contenido del pedido
    "n_items", "n_vendedores", "precio_total", "flete_total", "peso_total_g",
    "fotos_promedio", "cuotas_max",
    # Derivadas
    "precio_por_item", "flete_relativo", "mismo_estado",
]

CATEGORICAS = ["estado_cliente", "estado_vendedor", "categoria", "tipo_pago"]


def _a_fecha(serie):
    """Convierte texto o fechas a datetime sin zona horaria; lo que no se entiende queda NaT."""
    fechas = pd.to_datetime(serie, errors="coerce", utc=True, format="mixed")
    return fechas.dt.tz_convert(None)


def _dias(fin, inicio):
    return (fin - inicio).dt.total_seconds() / 86400


def crear_variables(df):
    """Recibe un DataFrame con las columnas del contrato y devuelve las variables del modelo."""
    df = pd.DataFrame(df).copy()

    # Tolerancia: si falta una columna opcional, se crea vacía (el imputador la rellena).
    for col in FECHAS + NUMEROS_CONTRATO + ["estado_cliente", "estado_vendedor", "categoria", "tipo_pago"]:
        if col not in df.columns:
            df[col] = np.nan

    for col in FECHAS:
        df[col] = _a_fecha(df[col])
    for col in NUMEROS_CONTRATO:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    compra = df["order_purchase_timestamp"]
    aprobado = df["order_approved_at"]
    transportista = df["order_delivered_carrier_date"]
    entrega = df["order_delivered_customer_date"]
    prometida = df["order_estimated_delivery_date"]

    X = pd.DataFrame(index=df.index)
    X["dias_retraso"] = _dias(entrega, prometida)
    X["retrasado"] = (X["dias_retraso"] > 0).astype(int)
    X["dias_entrega_total"] = _dias(entrega, compra)
    X["dias_aprobacion"] = _dias(aprobado, compra)
    X["dias_hasta_transportista"] = _dias(transportista, compra)
    X["dias_transporte"] = _dias(entrega, transportista)
    X["dias_prometidos"] = _dias(prometida, compra)
    X["dia_semana_compra"] = compra.dt.dayofweek

    for col in NUMEROS_CONTRATO:
        X[col] = df[col]

    X["precio_por_item"] = df["precio_total"] / df["n_items"].replace(0, np.nan)
    X["flete_relativo"] = df["flete_total"] / (df["precio_total"] + 1)
    X["mismo_estado"] = (df["estado_cliente"] == df["estado_vendedor"]).astype(int)

    for col in CATEGORICAS:
        X[col] = df[col].fillna("desconocido").astype(str)

    X = X.replace([np.inf, -np.inf], np.nan)
    return X[NUMERICAS + CATEGORICAS]
