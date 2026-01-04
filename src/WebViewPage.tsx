import { useState } from 'react';
import './WebViewPage.css';


type WebViewPageProps = {
  url: string;
  onBack: () => void;
};


const WebViewPage: React.FC<WebViewPageProps> = ({ url, onBack }) => {
  const [loading, setLoading] = useState(true);


  const handleOpenExternal = () => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };


  const handleIframeLoad = () => {
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


      <iframe
        src={url}
        title="Noticia"
        className="webview-iframe"
        onLoad={handleIframeLoad}
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms allow-top-navigation"
      />
    </div>
  );
};


export default WebViewPage;
