# Microproyecto 2 — clasificación de textos por ODS

**Autores:** David Cardenas y Mario Celis.

El trabajo clasifica textos en español del conjunto suministrado, derivado de OSDG Community Dataset, traducido y aumentado. Hay ejemplos de 16 ODS; el ODS 17 no está representado y no se puede predecir.

## Archivos que exige el PDF para el espacio de entrega

- `Microproyecto2_ODS.ipynb`: análisis, preparación, LSA, búsqueda, evaluación y exportación.
- `Microproyecto2_ODS.html`: versión visible del notebook con resultados.

El enunciado indica un espacio para adjuntar **estos dos archivos** y exige que todas las celdas muestren sus ejecuciones. La bonificación de Streamlit requiere además que el evaluador tenga acceso a la aplicación y sus artefactos; si la plataforma solo acepta los dos archivos, compartir la app por un canal complementario permitido por el docente.

## Archivos de apoyo para reproducir y ejecutar la bonificación

- `data/Datos_textosODS.xlsx`: corpus suministrado para reproducir el análisis.
- `word_predicto_app/streamlit_app.py`: bonificación oficial en Streamlit, con diseño inspirado en la referencia React: clasificador de texto libre, ejemplos, análisis CSV/TXT, explorador de ODS, matriz de confusión y evaluación. El resultado muestra márgenes de LinearSVC y probabilidades calibradas por temperatura.
- `word_predicto_app/text_pipeline.py`, `word_predicto_app/calibration.py`, `word_predicto_app/models/modelo_pipeline.joblib`, `word_predicto_app/models/modelo_calibrado.joblib` y `word_predicto_app/artifacts/`: inferencia, calibración y evidencia para la app.
- `word_predicto_app/ods_content.py`, `word_predicto_app/assets/sdg-icons/` y `.streamlit/config.toml`: descripciones editoriales, íconos y tema visual de la app.
- `word_predicto_app/export_app_artifacts.py`: exporta distribución y tópicos desde el corpus y el modelo final.
- `requirements.txt`: dependencias de Python.

La aplicación anterior FastAPI + React está en `legacy/` como código histórico; no es parte de la entrega ni se requiere para ejecutar Streamlit.

## Entorno e instalación

Los modelos se serializaron con **scikit-learn 1.8.0**. Se recomienda **Python 3.11 o 3.12**; Python 3.9 no puede instalar esa versión y provoca `InconsistentVersionWarning` al cargar los modelos con scikit-learn 1.6.1. No cargar los modelos con otra versión para una ejecución reproducible.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run word_predicto_app/streamlit_app.py
```

Para revisar el notebook: `jupyter notebook Microproyecto2_ODS.ipynb`. Ejecutarlo desde la raíz del proyecto. La exportación HTML se obtiene con `jupyter nbconvert --to html --output Microproyecto2_ODS.html Microproyecto2_ODS.ipynb` después de ejecutar todas las celdas.

## Método y artefactos

El pipeline final integra limpieza en español, TF-IDF de unigramas y bigramas, LSA con `TruncatedSVD` y `LinearSVC`. `GridSearchCV` ajusta el pipeline completo en cada fold de validación estratificada y agrupada; F1 macro es la métrica de selección por el desbalance de ODS. El test permanece aislado hasta la evaluación. `metrics_summary.json`, `reporte_por_ods.json`, `pares_confusion.json`, `terminos_por_ods.json` y `confusion_matrix.png` se generan en el notebook. `class_distribution.json` y `lsa_topics.json` se derivan del corpus y del pipeline serializado mediante `export_app_artifacts.py`, invocado al final del notebook. La sección 8.3 calibra el pipeline con temperatura y folds estratificados agrupados, exporta `modelo_calibrado.joblib` y `calibration_summary.json` y evalúa las probabilidades en el test. La app mantiene barras de márgenes con cero central y añade barras de probabilidad estimada de 0 a 100 %.
