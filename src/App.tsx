import { useEffect, useState } from 'react';
import mockdata from './config/json/merged_json.json';
import './App.css';
import Error from './Error';
import CONFIG from './config/config';
import SearchPage from './SearchPage';

// Tipos exactos
type DataState = 
  | { data: any[] }
  | { e: { description: string } };

type TrendsState = 
  | { trends: any[]; summary?: any }  // Summary opcional
  | { e: { description: string } };

function App() {
  const [dataState, setDataState] = useState<DataState>({ data: [] });
  const [trendsState, setTrendsState] = useState<TrendsState>({ trends: [] });
  const [loadingNews, setLoadingNews] = useState(true);
  const [loadingTrends, setLoadingTrends] = useState(true);

  const USE_SERVER = CONFIG.use_server;
  const NEWS_URL = CONFIG.news_url;
  const TRENDS_URL = CONFIG.trends_url;

  const downloadData = async () => {
    if (USE_SERVER) {
      try {
        const response = await fetch(NEWS_URL);
        if (!response.ok) {
          throw Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const res = await response.json();
        setDataState({ data: res });
      } catch (e: any) {
        setDataState({ e: { description: e.message } });
      }
    } else {
      setDataState({ data: mockdata });
    }
  };

  const downloadTrends = async () => {
    try {
      const response = await fetch(TRENDS_URL);
      if (!response.ok) {
        throw Error(`HTTP ${response.status}`);
      }
      const res = await response.json();
      setTrendsState({ 
        trends: res.trends || [], 
        summary: res.summary 
      });
    } catch (e: any) {
      setTrendsState({ e: { description: e.message } });
      console.warn('Trends no disponibles:', e.message);  // No rompe app
    }
  };

  useEffect(() => {
    async function fetchAll() {
      await Promise.all([
        downloadData().then(() => setLoadingNews(false)),
        downloadTrends().then(() => setLoadingTrends(false))
      ]);
    }
    fetchAll();
  }, []);

  const loading = loadingNews || loadingTrends;
  const hasNewsError = 'e' in dataState;
  const hasTrendsError = 'e' in trendsState;

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📰 El Panorama</h1>
        <p>Noticias España + Trends Google/X en tiempo real</p>
      </header>

      {loading ? (
        <div className="loading-container">
          <p>🔄 Cargando noticias y trends...</p>
        </div>
      ) : hasNewsError ? (
        <Error error={dataState.e} />
      ) : (
        <SearchPage 
          items={dataState.data} 
          trends={('trends' in trendsState) ? trendsState.trends : []}
        />
      )}

      {/* Status trends si falla */}
      {!loadingTrends && hasTrendsError && (
        <div className="trends-warning">
          ⚠️ Trends temporalmente no disponibles
        </div>
      )}
    </div>
  );
}

export default App;
