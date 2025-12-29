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
    if not text: return ""
    text = unidecode(text.strip())
    return text

def normalize_datetime(date_str):
    if not date_str:
        now = datetime.utcnow()
        return now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-Z]\d{2}?)', date_str)
    if match:
        dt_str = match.group(1)
        if dt_str.endswith('Z'):
            return dt_str + '.000Z'
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

def extract_image_abc(soup):
    """🎯 ABC.ES ROBUSTO - Múltiples figuras + figcaption suelta"""
    try:
        figures = soup.find_all('figure', class_='voc-img-figure')
        
        for figure in figures:
            img = figure.find('img', class_='voc-img')
            if not img or not img.get('src'): continue
            
            img_url = img.get('src')
            
            # figcaption en figura O siguiente elemento
            figcaption = figure.find('figcaption', class_='voc-figcaption-container')
            if not figcaption:
                next_fig = figure.find_next('figcaption', class_='voc-figcaption-container')
                if next_fig: figcaption = next_fig
            
            if figcaption:
                text_span = figcaption.find('span', class_='voc-figcaption--text')
                caption_text = clean_text(text_span.text) if text_span else ''
                
                credit_span = figcaption.find('span', class_='voc-figcaption--author')
                credit_text = clean_text(credit_span.text) if credit_span else ''
                
                if caption_text and credit_text:
                    credits = f"{caption_text}, {credit_text}"
                elif caption_text:
                    credits = caption_text
                elif credit_text:
                    credits = credit_text
                else:
                    credits = ''
                
                return {'url': img_url, 'credits': credits}
        
        # Fallbacks
        img = soup.find('img', class_='voc-img', src=True)
        if img and img.get('src'):
            return {'url': img.get('src'), 'credits': ''}
        
        meta_image = soup.find('meta', property='og:image')
        if meta_image:
            return {'url': meta_image.get('content', ''), 'credits': ''}
        
        return {'url': '', 'credits': ''}
    except:
        return {'url': '', 'credits': ''}

def scrape_article_details_abc(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = clean_text(soup.find('h1', class_='voc-title').text) if soup.find('h1', class_='voc-title') else ''
        subtitle = clean_text(soup.find('h2', class_='voc-subtitle').text) if soup.find('h2', class_='voc-subtitle') else ''
        
        author_section = soup.find('section', class_='voc-author')
        author = ''
        if author_section:
            author_link = author_section.select_one('p.voc-authorname a')
            author = clean_text(author_link.text) if author_link else ''
        
        tags = []
        nav_topics = soup.find('nav', class_='voc-topics__header')
        if nav_topics:
            tag_links = nav_topics.find_all('a', class_='voc-topics__link')
            tags = [clean_text(a.get('title', a.text.strip())) for a in tag_links[:8]]
        
        body_paragraphs = soup.find_all('p', class_='voc-p')[:12]
        body = ' '.join([clean_text(p.text) for p in body_paragraphs if len(clean_text(p.text)) > 30])
        
        image = extract_image_abc(soup)
        
        return {
            'title': title, 'subtitle': subtitle, 'author': author,
            'tags': tags, 'body': body[:3000], 'image': image
        }
    except Exception as e:
        print(f"Error ABC {url}: {e}")
        return {'title': '', 'subtitle': '', 'author': '', 'tags': [], 'body': '', 'image': {'url': '', 'credits': ''}}

def scrape_all_articles_abc(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
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
                ('url', link), ('author', final_author), ('image', details['image']),
                ('body', details['body'])
            ])
            results.append(ordered_article)
        
        return results[:20]
    except Exception as e:
        return {'error': str(e)}

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'error': 'Requiere "url" (abc.es)'}), 400
    
    if 'abc.es' in target_url.lower():
        data = scrape_all_articles_abc(target_url)
    else:
        data = {'error': 'Solo abc.es soportado'}
    return jsonify(data)

if __name__ == '__main__':
    print("🚀 ABC Scraper ROBUSTO - http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')
