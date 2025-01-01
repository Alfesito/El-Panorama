type WebViewPageProps = {
    url: string;
    onBack: () => void;
  };
  
  const WebViewPage: React.FC<WebViewPageProps> = ({ url, onBack }) => {
    return (
      <div className="webview-container">
        <button className="back-button" onClick={onBack}>
          Volver
        </button>
        <iframe
          src={url}
          title="Noticia"
          style={{
            width: '100%',
            height: '90vh',
            border: 'none',
          }}
        />
      </div>
    );
  };
  export default WebViewPage;