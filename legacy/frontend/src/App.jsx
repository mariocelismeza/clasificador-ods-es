import { useEffect, useState } from 'react';
import { fetchConfig } from './api';
import Header from './components/Header';
import Footer from './components/Footer';
import ClasificadorView from './components/ClasificadorView';
import ExploradorOdsView from './components/ExploradorOdsView';
import MatrizConfusionView from './components/MatrizConfusionView';
import AcercaDelProyectoView from './components/AcercaDelProyectoView';

export default function App() {
  const [config, setConfig] = useState(null);
  const [error, setError] = useState(null);
  const [view, setView] = useState('clasificador');

  useEffect(() => {
    fetchConfig()
      .then(setConfig)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center grid-bg-glow px-4">
        <div className="glass-panel rounded-2xl p-6 border border-red-500/30 max-w-md text-center">
          <p className="text-red-300 text-sm font-medium mb-1">No se pudo cargar la configuración del modelo</p>
          <p className="text-xs text-on-surface-variant">{error}</p>
          <p className="text-xs text-slate-500 mt-3">¿Está corriendo el backend (uvicorn main:app --port 8000)?</p>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="min-h-screen flex items-center justify-center grid-bg-glow">
        <div className="flex items-center gap-2 text-on-surface-variant text-sm">
          <span className="material-symbols-outlined animate-spin">progress_activity</span>
          Cargando modelo…
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen grid-bg-glow">
      <Header view={view} setView={setView} modeloListo={!!config} />
      <main className="w-full flex-1">
        <ClasificadorView visible={view === 'clasificador'} config={config} />
        <ExploradorOdsView visible={view === 'explorador-ods'} config={config} />
        <MatrizConfusionView visible={view === 'matriz-de-confusion'} config={config} />
        <AcercaDelProyectoView visible={view === 'acerca-del-proyecto'} config={config} />
      </main>
      <Footer />
    </div>
  );
}
