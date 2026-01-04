import { useState, useEffect } from 'react';
import './WebViewPage.css';

type WebViewPageProps = {
  url: string;
  onBack: () => void;
};

const WebViewPage: React.FC<WebViewPageProps> = ({ url, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [blocked, setBlocked] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 3000);

    const iframe = document.querySelector('iframe');
    if (iframe) {
      iframe.addEventListener('error', () => {
        setBlocked(true);
        setLoading(false);
      });
    }

    const checkBlocked = setTimeout(() => {
      try {
        const frame = document.querySelector('iframe') as HTMLIFrameElement;
        if (frame && !frame.contentWindow?.location.href) {
          setBlocked(true);
        }
      } catch (e) {
        setBlocked(true);
      }
      setLoading(false);
    }, 4000);

    return () => {
      clearTimeout(timer);
      clearTimeout(checkBlocked);
    };
  }, [url]);

  const handleOpenExternal = () => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="webview-container">
      <div className="webview-header">
        <button className="back-button" onClick={onBack}>
          ← Volver
        </button>
        <span className="webview-url">{new URL(url).hostname}</span>
        <button className="external-button" onClick={handleOpenExternal}>
          Abrir en pestaña ↗
        </button>
      </div>

      {loading && (
        <div className="webview-loading">
          <div className="spinner"></div>
          <p>Cargando noticia...</p>
        </div>
      )}

      {blocked && !loading && (
        <div className="webview-blocked">
          <div className="blocked-content">
            <h3>🔒 Contenido bloqueado</h3>
            <p>
              Este periódico no permite visualización dentro de otras webs por
              políticas de seguridad.
            </p>
            <button className="open-external-btn" onClick={handleOpenExternal}>
              📰 Abrir en nueva pestaña
            </button>
            <button className="back-btn-secondary" onClick={onBack}>
              Volver a las noticias
            </button>
          </div>
        </div>
      )}

      <iframe
        src={url}
        title="Noticia"
        className={`webview-iframe ${loading ? 'loading' : ''} ${blocked ? 'hidden' : ''}`}
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation"
        referrerPolicy="no-referrer-when-downgrade"
        onLoad={() => setLoading(false)}
      />
    </div>
  );
};

export default WebViewPage;
