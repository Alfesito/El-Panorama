import { useState, useEffect } from 'react';
import './WebViewPage.css';

type WebViewPageProps = {
  url: string;
  onBack: () => void;
};

const WebViewPage: React.FC<WebViewPageProps> = ({ url, onBack }) => {
  const [iframeError, setIframeError] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setIframeError(false);
    
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, [url]);

  const handleOpenExternal = () => {
    window.open(url, '_blank', 'noopener,noreferrer');
    onBack();
  };

  const handleIframeError = () => {
    setIframeError(true);
    setLoading(false);
  };

  return (
    <div className="webview-container">
      <div className="webview-header">
        <button className="back-button" onClick={onBack}>
          ← Volver
        </button>
        <button className="external-button" onClick={handleOpenExternal}>
          Abrir en nueva pestaña ↗
        </button>
      </div>

      {loading && (
        <div className="webview-loading">
          <div className="spinner"></div>
          <p>Cargando noticia...</p>
        </div>
      )}

      {iframeError ? (
        <div className="webview-error">
          <div className="error-content">
            <h3>⚠️ No se puede mostrar esta página</h3>
            <p>Algunos periódicos bloquean la visualización dentro de otras webs por seguridad.</p>
            <button className="external-button-large" onClick={handleOpenExternal}>
              📰 Abrir noticia en nueva pestaña
            </button>
            <button className="back-button-secondary" onClick={onBack}>
              Volver a las noticias
            </button>
          </div>
        </div>
      ) : (
        <iframe
          src={url}
          title="Noticia"
          className="webview-iframe"
          onError={handleIframeError}
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
        />
      )}
    </div>
  );
};

export default WebViewPage;
