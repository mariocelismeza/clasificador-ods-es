# Clasificador de ODS (bonificación opcional)

Aplicación web que reutiliza el pipeline entrenado en `Microproyecto2_ODS.ipynb`
(limpieza de texto → TF-IDF → LSA → SVM Lineal, con calibración de Platt para
probabilidades reales) para clasificar un texto libre según el Objetivo de
Desarrollo Sostenible (ODS) al que más se relaciona.

La aplicación es una API en **FastAPI** (`main.py`) consumida por una SPA en
**React + Vite + Tailwind CSS** (`frontend/`), con el diseño oscuro "Glacier"
(glassmorphism). FastAPI sirve tanto la API real como el build de producción
del frontend, así que todo se levanta con un solo comando.

## Estructura de esta carpeta

```
word_predicto_app/
├── main.py                         # Backend FastAPI: API real + documentación automática en /docs
├── frontend/                       # Código fuente de la SPA en React + Vite + Tailwind
│   └── src/                        # Componentes: Header, ClasificadorView, ExploradorOdsView, ...
├── static/                         # Build de producción de frontend/ (ya compilado, listo para usar)
├── text_pipeline.py                # SpanishTextCleaner + nombres de los 17 ODS
├── requirements.txt                # Dependencias Python (FastAPI + el pipeline de ML)
├── models/                         # Artefactos entrenados (sección 8 del notebook)
├── artifacts/                      # Datos reales para la interfaz (sección 8.2)
└── README.md
```

## Qué incluye la aplicación

- Texto libre → predicción con probabilidad calibrada, margen de decisión del
  SVM (también para los candidatos secundarios), palabras clave (TF-IDF) que
  explican la predicción, mapa de calor con la distribución sobre los 17 ODS
  (16 modelados + ODS 17 marcado como "N/A"), indicador de confianza
  alta/media/baja, latencia de inferencia real, exportación y copiado del
  resultado en JSON, historial de la sesión y **análisis en lote**
  (sube un .csv o .txt y clasifica varias filas a la vez). Atajo de teclado
  ⌘/Ctrl+Enter para lanzar la predicción sin usar el mouse.
- **Explorador ODS:** los 16 ODS del corpus con sus términos más frecuentes reales.
- **Matriz de Confusión:** la matriz real del conjunto de prueba y los pares de
  confusión más frecuentes.
- **Acerca del proyecto:** metodología y métricas reales del modelo, incluyendo
  los hiperparámetros reales del `TfidfVectorizer` ya entrenado (introspección
  directa del objeto serializado, no valores supuestos).

## Cómo ejecutar la aplicación

1. Ejecuta primero las **secciones 8.1 y 8.2** del notebook `Microproyecto2_ODS.ipynb`
   (ya deberían estar ejecutadas) — generan todo lo que hay en `models/` y `artifacts/`.

2. Instala las dependencias de Python (idealmente en un entorno virtual):

   ```bash
   cd word_predicto_app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Levanta el servidor (`http://localhost:8000`):

   ```bash
   uvicorn main:app --port 8000
   ```

   O, si prefieres ejecutarlo directamente:

   ```bash
   python main.py
   ```

   Esto **no necesita Node.js ni `npm install`** para funcionar: la carpeta
   `static/` ya trae el build de producción del frontend, y FastAPI lo sirve
   directamente. Node solo hace falta si quieres **editar** el código de
   `frontend/src/` — en ese caso:

   ```bash
   cd frontend
   npm install
   npm run build        # recompila hacia ../static
   ```

   o, para desarrollo con recarga en caliente (dos terminales: una con
   `uvicorn main:app --port 8000 --reload` y otra con lo siguiente):

   ```bash
   cd frontend
   npm install
   npm run dev           # http://localhost:5173, con proxy automático a la API en :8000
   ```

   La documentación interactiva de la API (generada automáticamente por
   FastAPI) queda disponible en `http://localhost:8000/docs`.

   La app requiere conexión a internet la primera vez que se abre en el
   navegador (carga Google Fonts e iconos Material Symbols desde CDN; el
   resto del CSS, Tailwind incluido, ya viene compilado localmente).

## Notas

- El modelo no puede predecir el **ODS 17** porque no está representado en el
  corpus de entrenamiento.
- La "probabilidad calibrada" viene de un `CalibratedClassifierCV` (Platt scaling)
  entrenado sobre el mismo SVM y los mismos hiperparámetros óptimos — no es un
  número inventado, es una calibración estándar de scikit-learn.
- El diseño "Glacier" (paleta oscura, glassmorphism) no incluye ningún bloque
  que sugiera una afiliación institucional con la ONU, ni IDs de sesión o
  versión inventados; los números de ejemplo son los valores reales del
  modelo y sus métricas.
- La interfaz FastAPI + React se conserva como extensión técnica adicional.
  Para la bonificación académica solicitada en el enunciado se incluye además
  `streamlit_app.py`, que reutiliza directamente el pipeline final serializado.

---

## Aplicación Streamlit (bonificación del Microproyecto 2)

Además de la interfaz FastAPI + React, el proyecto incluye `streamlit_app.py` para cumplir literalmente la bonificación indicada en el enunciado.

Desde la carpeta `word_predicto_app`:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

La aplicación carga `models/modelo_pipeline.joblib`, es decir, el mismo pipeline completo (limpieza + TF-IDF + LSA + SVM) evaluado en el notebook. Permite ingresar un texto libre y devuelve el ODS predicho.
