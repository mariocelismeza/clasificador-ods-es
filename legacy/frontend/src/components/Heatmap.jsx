// Mapa de calor de distribución sobre los 17 ODS. El ODS 17 siempre se muestra
// como celda neutra "N/A" porque el modelo nunca lo predice (no está en el corpus).
export default function Heatmap({ distribucion, sdgColors, prediccionActiva }) {
  const celdas = [];
  for (let n = 1; n <= 17; n++) {
    if (n === 17) {
      celdas.push(
        <div
          key={n}
          title="ODS 17: Excluido del corpus del clasificador"
          className="flex flex-col bg-surface-container-low/20 border border-dashed border-white/10 rounded-xl p-2 text-center opacity-40 select-none"
        >
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-mono-num text-slate-500 line-through">#17</span>
            <span className="w-2 h-2 rounded-full bg-slate-600"></span>
          </div>
          <div className="w-full bg-surface-container-highest/40 h-1.5 rounded-full my-1"></div>
          <span className="text-[9px] font-mono-num text-slate-500 uppercase">N/A</span>
        </div>
      );
      continue;
    }
    const pct = distribucion ? (distribucion[n] || 0) * 100 : 0;
    const esGanador = prediccionActiva && distribucion && Math.max(...Object.values(distribucion).map((v) => v)) * 100 === pct && pct > 0;
    let barClass = 'bg-slate-600';
    let numClass = 'text-slate-500';
    let opacity = 'opacity-40';
    if (pct >= 50) { barClass = 'bg-primary'; numClass = 'font-extrabold text-primary'; opacity = ''; }
    else if (pct >= 20) { barClass = 'bg-secondary'; numClass = 'font-bold text-white'; opacity = 'opacity-90'; }
    else if (pct >= 5) { barClass = 'bg-slate-500'; numClass = 'text-slate-300'; opacity = 'opacity-70'; }

    celdas.push(
      <div
        key={n}
        title={`ODS ${n}${distribucion ? ` (${pct.toFixed(1)}%)` : ''}`}
        className={
          'flex flex-col rounded-xl p-2 text-center transition-all cursor-default border ' +
          (esGanador
            ? 'bg-gradient-to-b from-primary-container to-surface-container-high text-white shadow-glow-cyan border-2 border-primary scale-[1.04] z-10'
            : `bg-surface-container-low/50 hover:bg-surface-container-high border-white/10 hover:border-white/20 ${opacity}`)
        }
      >
        <div className="flex items-center justify-between mb-1.5">
          <span className={`text-[10px] font-mono-num ${esGanador ? 'font-extrabold text-primary' : numClass}`}>#{String(n).padStart(2, '0')}</span>
          <span className="w-2 h-2 rounded-full" style={{ background: sdgColors?.[n] || '#334155' }}></span>
        </div>
        <div className="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden my-1">
          <div className={`h-full rounded-full ${barClass}`} style={{ width: `${pct}%` }}></div>
        </div>
        <span className={`text-[10px] font-mono-num mt-0.5 ${esGanador ? 'font-extrabold text-primary' : numClass}`}>{pct.toFixed(1)}%</span>
      </div>
    );
  }
  return celdas;
}
