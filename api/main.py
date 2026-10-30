"""
API de riesgo de mala reseña — Proyecto final Olist.

GET  /        -> confirma que la API está viva
POST /riesgo  -> recibe las 17 columnas del contrato y devuelve la probabilidad de 1-2 estrellas
GET  /docs    -> documentación automática (Swagger) que genera FastAPI
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

CARPETA = Path(__file__).resolve().parent

# preparacion.py debe estar en esta misma carpeta: el pipeline lo necesita al cargarse.
modelo = joblib.load(CARPETA / "modelo_riesgo.joblib")
with open(CARPETA / "umbral.json", encoding="utf-8") as f:
    UMBRAL = float(json.load(f)["umbral"])

app = FastAPI(
    title="API Olist · Riesgo de mala reseña",
    description=(
        "Predice, en el momento de la entrega, la probabilidad de que un pedido reciba una "
        "reseña de 1 o 2 estrellas. `riesgo_alto` es true si la probabilidad alcanza el umbral "
        "del 10% de pedidos más riesgosos (calculado con los datos de entrenamiento)."
    ),
    version="1.0.0",
)

# El modelo predice en el momento de la entrega: compra, entrega real y fecha prometida son obligatorias.
FECHAS_OBLIGATORIAS = {"order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"}
CAMPOS_FECHA = [
    "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
    "order_delivered_customer_date", "order_estimated_delivery_date",
]


class Pedido(BaseModel):
    """Las 17 columnas de entrada del contrato (todas menos mala_resena)."""

    order_id: str = Field(..., min_length=1, examples=["d6cb7abec3164d194483906f3702748a"])
    order_purchase_timestamp: str = Field(..., examples=["2018-03-07 22:02:23"])
    order_approved_at: Optional[str] = Field(None, examples=["2018-03-09 02:35:30"])
    order_delivered_carrier_date: Optional[str] = Field(None, examples=["2018-03-09 20:03:25"])
    order_delivered_customer_date: str = Field(..., examples=["2018-04-11 20:07:37"])
    order_estimated_delivery_date: str = Field(..., examples=["2018-04-04 00:00:00"])
    estado_cliente: str = Field(..., min_length=2, max_length=2, examples=["CE"])
    n_items: int = Field(..., ge=1, examples=[1])
    n_vendedores: int = Field(..., ge=1, examples=[1])
    precio_total: float = Field(..., ge=0, examples=[420.0])
    flete_total: float = Field(..., ge=0, examples=[35.5])
    peso_total_g: Optional[float] = Field(None, ge=0, examples=[1200.0])
    fotos_promedio: Optional[float] = Field(None, ge=0, examples=[2.0])
    categoria: Optional[str] = Field(None, examples=["informatica_acessorios"])
    estado_vendedor: Optional[str] = Field(None, examples=["SP"])
    tipo_pago: Optional[str] = Field(None, examples=["credit_card"])
    cuotas_max: Optional[float] = Field(None, ge=0, examples=[3])

    @field_validator(*CAMPOS_FECHA)
    @classmethod
    def fecha_valida(cls, valor, info):
        if valor is None or str(valor).strip() == "":
            if info.field_name in FECHAS_OBLIGATORIAS:
                raise ValueError("esta fecha es obligatoria")
            return None
        try:
            pd.Timestamp(valor)
        except Exception:
            raise ValueError("fecha inválida; use el formato 'AAAA-MM-DD HH:MM:SS'")
        return valor

    @field_validator("estado_cliente", "estado_vendedor")
    @classmethod
    def sigla_mayuscula(cls, valor):
        return valor.upper() if isinstance(valor, str) else valor


@app.get("/")
def inicio():
    return {
        "estado": "ok",
        "mensaje": "API de riesgo de mala reseña de Olist activa.",
        "umbral_riesgo_alto": round(UMBRAL, 4),
        "documentacion": "/docs",
        "hora_servidor": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


@app.post("/riesgo")
def riesgo(pedido: Pedido):
    fila = pd.DataFrame([pedido.model_dump()])
    try:
        probabilidad = float(modelo.predict_proba(fila)[:, 1][0])
    except Exception as error:  # el modelo no pudo procesar la fila
        raise HTTPException(status_code=500, detail=f"Error al predecir: {error}")
    riesgo_alto = probabilidad >= UMBRAL
    return {
        "order_id": pedido.order_id,
        "probabilidad": round(probabilidad, 4),
        "riesgo_alto": bool(riesgo_alto),
        "umbral": round(UMBRAL, 4),
        "accion_sugerida": "Contactar al cliente" if riesgo_alto else "Sin acción",
    }
