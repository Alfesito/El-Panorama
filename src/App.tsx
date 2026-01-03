import { useEffect, useState } from 'react';
import mockdata from './config/json/merged_json.json';
import './App.css';
import Error from './Error';
import CONFIG from './config/config';
import SearchPage from './SeachPage';

type DataState = 
  | { data: any[] }
  | { e: { description: string } };

type TrendsState = 
  | { trends: any[] | null; summary: any | null }
  | { e: { description: string } };

function App() {
  const [dataState, setDataState] = useState<DataState>({ data: [] });
  const [trendsState, setTrendsState] = useState<TrendsState>({ trends: null, summary: null });
  const [loading, setLoading] = useState<boolean>(true);

  const USE_SERVER = CONFIG.use_server;
  const NEWS_URL = CONFIG.news_url;
  const TRENDS_URL = CONFIG.trends_url;

  const downloadData = async () => {
    if (USE_SERVER) {
      try {
        const response = await fetch(NEWS_URL);
        if (response.status === 200) {
          const res = await response.json();
          setDataState({ data: res });
        } else {
          setDataState({ e: { description: `Error ${response.status}: ${response.statusText}` } });
        }
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
      if (response.status === 200) {
        const res = await response.json();
        setTrendsState({ 
          trends: res.trends || [], 
          summary: res.summary || null 
        });
      } else {
        setTrendsState({ e: { description: `Error trends: ${response.status}` } });
      }
    } catch (e: any) {
      setTrendsState({ e: { description: e.message } });
    }
  };

  useEffect(() => {
    async function fetchAll() {
      await Promise.all([downloadData(), downloadTrends()]);
      setTimeout(() => setLoading(false), 500);
    }
    fetchAll();
  }, []);

  return (
    <>
      <h1>El Panorama</h1>
      
      {/* Trends Section */}
      {!loading && 'trends' in trendsState && trendsState.trends && (
        <div className="trends-section mb-4 p-4 border rounded">
          <h3>🔥 Temas del día</h3>
          {trendsState.summary && (
            <p className="mb-3">
              <strong>{trendsState.summary.unique_total} trends únicos</strong> 
              (Google: {trendsState.summary.google_total}, X: {trendsState.summary.xtrends_total})
              <br />
              <small>Actualizado: {new Date(trendsState.summary.timestamp || '').toLocaleString('es-ES')}</small>
            </p>
          )}
          <div className="trends-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
            {trendsState.trends.slice(0, 12).map((trend: any) => (  // Top 12
              <div key={trend.id} className="trend-item p-2 bg-light rounded hover:shadow cursor-pointer">
                <strong>{trend.title}</strong>
                <br />
                <small>
                  {trend.source} • {trend.volume || 'N/A'} • {trend.timeframe}
                </small>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <p>Cargando noticias y trends...</p>
      ) : "e" in dataState ? (
        <Error error={dataState.e} />
      ) : (
        <SearchPage items={dataState.data} />
      )}
    </>
  );
}

export default App;
