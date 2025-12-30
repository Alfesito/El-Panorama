from Scraper.Base_Scraper import NewsScraperBase
import re

class ElMundoScraper(NewsScraperBase):
    def __init__(self):
        super().__init__('El Mundo')
    
    def _scrape_list_articles(self, soup, base_url):
        """🚀 TU CÓDIGO ORIGINAL v2.3 EXACTO"""
        results = []
        
        # 🎯 EXACTO: article[class*=ue-c-cover-content]
        articles = soup.find_all('article', class_=re.compile(r'ue-c-cover-content'))
        
        for i, article in enumerate(articles[:25]):
            # 🎯 TITLE EXACTO: h2.ue-c-cover-content__headline
            title_h2 = article.find('h2', class_='ue-c-cover-content__headline')
            title = self.text.cleantext(title_h2) if title_h2 else ''
            
            if not title or len(title) < 10:
                continue
            
            # 🎯 LINK EXACTO: a.ue-c-cover-content__link-whole-content ← CORREGIDO
            whole_link = article.find('a', class_='ue-c-cover-content__link-whole-content')
            link = whole_link.get('href', '') if whole_link else ''
            
            if link.startswith('/'): 
                link = 'https://www.elmundo.es' + link
            
            if not link.startswith('http'):
                continue
            
            # 🎯 AUTHOR EXACTO
            author_links = article.find_all('a', href=re.compile(r'autores?'))
            author = self.text.cleantext(author_links[0]) if author_links else 'Redacción'
            
            # 🎯 TAGS kicker
            kicker = article.find(class_=re.compile(r'ue-c-cover-content__kicker'))
            tags = [self.text.cleantext(kicker)] if kicker else ['General']
            
            # DATE & ID
            date_str = self.date.normalizedatetime()
            article_id = self.idgen.generateshortid('ElMundo', date_str, title)
                        
            # 🎯 OrderedDict EXACTO como original
            article_data = self.article.create_ordered_article(
                'El Mundo', article_id, date_str, tags[:3],
                title, '', link, author,
                {'url': '', 'credits': ''}, ''
            )
            results.append(article_data)
        
        return results[:20]
    
    def _scrape_article_details(self, soup):
        """Mínimo para compatibilidad (no usado en list)."""
        return {
            'title': '', 'subtitle': '', 'tags': [],
            'body': '', 'image': {'url': '', 'credits': ''}, 'author': 'Redacción'
        }

# Flask 
if __name__ == '__main__':
    try:
        from Flask_App.Flask_App import NewsFlaskApp
    except Exception:
        from Flask_App import NewsFlaskApp
    eldiario = ElMundoScraper()
    app = NewsFlaskApp(eldiario, "El Mundo", 5008, ["elmundo.es"])
    app.run()
