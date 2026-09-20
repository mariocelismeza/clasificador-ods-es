import { useEffect, useRef, useState } from 'react';

/**
 * Ícono "info" pequeño que muestra una explicación en lenguaje sencillo al
 * hacer clic (funciona igual en mouse y en touch). Pensado para acompañar
 * términos técnicos (probabilidad calibrada, margen del SVM, etc.) sin
 * saturar la interfaz.
 */
export default function InfoTooltip({ texto, posicion = 'top', align = 'center' }) {
  const [abierto, setAbierto] = useState(false);
  const contenedorRef = useRef(null);

  useEffect(() => {
    if (!abierto) return;
    function alClicFuera(e) {
      if (contenedorRef.current && !contenedorRef.current.contains(e.target)) {
        setAbierto(false);
      }
    }
    document.addEventListener('mousedown', alClicFuera);
    return () => document.removeEventListener('mousedown', alClicFuera);
  }, [abierto]);

  const esArriba = posicion === 'top';

  // El contenedor de la tarjeta principal usa overflow-hidden (para el efecto
  // de brillo en los bordes), así que un tooltip centrado puede salirse y
  // cortarse cuando el botón está cerca del borde derecho. `align` permite
  // anclar el tooltip a la izquierda o derecha del ícono en esos casos.
  const clasesAlineacion =
    align === 'right'
      ? 'right-0'
      : align === 'left'
      ? 'left-0'
      : 'left-1/2 -translate-x-1/2';

  return (
    <span className="relative inline-flex" ref={contenedorRef}>
      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        aria-label="Más información"
        aria-expanded={abierto}
        className="text-secondary hover:text-primary transition-colors inline-flex items-center focus:outline-none focus:text-primary"
      >
        <span className="material-symbols-outlined text-[14px] leading-none">info</span>
      </button>
      {abierto && (
        <div
          role="tooltip"
          className={
            'absolute z-50 w-64 max-w-[80vw] bg-surface-container-high border border-white/10 ' +
            'rounded-lg p-3 text-[11px] leading-relaxed text-on-surface-variant shadow-xl font-sans normal-case font-normal tracking-normal ' +
            clasesAlineacion + ' ' +
            (esArriba ? 'bottom-full mb-2' : 'top-full mt-2')
          }
        >
          {texto}
        </div>
      )}
    </span>
  );
}
