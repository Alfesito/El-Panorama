import { useState } from 'react';
import './SearchPage.css';
import WebViewPage from './WebViewPage';

type Item = {
  author: string;
  date: string;
  subtitles: string;
  tags: string[];
  title: string;
  url: string;
  newspaper: string;
};

type TrendsItem = {
  id: number;
  title: string;
  source: string;
  volume: string;
  timeframe: string;
};

type SearchPageProps = {
  items: Item[];
  trends?: TrendsItem[];
};

export default function SearchPage({ items, trends }: SearchPageProps) {
  const [query, setQuery] = useState('');
  const [finaldata, setFinaldata] = useState<Item[]>(items);
  const [selectedUrl, setSelectedUrl] = useState<string | null>(null);

  const filterByQuery = () => {
    const searchWords = query.toLowerCase().trim().split(/\s+/);
    const uniqueTitles = new Set<string>();
    const filtered = items.filter((item) => {
      const wordsInItem = [item.title, item.subtitles, ...item.tags]
        .join(' ')
        .toLowerCase()
        .split(/\s+/);
      const matches = searchWords.every((word) => wordsInItem.includes(word));
      if (matches && !uniqueTitles.has(item.title)) {
        uniqueTitles.add(item.title);
        return true;
      }
      return false;
    });
    setFinaldata(filtered);
  };

  const filterByTrend = (trendTitle: string) => {
    const uniqueTitles = new Set<string>();
    const filtered = items.filter((item) => {
      const searchText = trendTitle.toLowerCase();
      const itemText = [item.title, item.subtitles, ...item.tags].join(' ').toLowerCase();
      const matches = itemText.includes(searchText);
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
      {/* Header con logo */}
      <header className="page-header">
        <div className="header-content">
          <span className="logo-icon">📰</span>
          <h1>El Panorama</h1>
        </div>
      </header>

      {/* Layout principal */}
      <div className="main-layout">
        {/* Columna izquierda */}
        <div className="left-column">
          {/* Sección Panorama */}
          <div className="panorama-card">
            <div className="panorama-header">
              <span className="panorama-icon">📰</span>
              <h2>El Panorama</h2>
            </div>
            <p className="panorama-description">Resumen de las noticias más relevantes del día</p>
          </div>

          {/* Resultados */}
          <div className="resultados-card">
            <p className="results-count">{finaldata.length} resultados encontrados</p>
            
            <ul className="resultados-list">
              {finaldata.map((item, index) => (
                <li key={index} className="news-card">
                  <h3 className="news-title">{item.title}</h3>
                  
                  <div className="tags-row">
                    {item.tags.slice(0, 3).map((tag, idx) => (
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
                    <span>De <strong>{item.author}</strong> · A las <strong>{item.date}</strong></span>
                  </div>
                  
                  <div className="news-source">
                    <strong>{item.newspaper}</strong>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Sidebar derecha */}
        <aside className="right-sidebar">
          {/* Buscador */}
          <div className="search-card">
            <h4 className="sidebar-title">
              <span>🔍</span> Buscar noticias
            </h4>
            <div className="search-group">
              <input
                type="text"
                className="search-input"
                placeholder="Venezuela"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    filterByQuery();
                  }
                }}
              />
              <button className="search-btn" onClick={filterByQuery}>
                Buscar
              </button>
            </div>
          </div>

          {/* Trends */}
          <div className="trends-card">
            <h4 className="sidebar-title">
              <span>🔥</span> Trends populares
            </h4>
            <div className="trends-list">
              {trends?.slice(0, 15).map((trend) => (
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
