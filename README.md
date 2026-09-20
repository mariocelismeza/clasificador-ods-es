# Clasificador de ODS en español

Clasificación de textos en español según los Objetivos de Desarrollo Sostenible (ODS) mediante limpieza de texto, TF-IDF, análisis semántico latente (LSA) y una SVM lineal. Incluye un notebook ejecutado y una aplicación interactiva en Streamlit.

El corpus suministrado contiene ejemplos de **16 ODS**. No hay ejemplos del ODS 17, por lo que el modelo no puede predecirlo. En el conjunto de prueba aislado (1.931 textos), el modelo obtuvo **F1 macro de 0,768** y **exactitud de 81,4 %**.

## Ejecutar la aplicación

Usa Python 3.11 o 3.12 desde la raíz del repositorio:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run word_predicto_app/streamlit_app.py
```

La aplicación permite clasificar texto libre con el mismo pipeline evaluado en el notebook. Muestra la predicción, los márgenes de decisión y probabilidades estimadas por calibración de temperatura.

## Entrega académica

- [Notebook ejecutado](Microproyecto2_ODS.ipynb)
- [Versión HTML del notebook](Microproyecto2_ODS.html)
- [Instrucciones y detalle de los artefactos](README_ENTREGA.md)

Para volver a ejecutar el notebook, usa `jupyter notebook Microproyecto2_ODS.ipynb` desde la raíz del repositorio. El corpus está en `data/Datos_textosODS.xlsx`. La implementación histórica en React y FastAPI se conserva en `legacy/`; la aplicación de la bonificación es la de Streamlit.

**Autores:** David Cardenas y Mario Celis.
