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
    Extrae todos los artículos de todas las <section> presentes en el <main>.
    """
    try:
        # Realiza la solicitud al sitio web
        response = requests.get(url)
        response.raise_for_status()  # Lanza error si falla la solicitud

        # Analiza el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encuentra el contenedor principal <main>
        main = soup.find('main')
        if not main:
            return {'error': 'No se encontró el elemento <main>'}

        # Encuentra todas las <section> dentro de <main>
        sections = main.find_all('section')
        if not sections:
            return {'error': 'No se encontraron <section> dentro de <main>'}

        # Almacena los resultados
        results = []

        # Itera a través de cada <section>
        for section in sections:
            # Encuentra todos los <article> dentro de la sección
            articles = section.find_all('article')
            if not articles:
                continue  # Salta la sección si no tiene artículos

            # Procesa cada artículo
            for article in articles:
                # Extraer título y URL
                title_tag = article.find('h2').find('a')
                title = None
                link = None
                if title_tag:
                    raw_title = title_tag.text.strip()
                    title = clean_text(raw_title)
                    link = title_tag['href']
                
                # Extraer autor y fecha
                metadata_div = article.find('div')
                author = None
                date = None

                if metadata_div:
                    # Buscar autor
                    author_tags = metadata_div.find_all('a')
                    if author_tags:
                        author = clean_text(author_tags[0].text.strip())
                    
                    # Buscar fecha
                    date_spans = metadata_div.find_all('time')
                    if date_spans:
                        date = clean_text(date_spans[-1].text.strip())
                    else:
                        date = fecha_actual()

                # Obtener detalles adicionales del artículo
                article_details = scrape_article_details(link)

                # Agregar los resultados del artículo
                results.append({
                    'title': title,
                    'url': link,
                    'author': author,
                    'date': date,
                    'subtitles': article_details.get('subtitles', ''),
                    'tags': article_details.get('tags', []),
                    'newspaper': 'El País'
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
