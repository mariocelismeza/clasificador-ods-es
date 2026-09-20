export default function ExploradorOdsView({ visible, config }) {
  return (
    <div className={'max-w-[1480px] mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-12' + (visible ? '' : ' hidden')}>
      <div className="flex flex-col gap-1 mb-5">
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">Explorador de ODS</h1>
        <p className="text-xs sm:text-sm text-on-surface-variant max-w-4xl leading-relaxed">
          Los {config.n_ods_modelados} ODS presentes en el corpus de entrenamiento, con sus términos más frecuentes reales.
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {config.terminos_ordenados.map((item) => (
          <div key={item.ods} className="glass-panel rounded-2xl p-4 shadow-card-glass border border-white/10">
            <div className="flex items-center gap-3">
              <img
                src={`/sdg-icons/goal-${item.ods}.svg`}
                alt={`Ícono oficial ODS ${item.ods}: ${item.nombre}`}
                className="w-14 h-14 rounded-xl shrink-0 shadow-md"
                loading="lazy"
              />
              <span className="text-sm font-bold text-white">{item.ods}. {item.nombre}</span>
            </div>
            <div className="mt-2 text-xs text-on-surface-variant leading-relaxed">
              <strong className="text-white">Términos frecuentes:</strong> {item.terminos}
            </div>
          </div>
        ))}
      </div>
      <div className="bg-surface-container-low/60 border border-white/10 rounded-xl p-3 mt-4 text-xs text-on-surface-variant leading-relaxed flex items-start gap-3">
        <span className="material-symbols-outlined text-primary text-[18px] shrink-0 mt-0.5">info</span>
        <div>
          <strong className="text-white">ODS 17 — Alianzas para lograr los objetivos:</strong> no está representado en el corpus de entrenamiento (0 textos), por lo que el modelo nunca lo predice.
        </div>
      </div>
    </div>
  );
}
