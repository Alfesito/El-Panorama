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

  // Función para normalizar texto (quitar tildes, ñ -> n, etc.)
  const normalizeText = (text: string): string => {
    return text
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();
  };

  // MODIFICADO: Ahora acepta un parámetro opcional para buscar directamente
  const filterByQuery = (searchQuery?: string) => {
    const queryToUse = searchQuery !== undefined ? searchQuery : query;
    
    if (!queryToUse.trim()) {
      setFinaldata(items);
      return;
    }

    const searchWords = normalizeText(queryToUse).split(/\s+/);
    const uniqueTitles = new Set<string>();

    // Stopwords en español (palabras a ignorar)
    const stopwords = new Set(['el', 'la', 'los', 'las', 'de', 'del', 'y', 'en', 'un', 'una', 'es', 'por', 'con', 'para', 'al', 'a']);
    const filteredSearchWords = searchWords.filter(word => !stopwords.has(word) && word.length > 2);

    const filtered = items.filter((item) => {
      // Normalizar todos los campos
      const titleNorm = normalizeText(item.title);
      const subtitlesNorm = normalizeText(item.subtitles);
      const tagsNorm = item.tags.map(tag => normalizeText(tag));

      // Método 1: Match exacto en título (alta prioridad)
      if (filteredSearchWords.every(word => titleNorm.includes(word))) {
        if (!uniqueTitles.has(item.title)) {
          uniqueTitles.add(item.title);
          return true;
        }
        return false;
      }

      // Método 2: Match exacto en tags
      const matchInTags = filteredSearchWords.some(word => 
        tagsNorm.some(tag => tag === word || tag.includes(word))
      );
      if (matchInTags && filteredSearchWords.length <= 2) {
        if (!uniqueTitles.has(item.title)) {
          uniqueTitles.add(item.title);
          return true;
        }
        return false;
      }

      // Método 3: Al menos 70% de palabras clave presentes en título + subtítulos
      const combinedText = `${titleNorm} ${subtitlesNorm}`;
      const matchedWords = filteredSearchWords.filter(word => combinedText.includes(word));
      const matchRatio = matchedWords.length / filteredSearchWords.length;

      if (matchRatio >= 0.7) {
        if (!uniqueTitles.has(item.title)) {
          uniqueTitles.add(item.title);
          return true;
        }
      }

      return false;
    });

    console.log('✅ Resultados encontrados:', filtered.length);
    setFinaldata(filtered);
  };

  // MODIFICADO: Manejador simplificado para clicks en trends
  const handleTrendClick = (trendTitle: string) => {
    console.log('👆 Click en trend:', trendTitle);
    setQuery(trendTitle); // Actualiza el input visual
    filterByQuery(trendTitle); // Filtra inmediatamente con el texto del trend
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
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') filterByQuery();
                  }}
                />
              </div>
              <div className="col">
                <button id="buscador" onClick={() => filterByQuery()}>
                  Buscar
                </button>
              </div>
            </div>
          </div>

          {/* Resultados */}
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
                        De <strong>{item.author}</strong>  ·{' '}
                        A las <strong>{item.date}</strong>
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
            {trends?.slice(0, 25).map((trend) => (
              <div
                key={trend.id}
                className="trend-item"
                onClick={() => handleTrendClick(trend.title)}
                style={{ cursor: 'pointer' }}
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
