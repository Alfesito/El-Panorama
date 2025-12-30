from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from Http_Client.http_client import NewsHTTPClient
from Utils.Text_Utils import TextUtils
from Utils.Date_Utils import DateUtils
from Utils.Id_Utils import IDUtils
from Utils.Article_Utils import ArticleUtils
from Utils.Image_Utils import ImageUtils

class NewsScraperBase(ABC):
    def __init__(self, name):
        self.name = name
        self.http = NewsHTTPClient()
        self.text = TextUtils()
        self.date = DateUtils()
        self.idgen = IDUtils()
        self.article = ArticleUtils()
        self.image = ImageUtils()
    
    def get_page(self, url):
        """ÚNICA función HTTP simple con validación URL."""
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"URL inválida: {url}. Debe empezar con http:// o https://")
        
        resp = self.http.get(url)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')

    
    def scrape_list_page(self, url):
        """Llama SOLO a método específico de subclase."""
        soup = self.get_page(url)
        return self._scrape_list_articles(soup, url)
    
    def scrape_article_details(self, url):
        """Llama SOLO a método específico de subclase."""
        soup = self.get_page(url)
        return self._scrape_article_details(soup)
    
    @abstractmethod
    def _scrape_list_articles(self, soup, base_url):
        """EACH scraper define EXACTAMENTE cómo."""
        pass
    
    @abstractmethod
    def _scrape_article_details(self, soup):
        """EACH scraper define EXACTAMENTE cómo."""
        pass
