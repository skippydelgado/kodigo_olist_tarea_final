import json
import joblib
import pandas as pd
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="API Olist - Riesgo de Mala Reseña",
    description="Servicio web para predecir la probabilidad de recibir 1 o 2 estrellas en un pedido entregado."
)

# Cargar el modelo guardado y el umbral del Top 10%
modelo = joblib.load("modelo_riesgo.joblib")

try:
    with open("umbral.json", "r") as f:
        datos_umbral = json.load(f)
        UMBRAL = float(datos_umbral.get("umbral", 0.2609))
except Exception:
    UMBRAL = 0.2609

# Esquema Pydantic para validar las 17 columnas del contrato
class PedidoContrato(BaseModel):
    order_id: str
    order_purchase_timestamp: str
    order_approved_at: Optional[str] = None
    order_delivered_carrier_date: Optional[str] = None
    order_delivered_customer_date: Optional[str] = None
    order_estimated_delivery_date: str
    estado_cliente: str
    n_items: float
    n_vendedores: float
    precio_total: float
    flete_total: float
    peso_total_g: Optional[float] = None
    fotos_promedio: Optional[float] = None
    categoria: Optional[str] = None
    estado_vendedor: Optional[str] = None
    tipo_pago: Optional[str] = None
    cuotas_max: Optional[float] = None

@app.get("/")
def home():
    return {"status": "ok", "mensaje": "API de Riesgo Olist activa y lista."}

@app.post("/riesgo")
def predecir_riesgo(pedido: PedidoContrato):
    try:
        df_pedido = pd.DataFrame([pedido.model_dump()])
        probabilidad = float(modelo.predict_proba(df_pedido)[:, 1])
        riesgo_alto = bool(probabilidad >= UMBRAL)

        return {
            "order_id": pedido.order_id,
            "probabilidad": round(probabilidad, 4),
            "probabilidad_pct": f"{round(probabilidad * 100, 1)}%",
            "umbral": round(UMBRAL, 4),
            "riesgo_alto": riesgo_alto,
            "accion_sugerida": "Contactar cliente de inmediato" if riesgo_alto else "Operación normal"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")