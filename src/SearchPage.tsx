import { useState } from 'react';
import './SearchPage.css';
import WebViewPage from './WebViewPage';
import AnalysisCard from './AnalysisCard';

type Item = {
  author: string;
  date: string;
  subtitles: string;
  body?: string; // ← AÑADIDO (opcional)
  tags: string[];
  title: string;
  url: string;
  newspaper: string;
  image?: string;
};

type TrendsItem = {
  id: number;
  title: string;
  source: string;
  volume: string;
  timeframe: string;
  news_count: number;
};

type SearchPageProps = {
  items: Item[];
  trends?: TrendsItem[];
};

export default function SearchPage({ items, trends }: SearchPageProps) {
  const [query, setQuery] = useState('');
  const [finaldata, setFinaldata] = useState<Item[]>(items);
  const [selectedUrl, setSelectedUrl] = useState<string | null>(null);
  const [showAnalysis, setShowAnalysis] = useState(false);

  // Función auxiliar para normalizar texto (eliminar acentos)
  const normalizeText = (text: string): string => {
    return text
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  };

  // Función para formatear fecha relativa
  const formatRelativeTime = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInMs = now.getTime() - date.getTime();
      const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
      const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
      const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

      if (diffInMinutes < 1) {
        return 'Hace menos de 1 minuto';
      } else if (diffInMinutes < 60) {
        return `Hace ${diffInMinutes} minuto${diffInMinutes !== 1 ? 's' : ''}`;
      } else if (diffInHours < 24) {
        return `Hace ${diffInHours} hora${diffInHours !== 1 ? 's' : ''}`;
      } else if (diffInDays === 1) {
        return 'Hace 1 día';
      } else if (diffInDays < 7) {
        return `Hace ${diffInDays} días`;
      } else if (diffInDays < 30) {
        const weeks = Math.floor(diffInDays / 7);
        return `Hace ${weeks} semana${weeks !== 1 ? 's' : ''}`;
      } else if (diffInDays < 365) {
        const months = Math.floor(diffInDays / 30);
        return `Hace ${months} mes${months !== 1 ? 'es' : ''}`;
      } else {
        const years = Math.floor(diffInDays / 365);
        return `Hace ${years} año${years !== 1 ? 's' : ''}`;
      }
    } catch (error) {
      return dateString;
    }
  };

  const filterByQuery = () => {
    const searchWords = query.trim().split(/\s+/).map(normalizeText);
    
    if (searchWords.length === 0 || searchWords[0] === '') {
      setFinaldata(items);
      return;
    }
    
    const uniqueTitles = new Set<string>();
    
    const filtered = items.filter((item) => {
      // Incluir body si existe
      const itemText = normalizeText(
        [
          item.title, 
          item.subtitles, 
          item.body || '', // ← AÑADIDO
          ...item.tags
        ].join(' ')
      );
      
      // Verifica que TODAS las palabras de búsqueda estén presentes
      const matches = searchWords.every((word) => itemText.includes(word));
      
      if (matches && !uniqueTitles.has(item.title)) {
        uniqueTitles.add(item.title);
        return true;
      }
      return false;
    });
    
    setFinaldata(filtered);
  };

  const filterByTrend = (trendTitle: string) => {
    const searchWords = trendTitle.trim().split(/\s+/).map(normalizeText);
    const uniqueTitles = new Set<string>();
    
    const filtered = items.filter((item) => {
      // Incluir body si existe
      const itemText = normalizeText(
        [
          item.title, 
          item.subtitles, 
          item.body || '', // ← AÑADIDO
          ...item.tags
        ].join(' ')
      );
      
      // Verifica que TODAS las palabras del trend estén presentes
      const matches = searchWords.every((word) => itemText.includes(word));
      
      if (matches && !uniqueTitles.has(item.title)) {
        uniqueTitles.add(item.title);
        return true;
      }
      return false;
    });
    
    setFinaldata(filtered);
    setQuery(trendTitle);
  };

  return selectedUrl ? (
    <WebViewPage url={selectedUrl} onBack={() => setSelectedUrl(null)} />
  ) : (
    <div className="search-page-container">
      {/* Layout principal */}
      <div className="main-layout">
        {/* Columna izquierda */}
        <div className="left-column">
          {/* Pestañas */}
          <div className="tabs-container">
            <button 
              className={`tab-btn ${!showAnalysis ? 'active' : ''}`}
              onClick={() => setShowAnalysis(false)}
            >
              📰 Noticias
            </button>
            <button 
              className={`tab-btn ${showAnalysis ? 'active' : ''}`}
              onClick={() => setShowAnalysis(true)}
            >
              📊 Análisis
            </button>
          </div>

          {showAnalysis ? (
            // Sección de Análisis
            <AnalysisCard />
          ) : (
            // Sección de Noticias (original)
            <>
              {/* Card combinada: Panorama + Buscador horizontal */}
          <div className="panorama-search-card">
            {/* Header El Panorama */}
            <div className="panorama-section">
              <div className="header-content">
                <span className="logo-icon">📰</span>
                <header><h1>El Panorama</h1></header>
              </div>
            </div>

            {/* Buscador */}
            <div className="search-section">
              <h4 className="search-title">
                <span>🔍</span> Buscar noticias
              </h4>
              <div className="search-group-horizontal">
                <input
                  type="text"
                  className="search-input"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      filterByQuery();
                    }
                  }}
                  placeholder="Buscar noticias..."
                />
                <button className="search-btn" onClick={filterByQuery}>
                  Buscar
                </button>
              </div>
            </div>
          </div>

          {/* Resultados */}
          <div className="resultados-card">            
            <ul className="resultados-list">
              {finaldata.map((item, index) => (
                <li key={index} className="news-card">
                  <h3 className="news-title">{item.title}</h3>
                  
                  <div className="tags-row">
                    {item.tags.slice().map((tag, idx) => (
                      <span key={idx} className="tag-pill">{tag}</span>
                    ))}
                  </div>
                  
                  <button
                    onClick={() => setSelectedUrl(item.url)}
                    className="read-more-btn"
                  >
                    Leer más
                  </button>
                  
                  <div className="news-meta">
                    <span>De <strong>{item.author}</strong> · {formatRelativeTime(item.date)}</span>
                  </div>
                  
                  <div className="news-source">
                    <strong>{item.newspaper}</strong>
                  </div>
                </li>
              ))}
            </ul>
          </div>
            </>
          )}
        </div>

        {/* Sidebar derecha - Solo Trends */}
        <aside className="right-sidebar">
          {/* Trends */}
          <div className="trends-card">
            <h4 className="sidebar-title">
              <span>🔥</span> Trends populares
            </h4>
            <div className="trends-list">
              {trends
                ?.filter((trend) => trend.news_count !== 0)
                .slice(0, 20)
                .map((trend) => (
                  <div
                    key={trend.id}
                    className="trend-item"
                    onClick={() => filterByTrend(trend.title)}
                  >
                    {trend.title}
                  </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
