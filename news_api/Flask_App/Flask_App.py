from flask import Flask, jsonify, request

class NewsFlaskApp:
    """Flask app reutilizable para cualquier scraper."""
    
    def __init__(self, scraper_instance, name, port=5000, domains=None):
        self.scraper = scraper_instance
        self.name = name
        self.port = port
        self.domains = domains or [name.lower().replace(' ', '').replace('.', '')]
        self.app = Flask(__name__)
        self._register_routes()
    
    def _register_routes(self):
        @self.app.route('/scrape', methods=['GET'])
        def scrape():
            url = request.args.get('url')
            if not url:
                return jsonify({'error': f'Requiere parámetro url para {self.name}'}), 400
            
            for domain in self.domains:
                if domain in url.lower():
                    return jsonify(self.scraper.scrape_list_page(url))
            
            return jsonify({
                'error': f'Requiere url {self.name}', 
                'dominios': self.domains
            }), 400
        
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'OK',
                'scraper': self.name,
                'domains': self.domains,
                'port': self.port
            })
    
    def run(self, debug=True, host='127.0.0.1'):
        print(f"🚀 {self.name} Scraper - http://{host}:{self.port}/scrape")
        self.app.run(debug=debug, port=self.port, host=host)
