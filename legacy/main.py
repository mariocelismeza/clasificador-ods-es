"""
Backend FastAPI — Clasificador de textos según los ODS
Microproyecto 2 (Maestría en IA, Aprendizaje No Supervisado)

Backend construido sobre el mismo pipeline real
de Machine Learning (TF-IDF -> LSA -> SVM Lineal calibrado) y las mismas
funcionalidades. El frontend (React + Vite) consume esta API vía JSON; en
producción, este mismo proceso también sirve los archivos estáticos ya
compilados del frontend (carpeta frontend/dist), para poder levantar todo
con un solo comando.

Ejecutar con:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

import os
import sys
import json
import time
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_pipeline import NOMBRES_ODS  # noqa: E402

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "static")  # build de React (npm run build), si existe

SDG_COLORS = {
    1: "#E5243B", 2: "#DDA63A", 3: "#4C9F38", 4: "#C5192D", 5: "#FF3A21",
    6: "#26BDE2", 7: "#FCC30B", 8: "#A21942", 9: "#FD6925", 10: "#DD1367",
    11: "#FD9D24", 12: "#BF8B2E", 13: "#3F7E44", 14: "#0A97D9", 15: "#56C02B",
    16: "#00689D", 17: "#19486A",
}

EJEMPLOS = [
    {
        "id": "educacion",
        "titulo": "Educación rural y becas",
        "texto": (
            "Garantizar una educación inclusiva, equitativa y de calidad y promover oportunidades "
            "de aprendizaje durante toda la vida para todos los niños y jóvenes en zonas rurales "
            "mediante becas, tecnología digital y formación docente comunitaria."
        ),
        "color": SDG_COLORS[4],
    },
    {
        "id": "energia",
        "titulo": "Energía y transición",
        "texto": (
            "La transición hacia fuentes de energía renovable como la solar y la eólica es clave "
            "para reducir la dependencia de combustibles fósiles y garantizar el acceso universal "
            "a energía asequible y no contaminante."
        ),
        "color": SDG_COLORS[7],
    },
    {
        "id": "marina",
        "titulo": "Conservación marina",
        "texto": (
            "La sobrepesca y la contaminación plástica amenazan los ecosistemas marinos; se "
            "requieren áreas protegidas y políticas de pesca sostenible para preservar la vida "
            "submarina y los medios de subsistencia costeros."
        ),
        "color": SDG_COLORS[14],
    },
    {
        "id": "pobreza",
        "titulo": "Transferencias condicionadas",
        "texto": (
            "Un programa de transferencias monetarias condicionadas, combinado con microcréditos "
            "para pequeños productores rurales, permitió reducir la pobreza extrema en la región "
            "al financiar insumos agrícolas, vivienda básica y acceso a agua potable."
        ),
        "color": SDG_COLORS[1],
    },
    {
        "id": "genero",
        "titulo": "Brecha salarial de género",
        "texto": (
            "Pese a los avances normativos, la brecha salarial entre hombres y mujeres persiste "
            "en cargos directivos; se proponen cuotas de liderazgo femenino, licencias parentales "
            "equitativas y auditorías salariales obligatorias para cerrarla."
        ),
        "color": SDG_COLORS[5],
    },
    {
        "id": "institucionalidad",
        "titulo": "Transparencia e instituciones",
        "texto": (
            "El fortalecimiento de la independencia judicial, junto con mecanismos de rendición "
            "de cuentas y portales de datos abiertos, reduce los índices de corrupción y mejora "
            "la confianza ciudadana en las instituciones públicas."
        ),
        "color": SDG_COLORS[16],
    },
    {
        "id": "acceso_justicia",
        "titulo": "Acceso a la justicia",
        "texto": (
            "Centros de asistencia jurídica gratuita y jornadas móviles de registro civil "
            "permitieron que comunidades rurales sin documentos de identidad accedieran a la "
            "justicia, redujeran la violencia intrafamiliar y denunciaran casos de trata de personas."
        ),
        "color": SDG_COLORS[16],
    },
]

UMBRAL_ALTA_CONFIANZA = 0.70
UMBRAL_MEDIA_CONFIANZA = 0.40
LONGITUD_MINIMA_OPTIMA = 8  # palabras

_modelos = None
_artefactos = None


def cargar_modelos():
    global _modelos
    if _modelos is None:
        tfidf_pipeline = joblib.load(os.path.join(MODELS_DIR, "tfidf_pipeline.joblib"))
        svd_model = joblib.load(os.path.join(MODELS_DIR, "svd_model.joblib"))
        clasificador = joblib.load(os.path.join(MODELS_DIR, "clasificador_svm.joblib"))
        clasificador_calibrado = joblib.load(os.path.join(MODELS_DIR, "clasificador_svm_calibrado.joblib"))
        _modelos = (tfidf_pipeline, svd_model, clasificador, clasificador_calibrado)
    return _modelos


def tfidf_hparams():
    """Hiperparámetros reales del TfidfVectorizer ya entrenado (introspección directa
    del objeto serializado, no valores supuestos)."""
    tfidf_pipeline, _, _, _ = cargar_modelos()
    p = tfidf_pipeline.named_steps["tfidf"].get_params()
    return {
        "sublinear_tf": p.get("sublinear_tf"),
        "min_df": p.get("min_df"),
        "max_df": p.get("max_df"),
        "ngram_range": list(p.get("ngram_range")),
    }


def cargar_artefactos():
    global _artefactos
    if _artefactos is None:
        with open(os.path.join(ARTIFACTS_DIR, "metrics_summary.json"), encoding="utf-8") as f:
            metrics = json.load(f)
        with open(os.path.join(ARTIFACTS_DIR, "terminos_por_ods.json"), encoding="utf-8") as f:
            terminos = {int(d["ODS"]): d["términos_más_frecuentes"] for d in json.load(f)}
        with open(os.path.join(ARTIFACTS_DIR, "reporte_por_ods.json"), encoding="utf-8") as f:
            reporte = {int(d["ods"]): d for d in json.load(f)}
        with open(os.path.join(ARTIFACTS_DIR, "pares_confusion.json"), encoding="utf-8") as f:
            pares = json.load(f)
        _artefactos = (metrics, terminos, reporte, pares)
    return _artefactos


def clasificar_texto(texto, top_k_secundarios=2):
    tfidf_pipeline, svd_model, clasificador, clasificador_calibrado = cargar_modelos()

    cleaner = tfidf_pipeline.named_steps["cleaner"]
    tfidf_step = tfidf_pipeline.named_steps["tfidf"]

    texto_limpio = cleaner.transform([texto])
    vec_tfidf = tfidf_step.transform(texto_limpio)
    vec_lsa = svd_model.transform(vec_tfidf)

    proba = clasificador_calibrado.predict_proba(vec_lsa)[0]
    clases = list(clasificador_calibrado.classes_)
    orden = np.argsort(proba)[::-1]

    margenes = clasificador.decision_function(vec_lsa)[0]
    clases_margen = list(clasificador.classes_)

    ods_predicho = int(clases[orden[0]])
    proba_predicho = float(proba[orden[0]])
    margen_predicho = float(margenes[clases_margen.index(ods_predicho)])

    secundarios = []
    for idx in orden[1: 1 + top_k_secundarios]:
        c_ods = int(clases[idx])
        c_margen = float(margenes[clases_margen.index(c_ods)])
        secundarios.append({
            "ods": c_ods,
            "nombre": NOMBRES_ODS.get(c_ods, ""),
            "color": SDG_COLORS.get(c_ods, "#334155"),
            "proba": float(proba[idx]),
            "margen": c_margen,
        })

    distribucion = {int(c): float(p) for c, p in zip(clases, proba)}

    row = vec_tfidf.toarray()[0]
    feature_names = tfidf_step.get_feature_names_out()
    candidatos_idx = row.argsort()[::-1][:10]
    top_idx = [i for i in candidatos_idx if row[i] > 0][:6]
    keywords = [{"termino": feature_names[i], "peso": float(row[i])} for i in top_idx]

    return {
        "ods_predicho": ods_predicho,
        "nombre_ods": NOMBRES_ODS.get(ods_predicho, "Desconocido"),
        "color_ods": SDG_COLORS.get(ods_predicho, "#334155"),
        "proba": proba_predicho,
        "margen": margen_predicho,
        "secundarios": secundarios,
        "distribucion": distribucion,
        "keywords": keywords,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cargar modelos y artefactos una sola vez al iniciar el servidor.
    cargar_modelos()
    cargar_artefactos()
    yield


app = FastAPI(title="Clasificador ODS API", lifespan=lifespan)

# CORS habilitado para desarrollo con Vite (puerto 5173) hablando con este backend (puerto 8000).
# En producción, el frontend compilado se sirve desde este mismo origen, así que CORS no es
# necesario ahí, pero se deja abierto para no bloquear el flujo de desarrollo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextoIn(BaseModel):
    texto: str


@app.get("/api/config")
def api_config():
    """Todo lo que el frontend necesita al cargar: equivalente al contexto Jinja
    que antes armaba server.py para render_template()."""
    metrics, terminos, reporte, pares = cargar_artefactos()
    terminos_ordenados = [
        {"ods": k, "nombre": NOMBRES_ODS.get(k, ""), "color": SDG_COLORS.get(k, "#334155"), "terminos": v}
        for k, v in sorted(terminos.items())
    ]
    return {
        "metrics": metrics,
        "tfidf_params": tfidf_hparams(),
        "ejemplos": EJEMPLOS,
        "n_ods_modelados": len(terminos),
        "terminos_ordenados": terminos_ordenados,
        "pares": pares[:8],
        "sdg_colors": {str(k): v for k, v in SDG_COLORS.items()},
        "nombres_ods": {str(k): v for k, v in NOMBRES_ODS.items()},
        "umbral_alta": UMBRAL_ALTA_CONFIANZA,
        "umbral_alta_pct": int(UMBRAL_ALTA_CONFIANZA * 100),
        "umbral_media": UMBRAL_MEDIA_CONFIANZA,
        "umbral_media_pct": int(UMBRAL_MEDIA_CONFIANZA * 100),
        "longitud_minima": LONGITUD_MINIMA_OPTIMA,
    }


@app.post("/api/predecir")
def api_predecir(payload: TextoIn):
    texto = (payload.texto or "").strip()
    if not texto:
        raise HTTPException(status_code=400, detail="Por favor ingresa un texto antes de predecir.")

    t0 = time.perf_counter()
    resultado = clasificar_texto(texto)
    resultado["latencia_ms"] = (time.perf_counter() - t0) * 1000
    return resultado


@app.post("/api/lote")
async def api_lote(archivo: UploadFile = File(...)):
    if archivo is None or archivo.filename == "":
        raise HTTPException(status_code=400, detail="No se recibió ningún archivo.")

    nombre = archivo.filename.lower()
    contenido = await archivo.read()
    if nombre.endswith(".csv"):
        import io
        df_lote = pd.read_csv(io.BytesIO(contenido))
        textos_lote = df_lote.iloc[:, 0].astype(str).tolist()
    elif nombre.endswith(".txt"):
        textos_lote = [line.strip() for line in contenido.decode("utf-8").splitlines() if line.strip()]
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado. Usa .csv o .txt.")

    resultados = []
    for t in textos_lote:
        r = clasificar_texto(t)
        resultados.append({
            "texto": t[:120] + ("..." if len(t) > 120 else ""),
            "ods_predicho": r["ods_predicho"],
            "nombre_ods": r["nombre_ods"],
            "probabilidad": round(r["proba"], 4),
        })
    return {"resultados": resultados}


@app.get("/api/metrics")
def api_metrics():
    metrics, _, _, _ = cargar_artefactos()
    return metrics


@app.get("/api/confusion-matrix.png")
def api_confusion_matrix():
    ruta = os.path.join(ARTIFACTS_DIR, "confusion_matrix.png")
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="No encontrado")
    return FileResponse(ruta, media_type="image/png")


# Servir el frontend de React ya compilado (npm run build -> frontend/dist copiado a ./static)
# desde este mismo servidor, para poder levantar todo con un solo comando en producción/uso normal.
if os.path.isdir(FRONTEND_DIST_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")


if __name__ == "__main__":
    # Permite "python main.py" además de "uvicorn main:app --port 8000"
    # (igual que app.py/server.py), por si se ejecuta directamente por costumbre.
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
