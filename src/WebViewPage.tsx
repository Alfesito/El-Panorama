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
    
    const loadingTimer = setTimeout(() => {
      setLoading(false);
    }, 2000);

    const checkTimer = setTimeout(() => {
      const iframe = document.querySelector('.webview-iframe') as HTMLIFrameElement;
      if (iframe) {
        try {
          const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
          if (!iframeDoc || iframeDoc.body?.innerHTML === '') {
            setIframeError(true);
          }
        } catch (e) {
          setIframeError(true);
        }
      }
      setLoading(false);
    }, 3000);

    return () => {
      clearTimeout(loadingTimer);
      clearTimeout(checkTimer);
    };
  }, [url]);

  const handleOpenExternal = () => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const handleIframeLoad = () => {
    setLoading(false);
    const iframe = document.querySelector('.webview-iframe') as HTMLIFrameElement;
    if (iframe) {
      try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!iframeDoc || iframeDoc.body?.innerHTML === '') {
          setIframeError(true);
        }
      } catch (e) {
        setIframeError(true);
      }
    }
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

      {loading && !iframeError && (
        <div className="webview-loading">
          <div className="spinner"></div>
          <p>Cargando noticia...</p>
        </div>
      )}

      {iframeError ? (
        <div className="webview-error">
          <div className="error-content">
            <h3>⚠️ No se puede mostrar esta página</h3>
            <p>Este periódico bloquea la visualización dentro de otras webs por copyright.</p>
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
          onLoad={handleIframeLoad}
          sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation"
        />
      )}
    </div>
  );
};

export default WebViewPage;
