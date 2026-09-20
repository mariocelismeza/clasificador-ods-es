import { useEffect, useRef, useState } from 'react';
import { predecir, predecirLote } from '../api';
import Heatmap from './Heatmap';
import InfoTooltip from './InfoTooltip';

const EXPLICACIONES = {
  probabilidad:
    'Qué tan seguro está el modelo de esta predicción, en una escala de 0% a 100%. No es un cálculo arbitrario: se ajustó estadísticamente (calibración de Platt) para que un 80% realmente signifique que el modelo acierta ese tipo de casos aproximadamente 8 de cada 10 veces.',
  margen:
    'Qué tan lejos quedó tu texto de la "línea divisoria" entre este ODS y los demás. Mientras más alto el número, más clara fue la decisión del modelo; valores cercanos a 0 indican que el texto estuvo en la frontera entre dos categorías.',
  calibracion:
    'Un método estadístico estándar (Platt scaling) que convierte la confianza interna del modelo en una probabilidad real y confiable, en vez de un número arbitrario.',
  delta:
    'La diferencia de probabilidad entre el ODS que ganó y el segundo más cercano. Si es un número pequeño, el texto podría clasificarse razonablemente en cualquiera de los dos.',
  keywords:
    'Las palabras de tu texto que más influyeron en la predicción, porque son poco comunes en general pero muy frecuentes en textos de este ODS.',
  comparacion:
    'Compara la probabilidad calibrada del ODS ganador con sus candidatos secundarios, en la misma escala de 0% a 100%, para que veas qué tan clara (o ajustada) fue la decisión del modelo.',
};

function nivelConfianza(proba, umbralAlta, umbralMedia) {
  if (proba >= umbralAlta) {
    return { tier: 'alta', text: 'Alta certeza estadística', icon: 'check', classes: 'text-emerald-300 bg-emerald-950/60 border-emerald-500/30' };
  }
  if (proba >= umbralMedia) {
    return { tier: 'media', text: 'Certeza media — revisar candidatos', icon: 'info', classes: 'text-amber-300 bg-amber-950/60 border-amber-500/30' };
  }
  return { tier: 'baja', text: 'Certeza baja — resultado poco confiable', icon: 'warning', classes: 'text-red-300 bg-red-950/60 border-red-500/30' };
}

export default function ClasificadorView({ visible, config }) {
  const [texto, setTexto] = useState(config.ejemplos[0]?.texto || '');
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [batchOpen, setBatchOpen] = useState(false);
  const [batchResultados, setBatchResultados] = useState(null);
  const [batchError, setBatchError] = useState(null);
  const [copiado, setCopiado] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const palabras = texto.trim() === '' ? 0 : texto.trim().split(/\s+/).length;
  const caracteres = texto.length;
  const longitudOptima = palabras >= config.longitud_minima;

  async function ejecutarPrediccion() {
    const t = texto.trim();
    if (!t) {
      textareaRef.current?.focus();
      return;
    }
    setCargando(true);
    setError(null);
    try {
      const r = await predecir(t);
      setResultado(r);
      setHistorial((prev) => [
        {
          hora: new Date().toLocaleTimeString('es-CO', { hour12: false }),
          texto: t.slice(0, 80) + (t.length > 80 ? '…' : ''),
          ods: r.ods_predicho,
          nombre: r.nombre_ods,
          color: r.color_ods,
          proba: r.proba,
        },
        ...prev,
      ].slice(0, 20));
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    function onKeyDown(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        ejecutarPrediccion();
      }
    }
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [texto]);

  async function onBatchFile(e) {
    const archivo = e.target.files?.[0];
    if (!archivo) return;
    setBatchError(null);
    setBatchResultados(null);
    try {
      const r = await predecirLote(archivo);
      setBatchResultados(r.resultados);
    } catch (err) {
      setBatchError(err.message);
    } finally {
      e.target.value = '';
    }
  }

  function exportarJSON() {
    if (!resultado) return;
    const blob = new Blob([JSON.stringify(resultado, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'reporte-ods-inferencia.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  async function copiarResultado() {
    if (!resultado) return;
    const resumen = `ODS ${resultado.ods_predicho}: ${resultado.nombre_ods} (probabilidad calibrada: ${(resultado.proba * 100).toFixed(1)}%, margen SVM: ${resultado.margen.toFixed(2)})`;
    try {
      await navigator.clipboard.writeText(resumen);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      // portapapeles no disponible; no es crítico
    }
  }

  function descargarBatchCSV() {
    if (!batchResultados) return;
    const header = 'texto,ods_predicho,nombre_ods,probabilidad\n';
    const filas = batchResultados
      .map((r) => `"${r.texto.replace(/"/g, '""')}",${r.ods_predicho},"${r.nombre_ods}",${r.probabilidad}`)
      .join('\n');
    const blob = new Blob([header + filas], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resultados-lote.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  const confianza = resultado ? nivelConfianza(resultado.proba, config.umbral_alta, config.umbral_media) : null;
  const segundoCandidato = resultado?.secundarios?.[0];
  const deltaVsSegundo = resultado && segundoCandidato ? ((resultado.proba - segundoCandidato.proba) * 100).toFixed(1) : null;

  return (
    <div className={'max-w-[1480px] mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-12 flex flex-col gap-6' + (visible ? '' : ' hidden')}>
      {/* Breadcrumbs & Subheader */}
      <div className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-3">
          <nav aria-label="Ruta de navegación" className="flex items-center gap-1.5 text-xs text-on-surface-variant font-medium">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">home</span>
              Plataforma
            </span>
            <span className="material-symbols-outlined text-[13px] text-slate-500">chevron_right</span>
            <span>Clasificador en Vivo</span>
            <span className="material-symbols-outlined text-[13px] text-slate-500">chevron_right</span>
            <span className="text-white font-semibold">Inferencia de Texto &amp; Semántica</span>
          </nav>
          <div className="flex items-center gap-2.5 text-xs font-mono-num bg-surface-container-low/90 border border-white/10 px-3.5 py-1.5 rounded-xl text-on-surface-variant shadow-inner">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-primary inline-block shadow-[0_0_8px_rgba(125,211,252,0.8)]"></span>
              <span className="text-white font-medium">{config.n_ods_modelados} ODS modelados</span>
            </div>
            <span className="text-slate-600">•</span>
            <div className="flex items-center gap-1 text-emerald-400 font-medium">
              <span className="material-symbols-outlined text-[14px]">bolt</span>
              <span>{resultado ? `${resultado.latencia_ms.toFixed(0)} ms latencia` : 'sin ejecutar aún'}</span>
            </div>
            <span className="text-slate-600">•</span>
            <span className="text-secondary hidden sm:inline">Corpus: OSDG Community Dataset (ES)</span>
          </div>
        </div>
        <div className="flex flex-col gap-1.5">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
            Clasificador de Objetivos de Desarrollo Sostenible (ODS)
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant max-w-4xl leading-relaxed">
            Herramienta analítica de procesamiento de lenguaje natural basada en TF-IDF, Análisis Semántico Latente
            (LSA / TruncatedSVD) y Máquinas de Vectores de Soporte (
            <span className="font-semibold text-white font-mono-num text-xs bg-surface-container-high px-1.5 py-0.5 rounded border border-white/10">LinearSVC</span>
            ) para categorizar propuestas, proyectos y documentos en español conforme a la Agenda 2030 de la ONU.
          </p>
        </div>
      </div>

      {/* MAIN TWO-COLUMN GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT COLUMN */}
        <section aria-label="Entrada de texto y configuración de análisis" className="lg:col-span-6 flex flex-col gap-4">
          <div className="glass-panel rounded-2xl p-5 shadow-card-glass border border-white/10 flex flex-col justify-between min-h-[660px]">
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-6 h-6 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                    <span className="material-symbols-outlined text-[16px]">edit_document</span>
                  </div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-white">Texto a clasificar (Español)</h2>
                </div>
                <button
                  type="button"
                  onClick={() => { setTexto(''); textareaRef.current?.focus(); }}
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-on-surface-variant hover:text-red-400 transition-colors px-2.5 py-1 rounded-lg hover:bg-white/5 border border-transparent hover:border-red-500/20"
                >
                  <span className="material-symbols-outlined text-[15px]">delete_sweep</span>
                  Limpiar texto
                </button>
              </div>

              <div className="flex flex-col gap-2">
                <span className="text-[11px] font-medium text-secondary">Cargar ejemplos predefinidos del corpus analítico:</span>
                <div className="flex flex-wrap gap-2">
                  {config.ejemplos.map((ej, i) => (
                    <button
                      key={ej.id}
                      type="button"
                      onClick={() => setTexto(ej.texto)}
                      className={
                        'border border-white/10 text-xs font-medium px-3 py-1.5 rounded-xl transition-all inline-flex items-center gap-2 hover:border-primary/40 group shadow-sm active:scale-95 ' +
                        (i === 0 ? 'bg-surface-container-high hover:bg-surface-bright text-white' : 'bg-surface-container-low hover:bg-surface-container-high text-on-surface-variant hover:text-white')
                      }
                    >
                      <span className="w-2.5 h-2.5 rounded-full ring-2 group-hover:scale-110 transition-transform inline-block" style={{ background: ej.color, boxShadow: `0 0 0 2px ${ej.color}4d` }}></span>
                      {ej.titulo}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-2.5">
                <div className="relative rounded-xl border border-white/10 bg-surface-container-lowest/80 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary shadow-inner transition-all overflow-hidden group">
                  <div className="px-3.5 py-2 bg-surface-container-low/70 border-b border-white/5 flex items-center justify-between text-[11px] font-mono-num text-secondary">
                    <span className="flex items-center gap-1.5 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[14px] text-primary">terminal</span>
                      Entrada de Texto Natural (NLP UTF-8)
                    </span>
                    <span className="text-primary/80 font-medium">Tokenizador Activo</span>
                  </div>
                  <textarea
                    ref={textareaRef}
                    id="sdg-input-text"
                    rows={9}
                    value={texto}
                    onChange={(e) => setTexto(e.target.value)}
                    placeholder='Ingrese aquí el resumen de proyecto, propuesta comunitaria, artículo o documento público para inferir su correspondencia con los ODS...'
                    className="w-full bg-transparent p-4 text-xs sm:text-sm text-white placeholder:text-slate-500 focus:outline-none resize-none leading-relaxed border-0 focus:ring-0 selection:bg-primary/30"
                  />
                  <div className="px-3.5 py-2.5 bg-surface-container-low/50 border-t border-white/5 flex flex-wrap items-center gap-1.5">
                    <span className="text-[10px] uppercase font-mono-num text-slate-400 mr-1">Tokens detectados:</span>
                    {resultado && resultado.keywords?.length ? (
                      resultado.keywords.slice(0, 4).map((k) => (
                        <span key={k.termino} className="text-[10px] font-mono-num bg-primary/10 border border-primary/20 text-primary px-2 py-0.5 rounded-md">
                          {k.termino} +{k.peso.toFixed(2)}
                        </span>
                      ))
                    ) : (
                      <span className="text-[10px] font-mono-num text-slate-500">se muestran al predecir</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-between px-1 text-[11px] text-secondary font-mono-num">
                  <div className="flex items-center gap-2">
                    <span className="text-white font-medium">{caracteres} caracteres</span>
                    <span>•</span>
                    <span className="text-white font-medium">{palabras} palabras</span>
                  </div>
                  {palabras > 0 && (
                    <div className={
                      'flex items-center gap-1.5 font-sans font-medium px-2 py-0.5 rounded-md border ' +
                      (longitudOptima
                        ? 'text-emerald-400 bg-emerald-950/40 border-emerald-500/20'
                        : 'text-amber-400 bg-amber-950/40 border-amber-500/20')
                    }>
                      <span className="material-symbols-outlined text-[14px]">{longitudOptima ? 'check_circle' : 'info'}</span>
                      <span>{longitudOptima ? 'Longitud óptima para TF-IDF' : `Se recomiendan al menos ${config.longitud_minima} palabras`}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-surface-container-low/70 border border-white/10 rounded-xl p-3.5 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-xs select-none">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[16px] text-primary">tune</span>
                    <span className="font-bold text-white tracking-wide">Parámetros del Pipeline Scikit-Learn</span>
                  </div>
                  <span className="text-[10px] font-mono-num text-primary/80 bg-primary/10 px-2 py-0.5 rounded border border-primary/20">valores reales del modelo</span>
                </div>
                <div className="grid grid-cols-3 gap-2.5 pt-1 font-mono-num">
                  <div className="bg-surface-container-high/60 border border-white/5 p-2.5 rounded-xl flex flex-col gap-1">
                    <span className="text-secondary text-[9px] uppercase tracking-wider font-sans font-medium">Vectorizador</span>
                    <span className="text-xs font-bold text-white">TF-IDF ({config.tfidf_params.ngram_range[0]},{config.tfidf_params.ngram_range[1]})</span>
                    <span className="text-[10px] text-slate-400">sublinear_tf={String(config.tfidf_params.sublinear_tf)}</span>
                  </div>
                  <div className="bg-surface-container-high/60 border border-white/5 p-2.5 rounded-xl flex flex-col gap-1">
                    <span className="text-secondary text-[9px] uppercase tracking-wider font-sans font-medium">Descomposición</span>
                    <span className="text-xs font-bold text-white">LSA / TruncSVD</span>
                    <span className="text-[10px] text-slate-400">{config.metrics.n_componentes_lsa} componentes</span>
                  </div>
                  <div className="bg-surface-container-high/60 border border-white/5 p-2.5 rounded-xl flex flex-col gap-1">
                    <span className="text-secondary text-[9px] uppercase tracking-wider font-sans font-medium">Clasificador</span>
                    <span className="text-xs font-bold text-white">LinearSVC (C={config.metrics.hiperparametros_pipeline["classifier__C"]})</span>
                    <span className="text-[10px] text-slate-400">Calibrado con Platt</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-5 mt-4 border-t border-white/10 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
              <button
                type="button"
                onClick={ejecutarPrediccion}
                disabled={cargando}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 bg-gradient-to-r from-primary to-[#38bdf8] hover:from-[#60a5fa] hover:to-primary active:scale-[0.98] text-[#001f2e] text-xs font-bold px-6 py-3 rounded-xl shadow-glow-cyan transition-all focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-60"
              >
                <span className={'material-symbols-outlined text-[18px]' + (cargando ? ' animate-spin' : '')}>{cargando ? 'sync' : 'bolt'}</span>
                <span>{cargando ? 'Procesando vectores TF-IDF…' : 'Predecir ODS ⌘ + Enter'}</span>
              </button>
              <button
                type="button"
                onClick={() => { setBatchOpen((v) => !v); fileInputRef.current?.click(); }}
                className="inline-flex items-center justify-center gap-2 text-xs font-semibold text-on-surface-variant hover:text-white transition-all py-2.5 px-4 rounded-xl hover:bg-white/5 border border-white/10"
              >
                <span className="material-symbols-outlined text-[16px]">upload_file</span>
                <span>Procesar por Lotes (.CSV / .TXT)</span>
              </button>
              <input ref={fileInputRef} type="file" accept=".csv,.txt" className="hidden" onChange={onBatchFile} />
            </div>
            {error && (
              <div className="mt-3 flex items-center gap-2 text-xs text-red-300 bg-red-950/40 border border-red-500/30 px-3 py-2 rounded-lg">
                <span className="material-symbols-outlined text-[16px]">error</span>
                {error}
              </div>
            )}
          </div>

          {(batchResultados || batchError) && (
            <div className="glass-panel rounded-2xl p-4 shadow-card-glass border border-white/10 flex flex-col gap-3">
              <div className="flex items-center justify-between border-b border-white/10 pb-2">
                <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[15px] text-primary">upload_file</span>
                  Resultados del análisis en lote
                </span>
                <button type="button" onClick={() => { setBatchResultados(null); setBatchError(null); }} className="text-xs font-medium text-on-surface-variant hover:text-red-400">
                  <span className="material-symbols-outlined text-[15px]">close</span>
                </button>
              </div>
              {batchError ? (
                <span className="text-xs text-red-300">{batchError}</span>
              ) : (
                <>
                  <div className="overflow-auto max-h-72 flex flex-col gap-1.5">
                    {batchResultados.map((r, i) => (
                      <div key={i} className="flex items-center justify-between text-xs gap-3 border-b border-white/5 py-1.5">
                        <span className="flex-1 text-on-surface-variant truncate">{r.texto}</span>
                        <span className="text-white font-medium shrink-0">ODS {r.ods_predicho} — {r.nombre_ods}</span>
                        <span className="font-mono-num text-primary shrink-0 w-14 text-right">{(r.probabilidad * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                  </div>
                  <button
                    type="button"
                    onClick={descargarBatchCSV}
                    className="self-start inline-flex items-center gap-1.5 text-xs font-semibold bg-surface-container-high hover:bg-surface-bright border border-white/10 text-white px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <span className="material-symbols-outlined text-[15px] text-primary">download</span>
                    Descargar resultados (CSV)
                  </button>
                </>
              )}
            </div>
          )}
        </section>

        {/* RIGHT COLUMN */}
        <section aria-label="Resultados analíticos del modelo de lenguaje" className="lg:col-span-6 flex flex-col gap-4">
          <div className="flex items-center justify-between glass-panel border border-white/10 px-4 py-2.5 rounded-xl shadow-sm">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"></span>
              </span>
              <span className="text-xs font-bold text-white">{resultado ? 'Inferencia NLP Completada' : 'Modelo cargado — listo para inferencia'}</span>
            </div>
            <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-mono-num font-medium bg-emerald-950/40 border border-emerald-500/20 px-2.5 py-0.5 rounded-lg">
              <span className="material-symbols-outlined text-[14px]">check_circle</span>
              <span>LinearSVC listo</span>
            </div>
          </div>

          <div className="glass-panel-glow rounded-2xl shadow-card-glass overflow-hidden flex flex-col border border-primary/30 relative">
            <div className="bg-surface-container-high/80 border-b border-white/10 px-4 py-2.5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="bg-primary text-[#001f2e] text-[10px] font-mono-num font-bold px-2 py-0.5 rounded tracking-wide uppercase shadow-sm">Predicción Primaria</span>
                <span className="text-secondary text-xs font-medium hidden sm:inline">Mayor Relevancia Semántica</span>
              </div>
              <div className="flex items-center gap-1.5 text-secondary text-xs font-mono-num">
                <span className="material-symbols-outlined text-[15px] text-primary">verified</span>
                <span>Calibración Platt Activa</span>
                <InfoTooltip texto={EXPLICACIONES.calibracion} posicion="bottom" align="right" />
              </div>
            </div>
            <div className="p-5 flex flex-col gap-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-4">
                  {resultado ? (
                    <img
                      src={`/sdg-icons/goal-${resultado.ods_predicho}.svg`}
                      alt={`Ícono oficial ODS ${resultado.ods_predicho}: ${resultado.nombre_ods}`}
                      className="w-16 h-16 rounded-xl shrink-0 shadow-lg ring-1 ring-white/20"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-xl bg-surface-container-high border border-white/10 text-white flex flex-col items-center justify-center shrink-0 shadow-lg ring-1 ring-white/20">
                      <span className="font-mono-num text-3xl font-extrabold leading-none opacity-40">—</span>
                      <span className="text-[9px] font-bold tracking-tight uppercase mt-0.5 opacity-40">ODS ONU</span>
                    </div>
                  )}
                  <div className="flex flex-col">
                    <span className="text-[11px] font-bold tracking-widest text-primary uppercase font-mono-num">
                      {resultado ? `Objetivo ${resultado.ods_predicho} de las Naciones Unidas` : 'Sin predicción todavía'}
                    </span>
                    <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight leading-tight mt-0.5">
                      {resultado ? resultado.nombre_ods : 'Ingresa un texto y presiona "Predecir ODS"'}
                    </h3>
                  </div>
                </div>
                <div className="bg-surface-container-high/80 border border-white/10 px-3 py-1.5 rounded-xl text-right shrink-0">
                  <span className="flex items-center justify-end gap-1 text-[10px] uppercase font-mono-num text-secondary font-medium">
                    Margen Hiperplano
                    <InfoTooltip texto={EXPLICACIONES.margen} posicion="bottom" align="right" />
                  </span>
                  <span className="text-xs font-mono-num font-bold text-primary">{resultado ? `${resultado.margen >= 0 ? '+' : ''}${resultado.margen.toFixed(2)}` : '—'}</span>
                </div>
              </div>

              <div className="bg-surface-container-low/80 border border-white/10 p-4 rounded-xl flex flex-col gap-3">
                <div className="flex items-baseline justify-between">
                  <div>
                    <span className="flex items-center gap-1 text-[11px] font-medium text-secondary">
                      Probabilidad Calibrada (Platt)
                      <InfoTooltip texto={EXPLICACIONES.probabilidad} />
                    </span>
                    <div className="flex items-baseline gap-2">
                      <span className="text-3xl sm:text-4xl font-extrabold font-mono-num text-white tracking-tight">
                        {resultado ? `${(resultado.proba * 100).toFixed(1)}%` : '0.0%'}
                      </span>
                    </div>
                  </div>
                  {confianza && (
                    <div className={`text-right text-xs font-mono-num font-semibold flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${confianza.classes}`}>
                      <span className="material-symbols-outlined text-[16px]">{confianza.icon}</span>
                      <span>{confianza.text}</span>
                    </div>
                  )}
                </div>
                <div className="w-full bg-surface-container-highest rounded-full h-3 overflow-hidden p-0.5 flex border border-white/5">
                  <div
                    className="bg-gradient-to-r from-primary via-[#38bdf8] to-emerald-400 h-full rounded-full transition-all duration-700 shadow-glow-sm"
                    style={{ width: `${resultado ? resultado.proba * 100 : 0}%` }}
                  ></div>
                </div>
                <div className="flex items-center justify-between text-[11px] font-mono-num text-secondary pt-0.5">
                  <span>Criterio de alta confianza: &gt;{config.umbral_alta_pct}%</span>
                  <span className="text-white font-medium inline-flex items-center gap-1">
                    Delta vs 2° candidato: {deltaVsSegundo !== null ? `${deltaVsSegundo}%` : '—'}
                    <InfoTooltip texto={EXPLICACIONES.delta} posicion="bottom" align="right" />
                  </span>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[16px] text-primary">data_array</span>
                    Palabras clave con mayor peso TF-IDF:
                    <InfoTooltip texto={EXPLICACIONES.keywords} />
                  </span>
                  <span className="text-[10px] font-mono-num text-secondary">ranking vectorial</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {resultado?.keywords?.length ? (
                    resultado.keywords.map((k) => (
                      <div key={k.termino} className="inline-flex items-center gap-2 bg-surface-container-high border border-white/10 hover:border-primary/40 px-3 py-1.5 rounded-lg text-xs text-white transition-colors">
                        <span className="font-medium">{k.termino}</span>
                        <span className="font-mono-num text-[10px] font-bold text-primary bg-primary/10 border border-primary/20 px-1.5 py-0.5 rounded leading-none">+{k.peso.toFixed(2)}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500">Aún no hay predicción.</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-4 shadow-card-glass flex flex-col gap-3.5 border border-white/10">
            <div className="flex items-center justify-between border-b border-white/10 pb-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[15px] text-primary">bar_chart</span>
                Comparación de Probabilidades
                <InfoTooltip texto={EXPLICACIONES.comparacion} />
              </span>
              <span className="text-[11px] font-mono-num text-secondary">Predicho vs. candidatos secundarios</span>
            </div>
            <div className="flex flex-col gap-3">
              {resultado ? (
                [
                  { ods: resultado.ods_predicho, nombre: resultado.nombre_ods, proba: resultado.proba, margen: resultado.margen, esGanador: true },
                  ...resultado.secundarios.map((s) => ({ ...s, esGanador: false })),
                ].map((c) => (
                  <div key={c.ods} className="flex flex-col gap-1.5">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <span className="flex items-center gap-2 text-xs font-bold text-white min-w-0">
                        <img
                          src={`/sdg-icons/goal-${c.ods}.svg`}
                          alt={`Ícono oficial ODS ${c.ods}: ${c.nombre}`}
                          className="w-7 h-7 rounded-lg shrink-0 shadow-md"
                        />
                        <span className="truncate">ODS {c.ods}: {c.nombre}</span>
                        {c.esGanador && (
                          <span className="text-[9px] font-mono-num font-bold text-primary bg-primary/10 border border-primary/20 px-1.5 py-0.5 rounded uppercase shrink-0">
                            Ganador
                          </span>
                        )}
                      </span>
                      <span className="font-mono-num text-xs shrink-0 whitespace-nowrap">
                        <span className={c.esGanador ? 'font-extrabold text-primary' : 'font-bold text-slate-300'}>
                          {(c.proba * 100).toFixed(1)}%
                        </span>
                        <span className="text-slate-500 ml-2">margen {c.margen >= 0 ? '+' : ''}{c.margen.toFixed(2)}</span>
                      </span>
                    </div>
                    <div className="w-full bg-surface-container-highest rounded-full h-2.5 overflow-hidden">
                      <div
                        className={
                          'h-full rounded-full transition-all duration-700 ' +
                          (c.esGanador ? 'bg-gradient-to-r from-primary via-[#38bdf8] to-emerald-400 shadow-glow-sm' : 'bg-slate-500')
                        }
                        style={{ width: `${c.proba * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))
              ) : (
                <span className="text-xs text-slate-500">Aún no hay predicción.</span>
              )}
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-4 shadow-card-glass flex flex-col gap-3.5 border border-white/10">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px] text-primary">query_stats</span>
                Métricas de Rendimiento del Modelo
              </span>
              <span className="text-[11px] font-mono-num text-primary bg-primary/10 border border-primary/20 px-2 py-0.5 rounded">
                {config.metrics.vocabulario_tfidf.toLocaleString('es-CO')} términos
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 font-mono-num">
              <div className="bg-surface-container-low/80 border border-white/10 p-3 rounded-xl flex items-center justify-between">
                <div>
                  <span className="block text-[10px] uppercase font-sans text-secondary font-medium">F1-Score Macro</span>
                  <span className="text-xl font-bold text-white">{config.metrics.f1_macro_test.toFixed(3)}</span>
                  <span className="block text-[10px] text-slate-400 font-sans mt-0.5">Conjunto de prueba (n={config.metrics.n_test.toLocaleString('es-CO')})</span>
                </div>
                <div className="w-9 h-9 rounded-xl bg-surface-container-high border border-white/10 flex items-center justify-center text-primary">
                  <span className="material-symbols-outlined text-[19px]">balance</span>
                </div>
              </div>
              <div className="bg-surface-container-low/80 border border-white/10 p-3 rounded-xl flex items-center justify-between">
                <div>
                  <span className="block text-[10px] uppercase font-sans text-secondary font-medium">Exactitud (Accuracy)</span>
                  <span className="text-xl font-bold text-emerald-400">{(config.metrics.accuracy_test * 100).toFixed(1)}%</span>
                  <span className="block text-[10px] text-slate-400 font-sans mt-0.5">Test set independiente (n={config.metrics.n_test.toLocaleString('es-CO')})</span>
                </div>
                <div className="w-9 h-9 rounded-xl bg-surface-container-high border border-white/10 flex items-center justify-center text-emerald-400">
                  <span className="material-symbols-outlined text-[19px]">fact_check</span>
                </div>
              </div>
            </div>
            <div className="bg-surface-container-low/60 border border-white/10 rounded-xl p-3 flex items-start gap-3 text-on-surface-variant">
              <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">info</span>
              <div className="flex flex-col text-xs leading-relaxed">
                <span className="font-bold text-white">Nota metodológica sobre ODS 17 (Alianzas):</span>
                <p className="text-on-surface-variant mt-0.5">
                  El modelo se entrena sobre 16 ODS y nunca predice el ODS 17 ("Alianzas para lograr los objetivos"), porque no está representado en el corpus de entrenamiento (ver la pestaña "Explorador ODS").
                </p>
              </div>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-white/10">
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  disabled={!resultado}
                  onClick={exportarJSON}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold bg-surface-container-high hover:bg-surface-bright border border-white/10 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <span className="material-symbols-outlined text-[15px] text-primary">data_object</span>
                  Exportar informe JSON
                </button>
                <button
                  type="button"
                  disabled={!resultado}
                  onClick={copiarResultado}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold bg-surface-container-high hover:bg-surface-bright border border-white/10 text-white px-3 py-1.5 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <span className="material-symbols-outlined text-[15px] text-primary">content_copy</span>
                  Copiar resultado
                </button>
              </div>
              <span className={'text-xs font-medium text-emerald-400 transition-opacity' + (copiado ? '' : ' opacity-0')}>¡Copiado al portapapeles!</span>
            </div>

            <div className="flex items-center justify-between border-t border-white/10 pt-3 mt-1">
              <span className="text-xs font-bold text-white flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px] text-primary">history</span>
                Historial de esta sesión
              </span>
              <span className="text-[11px] font-mono-num text-secondary">solo en este navegador</span>
            </div>
            <div className="flex flex-col gap-2">
              {historial.length === 0 ? (
                <span className="text-xs text-slate-500">Todavía no has hecho ninguna predicción en esta sesión.</span>
              ) : (
                <>
                  <div className="text-xs font-bold uppercase tracking-wider text-white mb-1">{historial.length} predicción(es) en esta sesión</div>
                  {historial.map((h, i) => (
                    <div key={i} className="flex items-center justify-between py-2 border-t border-white/5 text-xs gap-3">
                      <span className="font-mono-num text-slate-500 shrink-0">{h.hora}</span>
                      <span className="flex-1 text-on-surface-variant truncate">{h.texto}</span>
                      <span className="flex items-center gap-1.5 text-white font-medium shrink-0">
                        <span className="w-2 h-2 rounded-full inline-block" style={{ background: h.color }}></span>
                        ODS {h.ods} — {h.nombre}
                      </span>
                      <span className="font-mono-num text-primary text-right shrink-0 w-14">{(h.proba * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>
        </section>
      </div>

      {/* BOTTOM: Heatmap */}
      <section aria-label="Distribución global de pesos semánticos" className="glass-panel rounded-2xl p-5 shadow-card-glass border border-white/10 flex flex-col gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-[16px]">grid_view</span>
            </div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">Distribución General de Pesos por ODS en el Documento Analizado</h3>
          </div>
          <div className="flex items-center gap-4 text-[11px] font-mono-num text-secondary">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-surface-container-high border border-white/10 inline-block"></span> 0 - 20%</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-primary/40 border border-primary/50 inline-block"></span> 20 - 50%</span>
            <span className="flex items-center gap-1.5 text-primary font-semibold"><span className="w-2.5 h-2.5 rounded-sm bg-primary inline-block shadow-glow-sm"></span> &gt; 50% (Predicción Ganadora)</span>
          </div>
        </div>
        <div className="grid grid-cols-3 sm:grid-cols-6 md:grid-cols-9 lg:grid-cols-[repeat(17,minmax(0,1fr))] gap-2 pt-1">
          <Heatmap distribucion={resultado?.distribucion} sdgColors={config.sdg_colors} prediccionActiva={!!resultado} />
        </div>
      </section>
    </div>
  );
}
