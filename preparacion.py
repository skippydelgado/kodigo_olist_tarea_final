import numpy as np
import pandas as pd

FECHAS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

NUMERICAS = [
    "dias_retraso", "retrasado", "dias_entrega_total", "dias_aprobacion",
    "dias_hasta_transportista", "dias_transporte", "dias_prometidos",
    "mes_compra", "dia_semana_compra",
    "n_items", "n_vendedores", "precio_total", "flete_total", "peso_total_g",
    "fotos_promedio", "cuotas_max", "precio_por_item", "flete_relativo", "mismo_estado",
]

CATEGORICAS = ["estado_cliente", "estado_vendedor", "categoria", "tipo_pago"]


def _dias(fin, inicio):
    return (fin - inicio).dt.total_seconds() / 86400


def crear_variables(df):
    df = df.copy()

    for col in FECHAS:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["n_items", "n_vendedores", "precio_total", "flete_total",
                "peso_total_g", "fotos_promedio", "cuotas_max"]:
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
    X["mes_compra"] = compra.dt.month
    X["dia_semana_compra"] = compra.dt.dayofweek

    for col in ["n_items", "n_vendedores", "precio_total", "flete_total",
                "peso_total_g", "fotos_promedio", "cuotas_max"]:
        X[col] = df[col]

    X["precio_por_item"] = df["precio_total"] / df["n_items"].replace(0, np.nan)
    X["flete_relativo"] = df["flete_total"] / (df["precio_total"] + 1)
    X["mismo_estado"] = (df["estado_cliente"] == df["estado_vendedor"]).astype(int)

    for col in CATEGORICAS:
        X[col] = df[col].fillna("desconocido").astype(str)

    X = X.replace([np.inf, -np.inf], np.nan)
    return X[NUMERICAS + CATEGORICAS]
