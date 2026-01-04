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
      {/* Layout principal: panorama + noticias a la izquierda | búsqueda + trends a la derecha */}
      <div className="main-layout">
        {/* Columna izquierda: Panorama + Resultados */}
        <div className="left-column">
          {/* Sección Panorama */}
          <div className="panorama-section">
            <h2>📰 El Panorama</h2>
            <p>Resumen de las noticias más relevantes del día</p>
            {/* Aquí puedes agregar contenido adicional del panorama */}
          </div>

          {/* Resultados de noticias */}
          <div className="resultados-section">
            <div id="productosresultados">
              <p className="results-count">
                {finaldata.length} resultado{finaldata.length !== 1 ? 's' : ''} encontrado{finaldata.length !== 1 ? 's' : ''}
              </p>
              <ul id="resultados">
                {finaldata.map((item, index) => (
                  <li key={index} className="result-item">
                    <div className="unproducto">
                      <h3>{item.title}</h3>
                      <p>{item.subtitles}</p>
                      <div className="tags-container">
                        {item.tags.slice(0, 3).map((tag, idx) => (
                          <span key={idx} className="tag-badge">{tag}</span>
                        ))}
                      </div>
                      <button
                        onClick={() => setSelectedUrl(item.url)}
                        className="view-button"
                      >
                        Leer más
                      </button>
                      <p>
                        De <strong>{item.author}</strong> · A las <strong>{item.date}</strong>
                      </p>
                      <p>
                        <strong>{item.newspaper}</strong>
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Columna derecha: Buscador + Trends (sticky) */}
        <aside className="right-sidebar">
          {/* Buscador */}
          <div className="buscador-sidebar">
            <h4>🔍 Buscar noticias</h4>
            <div className="search-input-group">
              <input
                id="filtro"
                type="text"
                placeholder="Busca tema..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    filterByQuery();
                  }
                }}
              />
              <button id="buscador" onClick={filterByQuery}>
                Buscar
              </button>
            </div>
          </div>

          {/* Trends */}
          <div className="trends-section">
            <h4>🔥 Trends populares</h4>
            <div className="trends-list">
              {trends?.slice(0, 15).map((trend) => (
                <div
                  key={trend.id}
                  className="trend-item"
                  onClick={() => filterByTrend(trend.title)}
                  style={{ cursor: 'pointer' }}
                  title={`Filtrar por "${trend.title}"`}
                >
                  <strong>{trend.title}</strong>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
