import { useState } from 'react';
import './AnalysisCard.css';
import analysisData from './config/json/analisis_historico.json';
import newsData from './config/json/merged_json.json';

type AnalysisItem = {
  tema: string;
  fecha_analisis: string;
  total_articulos: number;
  resumen_objetivo: string;
  lista_medios: string[];
  total_medios: number;
  noticias_analizadas: number;
  puntos_comunes: string[];
  analisis_5w1h?: {
    que?: string;
    quien?: string;
    cuando?: string;
    donde?: string;
    por_que?: string;
    como?: string;
  };
  divergencias_principales?: Array<{
    aspecto: string;
    diferencia: string;
    perspectivas_medios?: Record<string, string>;
    impacto_percepcion?: string;
  }>;
  cobertura_por_medio?: Record<string, {
    enfoque_principal?: string;
    tono?: string;
    elementos_destacados?: string[];
  }>;
  analisis_sentimiento?: {
    tono_general?: string;
    nivel_sensacionalismo_promedio?: number;
    descripcion?: string;
  };
  analisis_detallado_sesgo?: Record<string, {
    score_sesgo_0_100?: number;
    clasificacion?: string;
    lenguaje?: {
      nivel_emotividad_0_100?: number;
      palabras_cargadas?: string[];
      intensificadores?: string[];
      adjetivos_tendenciosos?: string[];
      uso_voz_pasiva_para_esconder_responsabilidad?: boolean;
    };
    atribucion_fuentes?: {
      citas_directas?: number;
      citas_indirectas?: number;
      afirmaciones_sin_fuente?: number;
      score_calidad_fuentes_0_100?: number;
      tipos_fuentes_usadas?: string[];
    };
  }>;
  sesgo_detectado?: Record<string, {
    orientacion_detectada?: string;
    nivel_bias?: number;
    indicadores?: string[];
  }>;
  palabras_mas_frecuentes_por_medio?: Record<string, {
    positivas?: string[];
    negativas?: string[];
    neutras?: string[];
  }>;
  omisiones_importantes?: Array<{
    medio: string;
    informacion_omitida: string;
  }>;
  omisiones_relevantes?: Array<{
    medio: string;
    informacion_omitida: string;
  }>;
  matriz_comparativa?: {
    medio_mas_objetivo?: string;
    score_mas_objetivo?: number;
    medio_mas_sesgado?: string;
    score_mas_sesgado?: number;
    consensus_nivel?: string;
  };
  recomendacion_para_lector?: string;
  modelo_usado?: string;
  metodo?: string;
  distribucion_articulos_por_medio?: Record<string, number>;
  estadisticas?: {
    distribucion_por_medio: Record<string, {
      num_articulos: number;
      porcentaje_cobertura: number;
      urls?: string[];
    }>;
  };
};

export default function AnalysisCard() {
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisItem | null>(null);

  if (selectedAnalysis) {
    return (
      <AnalysisDetail analysis={selectedAnalysis} onBack={() => setSelectedAnalysis(null)} />
    );
  }

  const analysisItems = (analysisData as unknown) as AnalysisItem[];

  return (
    <div className="analysis-list-container">
      <h3 className="analysis-list-title">📊 Análisis disponibles</h3>
      <div className="analysis-items-list">
        {analysisItems.map((analysis, idx) => {
          // Obtener imagen de la primera URL
          const firstMediaKey = Object.keys(analysis.estadisticas?.distribucion_por_medio || {})[0];
          const firstUrl = analysis.estadisticas?.distribucion_por_medio[firstMediaKey]?.urls?.[0] || '';
          
          // Función para obtener un título de noticia por periódico
          const getNewspaperTitle = (newspaper: string) => {
            const newsArray = (newsData as unknown) as Array<{ newspaper: string; title: string }>;
            // Buscar por nombre exacto primero
            let news = newsArray.find((n) => n.newspaper === newspaper);
            // Si no encuentra, buscar parcialmente (caso insensitivo)
            if (!news) {
              news = newsArray.find((n) => n.newspaper.toLowerCase().includes(newspaper.toLowerCase()) || newspaper.toLowerCase().includes(n.newspaper.toLowerCase()));
            }
            // Si aún no encuentra, tomar el primero del periódico
            if (!news) {
              news = newsArray.find((n) => n.newspaper === newspaper) || newsArray[0];
            }
            return news?.title || newspaper;
          };
          
          // Obtener títulos de todos los periódicos
          const newspaperTitles = analysis.lista_medios || [];
          
          return (
            <button
              key={idx}
              className="analysis-list-item"
              onClick={() => setSelectedAnalysis(analysis)}
            >
              <div className="analysis-list-image">
                {firstUrl ? (
                  <img 
                    src={`https://via.placeholder.com/60x80?text=${encodeURIComponent(firstMediaKey || 'News')}`}
                    alt="news"
                    className="analysis-list-img-thumbnail"
                  />
                ) : (
                  <span className="analysis-list-image-placeholder">📰</span>
                )}
              </div>
              <div className="analysis-item-content">
                <h4 className="analysis-item-title">{analysis.tema}</h4>
                {newspaperTitles.length > 0 && (
                  <div className="analysis-item-newspapers">
                    {newspaperTitles.map((newspaper, nIdx) => (
                      <div key={nIdx} className="analysis-newspaper-item">
                        <span className="analysis-newspaper-name">{newspaper}</span>
                        <p className="analysis-newspaper-headline">{getNewspaperTitle(newspaper)}</p>
                      </div>
                    ))}
                  </div>
                )}
                <p className="analysis-item-meta">
                  {analysis.total_articulos} artículos • {analysis.total_medios} medios
                </p>
                <p className="analysis-item-date">
                  {new Date(analysis.fecha_analisis).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
              <span className="analysis-item-arrow">→</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function AnalysisDetail({ analysis, onBack }: { analysis: AnalysisItem; onBack: () => void }) {
  const topMediaByVolume = Object.entries(analysis.estadisticas?.distribucion_por_medio || {})
    .sort(([, a], [, b]) => (b.num_articulos || 0) - (a.num_articulos || 0))
    .slice(0, 6);

  return (
    <div className="analysis-detail-container">
      {/* Header */}
      <div className="analysis-detail-header">
        <button className="back-btn" onClick={onBack}>
          ← Volver
        </button>
        <h2 className="analysis-detail-title">{analysis.tema}</h2>
      </div>

      {/* Contenido */}
      <div className="analysis-detail-content">
        {/* Fecha y metadatos */}
        <div className="analysis-detail-section">
          <div className="analysis-metadata">
            <div className="analysis-meta-item">
              <span className="analysis-meta-label">📅 Fecha de análisis:</span>
              <span>{new Date(analysis.fecha_analisis).toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
            </div>
            {analysis.modelo_usado && (
              <div className="analysis-meta-item">
                <span className="analysis-meta-label">🤖 Modelo:</span>
                <span>{analysis.modelo_usado}</span>
              </div>
            )}
            {analysis.metodo && (
              <div className="analysis-meta-item">
                <span className="analysis-meta-label">⚙️ Método:</span>
                <span>{analysis.metodo}</span>
              </div>
            )}
          </div>
        </div>

        {/* Resumen */}
        <div className="analysis-detail-section">
          <h3>Resumen Objetivo</h3>
          <p>{analysis.resumen_objetivo}</p>
        </div>

        {/* Análisis 5W1H */}
        {analysis.analisis_5w1h && (
          <div className="analysis-detail-section">
            <h3>Análisis 5W+1H</h3>
            <div className="analysis-5w1h-grid">
              {analysis.analisis_5w1h.que && (
                <div className="analysis-5w1h-item">
                  <span className="analysis-5w1h-label">¿QUÉ?</span>
                  <p>{analysis.analisis_5w1h.que}</p>
                </div>
              )}
              {analysis.analisis_5w1h.quien && (
                <div className="analysis-5w1h-item">
                  <span className="analysis-5w1h-label">¿QUIÉN?</span>
                  <p>{analysis.analisis_5w1h.quien}</p>
                </div>
              )}
              {analysis.analisis_5w1h.cuando && (
                <div className="analysis-5w1h-item">
                  <span className="analysis-5w1h-label">¿CUÁNDO?</span>
                  <p>{analysis.analisis_5w1h.cuando}</p>
                </div>
              )}
              {analysis.analisis_5w1h.donde && (
                <div className="analysis-5w1h-item">
                  <span className="analysis-5w1h-label">¿DÓNDE?</span>
                  <p>{analysis.analisis_5w1h.donde}</p>
                </div>
              )}
              {analysis.analisis_5w1h.por_que && (
                <div className="analysis-5w1h-item">
                  <span className="analysis-5w1h-label">¿POR QUÉ?</span>
                  <p>{analysis.analisis_5w1h.por_que}</p>
                </div>
              )}
              {analysis.analisis_5w1h.como && (
                <div className="analysis-5w1h-item">
                  <span className="analysis-5w1h-label">¿CÓMO?</span>
                  <p>{analysis.analisis_5w1h.como}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Puntos comunes */}
        <div className="analysis-detail-section">
          <h3>Puntos Clave</h3>
          <ul className="analysis-detail-list">
            {analysis.puntos_comunes.map((punto, idx) => (
              <li key={idx}>{punto}</li>
            ))}
          </ul>
        </div>

        {/* Análisis de sentimiento */}
        {analysis.analisis_sentimiento && (
          <div className="analysis-detail-section">
            <h3>Análisis de Sentimiento</h3>
            <div className="analysis-sentiment-box">
              <div className="analysis-sentiment-item">
                <span className="analysis-sentiment-label">Tono general:</span>
                <span className="analysis-sentiment-value">{analysis.analisis_sentimiento.tono_general}</span>
              </div>
              {analysis.analisis_sentimiento.nivel_sensacionalismo_promedio !== undefined && (
                <div className="analysis-sentiment-item">
                  <span className="analysis-sentiment-label">Sensacionalismo:</span>
                  <div className="analysis-sentiment-bar">
                    <div
                      className="analysis-sentiment-bar-fill"
                      style={{ width: `${(analysis.analisis_sentimiento.nivel_sensacionalismo_promedio || 0) * 100}%` }}
                    />
                  </div>
                </div>
              )}
              {analysis.analisis_sentimiento.descripcion && (
                <p className="analysis-sentiment-description">{analysis.analisis_sentimiento.descripcion}</p>
              )}
            </div>
          </div>
        )}

        {/* Análisis detallado de sesgo */}
        {analysis.analisis_detallado_sesgo && Object.keys(analysis.analisis_detallado_sesgo).length > 0 && (
          <div className="analysis-detail-section">
            <h3>Análisis Detallado de Sesgo</h3>
            <div className="analysis-detailed-bias-grid">
              {Object.entries(analysis.analisis_detallado_sesgo).map(([medio, sesgo]) => (
                <div key={medio} className="analysis-detailed-bias-item">
                  <h4>{medio}</h4>
                  {sesgo.score_sesgo_0_100 !== undefined && (
                    <div className="analysis-bias-score">
                      <span className="analysis-bias-score-label">Score de sesgo:</span>
                      <div className="analysis-bias-score-bar">
                        <div
                          className="analysis-bias-score-fill"
                          style={{
                            width: `${sesgo.score_sesgo_0_100}%`,
                            background: sesgo.score_sesgo_0_100 > 60 ? '#ef5350' : sesgo.score_sesgo_0_100 > 40 ? '#ffa726' : '#81c784'
                          }}
                        />
                      </div>
                      <span className="analysis-bias-score-value">{sesgo.score_sesgo_0_100}%</span>
                    </div>
                  )}
                  {sesgo.clasificacion && (
                    <p className="analysis-bias-classification">{sesgo.clasificacion}</p>
                  )}
                  {sesgo.lenguaje && (
                    <div className="analysis-bias-language">
                      {sesgo.lenguaje.nivel_emotividad_0_100 !== undefined && (
                        <p><strong>Emotividad:</strong> {sesgo.lenguaje.nivel_emotividad_0_100}%</p>
                      )}
                      {sesgo.lenguaje.palabras_cargadas && sesgo.lenguaje.palabras_cargadas.length > 0 && (
                        <p><strong>Palabras cargadas:</strong> {sesgo.lenguaje.palabras_cargadas.join(', ')}</p>
                      )}
                    </div>
                  )}
                  {sesgo.atribucion_fuentes && (
                    <div className="analysis-bias-sources">
                      <p><strong>Citas directas:</strong> {sesgo.atribucion_fuentes.citas_directas}</p>
                      <p><strong>Citas indirectas:</strong> {sesgo.atribucion_fuentes.citas_indirectas}</p>
                      {sesgo.atribucion_fuentes.score_calidad_fuentes_0_100 !== undefined && (
                        <p><strong>Calidad de fuentes:</strong> {sesgo.atribucion_fuentes.score_calidad_fuentes_0_100}%</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Distribución de medios */}
        <div className="analysis-detail-section">
          <h3>Cobertura por Medio</h3>
          <div className="analysis-detail-media">
            {topMediaByVolume.map(([medio, data]) => (
              <div key={medio} className="analysis-media-item">
                <div className="analysis-media-header">
                  <span className="analysis-media-name">{medio}</span>
                  <span className="analysis-media-badge">{data.num_articulos}</span>
                </div>
                <div className="analysis-media-bar-container">
                  <div 
                    className="analysis-media-bar"
                    style={{ width: `${data.porcentaje_cobertura}%` }}
                  />
                </div>
                <span className="analysis-media-percent">{data.porcentaje_cobertura.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* URLs de artículos */}
        {analysis.estadisticas?.distribucion_por_medio && (
          <div className="analysis-detail-section">
            <h3>Artículos Analizados</h3>
            <div className="analysis-articles-urls">
              {Object.entries(analysis.estadisticas.distribucion_por_medio).map(([medio, data]) => (
                data.urls && data.urls.length > 0 && (
                  <div key={medio} className="analysis-medium-articles">
                    <h4>{medio} ({data.urls.length})</h4>
                    <ul className="analysis-urls-list">
                      {data.urls.slice(0, 3).map((url, idx) => (
                        <li key={idx}>
                          <a href={url} target="_blank" rel="noopener noreferrer" className="analysis-url-link">
                            {url.substring(0, 60)}...
                          </a>
                        </li>
                      ))}
                      {data.urls.length > 3 && (
                        <li className="analysis-urls-more">+{data.urls.length - 3} más</li>
                      )}
                    </ul>
                  </div>
                )
              ))}
            </div>
          </div>
        )}

        {/* Cobertura detallada por medio */}
        {analysis.cobertura_por_medio && Object.keys(analysis.cobertura_por_medio).length > 0 && (
          <div className="analysis-detail-section">
            <h3>Enfoque por Medio</h3>
            <div className="analysis-media-coverage">
              {Object.entries(analysis.cobertura_por_medio).map(([medio, coverage]) => (
                <div key={medio} className="analysis-media-coverage-item">
                  <h4>{medio}</h4>
                  <div className="analysis-coverage-detail">
                    {coverage.enfoque_principal && (
                      <p><strong>Enfoque:</strong> {coverage.enfoque_principal}</p>
                    )}
                    {coverage.tono && (
                      <p><strong>Tono:</strong> <span className={`analysis-tone-badge ${coverage.tono}`}>{coverage.tono}</span></p>
                    )}
                    {coverage.elementos_destacados && coverage.elementos_destacados.length > 0 && (
                      <p><strong>Elementos destacados:</strong> {coverage.elementos_destacados.join(', ')}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sesgo detectado */}
        {analysis.sesgo_detectado && Object.keys(analysis.sesgo_detectado).length > 0 && (
          <div className="analysis-detail-section">
            <h3>Sesgo Detectado</h3>
            <div className="analysis-bias-grid">
              {Object.entries(analysis.sesgo_detectado).map(([medio, bias]) => (
                <div key={medio} className="analysis-bias-item">
                  <h4>{medio}</h4>
                  <div className="analysis-bias-detail">
                    {bias.orientacion_detectada && (
                      <p><strong>Orientación:</strong> {bias.orientacion_detectada}</p>
                    )}
                    {bias.nivel_bias !== undefined && (
                      <div className="analysis-bias-level">
                        <span className="analysis-bias-label">Nivel de sesgo:</span>
                        <div className="analysis-bias-bar-container">
                          <div
                            className="analysis-bias-bar"
                            style={{ 
                              width: `${Math.min(bias.nivel_bias * 100, 100)}%`,
                              background: bias.nivel_bias > 0.6 ? '#ef5350' : bias.nivel_bias > 0.4 ? '#ffa726' : '#81c784'
                            }}
                          />
                        </div>
                        <span className="analysis-bias-value">{(bias.nivel_bias * 100).toFixed(0)}%</span>
                      </div>
                    )}
                    {bias.indicadores && bias.indicadores.length > 0 && (
                      <ul className="analysis-bias-indicators">
                        {bias.indicadores.map((ind, i) => (
                          <li key={i}>{ind}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Matriz comparativa */}
        {analysis.matriz_comparativa && (
          <div className="analysis-detail-section">
            <h3>Matriz Comparativa de Sesgo</h3>
            <div className="analysis-matrix-box">
              {analysis.matriz_comparativa.medio_mas_objetivo && (
                <div className="analysis-matrix-item">
                  <span className="analysis-matrix-label">✅ Más objetivo:</span>
                  <span className="analysis-matrix-value">{analysis.matriz_comparativa.medio_mas_objetivo}</span>
                </div>
              )}
              {analysis.matriz_comparativa.medio_mas_sesgado && (
                <div className="analysis-matrix-item">
                  <span className="analysis-matrix-label">⚠️ Más sesgado:</span>
                  <span className="analysis-matrix-value">{analysis.matriz_comparativa.medio_mas_sesgado}</span>
                </div>
              )}
              {analysis.matriz_comparativa.consensus_nivel && (
                <div className="analysis-matrix-item">
                  <span className="analysis-matrix-label">📊 Consenso:</span>
                  <span className="analysis-matrix-value">{analysis.matriz_comparativa.consensus_nivel}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Divergencias principales */}
        {analysis.divergencias_principales && analysis.divergencias_principales.length > 0 && (
          <div className="analysis-detail-section">
            <h3>Divergencias Principales</h3>
            <div className="analysis-divergences">
              {analysis.divergencias_principales.map((div, idx) => (
                <div key={idx} className="analysis-divergence-item">
                  <h4>{div.aspecto}</h4>
                  <p><strong>Diferencia:</strong> {div.diferencia}</p>
                  {div.impacto_percepcion && (
                    <p><strong>Impacto en percepción:</strong> {div.impacto_percepcion}</p>
                  )}
                  {div.perspectivas_medios && Object.keys(div.perspectivas_medios).length > 0 && (
                    <div className="analysis-perspectives">
                      <strong>Perspectivas por medio:</strong>
                      <ul>
                        {Object.entries(div.perspectivas_medios).map(([medio, perspectiva]) => (
                          <li key={medio}><strong>{medio}:</strong> {perspectiva}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Palabras más frecuentes */}
        {analysis.palabras_mas_frecuentes_por_medio && Object.keys(analysis.palabras_mas_frecuentes_por_medio).length > 0 && (
          <div className="analysis-detail-section">
            <h3>Palabras Más Frecuentes por Medio</h3>
            <div className="analysis-words-grid">
              {Object.entries(analysis.palabras_mas_frecuentes_por_medio).map(([medio, palabras]) => (
                <div key={medio} className="analysis-words-item">
                  <h4>{medio}</h4>
                  {palabras.positivas && palabras.positivas.length > 0 && (
                    <div className="analysis-words-category">
                      <span className="analysis-words-label positivas">Positivas:</span>
                      <span className="analysis-words-list">{palabras.positivas.join(', ')}</span>
                    </div>
                  )}
                  {palabras.negativas && palabras.negativas.length > 0 && (
                    <div className="analysis-words-category">
                      <span className="analysis-words-label negativas">Negativas:</span>
                      <span className="analysis-words-list">{palabras.negativas.join(', ')}</span>
                    </div>
                  )}
                  {palabras.neutras && palabras.neutras.length > 0 && (
                    <div className="analysis-words-category">
                      <span className="analysis-words-label neutras">Neutras:</span>
                      <span className="analysis-words-list">{palabras.neutras.join(', ')}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Omisiones */}
        {(analysis.omisiones_importantes || analysis.omisiones_relevantes) && (
          <div className="analysis-detail-section">
            <h3>Omisiones Importantes</h3>
            <div className="analysis-omissions">
              {(analysis.omisiones_importantes || analysis.omisiones_relevantes)?.map((omision, idx) => (
                <div key={idx} className="analysis-omission-item">
                  <strong>{omision.medio}:</strong>
                  <p>{omision.informacion_omitida}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recomendación para el lector */}
        {analysis.recomendacion_para_lector && (
          <div className="analysis-detail-section">
            <h3>💡 Recomendación</h3>
            <div className="analysis-recommendation-box">
              <p>{analysis.recomendacion_para_lector}</p>
            </div>
          </div>
        )}

        {/* Estadísticas finales */}
        <div className="analysis-detail-section">
          <h3>Estadísticas</h3>
          <div className="analysis-detail-stats">
            <div className="analysis-stat">
              <span className="analysis-stat-label">Total de artículos</span>
              <span className="analysis-stat-value">{analysis.total_articulos}</span>
            </div>
            <div className="analysis-stat">
              <span className="analysis-stat-label">Medios únicos</span>
              <span className="analysis-stat-value">{analysis.total_medios}</span>
            </div>
            <div className="analysis-stat">
              <span className="analysis-stat-label">Fecha de análisis</span>
              <span className="analysis-stat-value">
                {new Date(analysis.fecha_analisis).toLocaleDateString('es-ES')}
              </span>
            </div>
          </div>
        </div>

        {/* Lista de medios */}
        <div className="analysis-detail-section">
          <h3>Medios Analizados</h3>
          <div className="analysis-medios-tags">
            {analysis.lista_medios.map((medio) => (
              <span key={medio} className="analysis-medio-tag">{medio}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
