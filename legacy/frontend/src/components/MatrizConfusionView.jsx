export default function MatrizConfusionView({ visible, config }) {
  return (
    <div className={'max-w-[1480px] mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-12' + (visible ? '' : ' hidden')}>
      <div className="flex flex-col gap-1 mb-5">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">Matriz de Confusión</h1>
        <p className="text-xs sm:text-sm text-on-surface-variant max-w-4xl leading-relaxed">
          Matriz de confusión real sobre el conjunto de prueba ({config.metrics.n_test.toLocaleString('es-CO')} textos no usados en el entrenamiento), normalizada por fila.
        </p>
      </div>
      <div className="glass-panel rounded-2xl p-4 shadow-card-glass border border-white/10 mb-4">
        <img alt="Matriz de confusión" className="w-full rounded-xl" src="/api/confusion-matrix.png" />
      </div>
      <div className="glass-panel rounded-2xl p-4 shadow-card-glass border border-white/10">
        <div className="text-xs font-bold uppercase tracking-wider text-white mb-2 flex items-center gap-1.5">
          <span className="material-symbols-outlined text-[15px] text-primary">alt_route</span>
          Pares de confusión más frecuentes
        </div>
        {config.pares.map((p, i) => (
          <div key={i} className="flex items-center justify-between py-2 border-t border-white/5 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-sm inline-block" style={{ background: config.sdg_colors[p.ods_real] || '#334155' }}></span>
              <span className="text-on-surface-variant">
                ODS {p.ods_real} ({config.nombres_ods[p.ods_real] || ''}) → predicho como ODS {p.ods_predicho} ({config.nombres_ods[p.ods_predicho] || ''})
              </span>
            </div>
            <span className="font-mono-num text-secondary">{p.n_casos} casos</span>
          </div>
        ))}
      </div>
    </div>
  );
}
