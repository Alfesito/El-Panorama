from flask import Flask, json, jsonify, request
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
    Scrapea los detalles del artículo, extrayendo las etiquetas dentro de <a> 
    presentes en los <li> de una lista con clase 'article-tags-list'.
    """
    try:
        # Solicitar el contenido de la página
        response = requests.get(url)
        response.raise_for_status()
        
        # Analizar el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Localizar el contenedor principal con clase 'article-tags-list'
        tag_list = soup.find('ul', {'class': 'article-tags-list'})
        if not tag_list:
            return {'error': 'No se encontró la lista de etiquetas con clase "article-tags-list"'}

        # Extraer el texto de cada enlace <a> dentro de los <li>
        tags = []
        for li in tag_list.find_all('li'):
            a_tag = li.find('a')  # Busca el <a> dentro del <li>
            if a_tag and a_tag.text:
                tags.append(clean_text(a_tag.text.strip()))  # Extrae y limpia el texto

        return {
            'tags': tags
        }

    except Exception as e:
        return {'error': str(e)}


def scrape_all_articles(url):
    try:
        # Realiza la solicitud al sitio web
        response = requests.get(url)
        response.raise_for_status()  # Lanza error si falla la solicitud

        # Analiza el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Navega hacia el primer <section> del primer <div> dentro de <main>
        main = soup.find('main')
        if not main:
            return {'error': 'No se encontró el elemento <main>'}

        articles = main.find_all('article')
        if not articles:
            return {'error': 'No se encontró los <div> dentro de <main>'}

        # Extrae título, URL
        results = []
        for article in articles:
            # Asegúrate de que el <h2> y su <a> existan antes de acceder a ellos
            title_tag = article.find('h2')
            link = None
            title = None
            if title_tag:
                a_tag = title_tag.find('a')
                if a_tag:
                    raw_title = a_tag.text.strip()
                    title = clean_text(raw_title)
                    link = a_tag['href']
            
            # Extraer autor, agencia y lugar
            metadata_div = article.find('div')
            author = None

            if metadata_div:
                # Buscar autor y agencia
                author_tag = metadata_div.find('div', {'class': 'article__author'}).find('a')
                if author_tag:
                    author = clean_text(author_tag.text.strip())
                
                # Buscar el último <span> para la ubicación
                date_span = metadata_div.find('div', {'class': 'article__author'}).find('time')
                if date_span and 'data-module-launcher-config' in date_span.attrs:
                    # Extraer el valor del atributo 'data-module-launcher-config' que contiene la fecha en formato JSON
                    config_data = date_span.attrs['data-module-launcher-config']
                    # Convertir el string JSON a un diccionario
                    config_dict = json.loads(config_data)
                    # Extraer la fecha de publicación
                    if 'publishDate' in config_dict:
                        date = config_dict['publishDate']
                else:
                    date = fecha_actual()

                # Extraer encabezado
                subtitles = None
                header_div = metadata_div.find('div', {'class': 'article__summary'}) if metadata_div else None
                if header_div:
                    header_text = header_div.find('p')
                    if header_text:
                        subtitles = clean_text(header_text.text.strip())
                
            article_details = scrape_article_details(link)

            # Solo agregar si se encontró un título y URL
            results.append({
                'title': title,
                'url': link,
                'author': author,
                'date': date,
                'subtitles': subtitles,
                'tags': article_details.get('tags', []),
                'newspaper': 'La Razón'
            })

        return results
    except Exception as e:
        return {'error': str(e)}

app = Flask(__name__)

@app.route('/main', methods=['GET']) #limitar el numero de articulos
def scrape():
    # Obtén la URL como parámetro de la solicitud
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'Se requiere un parámetro "url"'}), 400

    # Llama a la función de scraping
    data = scrape_all_articles(target_url)

    # Devuelve los resultados en formato JSON
    return jsonify(data)

@app.route('/espana', methods=['GET'])
def espana():
    # Obtén la URL como parámetro de la solicitud
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'Se requiere un parámetro "url"'}), 400

    # Llama a la función de scraping
    data = scrape_all_articles(target_url+'/espana')

    # Devuelve los resultados en formato JSON
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
