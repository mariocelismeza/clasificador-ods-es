"""Interfaz Streamlit oficial del pipeline final evaluado en el notebook."""
from base64 import b64encode
from datetime import datetime
from html import escape
from pathlib import Path
from io import BytesIO
import json
import sys

import joblib
import numpy as np
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ART = APP_DIR / "artifacts"
MODEL = APP_DIR / "models" / "modelo_pipeline.joblib"
CALIBRATED_MODEL = APP_DIR / "models" / "modelo_calibrado.joblib"
ICONS = APP_DIR / "assets" / "sdg-icons"
sys.path.insert(0, str(APP_DIR))
from text_pipeline import NOMBRES_ODS  # noqa: E402
from ods_content import DESCRIPCIONES_ODS  # noqa: E402

st.set_page_config(
    page_title="Clasificador ODS · Microproyecto 2",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown("""
<style>
.stApp {background:radial-gradient(circle at 50% -25%,#15304b 0%,#0a0e1a 54%);color:#e0e8f0}
[data-testid="stHeader"] {background:transparent}
.block-container {max-width:1480px;padding-top:1.15rem;padding-bottom:3rem}
h1,h2,h3 {letter-spacing:-.025em}
.brand {display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;padding:.2rem 0 .95rem;border-bottom:1px solid #243448}
.brand-left {display:flex;align-items:center;gap:.7rem}
.brand-mark {display:grid;place-items:center;width:38px;height:38px;border-radius:11px;color:#001f2e;background:linear-gradient(145deg,#9be3ff,#4d98c7);font-weight:900;font-size:22px;box-shadow:0 0 18px #7dd3fc35}
.brand-name {color:#f5f9fc;font-weight:750;font-size:1rem;line-height:1.3}
.brand-name small {color:#7dd3fc;background:#7dd3fc1b;border:1px solid #7dd3fc38;border-radius:4px;font-size:.57rem;padding:2px 5px;vertical-align:2px;margin-left:5px;letter-spacing:.07em}
.brand-sub {color:#9bb2c3;font-size:.69rem;line-height:1.5}
.model-status {display:inline-flex;align-items:center;gap:.48rem;padding:.42rem .78rem;border:1px solid #34485a;border-radius:999px;background:#111828;color:#d3e5ec;font-size:.72rem}
.model-status strong {color:#7dd3fc;font-weight:650}.status-dot {width:7px;height:7px;background:#34d399;border-radius:50%;box-shadow:0 0 8px #34d399}
.eyebrow {color:#7dd3fc;font-size:.7rem;font-weight:750;letter-spacing:.11em;text-transform:uppercase}
.breadcrumb {display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;border-bottom:1px solid #29364a;padding:0 0 .75rem;margin:.45rem 0 .95rem;color:#a0b4c4;font-size:.73rem}
.breadcrumb strong {color:#f4f8fb}.summary-chip {padding:.3rem .65rem;border:1px solid #34485a;background:#111828;border-radius:8px;color:#d3e5ec}
.hero-title {color:#f4f8fb;font-size:1.55rem;font-weight:750;line-height:1.2;margin:.4rem 0}
.hero-copy {color:#aabfce;max-width:90ch;margin:0 0 1.25rem;line-height:1.55;font-size:.86rem}
.panel-title {display:flex;align-items:center;gap:.55rem;color:#f2f7fa;font-size:.76rem;font-weight:750;letter-spacing:.06em;text-transform:uppercase}
.panel-icon {display:inline-grid;place-items:center;width:25px;height:25px;border-radius:7px;background:#7dd3fc1a;border:1px solid #7dd3fc38;color:#7dd3fc;font-size:.85rem}
.panel-rule {height:1px;background:#2b3a4e;margin:.6rem 0 .95rem}
.pipeline-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:.8rem 0}
.pipeline-step {background:#1a2438b7;border:1px solid #334051;border-radius:10px;padding:10px;min-width:0}
.pipeline-step span {display:block;color:#9cb3c4;font-size:.62rem;text-transform:uppercase;letter-spacing:.07em}
.pipeline-step strong {display:block;color:#f3f7fa;font-size:.77rem;margin:.22rem 0;overflow-wrap:anywhere}
.pipeline-step small {color:#9fb1be;font-size:.66rem}
.ready {border:1px solid #34485a;border-radius:10px;background:#141e30;padding:.65rem .8rem;color:#d8e7ec;font-size:.77rem;margin-bottom:.7rem}
.ready strong {color:#5ee3aa}
.result-head {display:flex;align-items:center;justify-content:space-between;gap:8px;border-bottom:1px solid #35465a;padding-bottom:.8rem;margin-bottom:1rem}
.result-badge {background:#7dd3fc;color:#001f2e;border-radius:5px;padding:3px 8px;font-weight:800;font-size:.66rem;letter-spacing:.08em}
.muted-label {color:#9fb6c7;font-size:.68rem}
.result-main {display:flex;align-items:center;gap:15px;min-height:76px}
.result-main img,.result-icon {width:66px;height:66px;border-radius:11px;flex:none;box-shadow:0 3px 12px #0005}
.result-icon {display:grid;place-items:center;background:#202c42;color:#8fa6b8;font-size:2rem;border:1px solid #35465a}
.result-kicker {color:#7dd3fc;font-size:.68rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}
.result-title {color:#f4f8fb;font-size:1.45rem;font-weight:780;line-height:1.2;margin:.3rem 0}
.result-note {color:#aabfce;line-height:1.5;font-size:.78rem;margin:.85rem 0}
.margin-box {background:#111b2d;border:1px solid #34485a;border-radius:11px;padding:14px;margin-top:1rem}
.margin-head {display:flex;align-items:baseline;justify-content:space-between;gap:10px;color:#adc3d2;font-size:.75rem}
.margin-head strong {color:#f3f8fc;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:1.65rem}
.signed-track {position:relative;height:12px;border-radius:999px;background:#27344b;margin:13px 0 6px;overflow:hidden}
.signed-track::after {content:"";position:absolute;left:50%;top:0;bottom:0;width:2px;background:#b1c6d4a6;z-index:2}
.signed-fill {position:absolute;top:1px;bottom:1px;border-radius:999px;background:#7389a3}
.signed-fill.winner {background:linear-gradient(90deg,#70c7f1,#19c9a2);box-shadow:0 0 10px #26bde2a3}
.margin-axis {display:flex;justify-content:space-between;color:#91aabd;font-size:.65rem;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.margin-detail {display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;border-top:1px solid #2b3c52;margin-top:12px;padding-top:10px;color:#a9c0ce;font-size:.7rem}
.margin-detail strong {color:#e7f3f8;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.term-heading {display:flex;justify-content:space-between;gap:8px;margin:1.1rem 0 .55rem;color:#eef6fa;font-size:.75rem;font-weight:700}
.term-heading small {color:#97afbf;font-size:.68rem;font-weight:400}
.term-chips {display:flex;flex-wrap:wrap;gap:7px;padding-bottom:14px}
.term-chip {display:inline-flex;align-items:center;gap:8px;background:#202e45;border:1px solid #364b65;border-radius:8px;padding:5px 9px;color:#dce9f2;font-size:.74rem}
.term-chip strong {color:#82cefa;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.68rem;background:#7dd3fc16;padding:2px 4px;border-radius:4px}
.comparison-row {margin:10px 0 14px}
.comparison-head {display:flex;align-items:center;justify-content:space-between;gap:10px;color:#e4edf3;font-size:.77rem}
.comparison-name {display:flex;align-items:center;gap:9px;min-width:0}.comparison-name img {width:31px;height:31px;border-radius:5px;flex:none}.comparison-name span {overflow-wrap:anywhere}
.comparison-value {color:#bed2df;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;white-space:nowrap}
.comparison-row .signed-track {height:10px;margin:8px 0 0}
.comparison-note {color:#95afbe;font-size:.69rem;line-height:1.5;margin-top:.65rem}
.probability-intro {color:#adc4d2;font-size:.75rem;line-height:1.5;margin:.15rem 0 .8rem}
.probability-row {padding:9px 0}
.probability-head {display:flex;align-items:center;justify-content:space-between;gap:10px;color:#e4edf3;font-size:.77rem}
.probability-head strong {color:#e8f4fa;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.86rem;white-space:nowrap}
.probability-row.winner .probability-head strong {color:#7dd3fc}
.probability-track {height:11px;border-radius:999px;background:#27344b;margin-top:8px;overflow:hidden}
.probability-fill {height:100%;border-radius:999px;background:#7389a3}
.probability-row.winner .probability-fill {background:linear-gradient(90deg,#7dd3fc,#25c9a7);box-shadow:0 0 9px #25c9a766}
.probability-foot {color:#95afbe;font-size:.69rem;line-height:1.5;margin-top:.6rem}
.candidate {display:flex;align-items:center;justify-content:space-between;gap:8px;color:#dce7ef;border-top:1px solid #28384d;padding:9px 0;font-size:.76rem}
.candidate strong {color:#7dd3fc;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.metrics-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.metric-card {background:#141e30;border:1px solid #324355;border-radius:11px;padding:12px}
.metric-card span {display:block;color:#9fb6c7;font-size:.69rem;text-transform:uppercase}.metric-card strong {display:block;color:#f7fbfd;font-size:1.38rem;margin:.2rem 0}.metric-card small {color:#9fb6c7;font-size:.67rem}
.ods-rank-grid {display:grid;grid-template-columns:repeat(9,minmax(0,1fr));gap:8px;margin:.7rem 0 1.2rem}
.ods-rank {background:#151f31;border:1px solid #34465a;border-radius:9px;padding:9px;color:#b9cad7;font-size:.69rem;display:flex;flex-direction:column;gap:5px}
.ods-rank strong {color:#e0e8f0;font-size:.85rem}.ods-rank.winner {border-color:#7dd3fc;background:#15405a;color:#e7f7ff;box-shadow:0 0 15px #7dd3fc31}.ods-rank.winner strong{color:#7dd3fc}.ods-rank.unavailable{opacity:.55}
.ods-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:.8rem}
.ods-card {background:linear-gradient(135deg,#182338,#101a2b);border:1px solid #28384d;border-radius:14px;padding:15px;box-shadow:0 8px 24px #0003}
.ods-head {display:flex;align-items:center;gap:13px}
.ods-head img {width:54px;height:54px;border-radius:8px;flex:none}
.ods-name {color:#f3f7fa;font-weight:700;line-height:1.25}
.ods-count {color:#9fb6c7;font-size:.8rem;margin-top:3px}
.ods-terms {color:#b6c9d5;font-size:.84rem;line-height:1.4;margin-top:10px}
.ods-description {color:#d2e0e8;font-size:.87rem;line-height:1.4;margin-top:10px}
.footnote {color:#94aabd;font-size:.75rem;line-height:1.5;margin-top:1.2rem}
.app-footer {border-top:1px solid #29394a;margin-top:2.5rem;padding:1.4rem 0;color:#9fb1bf;text-align:center;font-size:.72rem;line-height:1.7}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#344050 !important;background:linear-gradient(135deg,#141c2ebe,#0f1524e8);border-radius:16px;box-shadow:0 8px 28px #0004}
.st-key-result_panel [data-testid="stVerticalBlockBorderWrapper"] {border-color:#35617a !important;background:linear-gradient(135deg,#18283be5,#111828f5)}
.stTabs [role="tablist"] {gap:5px;border:1px solid #273747;background:#111828;border-radius:12px;padding:4px;width:max-content;max-width:100%;overflow-x:auto;margin:1rem 0 .4rem}
.stTabs [role="tab"] {border-radius:8px;min-height:34px;padding:4px 12px;color:#a0b4c4;font-size:.76rem}
.stTabs [role="tab"][aria-selected="true"] {background:#7dd3fc1b;color:#7dd3fc;border:1px solid #7dd3fc4d;font-weight:700}
.stTabs .react-aria-SelectionIndicator {display:none}
.stButton button[kind="primary"] {font-weight:750;background:linear-gradient(90deg,#9be3ff,#56b6e8);color:#001f2e;border:0;box-shadow:0 0 20px #7dd3fc2e}
.stTextArea textarea {background:#0e1524;border-color:#34465b;min-height:210px}
.st-key-input_panel .stButton button {border-radius:9px}
.st-key-examples_bar {gap:6px!important;margin:.15rem 0 .35rem}
.st-key-examples_bar [data-testid="stButton"] button {width:auto!important;min-height:26px;height:26px;padding:3px 10px 3px 8px;border-radius:999px!important;background:#192335;border:1px solid #324154;color:#c8d5df;font-size:.72rem;font-weight:450;white-space:nowrap;box-shadow:none}
.st-key-examples_bar [data-testid="stButton"] button:hover {background:#223149;border-color:#6eaac6;color:#fff}
.st-key-examples_bar [data-testid="stButton"] button::before {content:"";display:inline-block;width:8px;height:8px;flex:none;border-radius:50%;margin-right:6px;background:var(--example-color,#7dd3fc);box-shadow:0 0 5px var(--example-color,#7dd3fc)}
.st-key-example_educacion {--example-color:#c5192d}.st-key-example_energia {--example-color:#fcc30b}.st-key-example_marina {--example-color:#0a97d9}.st-key-example_pobreza {--example-color:#e5243b}.st-key-example_genero {--example-color:#ff3a21}.st-key-example_institucionalidad,.st-key-example_acceso_justicia {--example-color:#00689d}
@media(max-width:900px){.st-key-classifier_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"]{flex-direction:column!important}.st-key-classifier_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{width:100%!important;flex:0 0 100%!important}}
@media(max-width:800px){.ods-grid{grid-template-columns:1fr}.ods-rank-grid{grid-template-columns:repeat(4,minmax(0,1fr))}.model-status{display:none}.pipeline-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.hero-title{font-size:1.38rem}}
@media(max-width:490px){.pipeline-grid{grid-template-columns:1fr}}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    return joblib.load(MODEL)


@st.cache_resource
def load_calibrated_model():
    return joblib.load(CALIBRATED_MODEL)


@st.cache_data
def read_json(name):
    return json.loads((ART / name).read_text(encoding="utf-8"))


@st.cache_data
def icon_data(ods):
    return b64encode((ICONS / f"goal-{ods}.svg").read_bytes()).decode("ascii")


try:
    model = load_model()
    calibrated_model = load_calibrated_model()
    metrics = read_json("metrics_summary.json")
    calibration = read_json("calibration_summary.json")
    terms = read_json("terminos_por_ods.json")
    report = read_json("reporte_por_ods.json")
    pairs = read_json("pares_confusion.json")
    topics = read_json("lsa_topics.json")
    distribution = read_json("class_distribution.json")
    classes = [int(value) for value in model.classes_]
    assert set(classes) == set(map(int, distribution))
    assert metrics["n_componentes_lsa"] == model.named_steps["svd"].n_components
    assert metrics["vocabulario_tfidf"] == len(model.named_steps["preprocess"].named_steps["tfidf"].vocabulary_)
    assert metrics["hiperparametros_pipeline"]["classifier__C"] == model.named_steps["classifier"].C
    assert metrics["hiperparametros_pipeline"]["classifier__class_weight"] == model.named_steps["classifier"].class_weight
    assert list(map(int, calibrated_model.classes_)) == classes
    assert calibration["metodo"] == "temperature" and calibration["predicciones_preservadas"]
    assert calibration["n_test"] == metrics["n_test"]
    ngrams = model.named_steps["preprocess"].named_steps["tfidf"].ngram_range
except (FileNotFoundError, ValueError, ImportError, KeyError, AssertionError) as exc:
    st.error(f"No se pudieron cargar artefactos coherentes. Revise el entorno de README_ENTREGA.md. Detalle: {exc}")
    st.stop()


def ods_name(number):
    return f"ODS {number} · {NOMBRES_ODS[number]}"


def es_int(number):
    return f"{number:,}".replace(",", ".")


def probability_label(probability):
    percentage = 100.0 * float(probability)
    if percentage < 0.05:
        return "<0.1 %"
    if percentage >= 99.95:
        return ">99.9 %"
    return f"{percentage:.1f} %"


def clear_result():
    st.session_state.result = None


def set_example(text):
    st.session_state.input_text = text
    clear_result()


def clear_input():
    st.session_state.input_text = ""
    clear_result()


def classify(text):
    prediction = int(model.predict([text])[0])
    scores = np.asarray(model.decision_function([text])).reshape(-1)
    ranking = sorted(zip(classes, scores), key=lambda item: item[1], reverse=True)
    probabilities = np.asarray(calibrated_model.predict_proba([text])).reshape(-1)
    probability_ranking = sorted(zip(classes, probabilities), key=lambda item: item[1], reverse=True)
    assert int(probability_ranking[0][0]) == prediction
    preprocess = model.named_steps["preprocess"]
    cleaned = preprocess.named_steps["cleaner"].transform([text])
    tfidf = preprocess.named_steps["tfidf"].transform(cleaned)
    vocabulary = preprocess.named_steps["tfidf"].get_feature_names_out()
    indices = np.argsort(tfidf.data)[::-1][:8]
    matched = [vocabulary[tfidf.indices[index]] for index in indices]
    term_weights = [(vocabulary[tfidf.indices[index]], float(tfidf.data[index])) for index in indices]
    return {"prediction": prediction, "ranking": ranking, "probabilities": probability_ranking,
            "terms": matched, "term_weights": term_weights}


def margin_bar(score, scale, winner=False):
    """Barra firmada con cero central y escala común para un solo texto."""
    width = min(50.0, 50.0 * abs(float(score)) / scale) if scale else 0.0
    left = 50.0 if score >= 0 else 50.0 - width
    return (f'<div class="signed-track" role="img" aria-label="Margen {float(score):+.3f}, cero en el centro">'
            f'<div class="signed-fill {"winner" if winner else ""}" '
            f'style="left:{left:.2f}%;width:{width:.2f}%"></div></div>')


def metric_cards():
    st.markdown(
        '<div class="metrics-grid">'
        f'<div class="metric-card"><span>F1 macro · test</span><strong>{metrics["f1_macro_test"]:.3f}</strong><small>{es_int(metrics["n_test"])} textos de prueba</small></div>'
        f'<div class="metric-card"><span>Exactitud · test</span><strong>{metrics["accuracy_test"]:.1%}</strong><small>Conjunto de prueba aislado</small></div>'
        '</div>', unsafe_allow_html=True,
    )


if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "result" not in st.session_state:
    st.session_state.result = None
elif st.session_state.result is not None and (
    "probabilities" not in st.session_state.result or "term_weights" not in st.session_state.result
):
    previous_text = st.session_state.get("input_text", "")
    st.session_state.result = classify(previous_text) if len(previous_text.split()) >= 5 else None
if "history" not in st.session_state:
    st.session_state.history = []

st.markdown(
    '<div class="brand"><div class="brand-left"><div class="brand-mark">◎</div><div>'
    '<div class="brand-name">Clasificador de ODS <small>AI CORE</small></div>'
    '<div class="brand-sub">Proyecto académico · Maestría en IA</div></div></div>'
    '<div class="model-status"><span class="status-dot"></span>Modelo cargado · '
    '<strong>TF-IDF + LSA + LinearSVC</strong></div></div>', unsafe_allow_html=True,
)
classify_tab, explore_tab, errors_tab, about_tab = st.tabs([
    "Clasificador en vivo", "Explorador ODS", "Matriz de confusión", "Acerca del proyecto",
])

with classify_tab:
    st.markdown(
        '<div class="breadcrumb"><span>Plataforma &nbsp;›&nbsp; Clasificador en vivo &nbsp;›&nbsp; '
        '<strong>Inferencia de texto</strong></span><span class="summary-chip">'
        f'{len(classes)} ODS modelados &nbsp;·&nbsp; Corpus OSDG (ES)</span></div>'
        '<div class="eyebrow">Análisis de texto en español</div>'
        '<div class="hero-title">Clasificador de Objetivos de Desarrollo Sostenible</div>'
        '<div class="hero-copy">Analiza una propuesta o un texto libre con el pipeline del proyecto: '
        'limpieza en español, TF-IDF, análisis semántico latente y LinearSVC. '
        'La salida es una sugerencia para revisar en su contexto.</div>', unsafe_allow_html=True,
    )
    with st.container(key="classifier_layout"):
        left, right = st.columns([1, 1], gap="large")
        with left:
            with st.container(border=True, key="input_panel"):
                st.markdown('<div class="panel-title"><span class="panel-icon">✎</span> Texto a clasificar (español)</div><div class="panel-rule"></div>', unsafe_allow_html=True)
                st.caption("Cargar ejemplos predefinidos del corpus analítico:")
                examples = [
                    ("educacion", "Educación rural y becas", "Garantizar una educación inclusiva, equitativa y de calidad y promover oportunidades de aprendizaje durante toda la vida para todos los niños y jóvenes en zonas rurales mediante becas, tecnología digital y formación docente comunitaria."),
                    ("energia", "Energía y transición", "La transición hacia fuentes de energía renovable como la solar y la eólica es clave para reducir la dependencia de combustibles fósiles y garantizar el acceso universal a energía asequible y no contaminante."),
                    ("marina", "Conservación marina", "La sobrepesca, la pesca ilegal y la contaminación de los océanos afectan a los peces y los ecosistemas marinos. Proteger arrecifes de coral, mares y especies acuáticas con áreas marinas protegidas y pesca sostenible ayuda a conservar la vida submarina."),
                    ("pobreza", "Transferencias condicionadas", "Un programa de transferencias monetarias condicionadas, combinado con microcréditos para pequeños productores rurales, permitió reducir la pobreza extrema en la región al financiar insumos agrícolas, vivienda básica y acceso a agua potable."),
                    ("genero", "Brecha salarial de género", "Pese a los avances normativos, la brecha salarial entre hombres y mujeres persiste en cargos directivos; se proponen cuotas de liderazgo femenino, licencias parentales equitativas y auditorías salariales obligatorias para cerrarla."),
                    ("institucionalidad", "Transparencia e instituciones", "El fortalecimiento de la independencia judicial, junto con mecanismos de rendición de cuentas y portales de datos abiertos, reduce los índices de corrupción y mejora la confianza ciudadana en las instituciones públicas."),
                    ("acceso_justicia", "Acceso a la justicia", "Centros de asistencia jurídica gratuita y jornadas móviles de registro civil permitieron que comunidades rurales sin documentos de identidad accedieran a la justicia, redujeran la violencia intrafamiliar y denunciaran casos de trata de personas."),
                ]
                with st.container(horizontal=True, wrap=True, key="examples_bar", gap="small"):
                    for example_id, label, sample in examples:
                        st.button(label, key=f"example_{example_id}", on_click=set_example,
                                  args=(sample,), width="content")
                text = st.text_area(
                    "Entrada de texto natural",
                    key="input_text",
                    height=220,
                    placeholder="Escribe aquí el resumen de un proyecto, una propuesta comunitaria o un documento público...",
                    on_change=clear_result,
                )
                words = len(text.split())
                st.caption(f"{len(text)} caracteres · {words} palabras" + (" · Se recomiendan al menos cinco palabras." if words < 5 else " · Texto listo para analizar."))
                st.markdown(
                    '<div class="panel-title"><span class="panel-icon">⚙</span> Parámetros del pipeline</div>'
                    '<div class="pipeline-grid">'
                    f'<div class="pipeline-step"><span>Vectorizador</span><strong>TF-IDF {ngrams}</strong><small>Unigramas y bigramas</small></div>'
                    f'<div class="pipeline-step"><span>Reducción</span><strong>LSA / TruncatedSVD</strong><small>{metrics["n_componentes_lsa"]} componentes</small></div>'
                    f'<div class="pipeline-step"><span>Clasificador</span><strong>LinearSVC</strong><small>C={metrics["hiperparametros_pipeline"]["classifier__C"]}</small></div>'
                    '</div>', unsafe_allow_html=True,
                )
                action_col, clear_col = st.columns([3, 1])
                if action_col.button("Predecir ODS", type="primary", width="stretch"):
                    if words < 5:
                        st.warning("Escribe al menos cinco palabras antes de clasificar.")
                    else:
                        st.session_state.result = classify(text)
                        st.session_state.history = ([{
                            "time": datetime.now().strftime("%H:%M"),
                            "text": text[:90] + ("…" if len(text) > 90 else ""),
                            "ods": st.session_state.result["prediction"],
                        }] + st.session_state.history)[:10]
                clear_col.button("Limpiar", on_click=clear_input, width="stretch")
            with st.expander("Analizar varios textos desde CSV o TXT"):
                st.caption("CSV: una columna llamada `texto` o `text`. TXT: un texto por línea. Se procesan hasta 500 textos y se descargan los resultados.")
                uploaded = st.file_uploader("Archivo CSV o TXT", type=["csv", "txt"], key="batch_file")
                if uploaded is not None and st.button("Procesar archivo", key="batch_submit"):
                    try:
                        if uploaded.size > 2_000_000:
                            raise ValueError("El archivo supera 2 MB.")
                        if uploaded.name.lower().endswith(".csv"):
                            table = pd.read_csv(BytesIO(uploaded.getvalue()))
                            col = next((c for c in ("texto", "text") if c in table.columns), None)
                            if col is None:
                                raise ValueError("El CSV requiere una columna 'texto' o 'text'.")
                            texts = table[col].dropna().astype(str).str.strip().tolist()
                        else:
                            texts = [line.strip() for line in uploaded.getvalue().decode("utf-8-sig").splitlines()]
                        texts = [line for line in texts if line and len(line) <= 20_000]
                        if not texts or len(texts) > 500:
                            raise ValueError("Incluye entre 1 y 500 textos no vacíos de máximo 20.000 caracteres.")
                        predicted_batch = model.predict(texts)
                        st.session_state.batch_result = pd.DataFrame({"texto": texts, "ods_predicho": predicted_batch,
                                                                        "nombre_ods": [NOMBRES_ODS[int(x)] for x in predicted_batch]})
                    except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as exc:
                        st.error(f"No se pudo procesar el archivo: {exc}")
                if st.session_state.get("batch_result") is not None:
                    batch = st.session_state.batch_result
                    st.dataframe(batch, hide_index=True, width="stretch")
                    st.download_button("Descargar resultados CSV", batch.to_csv(index=False).encode("utf-8-sig"),
                                       file_name="clasificaciones_ods.csv", mime="text/csv")
        with right:
            result = st.session_state.result
            st.markdown(f'<div class="ready"><span class="status-dot" style="display:inline-block;margin-right:8px"></span>'
                        f'{"Inferencia completada" if result else "Modelo cargado · listo para inferencia"} &nbsp;·&nbsp; '
                        '<strong>LinearSVC listo</strong></div>', unsafe_allow_html=True)
            with st.container(border=True, key="result_panel"):
                st.markdown('<div class="result-head"><span class="result-badge">PREDICCIÓN PRINCIPAL</span>'
                            '<span class="muted-label">Modelo final del notebook</span></div>', unsafe_allow_html=True)
                if result is None:
                    st.markdown('<div class="result-main"><div class="result-icon">—</div><div>'
                                '<div class="result-kicker">Sin predicción todavía</div>'
                                '<div class="result-title">Ingresa un texto y presiona “Predecir ODS”</div></div></div>'
                                '<div class="result-note">El modelo distingue los 16 ODS presentes en el corpus.</div>',
                                unsafe_allow_html=True)
                else:
                    predicted = result["prediction"]
                    winner_margin = float(result["ranking"][0][1])
                    second_margin = float(result["ranking"][1][1])
                    score_scale = max(abs(float(score)) for _, score in result["ranking"])
                    st.markdown(
                        f'<div class="result-main"><img src="data:image/svg+xml;base64,{icon_data(predicted)}" alt="Ícono ODS {predicted}">'
                        f'<div><div class="result-kicker">Objetivo {predicted} · Agenda 2030</div>'
                        f'<div class="result-title">{escape(NOMBRES_ODS[predicted])}</div></div></div>'
                        '<div class="result-note">Sugerencia automática. Comprueba el sentido completo del texto antes de asignar el ODS.</div>'
                        '<div class="margin-box"><div class="margin-head"><span>Margen de decisión de LinearSVC</span>'
                        f'<strong>{winner_margin:+.3f}</strong></div>'
                        + margin_bar(winner_margin, score_scale, winner=True)
                        + f'<div class="margin-axis"><span>−{score_scale:.2f}</span><span>0</span><span>+{score_scale:.2f}</span></div>'
                        + f'<div class="margin-detail"><span>Escala común para este texto</span><span>Diferencia frente al 2.º: <strong>{winner_margin - second_margin:+.3f}</strong></span></div></div>',
                        unsafe_allow_html=True,
                    )
                    chips = ''.join(f'<div class="term-chip">{escape(term)}<strong>{weight:.2f}</strong></div>'
                                    for term, weight in result["term_weights"][:6])
                    st.markdown('<div class="term-heading"><span>Términos con mayor peso TF-IDF</span>'
                                '<small>Representación del texto</small></div>'
                                f'<div class="term-chips">{chips}</div>', unsafe_allow_html=True)
                    with st.expander("Ver ranking y términos técnicos"):
                        st.caption("Los márgenes de LinearSVC ordenan candidatos dentro de este texto. La longitud de cada barra usa la misma escala firmada, con cero central. No son porcentajes ni probabilidades.")
                        top = pd.DataFrame([{"ODS": ods_name(ods), "Margen": round(float(score), 3)} for ods, score in result["ranking"][:5]])
                        st.dataframe(top, hide_index=True, width="stretch")
                        st.caption("Términos con mayor peso TF-IDF: " + (", ".join(result["terms"]) if result["terms"] else "ninguno del vocabulario"))
                        st.caption("Describen la representación del texto; no explican por sí solos la predicción.")
            if result is not None:
                with st.container(border=True, key="probability_panel"):
                    st.markdown('<div class="panel-title"><span class="panel-icon">▥</span> Probabilidades calibradas</div>'
                                '<div class="panel-rule"></div>'
                                '<div class="probability-intro">Distribución estimada entre los 16 ODS que el modelo conoce. '
                                'Las barras suman 100 % entre todas las clases.</div>', unsafe_allow_html=True)
                    probability_rows = []
                    for rank, (ods, probability) in enumerate(result["probabilities"][:3]):
                        percentage = 100.0 * float(probability)
                        probability_rows.append(
                            f'<div class="probability-row {"winner" if rank == 0 else ""}">'
                            f'<div class="probability-head"><div class="comparison-name">'
                            f'<img src="data:image/svg+xml;base64,{icon_data(ods)}" alt="Ícono ODS {ods}">'
                            f'<span>ODS {ods} · {escape(NOMBRES_ODS[ods])}</span></div>'
                            f'<strong>{escape(probability_label(probability))}</strong></div>'
                            f'<div class="probability-track" role="progressbar" aria-label="ODS {ods}" '
                            f'aria-valuemin="0" aria-valuemax="100" aria-valuenow="{percentage:.1f}">'
                            f'<div class="probability-fill" style="width:{percentage:.2f}%"></div></div></div>'
                        )
                    st.markdown(''.join(probability_rows) +
                                '<div class="probability-foot">Estimaciones por calibración de temperatura; '
                                'un porcentaje individual no garantiza que la clasificación sea correcta. '
                                'La calibración se evaluó en el test aislado.</div>', unsafe_allow_html=True)
                    with st.expander("Ver los 16 ODS y la evaluación de calibración"):
                        st.dataframe(pd.DataFrame([
                            {"ODS": ods_name(ods), "Probabilidad estimada": probability_label(probability)}
                            for ods, probability in result["probabilities"]
                        ]), hide_index=True, width="stretch")
                        st.caption(f'Log loss en test: {calibration["log_loss_test"]:.3f} · '
                                   f'ECE de la clase ganadora: {calibration["ece_top_label_test"]:.3f} · '
                                   f'{calibration["cv_folds"]} folds agrupados en entrenamiento.')
                with st.container(border=True, key="comparison_panel"):
                    st.markdown('<div class="panel-title"><span class="panel-icon">▥</span> Comparación de márgenes</div>'
                                '<div class="panel-rule"></div>', unsafe_allow_html=True)
                    rows = []
                    for rank, (ods, score) in enumerate(result["ranking"][:3]):
                        rows.append(
                            f'<div class="comparison-row"><div class="comparison-head">'
                            f'<div class="comparison-name"><img src="data:image/svg+xml;base64,{icon_data(ods)}" alt="Ícono ODS {ods}">'
                            f'<span>ODS {ods} · {escape(NOMBRES_ODS[ods])}{" · ganador" if rank == 0 else ""}</span></div>'
                            f'<strong class="comparison-value">{float(score):+.3f}</strong></div>'
                            + margin_bar(score, score_scale, winner=rank == 0) + '</div>'
                        )
                    st.markdown(''.join(rows) + '<div class="comparison-note">Todas las barras comparten la escala del resultado principal: '
                                'izquierda = margen negativo, derecha = positivo. Muestran puntajes de decisión, no certeza estadística.</div>',
                                unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown('<div class="panel-title"><span class="panel-icon">▥</span> Rendimiento del modelo</div><div class="panel-rule"></div>', unsafe_allow_html=True)
                metric_cards()
                st.markdown('<div class="footnote">El ODS 17 no tiene ejemplos en el corpus suministrado y el modelo no puede predecirlo.</div>', unsafe_allow_html=True)
                if result is not None:
                    export = {"texto": text, "ods_predicho": result["prediction"],
                              "nombre_ods": NOMBRES_ODS[result["prediction"]],
                              "margenes": [{"ods": ods, "margen": float(score)} for ods, score in result["ranking"]],
                              "probabilidades_calibradas": [{"ods": ods, "probabilidad": float(probability)}
                                                           for ods, probability in result["probabilities"]]}
                    st.download_button("Exportar resultado JSON", json.dumps(export, ensure_ascii=False, indent=2),
                                       file_name="resultado_ods.json", mime="application/json")
            with st.expander("Historial de esta sesión"):
                if not st.session_state.history:
                    st.caption("Todavía no hay predicciones en esta sesión.")
                for item in st.session_state.history:
                    st.write(f'**{item["time"]} · ODS {item["ods"]}** — {item["text"]}')
    if result is not None:
        st.markdown('<div class="panel-title" style="margin-top:1.3rem"><span class="panel-icon">▦</span> Ranking de ODS para este texto</div>', unsafe_allow_html=True)
        st.caption("Orden de los márgenes de decisión; no representan probabilidades. El ODS 17 no fue entrenado.")
        rank_map = {ods: idx + 1 for idx, (ods, _) in enumerate(result["ranking"])}
        st.markdown('<div class="ods-rank-grid">' + ''.join(
            f'<div class="ods-rank {"winner" if ods == result["prediction"] else ""}">'
            f'<span>ODS {ods}</span><strong>#{rank_map[ods]}</strong></div>' for ods in classes
        ) + '<div class="ods-rank unavailable"><span>ODS 17</span><strong>—</strong></div></div>', unsafe_allow_html=True)

with explore_tab:
    st.markdown('<div class="hero-title">Explorador de ODS</div><div class="hero-copy">Los 16 objetivos presentes en el corpus, con su frecuencia y términos reales. Las descripciones breves son contenido editorial basado en las definiciones de la ONU.</div>', unsafe_allow_html=True)
    term_map = {int(row["ODS"]): row["términos_más_frecuentes"] for row in terms}
    cards = []
    for ods in classes:
        icon = icon_data(ods)
        cards.append(
            f'<div class="ods-card"><div class="ods-head"><img src="data:image/svg+xml;base64,{icon}" alt="Ícono ODS {ods}">'
            f'<div><div class="ods-name">ODS {ods} · {escape(NOMBRES_ODS[ods])}</div>'
            f'<div class="ods-count">{es_int(distribution[str(ods)])} textos del corpus</div></div></div>'
            f'<div class="ods-description">{escape(DESCRIPCIONES_ODS[ods])}</div>'
            f'<div class="ods-terms"><strong>Términos frecuentes:</strong> {escape(term_map[ods])}</div></div>'
        )
    st.markdown('<div class="ods-grid">' + "".join(cards) + '</div>', unsafe_allow_html=True)
    st.info("ODS 17 · Alianzas para lograr los objetivos: sin ejemplos de entrenamiento en este corpus.")
    st.caption("Descripciones resumidas por el equipo a partir de [las definiciones de la ONU](https://sdgs.un.org/es/goals). Uso académico de los íconos; este proyecto no está afiliado ni respaldado por la ONU.")

with errors_tab:
    st.markdown('<div class="hero-title">Matriz de confusión</div>', unsafe_allow_html=True)
    st.caption(f'Resultado del modelo final en {es_int(metrics["n_test"])} textos de prueba aislados; la matriz está normalizada por ODS real.')
    with st.container(border=True):
        st.image(str(ART / "confusion_matrix.png"), caption="Matriz de confusión normalizada, generada en el notebook.", width="stretch")
    with st.container(border=True):
        st.markdown('<div class="panel-title"><span class="panel-icon">↗</span> Pares de confusión más frecuentes</div><div class="panel-rule"></div>', unsafe_allow_html=True)
        for pair in pairs:
            st.markdown(f'<div class="candidate"><span>ODS {pair["ods_real"]} → ODS {pair["ods_predicho"]}</span>'
                        f'<strong>{pair["n_casos"]} casos</strong></div>', unsafe_allow_html=True)
        st.caption("Estos pares sugieren posible solapamiento temático; la matriz no prueba la causa de cada error.")

with about_tab:
    st.markdown('<div class="hero-title">Acerca del proyecto</div><div class="hero-copy">Bonificación de Streamlit del Microproyecto 2 · Maestría en Inteligencia Artificial · David Cardenas y Mario Celis.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"""La aplicación utiliza el **mismo pipeline final** documentado en `Microproyecto2_ODS.ipynb`: limpieza de texto en español → TF-IDF ({es_int(metrics['vocabulario_tfidf'])} términos) → LSA / TruncatedSVD ({metrics['n_componentes_lsa']} componentes) → LinearSVC. Los porcentajes se obtienen mediante calibración de temperatura ajustada con cinco folds agrupados del entrenamiento. El corpus deriva de OSDG Community Dataset traducido al español y aumentado.""")
    st.markdown("### Evaluación del modelo final")
    st.caption("Resultados calculados en el notebook sobre textos de prueba que no se utilizaron para entrenar ni seleccionar hiperparámetros.")
    a, b, c, d = st.columns(4)
    a.metric("F1 macro · test", f'{metrics["f1_macro_test"]:.3f}')
    b.metric("Accuracy · test", f'{metrics["accuracy_test"]:.3f}')
    c.metric("F1 ponderado · test", f'{metrics["f1_weighted_test"]:.3f}')
    d.metric("F1 macro · CV", f'{metrics["f1_macro_cv"]:.3f}')
    st.caption("F1 macro es la métrica principal porque da el mismo peso a cada ODS. CV es la validación cruzada sobre entrenamiento; el test se mantuvo aislado.")
    results_tab, lsa_tab, method_tab = st.tabs(["Resultados por ODS", "Análisis LSA", "Método y alcance"])
    with results_tab:
        st.write(f'Entrenamiento: **{es_int(metrics["n_train"])}** textos · Test: **{es_int(metrics["n_test"])}** · Vocabulario TF-IDF: **{es_int(metrics["vocabulario_tfidf"])}** términos')
        st.write(f'Pipeline seleccionado: **{metrics["n_componentes_lsa"]}** componentes LSA · LinearSVC **C={metrics["hiperparametros_pipeline"]["classifier__C"]}** · ponderación **{metrics["hiperparametros_pipeline"]["classifier__class_weight"]}**')
        st.markdown("#### Precision, recall y F1 por ODS en test")
        per_class = pd.DataFrame(report).rename(columns={"ods": "ODS", "precision": "Precisión", "recall": "Recall", "f1-score": "F1", "support": "Casos de test"})
        per_class["ODS"] = per_class["ODS"].astype(int)
        st.dataframe(per_class[["ODS", "Precisión", "Recall", "F1", "Casos de test"]], hide_index=True, width="stretch")
        st.markdown("#### Distribución del corpus")
        counts = pd.DataFrame([{"ODS": ods, "Textos": distribution[str(ods)]} for ods in classes]).set_index("ODS")
        st.bar_chart(counts, horizontal=True)
    with lsa_tab:
        st.caption("Componentes calculadas por TruncatedSVD sobre TF-IDF. El signo de una componente es arbitrario.")
        for topic in topics:
            with st.expander(f'Componente {topic["componente"]} · {topic["interpretacion"]}', expanded=topic["componente"] <= 2):
                st.dataframe(pd.DataFrame(topic["terminos"]), hide_index=True, width="stretch")
                st.caption("Interpretación cualitativa de los términos, no asignación supervisada de ODS.")
    with method_tab:
        st.markdown("""El corpus deriva de OSDG Community Dataset, traducido al español y aumentado. El pipeline aplica limpieza, TF-IDF de unigramas y bigramas, reducción LSA con `TruncatedSVD` y clasificación mediante `LinearSVC`.

La selección utilizó F1 macro y validación cruzada estratificada por ODS y agrupada por duplicados o casi duplicados. Cada fold ajustó de nuevo todas las transformaciones. El test quedó fuera de la selección. El desempeño en textos de otras fuentes puede diferir.

El ODS 17 no está representado en el corpus y no puede ser predicho. Esta aplicación usa el pipeline final del notebook, conserva los márgenes de decisión y añade probabilidades estimadas mediante calibración de temperatura. La calibración se entrenó con folds agrupados del conjunto de entrenamiento y se evaluó en el test aislado. Una probabilidad individual no garantiza que el ODS sugerido sea correcto.

**Autores:** David Cardenas y Mario Celis.""")

st.markdown('<div class="app-footer">Microproyecto 2 · Maestría en IA · Aprendizaje No Supervisado<br>'
            'Corpus OSDG en español · 16 ODS modelados · Sin afiliación ni respaldo de la ONU</div>',
            unsafe_allow_html=True)
