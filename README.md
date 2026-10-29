# API de Riesgo de Mala Reseña - Olist

Este servicio web proporciona un modelo predictivo basado en **XGBoost** para calcular la probabilidad de recibir una reseña negativa (1 o 2 estrellas) en un pedido de Olist una vez que ha sido entregado.

El servicio está construido con **FastAPI** y estructurado para su despliegue inmediato en plataformas como Render.

---

## 📋 Estructura de Archivos del Proyecto

```text
api/
├── main.py              # Aplicación FastAPI y definición de endpoints.
├── preparacion.py       # Transformaciones y creación de variables de entrada.
├── modelo_riesgo.joblib # Serialización del modelo XGBoost entrenado.
├── umbral.json          # Valor del umbral límite (Top 10% de mayor riesgo).
└── requirements.txt     # Dependencias requeridas para producción.
```

---

## 🚀 Instalación y Ejecución Local

### 1. Clonar o descargar este directorio
Asegúrate de tener todos los archivos listados anteriormente en la misma carpeta.

### 2. Crear un entorno virtual e instalar dependencias
```bash
# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar las dependencias
pip install -r requirements.txt
```

### 3. Iniciar el servidor de desarrollo
```bash
uvicorn main:app --reload
```
La API estará disponible en `http://127.0.0.1:8000` y la documentación interactiva (Swagger UI) en `http://127.0.0.1:8000/docs`.

---

## 🛠️ Endpoints

### 1. Verificación de Estado (Health Check)
* **Método:** `GET`
* **Ruta:** `/`
* **Respuesta de ejemplo (JSON):**
  ```json
  {
    "status": "ok",
    "mensaje": "API de Riesgo Olist activa y lista."
  }
  ```

### 2. Clasificación de Riesgo de un Pedido
* **Método:** `POST`
* **Ruta:** `/riesgo`
* **Payload de entrada (JSON que cumple las 17 columnas del contrato):**
  ```json
  {
    "order_id": "00010242fe8c5a6d1ba2dd792cb16214",
    "order_purchase_timestamp": "2017-09-13 08:59:02",
    "order_approved_at": "2017-09-13 09:05:55",
    "order_delivered_carrier_date": "2017-09-19 18:34:16",
    "order_delivered_customer_date": "2017-09-20 23:43:48",
    "order_estimated_delivery_date": "2017-09-29 00:00:00",
    "estado_cliente": "SP",
    "n_items": 1.0,
    "n_vendedores": 1.0,
    "precio_total": 58.90,
    "flete_total": 13.29,
    "peso_total_g": 650.0,
    "fotos_promedio": 4.0,
    "categoria": "cool_stuff",
    "estado_vendedor": "SP",
    "tipo_pago": "credit_card",
    "cuotas_max": 2.0
  }
  ```

* **Respuesta esperada (JSON):**
  ```json
  {
    "order_id": "00010242fe8c5a6d1ba2dd792cb16214",
    "probabilidad": 0.081,
    "probabilidad_pct": "8.1%",
    "umbral": 0.2609,
    "riesgo_alto": false,
    "accion_sugerida": "Operación normal"
  }
  ```

Si la `probabilidad` calculada es mayor o igual al `umbral` ($0.2609$), la bandera `riesgo_alto` se tornará `true` y la acción sugerida indicará `"Contactar cliente de inmediato"`.
