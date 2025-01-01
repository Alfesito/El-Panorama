import { useEffect, useState } from 'react';
import mockdata from './config/json/merged_json.json';
import './App.css';
import Error from './Error';
import CONFIG from './config/config';
import SearchPage from './SeachPage';

type DataState = 
  | { data: any[] } // Cuando hay datos válidos
  | { e: { description: string } }; // Cuando hay un error

function App() {
  const [dataState, setDataState] = useState<DataState>({ data: [] });
  const [loading, setLoading] = useState<boolean>(true);

  const USE_SERVER = CONFIG.use_server;
  const URL_SERVER = CONFIG.server_url;

  const downloadData = async () => {
    if (USE_SERVER) {
      try {
        const response = await fetch(URL_SERVER);
        if (response.status === 200) {
          const res = await response.json();
          setDataState({ data: res }); // Ajusta según la estructura de respuesta del servidor
        } else {
          setDataState({ e: { description: `Error ${response.status}: ${response.statusText}` } });
        }
      } catch (e: any) {
        setDataState({ e: { description: e.message } });
      }
    } else {
      setDataState({ data: mockdata });
    }
  };

  useEffect(() => {
    async function fetchData() {
      await downloadData();
      setTimeout(() => {
        setLoading(false);
      }, 500);
    }
    fetchData();
  }, []);

  return (
    <>
      <h1>El Panorama</h1>
      <p>
        {loading ? (
          <p>Cargando datos...</p>
        ) : "e" in dataState ? ( // Verifica si hay un error
          <Error error={dataState.e} />
        ) : (
          <SearchPage items={dataState.data} />
        )}
      </p>
    </>
  );
}

export default App;
