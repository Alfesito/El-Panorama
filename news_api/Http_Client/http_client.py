import requests
from random import choice
import time

class NewsHTTPClient:
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    
    def __init__(self, timeout=15, delay=0.5):
        self.timeout = timeout
        self.delay = delay
    
    def get(self, url, headers=None, **kwargs):
        if headers is None:
            headers = {'User-Agent': choice(self.USER_AGENTS)}
        
        time.sleep(self.delay)
        return requests.get(url, headers=headers, timeout=self.timeout, **kwargs)
