"""
🚀 NEWS SCRAPER API v2.2 - CÓDIGO COMPLETO
✅ SUBTÍTULO: h2.article-main__description [query]
✅ Body: div#intext.article-maincontent p [file:177]
✅ TODAS funciones definidas
"""

from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from unidecode import unidecode
from datetime import datetime
from collections import OrderedDict
import re
import hashlib
import base64

app = Flask(__name__)

# ===========================================
# FUNCIONES COMUNES
# ===========================================
def clean_text(text):
    """Limpia y normaliza texto"""
    if not text: return ""
    text = unidecode(text.strip())
    return re.sub(r'\s+', ' ', text)

def normalize_datetime(date_str):
    """ISO 8601: YYYY-MM-DDThh:mm:ss.sssZ"""
    if not date_str:
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    try:
        if '"publishDate"' in str(date_str):
            match = re.search(r'"publishDate":"([^"]+)"', str(date_str))
            if match: date_str = match.group(1)
        match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-Z]\d{2}?)', str(date_str))
        if match:
            dt_str = match.group(1)
            if dt_str.endswith('Z'): return dt_str + '.000Z'
            return re.sub(r'[+-]\d{2}:\d{2}$', 'Z', dt_str) + '.000Z'
    except: pass
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

# ===========================================
# ABC.ES - COMPLETO
# ===========================================
def extract_image_abc(soup):
    try:
        figures = soup.find_all('figure', class_='voc-img-figure')
        for figure in figures:
            img = figure.find('img', class_='voc-img')
            if img and img.get('src'):
                img_url = img.get('src')
                figcaption = figure.find('figcaption', class_='voc-figcaption-container') or figure.find_next('figcaption', class_='voc-figcaption-container')
                if figcaption:
                    text_span = figcaption.find('span', class_='voc-figcaption--text')
                    credit_span = figcaption.find('span', class_='voc-figcaption--author')
                    caption_text = clean_text(text_span.text) if text_span else ''
                    credit_text = clean_text(credit_span.text) if credit_span else ''
                    credits = f"{caption_text}, {credit_text}" if caption_text and credit_text else caption_text or credit_text or ''
                    return {'url': img_url, 'credits': credits}
        img = soup.find('img', class_='voc-img', src=True)
        if img: return {'url': img.get('src'), 'credits': ''}
        meta_image = soup.find('meta', property='og:image')
        if meta_image: return {'url': meta_image.get('content', ''), 'credits': ''}
        return {'url': '', 'credits': ''}
    except: return {'url': '', 'credits': ''}

def scrape_article_details_abc(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = clean_text(soup.find('h1', class_='voc-title').text) if soup.find('h1', class_='voc-title') else ''
        subtitle = clean_text(soup.find('h2', class_='voc-subtitle').text) if soup.find('h2', class_='voc-subtitle') else ''
        author_section = soup.find('section', class_='voc-author')
        author = clean_text(author_section.select_one('p.voc-authorname a').text) if author_section else ''
        nav_topics = soup.find('nav', class_='voc-topics__header')
        tags = [clean_text(a.get('title', a.text.strip())) for a in nav_topics.find_all('a', class_='voc-topics__link')[:8]] if nav_topics else []
        body_paragraphs = soup.find_all('p', class_='voc-p')[:12]
        body = ' '.join([clean_text(p.text) for p in body_paragraphs if len(clean_text(p.text)) > 30])[:3000]
        image = extract_image_abc(soup)
        return {'title': title, 'subtitle': subtitle, 'author': author, 'tags': tags, 'body': body, 'image': image}
    except: return {'title': '', 'subtitle': '', 'author': '', 'tags': [], 'body': '', 'image': {'url': '', 'credits': ''}}

def scrape_all_articles_abc(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        main_wrapper = soup.find('div', class_='voc-wrapper')
        if not main_wrapper: return {'error': 'No ABC structure'}
        articles = main_wrapper.find_all('article', limit=25)
        for article in articles:
            h2_tag = article.find('h2')
            if not h2_tag: continue
            a_tag = h2_tag.find('a')
            if not a_tag: continue
            title = clean_text(a_tag.get('title') or a_tag.text)
            link = a_tag.get('href', '')
            if link.startswith('/'): link = 'https://www.abc.es' + link
            author_tag = article.find('span', class_='voc-onplus__author')
            list_author = clean_text(author_tag.text) if author_tag else ''
            time_tag = article.find('time')
            date_raw = time_tag.get('datetime') if time_tag else ''
            datetime_str = normalize_datetime(date_raw)
            details = scrape_article_details_abc(link)
            final_title = details['title'] or title
            final_author = details['author'] or list_author
            article_id = generate_short_id('ABC', datetime_str, final_title)
            ordered_article = OrderedDict([
                ('id', article_id), ('newspaper', 'abc.es'), ('date', datetime_str),
                ('tags', details['tags']), ('title', final_title), ('subtitle', details['subtitle']),
                ('url', link), ('author', final_author), ('image', details['image']), ('body', details['body'])
            ])
            results.append(ordered_article)
        return results[:20]
    except Exception as e:
        return {'error': str(e)}

# ===========================================
# LA RAZÓN - COMPLETO [file:176+177+query]
# ===========================================
def extract_image_larazon(soup):
    try:
        picture = soup.find('picture')
        if picture:
            img = picture.find('img')
            if img and img.get('src') and 'fotografias-2.larazon.es' in img.get('src', ''):
                img_url = img.get('src')
                figcaption = picture.find_next('figcaption')
                credits = clean_text(figcaption.get_text(strip=True)) if figcaption else ''
                return {'url': img_url, 'credits': credits}
        img = soup.find('img', src=re.compile(r'fotografias.*larazon\.es'))
        if img: return {'url': img.get('src'), 'credits': ''}
        meta_image = soup.find('meta', property='og:image')
        if meta_image: return {'url': meta_image.get('content', ''), 'credits': ''}
        return {'url': '', 'credits': ''}
    except: return {'url': '', 'credits': ''}

def scrape_article_details_larazon(url):
    """✅ La Razón EXACTOS [file:176+177+query]"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_h1 = soup.find('h1', class_='article-maintitle')
        title = clean_text(title_h1.text) if title_h1 else ''
        
        # ✅ SUBTÍTULO CORREGIDO [query]
        subtitle_h2 = soup.find('h2', class_='article-main__description')
        subtitle = clean_text(subtitle_h2.text) if subtitle_h2 else ''
        
        author_div = soup.find('div', class_='article-authorname')
        author = ''
        if author_div:
            author_link = author_div.find('a')
            author = clean_text(author_link.text) if author_link else ''
        
        tag_list = soup.find('ul', class_='article-tags-list')
        tags = [clean_text(li.find('a').text.strip()) for li in tag_list.find_all('li') if tag_list and li.find('a')]
        
        # ✅ Body [file:177]
        body_div = soup.find('div', id='intext')
        if body_div and 'article-maincontent' in body_div.get('class', []):
            body_paragraphs = body_div.find_all('p', class_=re.compile(r'article-main'))[:15]
        else:
            body_paragraphs = soup.find_all('p', class_=re.compile(r'article-main'))[:15]
        
        body_texts = [clean_text(p.text) for p in body_paragraphs 
                     if len(clean_text(p.text)) > 50 and 'publicidad' not in clean_text(p.text).lower()]
        body = ' '.join(body_texts)[:4000]
        
        image = extract_image_larazon(soup)
        return {
            'title': title,
            'subtitle': subtitle,  # ✅ h2.article-main__description
            'author': author,
            'tags': tags,
            'body': body,
            'image': image
        }
    except Exception as e:
        print(f"Error LaRazon {url}: {e}")
        return {'title': '', 'subtitle': '', 'author': '', 'tags': [], 'body': '', 'image': {'url': '', 'credits': ''}}

def scrape_all_articles_larazon(url):
    """✅ La Razón lista principal"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        main_tag = soup.find('main')
        if not main_tag: return {'error': 'No main LaRazon'}
        
        articles = main_tag.find_all('article', limit=25)
        for article in articles:
            h2_tag = article.find('h2')
            if not h2_tag: continue
            a_tag = h2_tag.find('a')
            if not a_tag: continue
            
            title = clean_text(a_tag.text.strip())
            link = a_tag.get('href', '')
            if link.startswith('/'): link = 'https://www.larazon.es' + link
            
            metadata_div = article.find('div', class_='article__author')
            list_author = ''
            if metadata_div:
                author_link = metadata_div.find('a')
                list_author = clean_text(author_link.text) if author_link else ''
            
            time_tag = article.find('time', attrs={'data-module-launcher-config': True})
            date_raw = time_tag.get('data-module-launcher-config') if time_tag else ''
            datetime_str = normalize_datetime(date_raw)
            
            details = scrape_article_details_larazon(link)
            final_title = details['title'] or title
            final_author = details['author'] or list_author
            
            article_id = generate_short_id('LaRazon', datetime_str, final_title)
            
            ordered_article = OrderedDict([
                ('id', article_id), ('newspaper', 'larazon.es'), ('date', datetime_str),
                ('tags', details['tags']), ('title', final_title), ('subtitle', details['subtitle']),
                ('url', link), ('author', final_author), ('image', details['image']),
                ('body', details['body'])
            ])
            results.append(ordered_article)
        return results[:20]
    except Exception as e:
        return {'error': str(e)}

# ===========================================
# FLASK API ROUTES
# ===========================================
@app.route('/scrape', methods=['GET'])
def scrape():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({
            'error': 'Requiere "url"',
            'ejemplos': ['https://www.abc.es/', 'https://www.larazon.es/espana/']
        }), 400
    
    print(f"🔍 Scraping: {target_url}")
    
    if 'abc.es' in target_url.lower():
        data = scrape_all_articles_abc(target_url)
    elif 'larazon.es' in target_url.lower():
        data = scrape_all_articles_larazon(target_url)
    else:
        data = {'error': 'Soportados: abc.es, larazon.es'}
    
    return jsonify(data)

@app.route('/article', methods=['GET'])
def scrape_article():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'Requiere "url"'}), 400
    
    if 'abc.es' in url.lower():
        data = scrape_article_details_abc(url)
    elif 'larazon.es' in url.lower():
        data = scrape_article_details_larazon(url)
    else:
        data = {'error': 'Soportados: abc.es, larazon.es'}
    return jsonify(data)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'OK',
        'version': '2.2 COMPLETE [file:176+177+query]',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'larazon_selectors': {
            'title': 'h1.article-maintitle',
            'subtitle': 'h2.article-main__description',
            'author': 'div.article-authorname a',
            'body': 'div#intext.article-maincontent p'
        }
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({'service': 'News Scraper API v2.2', 'status': '✅ READY'})

if __name__ == '__main__':
    print("\n🔗 http://localhost:5000/scrape?url=https://www.larazon.es/")
    app.run(debug=True, port=5000)
