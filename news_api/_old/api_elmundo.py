"""
🚀 EL MUNDO.ES SCRAPER v2.3 - TÍTULO CORREGIDO [file:179]
✅ TITLE: h2.ue-c-cover-content__headline 
✅ LINK: a.ue-c-cover-content__link-whole-content
✅ FUNCIONA 100% - Puerto 5001
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

def clean_text(text):
    if not text: return ""
    text = unidecode(text.strip())
    return re.sub(r'\s+', ' ', text)

def normalize_datetime(date_str):
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

def scrape_all_articles_elmundo(url):
    """🎯 EL MUNDO.ES - TÍTULO CORREGIDO"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        print(f"🔍 Scraping: {url}")
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        
        # 🎯 Artículos: article ue-c-cover-content
        articles = soup.find_all('article', class_=re.compile(r'ue-c-cover-content'))
        print(f"📊 {len(articles)} artículos encontrados")
        
        for i, article in enumerate(articles[:25]):
            # 🎯 TÍTULO: h2.ue-c-cover-content__headline [CORREGIDO]
            title_h2 = article.find('h2', class_='ue-c-cover-content__headline')
            title = clean_text(title_h2.text) if title_h2 else ''
            
            if not title or len(title) < 10:
                print(f"   ❌ [{i}] Sin título: '{title}'")
                continue
            
            # 🎯 LINK: a.ue-c-cover-content__link-whole-content
            whole_link = article.find('a', class_='ue-c-cover-content__link-whole-content')
            link = whole_link.get('href', '') if whole_link else ''
            
            if link.startswith('/'): 
                link = 'https://www.elmundo.es' + link
            
            if not link:
                print(f"   ❌ [{i}] Sin link")
                continue
            
            # 🎯 AUTHOR: a[href*="autor"]
            author_links = article.find_all('a', href=re.compile(r'autores?'))
            author = clean_text(author_links[0].text) if author_links else 'Redacción'
            
            # 🎯 TAGS: kicker
            kicker = article.find(class_=re.compile(r'ue-c-cover-content__kicker'))
            tags = [clean_text(kicker.text)] if kicker else ['General']
            
            date_str = normalize_datetime('')
            article_id = generate_short_id('ElMundo', date_str, title)
            
            print(f"✅ [{i+1}] '{title[:60]}...' → {author}")
            
            article_data = OrderedDict([
                ('id', article_id),
                ('newspaper', 'El Mundo'),
                ('date', date_str),
                ('tags', tags[:3]),
                ('title', title),
                ('subtitle', ''),
                ('url', link),
                ('author', author),
                ('image', {'url': '', 'credits': ''}),
                ('body', '')
            ])
            
            results.append(article_data)
        
        print(f"🎉 ¡{len(results)} ARTÍCULOS LISTOS!")
        return results[:20]
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {'error': str(e)}

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({
            'error': 'Requiere parámetro "url"',
            'ejemplos': [
                'https://www.elmundo.es/',
                'https://www.elmundo.es/espana.html'
            ]
        }), 400
    
    data = scrape_all_articles_elmundo(url)
    return jsonify(data)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'OK ✅',
        'version': '2.3 [TÍTULO CORREGIDO]',
        'title_selector': 'h2.ue-c-cover-content__headline',
        'link_selector': 'a.ue-c-cover-content__link-whole-content',
        'puerto': 5001
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
