from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
from datetime import datetime

def clean_text(text):
    """
    Elimina caracteres Unicode especiales y normaliza tildes.
    """
    # Normaliza el texto y elimina caracteres con tildes
    text = unidecode(text)
    return text

def fecha_actual():
    return datetime.now().strftime('%d %b %Y')

def scrape_article_details(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encuentra el contenedor principal
        info_container = soup.find('div', {'class': 'voc-info-container'})
        if not info_container:
            return {'subtitles': '', 'tags': []}

        # Extrae textos de <h2>
        h2_tags = info_container.find_all('h2')
        subtitles = [h2.get_text(strip=True) for h2 in h2_tags]
        
        # Une todos los subtítulos en uno solo
        unified_subtitles = clean_text(".\n".join(subtitles))

        # Encuentra enlaces <a> dentro del segundo <ul> de la sección de navegación
        nav_section = soup.find('div', {'class': 'voc-wrapper'}).find('nav', {'class': 'voc-topics__header'})
        tags = []
        if nav_section:
            ul_tags = nav_section.find_all('ul')  # Encuentra todos los <ul>
            a_tags = ul_tags[0].find_all('a', {'class': 'voc-topics__link'})  # Busca los enlaces dentro del segundo <ul>
            tags = [clean_text(a.get('title', '').strip()) for a in a_tags]
        
        date = clean_text(soup.find('div', {'class': 'voc-wrapper'}).find('time').get('datetime', '').strip())

        return {
            'subtitles': unified_subtitles,
            'tags': tags,
            'date': date
        }
    except Exception as e:
        return {'error': f'Error al procesar el detalle del artículo: {e}'}

def scrape_all_articles(url, headers):
    """
    Extrae todos los artículos de todas las <div> presentes en el contenedor principal.
    """
    try:
        # Realiza la solicitud al sitio web
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza error si falla la solicitud

        # Analiza el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encuentra el contenedor principal
        main = soup.find('div', {'class': 'voc-wrapper'})
        if not main:
            return {'error': 'No se encontró el contenedor principal'}

        # Encuentra todos los <article> dentro del contenedor principal
        articles = main.find_all('article')
        if not articles:
            return {'error': 'No se encontraron artículos'}

        # Almacena los resultados
        results = []

        # Itera sobre cada artículo para extraer la información
        for article in articles:
            # Verifica que exista un <h2> dentro del artículo
            h2_tag = article.find('h2')
            if not h2_tag:
                continue  # Salta este artículo si no tiene <h2>

            # Verifica que exista un enlace <a> dentro del <h2>
            a_tag = h2_tag.find('a')
            if not a_tag:
                continue  # Salta este artículo si no tiene <a>

            # Extraer título y URL
            title = clean_text(a_tag.get('title', '').strip())  # Usa el atributo 'title' si está presente
            link = clean_text(a_tag.get('href', '').strip())  # Usa el atributo 'href' si está presente

            author_tag = article.find('span', {'class': 'voc-onplus__author'})
            author = clean_text(author_tag.text.strip()) if author_tag else None
        
            # Obtener detalles adicionales del artículo
            article_details = scrape_article_details(link, headers)

            # Guarda los resultados
            results.append({
                'title': title,
                'url': link,
                'author': author,
                'subtitles': article_details.get('subtitles', ''),
                'tags': article_details.get('tags', []),
                'date': article_details.get('date', fecha_actual()),
                'newspaper': 'ABC'
            })
        return results

    except Exception as e:
        return {'error': str(e)}

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    # Obtén la URL como parámetro de la solicitud
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'Se requiere un parámetro "url"'}), 400

    try:
        # Define un encabezado User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }

        # Llama a la función de scraping con el encabezado incluido
        data = scrape_all_articles(target_url, headers)

        # Devuelve los resultados en formato JSON
        return jsonify(data)

    except requests.exceptions.RequestException as e:
        # Manejo de errores en la solicitud HTTP
        return jsonify({'error': f'Error de solicitud: {str(e)}'}), 500
    except Exception as e:
        # Otros errores generales
        return jsonify({'error': f'Error interno: {str(e)}'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
