const NAV_ITEMS = [
  { path: 'clasificador', label: 'Clasificador en vivo' },
  { path: 'explorador-ods', label: 'Explorador ODS' },
  { path: 'matriz-de-confusion', label: 'Matriz de Confusión' },
  { path: 'acerca-del-proyecto', label: 'Acerca del proyecto' },
];

export default function Header({ view, setView, modeloListo }) {
  return (
    <header className="sticky top-0 z-50 w-full bg-[#0a0e1a]/80 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-[1480px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-primary-container flex items-center justify-center text-[#001f2e] font-bold shadow-glow-sm">
              <span className="material-symbols-outlined text-[20px]">model_training</span>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold tracking-tight text-white leading-tight">Clasificador de ODS</span>
                <span className="text-[10px] font-mono-num font-semibold text-primary px-1.5 py-0.5 rounded bg-primary/10 border border-primary/20">AI CORE</span>
              </div>
              <span className="text-[11px] font-medium text-secondary leading-none">Proyecto académico · Maestría en IA</span>
            </div>
          </div>
          <div className="hidden xl:inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-surface-container-low/70 text-xs font-mono-num text-on-surface-variant backdrop-blur-md">
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${modeloListo ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${modeloListo ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
            </span>
            <span className="text-white font-medium">{modeloListo ? 'Modelo cargado' : 'Cargando modelo…'}</span>
            <span className="text-slate-600">·</span>
            <span className="text-primary font-semibold">TF-IDF + LSA + LinearSVC</span>
          </div>
        </div>
        <nav className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-container-low/80 border border-white/5 overflow-x-auto max-w-full">
          {NAV_ITEMS.map((item) => {
            const activo = view === item.path;
            return (
              <a
                key={item.path}
                href="#"
                aria-current={activo ? 'page' : undefined}
                data-path={item.path}
                onClick={(e) => { e.preventDefault(); setView(item.path); }}
                className={
                  'px-3.5 py-1.5 rounded-lg text-xs transition-all flex items-center gap-1.5 whitespace-nowrap ' +
                  (activo
                    ? 'font-semibold text-primary bg-primary/15 border border-primary/30 shadow-glow-sm'
                    : 'font-medium text-on-surface-variant hover:text-white hover:bg-white/5')
                }
              >
                {item.path === 'clasificador' && <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>}
                {item.label}
              </a>
            );
          })}
        </nav>
        <div className="flex items-center gap-3 shrink-0">
          <div className="hidden sm:flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-400">
              <span className="material-symbols-outlined text-[16px]">check_circle</span>
              Modelos cargados
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
