import requests
from random import choice
import time

from .user_agents import get_random_user_agent, mutate_user_agent_prefix

class NewsHTTPClient:
    """Cliente HTTP simple para las peticiones de scraping.

    Uso:
      client = NewsHTTPClient(timeout=12, delay=0.2)
      client.get(url)  # usa un User-Agent aleatorio de todo el pool
      client.get(url, ua_category='mobile')  # fuerza User-Agent móvil
      client.get(url, headers={'User-Agent': 'Mi-Agente'})  # usa headers específicos

    Nota: si pasas headers explícitos no se sobrescribe el User-Agent salvo que no exista.
    """

    def __init__(self, timeout=15, delay=0.5):
        self.timeout = timeout
        self.delay = delay

    def get(self, url, headers=None, ua_category: str = None, mutate_ua_prefix: bool = False, allow_bots: bool = False, **kwargs):
        """Realiza una GET con rotación de User-Agent.

        Parámetros:
          - ua_category: None|'desktop'|'mobile'|'tablet'|'headless' etc. para seleccionar la familia de UA.
          - mutate_ua_prefix: si True, reemplaza el prefijo (p.ej. 'Mozilla/5.0') por una alternativa aleatoria.
          - allow_bots: si True, permite usar user-agents de tipo bot (por defecto False).
          - headers: diccionario de cabeceras; si no incluye 'User-Agent', se añadirá una aleatoria.

        Nota: por seguridad y para evitar bloqueos, las UAs de bots están deshabilitadas
        por defecto. Si realmente quieres usarlas, establece `allow_bots=True`.
        """
        if headers is None:
            headers = {}

        # Si el usuario solicita explícitamente categoría 'bot' y no está permitido, fallar rápido
        if ua_category and ua_category.lower() in ('bot', 'bots') and not allow_bots:
            raise ValueError("ua_category 'bot' está deshabilitado. Pasa allow_bots=True para habilitarlo.")

        # Añadir User-Agent aleatorio si no viene en headers
        if 'User-Agent' not in {k.title(): v for k, v in headers.items()}:
            ua = get_random_user_agent(ua_category) if not (ua_category and ua_category.lower() in ('bot','bots')) else get_random_user_agent('bot')
            if mutate_ua_prefix:
                ua = mutate_user_agent_prefix(ua)
            headers['User-Agent'] = ua

        # Respetar pequeño delay entre peticiones para no saturar al origen
        time.sleep(self.delay)
        return requests.get(url, headers=headers, timeout=self.timeout, **kwargs)
