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
    if not date_str:
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})', date_str)
    if match:
        dt_str = match.group(1)
        return re.sub(r'[+-]\d{2}:\d{2}$', 'Z', dt_str) + '.000Z'
    
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

# [Funciones clean_text, normalize_datetime, encode_to_base62, generate_short_id igual que antes]
def extract_image(soup):
    """IMAGEN ROBUSTA eldiario.es"""
    try:
        main_figure = soup.find('figure', class_='ni-figure')
        if main_figure:
            img = main_figure.find('img')
            if img and img.get('src') and 'static.eldiario.es' in img.get('src', ''):
                img_url = img.get('src')
                figcaption = main_figure.find('figcaption', class_='image-footer')
                credits = ''
                if figcaption:
                    author_span = figcaption.find('span', class_='author')
                    credits = clean_text(author_span.text) if author_span else ''
                return {'url': img_url, 'credits': credits}
        
        img = soup.find('img', src=re.compile(r'static\.eldiario\.es.*\.jpg'))
        if img:
            return {'url': img.get('src'), 'credits': ''}
        
        meta_image = soup.find('meta', property='og:image')
        if meta_image:
            return {'url': meta_image.get('content', ''), 'credits': ''}
        
        return {'url': '', 'credits': ''}
    except:
        return {'url': '', 'credits': ''}

def scrape_article_details(url):
    """AUTOR 100% ROBUSTO + IMAGEN"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = clean_text(soup.find('h1', class_='title').text) if soup.find('h1', class_='title') else ''
        subtitle = clean_text(soup.select_one('ul.footer li.subtitle--hasAnchor h2').text) if soup.select_one('ul.footer li.subtitle--hasAnchor h2') else ''
        
        # 🎯 AUTOR 3 SELECTORES
        author = ''
        news_info = soup.find('div', class_='news-info')
        if news_info:
            info_wrapper = news_info.find('div', class_='info-wrapper')
            if info_wrapper:
                authors_p = info_wrapper.find('p', class_='authors')
                if authors_p:
                    author_link = authors_p.find('a')
                    author = clean_text(author_link.text) if author_link else ''
        
        if not author:
            authors_p = soup.find('p', class_='authors')
            if authors_p:
                author_link = authors_p.find('a')
                author = clean_text(author_link.text) if author_link else ''
        
        if not author:
            author_links = soup.find_all('a', href=re.compile(r'/autores/'))
            if author_links:
                author = clean_text(author_links[0].text)
        
        # Tags
        tags = [clean_text(tag.text) for tag in soup.select('ul.tags-wrapper li a.tag-link')[:8]]
        
        # Body
        body_paragraphs = soup.find_all('p', class_='article-text')[:12]
        body = ' '.join([clean_text(p.text) for p in body_paragraphs if len(clean_text(p.text)) > 30])
        
        image = extract_image(soup)
        
        return {
            'title': title,
            'subtitle': subtitle,
            'author': author,  # ✅ Pedro Agueda, Aitor Riveiro, Alberto Ortiz
            'tags': tags,
            'body': body[:3000],
            'image': image
        }
    except Exception as e:
        print(f"Error: {e}")
        return {'title': '', 'subtitle': '', 'author': '', 'tags': [], 'body': '', 'image': {'url': '', 'credits': ''}}

def scrape_all_articles(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        articles = soup.find_all('figure', class_='ni-figure')[:20]
        
        for article in articles:
            title_a = article.find('a')
            if not title_a:
                continue
            title = clean_text(title_a.text)
            link = title_a.get('href', '')
            if link.startswith('/'):
                link = 'https://www.eldiario.es' + link
            
            news_info = article.find('div', class_='news-info')
            author = ''
            date_raw = ''
            if news_info:
                info_wrapper = news_info.find('div', class_='info-wrapper')
                if info_wrapper:
                    authors_p = info_wrapper.find('p', class_='authors')
                    if authors_p:
                        author_link = authors_p.find('a')
                        author = clean_text(author_link.text) if author_link else ''
                
                time_tag = news_info.find('time')
                date_raw = time_tag.get('datetime') if time_tag else ''
            
            datetime_str = normalize_datetime(date_raw)
            details = scrape_article_details(link)
            final_title = details['title'] or title
            final_author = details['author'] or author
            
            article_id = generate_short_id('ElDiario', datetime_str, final_title)
            
            ordered_article = OrderedDict([
                ('id', article_id),
                ('newspaper', 'eldiario.es'),
                ('date', datetime_str),
                ('tags', details['tags']),
                ('title', final_title),
                ('subtitle', details['subtitle']),
                ('url', link),
                ('author', final_author),  # ✅ Aitor Riveiro
                ('image', details['image']),
                ('body', details['body'])
            ])
            
            results.append(ordered_article)
        
        return results
    except Exception as e:
        return {'error': str(e)}

# Flask app igual...
app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'Requiere "url"'}), 400
    data = scrape_all_articles(target_url)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
