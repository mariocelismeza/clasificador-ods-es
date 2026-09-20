export default function AcercaDelProyectoView({ visible, config }) {
  const m = config.metrics;
  return (
    <div className={'max-w-[1480px] mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-12' + (visible ? '' : ' hidden')}>
      <div className="flex flex-col gap-1 mb-5">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">Acerca del proyecto</h1>
      </div>
      <div className="glass-panel rounded-2xl p-4 shadow-card-glass border border-white/10 mb-4">
        <p className="text-sm text-on-surface-variant leading-relaxed">
          Esta aplicación es la bonificación opcional del <strong className="text-white">Microproyecto 2</strong> de la
          Maestría en Inteligencia Artificial (curso de Aprendizaje No Supervisado). Reutiliza exactamente el mismo
          pipeline entrenado y documentado en <code className="text-primary">Microproyecto2_ODS.ipynb</code>: limpieza
          de texto en español (stopwords + stemming Snowball) → TF-IDF ({m.vocabulario_tfidf.toLocaleString('es-CO')} términos)
          → LSA / TruncatedSVD ({m.n_componentes_lsa} componentes) → SVM Lineal calibrado.
        </p>
        <p className="text-sm text-on-surface-variant leading-relaxed mt-2">
          El corpus de entrenamiento es el <strong className="text-white">OSDG Community Dataset</strong> (versión en
          español, traducida con DeepL y aumentada con la API de ChatGPT).
        </p>
      </div>
      <div className="glass-panel rounded-2xl p-4 shadow-card-glass border border-white/10 mb-4">
        <table className="w-full text-sm font-mono-num text-on-surface-variant">
          <tbody>
            <tr><td className="py-1">F1 macro</td><td className="py-1 text-right text-white">{m.f1_macro_test.toFixed(4)}</td></tr>
            <tr><td className="py-1">F1 weighted</td><td className="py-1 text-right text-white">{m.f1_weighted_test.toFixed(4)}</td></tr>
            <tr><td className="py-1">Accuracy</td><td className="py-1 text-right text-white">{m.accuracy_test.toFixed(4)}</td></tr>
            <tr><td className="py-1">F1 macro (validación cruzada)</td><td className="py-1 text-right text-white">{m.f1_macro_cv.toFixed(4)}</td></tr>
            <tr><td className="py-1">Textos de entrenamiento</td><td className="py-1 text-right text-white">{m.n_train.toLocaleString('es-CO')}</td></tr>
          </tbody>
        </table>
      </div>
      <div className="bg-surface-container-low/60 border border-white/10 rounded-xl p-3 text-xs text-on-surface-variant leading-relaxed flex items-start gap-3">
        <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">info</span>
        <div>
          <strong className="text-white">Limitaciones documentadas:</strong>
          <ul className="list-disc ml-4 mt-1">
            <li>No puede predecir el ODS 17 (ausente del corpus de entrenamiento).</li>
            <li>Los ODS de temática económica (8, 9, 10, 12) son, en promedio, más difíciles de distinguir entre sí.</li>
            <li>El corpus proviene de traducción automática y aumentación sintética; el desempeño sobre texto genuinamente nuevo podría diferir ligeramente.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
