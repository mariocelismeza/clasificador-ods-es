"""Limpieza compartida por el notebook y el pipeline serializado de Streamlit."""

import re
import unicodedata

from nltk.stem import SnowballStemmer
from sklearn.base import BaseEstimator, TransformerMixin

STOPWORDS_ES = set((
    "de la que el en y a los del se las por un para con no una su al lo como más pero sus le ya o "
    "este si porque esta entre cuando muy sin sobre tambien me hasta hay donde quien desde todo nos "
    "durante todos uno les ni contra otros ese eso ante ellos e esto mi antes algunos que unos yo "
    "otro otras otra el tanto esa estos mucho quienes nada muchos cual poco ella estar estas algunas "
    "algo nosotros mi mis tu te ti tu tus ellas nosotras vosotros vosotras os mio mia mios mias tuyo "
    "tuya tuyos tuyas suyo suya suyos suyas nuestro nuestra nuestros nuestras vuestro vuestra "
    "vuestros vuestras esos esas estoy estas esta estamos estais estan este estes estemos esteis "
    "esten estare estaras estara estaremos estareis estaran estaria estarias estariamos estariais "
    "estarian estaba estabas estabamos estabais estaban soy eres es somos sois son sea seas seamos "
    "seais sean sere seras sera seremos sereis seran seria serias seriamos seriais serian era eras "
    "eramos erais eran fui fuiste fue fuimos fuisteis fueron siendo sido tengo tienes tiene tenemos "
    "teneis tienen haber puede pueden puedo puedes podemos podeis ser hacer tras solo "
    "asimismo asi cada dentro fuera ademas mediante debe deben como cual cuales "
    "pais paises hace hacia segun dicha dicho cuenta parte forma manera traves ademas mismo misma "
    "mismos mismas cuyo cuya cuyos cuyas tal tales dos tres si no"
).split())

TOKEN_RE = re.compile(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+")
spanish_stemmer = SnowballStemmer("spanish")


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


STOPWORDS_ES_NORM = {strip_accents(w) for w in STOPWORDS_ES}


class SpanishTextCleaner(BaseEstimator, TransformerMixin):
    """Limpieza y normalización de texto en español:
    minúsculas -> tokenización (regex, sin dependencias de descarga) ->
    eliminación de stopwords y tokens muy cortos -> stemming (Snowball).
    Compatible con Pipeline de scikit-learn (fit/transform).

    Idéntica a la usada durante el entrenamiento en el notebook (sección 2),
    para garantizar que la aplicación reproduzca exactamente el mismo
    preprocesamiento sobre el que se ajustó el modelo.
    """

    def __init__(self, stopwords=None, use_stemming=True, min_token_len=3):
        self.stopwords = stopwords
        self.use_stemming = use_stemming
        self.min_token_len = min_token_len

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self._clean_one(text) for text in X]

    def _clean_one(self, text):
        text = str(text).lower()
        tokens = TOKEN_RE.findall(text)
        stopwords_norm = self.stopwords or set()
        tokens = [
            t for t in tokens
            if strip_accents(t) not in stopwords_norm and len(t) >= self.min_token_len
        ]
        if self.use_stemming:
            tokens = [spanish_stemmer.stem(t) for t in tokens]
        return " ".join(tokens)


# Nombres oficiales de los ODS (1-17), para mostrar en la aplicación en vez de solo el número.
# El ODS 17 no está presente en los datos de entrenamiento (ver notebook, sección 1.1),
# por lo que el modelo nunca lo predice, pero se deja aquí para referencia completa.
NOMBRES_ODS = {
    1: "Fin de la pobreza",
    2: "Hambre cero",
    3: "Salud y bienestar",
    4: "Educación de calidad",
    5: "Igualdad de género",
    6: "Agua limpia y saneamiento",
    7: "Energía asequible y no contaminante",
    8: "Trabajo decente y crecimiento económico",
    9: "Industria, innovación e infraestructura",
    10: "Reducción de las desigualdades",
    11: "Ciudades y comunidades sostenibles",
    12: "Producción y consumo responsables",
    13: "Acción por el clima",
    14: "Vida submarina",
    15: "Vida de ecosistemas terrestres",
    16: "Paz, justicia e instituciones sólidas",
    17: "Alianzas para lograr los objetivos",
}
