from bs4 import BeautifulSoup

class ImageUtils:
    @staticmethod
    def extract_image(soup, specific_selectors=None):
        """Busca imagen principal con créditos. Fallbacks múltiples."""
        if specific_selectors:
            # Selectores específicos por periódico
            for selector in specific_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    return {'url': img['src'], 'credits': ''}
        
        # OG fallback universal
        og_image = soup.find('meta', property='og:image')
        if og_image:
            return {'url': og_image.get('content', ''), 'credits': ''}
        
        return {'url': '', 'credits': ''}
