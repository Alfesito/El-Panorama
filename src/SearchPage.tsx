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

  const getUniqueTags = (arr: Item[]): string[] => {
    const allTags = arr.flatMap((item) => item.tags);
    return Array.from(new Set(allTags));
  };

  const tags = getUniqueTags(items);

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

  const filterByTag = (selectedTag: string) => {
    const uniqueTitles = new Set<string>();
    if (selectedTag === 'All') {
      setFinaldata(items);
    } else {
      const filtered = items.filter((item) => {
        const matches = item.tags.includes(selectedTag);
        if (matches && !uniqueTitles.has(item.title)) {
          uniqueTitles.add(item.title);
          return true;
        }
        return false;
      });
      setFinaldata(filtered);
    }
    setQuery('');
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
      {/* Layout principal: búsqueda + resultados | trends sidebar */}
      <div className="main-layout">
        {/* Columna izquierda: búsqueda + resultados */}
        <div className="left-column">
          {/* Buscador */}
          <div className="buscador">
            <div className="search-filter-row">
              <div className="col">
                <input
                  id="filtro"
                  type="text"
                  placeholder="Busca tema"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </div>
              <div className="col">
                <button id="buscador" onClick={filterByQuery}>
                  Buscar
                </button>
              </div>
              <div className="col">
                <select
                  id="selector"
                  defaultValue="All"
                  onChange={(e) => filterByTag(e.target.value)}
                >
                  <option value="All">Todos</option>
                  {tags.slice(0, 10).map((tag, index) => (
                    <option key={index} value={tag}>
                      {tag}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Resultados */}
          <div className="resultados-section">
            <div id="productosresultados">
              <ul id="resultados">
                {finaldata.map((item, index) => (
                  <li key={index} className="result-item">
                    <div className="unproducto">
                      <h3>{item.title}</h3>
                      <p>{item.subtitles}</p>
                      <button
                        onClick={() => setSelectedUrl(item.url)}
                        className="view-button"
                      >
                        Leer más
                      </button>
                      <p>
                        <strong>Autor:</strong> {item.author} |{' '}
                        <strong>Fecha:</strong> {item.date}
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

        {/* Sidebar Trends Derecha (sticky desde arriba) */}
        <aside className="trends-sidebar">
          <h4>🔥 Trends populares</h4>
          <div className="trends-list">
            {trends?.slice(0, 15).map((trend) => (
              <div
                key={trend.id}
                className="trend-item"
                onClick={() => filterByTrend(trend.title)}
                title={`Filtrar por "${trend.title}"`}
              >
                <strong>{trend.title}</strong>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
