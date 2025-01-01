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

type SearchPageProps = {
  items: Item[];
};

export default function SearchPage({ items }: SearchPageProps) {
    const [query, setQuery] = useState('');
    const [finaldata, setFinaldata] = useState<Item[]>(items);
    const [selectedUrl, setSelectedUrl] = useState<string | null>(null); // Estado para el URL de la noticia seleccionada
  
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
  
    return selectedUrl ? (
      <WebViewPage url={selectedUrl} onBack={() => setSelectedUrl(null)} />
    ) : (
      <div>
        <div className="buscador">
          <div className="search-filter-row">
            <div className="col">
              <input
                id="filtro"
                type="text"
                placeholder="Busca un artículo"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
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
                <option value="All">All</option>
                {tags.map((tag, index) => (
                  <option key={index} value={tag}>
                    {tag}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
  
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
                    <strong> {item.newspaper} </strong>
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
  
  