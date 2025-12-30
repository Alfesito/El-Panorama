from flask import Flask, jsonify, request
from Newspapers.api_abc import ABCScraper
from Newspapers.api_elmundo import ElMundoScraper
from Newspapers.api_eldiario import ElDiarioScraper
from Newspapers.api_elpais import ElPaisScraper
from Newspapers.api_larazon import LaRazonScraper

SCRAPERS = {
    'abc.es': ABCScraper(),
    'elmundo.es': ElMundoScraper(),
    'eldiario.es': ElDiarioScraper(),
    'elpais.com': ElPaisScraper(),
    'larazon.es': LaRazonScraper()
}

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Requiere parámetro url'}), 400
    
    for domain, scraper in SCRAPERS.items():
        if domain in url.lower():
            print(f"🔍 {domain}: {url}")
            return jsonify(scraper.scrape_list_page(url))
    
    return jsonify({
        'error': 'Periódico no soportado',
        'soportados': list(SCRAPERS.keys()),
        'ejemplos': [
            'https://www.abc.es',
            'https://www.elmundo.es',
            'https://www.eldiario.es',
            'https://elpais.com',
            'https://www.larazon.es'
        ]
    }), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'OK',
        'total': len(SCRAPERS),
        'periódicos': list(SCRAPERS.keys())
    })

if __name__ == '__main__':
    print("🚀 NEWS API CENTRAL - 5 PERIÓDICOS")
    print("python news_api.py → puerto 5000")
    app.run(debug=True, port=5000)
