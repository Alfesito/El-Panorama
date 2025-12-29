from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
from datetime import datetime
from collections import OrderedDict
import re
import hashlib
import base64

def clean_text(text):
    if not text:
        return ""
    text = unidecode(text.strip())
    return text

def normalize_datetime(date_str):
    """ISO 8601 completo: YYYY-MM-DDThh:mm:ss.sssZ"""
    if not date_str:
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    patterns = [
        r'(\d{1,2})\s*(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\.?\s+(\d{4})\s+(\d{1,2}):(\d{2})',
        r'(\d{4})-(\d{1,2})-(\d{1,2})T(\d{2}):(\d{2}):(\d{2})',
        r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}):(\d{2})'
    ]
    
    meses = {
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05',
        'jun': '06', 'jul': '07', 'ago': '08', 'sep': '09', 'oct': '10',
        'nov': '11', 'dic': '12'
    }
    
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            if 'ene' in pattern:
                dia, mes, ano, hora, minuto = match.groups()
                mes_num = meses.get(mes)
                if mes_num:
                    return f"{ano}-{mes_num}-{dia.zfill(2)}T{hora.zfill(2)}:{minuto}:00.000Z"
            elif len(match.groups()) >= 4:
                ano, mes, dia, hora, minuto, segundo = match.groups()[:6]
                return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}T{hora}:{minuto}:{segundo or '00'}.000Z"
    
    now = datetime.utcnow()
    return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def encode_to_base62(data):
    hash_obj = hashlib.md5(data.encode('utf-8'))
    b64 = base64.b64encode(hash_obj.digest()).decode('utf-8')
    base62 = b64.replace('+', 'Z').replace('/', 'Y').replace('=', 'X')
    return base62[:6].upper()

def generate_short_id(newspaper, datetime_str, title):
    content = f"{datetime_str}{title[:30]}{newspaper}"
    return encode_to_base62(content)

def parse_srcset(srcset):
    if not srcset:
        return ''
    urls = srcset.split(',')[0].strip().split(' ')[0]
    if urls.startswith('http'):
        return urls
    return ''

def extract_image(soup):
    try:
        main_figure = soup.find('figure', class_='am am-h')
        if main_figure:
            img = main_figure.find('img')
            if img:
                img_url = (img.get('src') or 
                          img.get('data-src') or 
                          parse_srcset(img.get('srcset', '')))
                if img_url:
                    credits_span = main_figure.find('span', class_='amm')
                    credits = clean_text(credits_span.text) if credits_span else ''
                    return {'url': img_url, 'credits': credits}
        
        figure = soup.find('figure')
        if figure:
            img = figure.find('img')
            if img:
                img_url = (img.get('src') or 
                          img.get('data-src') or 
                          parse_srcset(img.get('srcset', '')))
                credits_span = figure.find('span', class_='amm') or figure.find('figcaption')
                credits = clean_text(credits_span.text) if credits_span else ''
                return {'url': img_url, 'credits': credits}
        
        meta_image = soup.find('meta', property='og:image')
        if meta_image:
            return {'url': meta_image.get('content', ''), 'credits': ''}
        
        return {'url': '', 'credits': ''}
    except Exception:
        return {'url': '', 'credits': ''}

def scrape_article_details(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_h1 = soup.find('h1', class_='at')
        title = clean_text(title_h1.text) if title_h1 else ''
        
        subtitle_p = soup.find('p', class_='ast')
        subtitle = clean_text(subtitle_p.text) if subtitle_p else ''
        
        tags = []
        archived_section = soup.find('section', {'data-dtm-region': 'articulo_archivado-en'})
        if archived_section:
            tags = [clean_text(li.text) for li in archived_section.find_all('li')]
        
        body_paragraphs = []
        cuerpo_section = soup.find('div', {'data-dtm-region': 'articulo_cuerpo'})
        if cuerpo_section:
            body_paragraphs = cuerpo_section.find_all('p')[:15]
        else:
            body_paragraphs = soup.find_all('p', limit=15)
        
        body = ' '.join([clean_text(p.text) for p in body_paragraphs if len(clean_text(p.text)) > 30])
        
        image = extract_image(soup)
        
        return {
            'title': title,
            'subtitle': subtitle,
            'tags': tags[:8],
            'body': body[:3000],
            'image': image
        }
    
    except Exception as e:
        print(f"Error scraping details {url}: {e}")
        return {'title': '', 'subtitle': '', 'tags': [], 'body': '', 'image': {'url': '', 'credits': ''}}

def create_ordered_article(newspaper, article_id, date, tags, title, subtitle, url, author, image, body):
    """
    Crea artículo con ORDEN EXACTO: ID PRIMERO
    """
    return OrderedDict([
        ('id', article_id),        # ← 1º ID
        ('newspaper', newspaper),  # 2º
        ('date', date),            # 3º
        ('tags', tags),            # 4º
        ('title', title),          # 5º
        ('subtitle', subtitle),    # 6º
        ('url', url),              # 7º
        ('author', author),        # 8º
        ('image', image),          # 9º
        ('body', body)             # 10º
    ])

def scrape_all_articles(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        main = soup.find('main')
        if not main:
            return {'error': 'No se encontró <main>'}

        results = []
        sections = main.find_all('section')

        for section in sections:
            articles = section.find_all('article')
            for article in articles:
                h2_tag = article.find('h2')
                title_tag = h2_tag.find('a') if h2_tag else None
                list_title = clean_text(title_tag.text) if title_tag else ''
                link = title_tag.get('href') if title_tag else ''

                if not link or not list_title:
                    continue

                if link.startswith('/'):
                    link = 'https://elpais.com' + link

                metadata_div = article.find('div', recursive=False)
                author = ''
                date_raw = ''
                if metadata_div:
                    author_tags = metadata_div.find_all('a')
                    if author_tags:
                        author = clean_text(author_tags[0].text)
                    
                    date_spans = metadata_div.find_all('time')
                    if date_spans:
                        date_raw = date_spans[-1].get('datetime') or date_spans[-1].text.strip()

                datetime_str = normalize_datetime(date_raw)
                article_details = scrape_article_details(link)
                final_title = article_details['title'] or list_title
                article_id = generate_short_id('ElPais', datetime_str, final_title)

                # 🎯 ORDEN EXACTO con ID PRIMERO
                ordered_article = create_ordered_article(
                    newspaper='El País',
                    article_id=article_id,
                    date=datetime_str,
                    tags=article_details['tags'],
                    title=final_title,
                    subtitle=article_details['subtitle'],
                    url=link,
                    author=author,
                    image=article_details['image'],
                    body=article_details['body']
                )
                
                results.append(ordered_article)

        return results

    except Exception as e:
        return {'error': str(e)}

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'Se requiere parámetro "url"'}), 400
    
    data = scrape_all_articles(target_url)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
