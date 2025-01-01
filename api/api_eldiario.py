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

def scrape_article_details(url):
    """
    Scrapea los detalles del artículo, extrayendo el texto de <h2> dentro del primer <div> en el <header>
    y el texto dentro de los <li> dentro de un <section> con el atributo data-dtm-region="articulo_archivado-en".
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Analiza el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Navega hacia el primer <article> dentro del <body>
        article = soup.find('article')
        if not article:
            return {'error': f'No se encontró el artículo en {url}'}

        # Navega hacia el <header> y luego al primer <div> dentro de él
        header = article.find('header')
        if not header:
            return {'error': 'No se encontró el <header> en el artículo'}

        first_div = header.find('div')
        if not first_div:
            return {'error': 'No se encontró el primer <div> dentro del <header>'}

        # Extrae el texto de <h2>
        h2_tag = first_div.find('h2')
        if not h2_tag:
            return {'error': 'No se encontró el <h2> dentro del primer <div> en el <header>'}

        # Extrae el texto de <li> dentro de un <section> con data-dtm-region="articulo_archivado-en"
        archived_section = article.find('section', {'data-dtm-region': 'articulo_archivado-en'})
        tags = []
        if archived_section:
            li_tags = archived_section.find_all('li')
            tags = [clean_text(li.text.strip()) for li in li_tags]

        return {
            'subtitles': clean_text(h2_tag.text.strip()),
            'tags': tags
        }

    except Exception as e:
        return {'error': str(e)}

def scrape_all_articles(url):
    """
    Scrapea los títulos y URLs de los artículos de la página.
    """
    try:
        # Realiza la solicitud
        response = requests.get(url)
        response.raise_for_status()

        # Analiza el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encuentra todos los <article> con la clase específica
        articles = soup.find_all('div')
        if not articles:
            return {'error': 'No se encontraron artículos con la clase esperada'}

        # Lista para almacenar resultados
        results = []

        for article in articles:
            # Extraer el título del artículo
            h2_tags = article.find_all('h2')
            if not h2_tags:
                continue

            for h2_tag in h2_tags:
                # Extraer el enlace y el texto del título
                a_tag = h2_tag.find('a')
                if not a_tag:
                    continue

                title = clean_text(a_tag.text.strip())
                link_text = clean_text(a_tag.get('href', ''))

                if 'http' in link_text:
                    link = link_text
                else:
                    link = url+link_text

                results.append({
                    'title': title,
                    'url': link,
                    'newspaper': 'El Diario'
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

    # Llama a la función de scraping
    data = scrape_all_articles(target_url)

    # Devuelve los resultados en formato JSON
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
