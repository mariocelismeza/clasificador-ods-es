export default function Footer() {
  return (
    <footer className="w-full bg-surface-container-lowest border-t border-white/10 py-5 mt-auto">
      <div className="max-w-[1480px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center gap-1 text-xs text-secondary text-center leading-relaxed">
        <span>Proyecto académico — Microproyecto 2, Maestría en IA (Aprendizaje No Supervisado)</span>
        <span className="text-on-surface-variant">Basado en el OSDG Community Dataset y en los 17 Objetivos de Desarrollo Sostenible de la Agenda 2030 de la ONU.</span>
        <span className="text-slate-600">Esta aplicación no está afiliada ni respaldada por las Naciones Unidas.</span>
      </div>
    </footer>
  );
}
