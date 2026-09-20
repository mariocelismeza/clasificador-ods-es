"""Exportación auxiliar desde el pipeline y el corpus reales; ejecutar tras el notebook."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'word_predicto_app' / 'artifacts'
MODEL = ROOT / 'word_predicto_app' / 'models' / 'modelo_pipeline.joblib'
model = joblib.load(MODEL)
df = pd.read_excel(ROOT / 'data' / 'Datos_textosODS.xlsx')
counts = df['ODS'].value_counts().sort_index()
assert set(map(int, counts.index)) == set(map(int, model.classes_))
(ART / 'class_distribution.json').write_text(json.dumps({str(int(k)): int(v) for k,v in counts.items()}, ensure_ascii=False, indent=2), encoding='utf-8')
terms = model.named_steps['preprocess'].named_steps['tfidf'].get_feature_names_out()
interpretations = [
    'Vocabulario general de desarrollo; sin ODS único',
    'Derechos e instituciones: asociación cualitativa con ODS 16',
    'Eje social frente a agua y energía; varios ODS',
    'Educación: asociación cualitativa con ODS 4',
    'Salud y atención: asociación cualitativa con ODS 3',
    'Género frente a educación: asociación cualitativa con ODS 5 y 4',
    'Energía frente a agua y clima: asociación con ODS 7, 6 y 13',
    'Agua frente a clima: asociación con ODS 6 y 13',
]
topics = []
for i, component in enumerate(model.named_steps['svd'].components_[:8]):
    selected = np.argsort(np.abs(component))[::-1][:10]
    topics.append({'componente': i+1, 'interpretacion': interpretations[i], 'terminos': [{'termino': str(terms[j]), 'peso': float(component[j])} for j in selected]})
(ART / 'lsa_topics.json').write_text(json.dumps(topics, ensure_ascii=False, indent=2), encoding='utf-8')
print('Distribución y 8 componentes exportados desde el corpus y el pipeline final.')
