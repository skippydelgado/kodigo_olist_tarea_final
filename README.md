# Proyecto final · Olist: del pedido a la reseña

**Equipo:** Ruiz Melissa, Rodrigo y Cesar · Bootcamp AIMLF1 (Kodigo)

Proyecto de punta a punta con datos reales de Olist: SQL → modelo de riesgo de mala reseña → segmentación de vendedores → sentimiento de comentarios con deep learning → API en Render → app en Streamlit → ficha del modelo.

```
olist-proyecto-final/
├── Proyecto_Final.ipynb      ← notebook (Colab) que genera todo
├── preparacion.py            ← variables del modelo (lo importa el notebook y la API)
├── ficha_modelo.md           ← ficha del modelo (la genera el notebook)
├── api/                      ← se despliega en Render
│   ├── main.py
│   ├── preparacion.py, modelo_riesgo.joblib, umbral.json   ← los genera el notebook
│   └── requirements.txt, .python-version                     ← los genera el notebook (versiones de Colab)
├── app/                      ← se despliega en Streamlit Community Cloud
│   ├── streamlit_app.py, comun.py, paginas/
│   ├── ficha_modelo.md, datos/*.csv                          ← los genera el notebook
│   └── requirements.txt
├── render.yaml               ← (opcional) configuración de Render en un archivo
├── api_url.txt, app_url.txt  ← una línea con cada URL
```

---

# Guía de implementación paso a paso (desde cero)

Tiempo estimado: 1 a 1.5 horas la primera vez. No hace falta instalar nada en la computadora: todo se hace en el navegador.

## Paso 0 · Ejecutar el notebook en Colab

1. Abrir [colab.research.google.com](https://colab.research.google.com) → **Archivo › Subir notebook** → elegir `Proyecto_Final.ipynb`.
2. Activar la GPU: **Entorno de ejecución › Cambiar tipo de entorno de ejecución › T4 GPU** → Guardar.
3. Subir `preparacion.py` no hace falta: el notebook lo escribe solo (`%%writefile`).
4. **Entorno de ejecución › Reiniciar y ejecutar todo.** Cuando aparezca `Contraseña:` en la primera celda, escribir la contraseña del curso y presionar Enter. La contraseña **no** queda guardada en el notebook.
5. Esperar a que termine (unos 10–15 minutos: la descarga del modelo de sentimiento pesa ~1 GB).
6. En la celda de la Parte 5 que imprime versiones, anotar la versión de **Python** (por ejemplo `3.12.12`). La necesitarás en Render.
7. Al final se crea `artefactos_proyecto.zip`. En el panel de archivos de Colab (ícono de carpeta, a la izquierda) → clic derecho sobre `artefactos_proyecto.zip` → **Descargar**.
8. Descargar también el notebook ejecutado: **Archivo › Descargar › Descargar .ipynb** (no viene dentro del zip).
9. Descomprimir el zip en la computadora. Trae `api/` **completa** (main.py, preparacion.py, modelo, umbral y requirements) y, de `app/`, **solo los datos** (`app/datos/` y `app/ficha_modelo.md`). El código de la app (`streamlit_app.py`, `comun.py`, `paginas/`, `requirements.txt`) viene en este paquete: hay que **juntar las dos cosas** en la misma carpeta `app/` (ver Paso 2).

## Paso 1 · Crear las cuentas (una sola vez)

1. **GitHub:** entrar a [github.com/signup](https://github.com/signup), crear la cuenta con el correo y verificarla.
2. **Render:** entrar a [render.com](https://render.com) → **Get Started** → **Sign up with GitHub** (así Render ya puede ver los repositorios). No pide tarjeta para el plan gratuito.
3. **Streamlit Community Cloud:** entrar a [share.streamlit.io](https://share.streamlit.io) → **Continue with GitHub** → autorizar.

Basta con que **un integrante** tenga las cuentas; después puede invitar a los demás al repositorio (Settings › Collaborators).

## Paso 2 · Crear el repositorio en GitHub y subir los archivos

1. En GitHub: botón **+** (arriba a la derecha) → **New repository**.
   - Nombre: `olist-proyecto-final` · Visibilidad: **Public** (lo más simple: el docente puede verlo y Streamlit lo despliega sin permisos extra) · marcar **Add a README file** → **Create repository**.
2. Preparar en la computadora una carpeta con esta estructura (copiando de este paquete y del zip de Colab):
   - De este paquete: `README.md`, `render.yaml`, `.gitignore`, `api/main.py`, toda la carpeta `app/` (código).
   - El notebook descargado de Colab: `Proyecto_Final.ipynb`.
   - Del zip de Colab: `preparacion.py`, `ficha_modelo.md`, y **dentro de `api/`**: `preparacion.py`, `modelo_riesgo.joblib`, `umbral.json`, `requirements.txt`, `.python-version`; **dentro de `app/`**: la carpeta `datos/` y `ficha_modelo.md`.
3. En la página del repositorio: **Add file › Upload files** → arrastrar **todas las carpetas y archivos** → abajo, mensaje "Primera versión" → **Commit changes**.
   - Si GitHub no muestra el archivo oculto `.python-version` o `.gitignore`, no pasa nada: en Render se fija la versión de Python con una variable (Paso 3).
4. Revisar que en GitHub existan `api/modelo_riesgo.joblib` y `app/datos/ejemplos_pedidos.csv`.

## Paso 3 · Publicar la API en Render

1. En [dashboard.render.com](https://dashboard.render.com): **New + › Web Service** → **Build and deploy from a Git repository** → elegir `olist-proyecto-final` → **Connect**.
2. Completar:

   | Campo | Valor |
   |---|---|
   | Name | `olist-riesgo-api` (será parte de la URL) |
   | Region | Oregon (US West) |
   | Branch | `main` |
   | **Root Directory** | `api` |
   | Runtime / Language | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | **Free** |

3. Abrir **Advanced › Add Environment Variable**: `PYTHON_VERSION` = la versión que imprimió Colab (por ejemplo `3.12.12`).
4. **Create Web Service.** El primer despliegue tarda 3–8 minutos. Cuando el log diga `Your service is live 🎉`, copiar la URL de arriba (algo como `https://olist-riesgo-api.onrender.com`).
5. Probar en el navegador:
   - `https://…onrender.com/` → debe mostrar `{"estado":"ok", …}`.
   - `https://…onrender.com/docs` → documentación; abrir `POST /riesgo` → **Try it out** → **Execute** con el ejemplo: debe devolver `probabilidad` y `riesgo_alto`. Cambiar `precio_total` a `-5` → debe responder **422**.
6. Guardar la URL en `api_url.txt` (una sola línea) y subirlo al repositorio.

**Si falla:** abrir la pestaña **Logs** del servicio.
- `ModuleNotFoundError: No module named 'preparacion'` o `crear_variables` → falta `api/preparacion.py`.
- Error al cargar el `.joblib` (`AttributeError`, `ValueError … incompatible dtype`) → `api/requirements.txt` no es el que generó Colab. Volver a subir el generado.
- `No matching distribution found for numpy==…` → la versión de Python en `PYTHON_VERSION` no coincide con la de Colab.
- El plan gratuito se "duerme" tras 15 minutos sin visitas: la primera consulta tarda hasta un minuto. Antes de la defensa, abrir la URL `/` un par de minutos antes.

## Paso 4 · Publicar la app en Streamlit Community Cloud

1. En [share.streamlit.io](https://share.streamlit.io): **Create app › Deploy a public app from GitHub**.
2. Completar:
   - Repository: `tu-usuario/olist-proyecto-final` · Branch: `main`
   - **Main file path:** `app/streamlit_app.py`
   - App URL: elegir un nombre, por ejemplo `olist-riesgo`.
3. Abrir **Advanced settings**:
   - Python version: la misma de Colab (o la más cercana disponible).
   - **Secrets:** pegar (con la URL real de Render, sin `/` al final):
     ```toml
     API_URL = "https://olist-riesgo-api.onrender.com"
     ```
4. **Deploy.** Tarda 2–4 minutos. Revisar las 4 páginas del menú lateral: *Riesgo de un pedido* (elegir un pedido → **Calcular riesgo**), *Comentarios*, *Segmentos de vendedores* y *Ficha del modelo*.
5. Guardar la URL de la app en `app_url.txt` y subirlo al repositorio.

Para cambiar la URL de la API después: en la app → **⋮ › Settings › Secrets**.

## Paso 5 · Cerrar el notebook y armar la entrega

1. En Colab, en la celda **"Prueba de la API desplegada"**, reemplazar `https://SU-API.onrender.com` por la URL real y ejecutar esa celda: debe imprimir una probabilidad.
2. **Entorno de ejecución › Reiniciar y ejecutar todo** una última vez (el notebook debe correr completo) y descargar el `.ipynb` (**Archivo › Descargar › .ipynb**), renombrado `Proyecto_Final.ipynb`.
3. Crear el zip `Apellido1_Apellido2_Proyecto_Final.zip` con:
   ```
   Proyecto_Final.ipynb
   preparacion.py
   modelo_riesgo.joblib
   segmentos_vendedores.csv, perfil_segmentos.csv   ← elegimos 3B
   sentimiento_muestra.csv
   ficha_modelo.md
   api_url.txt
   app_url.txt
   api/      (main.py, preparacion.py, modelo_riesgo.joblib, umbral.json, requirements.txt)
   app/      (streamlit_app.py, comun.py, paginas/, datos/, ficha_modelo.md, requirements.txt)
   ```
4. La API y la app deben seguir publicadas hasta que salgan las notas.

---

## Endpoints de la API

| Método y ruta | Recibe | Devuelve |
|---|---|---|
| `GET /` | nada | `{"estado": "ok", "umbral_riesgo_alto": …}` |
| `POST /riesgo` | JSON con las 17 columnas del contrato (fechas como texto `"2018-03-07 22:02:23"`; opcionales: `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `peso_total_g`, `fotos_promedio`, `categoria`, `estado_vendedor`, `tipo_pago`, `cuotas_max`) | `{"order_id", "probabilidad", "riesgo_alto", "umbral", "accion_sugerida"}` |
| `GET /docs` | — | documentación interactiva (Swagger) |

Validación con Pydantic (responde **422**): precio o flete negativos, `n_items`/`n_vendedores` < 1, falta un campo obligatorio, fecha que no se puede leer, `estado_cliente` que no tiene 2 letras.

## Guion para la defensa (3 minutos de demo)

1. Abrir la app → *Riesgo de un pedido* → elegir un pedido con "retraso +X días" → **Calcular riesgo** → mostrar la probabilidad, el umbral y "Riesgo alto". Cambiar `order_delivered_customer_date` a una fecha anterior a la prometida y volver a calcular: el riesgo baja.
2. Abrir `…onrender.com/docs` para mostrar que la API es real (y un 422 con precio negativo).
3. *Comentarios*: coincidencia, tabla cruzada y un desacuerdo clasificado.
4. *Segmentos*: el grupo "Con problemas de entrega" y su acción.
5. *Ficha*: "de cada 10 clientes que llamamos, unos X…".
