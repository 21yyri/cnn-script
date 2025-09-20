import feedparser, requests, os, pytz
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
from time import mktime

def format_categoria(categoria: str) -> str:
    """Retorna a categoria com capitalização e acentuação."""
    
    match categoria:
        case 'politica':
            return 'Política'
        case 'educacao':
            return 'Educação'
        case 'saude':
            return 'Saúde'
        case _:
            return categoria.capitalize()


def get_imagem(url: str) -> str:
    """Recebe uma notícia e retorna a URL para a imagem de capa da notícia."""
    
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    imagem = soup.select('img.flex.size-full.object-cover')[2]
    return imagem.get("src")


COMUNICA_URL = "http://127.0.0.1:8000/api"

RSS_URL = "https://admin.cnnbrasil.com.br/feed/"
feed = feedparser.parse(RSS_URL)

if feed.status != 200:
    raise requests.exceptions.HTTPError()

CATEGORIAS = [
    'economia', 'politica', 
    'esportes', 'educacao', 
    'nacional', 'saude',
    'tecnologia', 'nacional'
]

load_dotenv()
token = requests.post(f"{COMUNICA_URL}/login/", json = {
    "username": os.getenv("MATRICULA"),
    "password": os.getenv("SENHA")
}).json().get("Token")

for entry in feed.entries:
    categoria = entry.link.split('/')[3]
    if categoria not in CATEGORIAS:
        continue
    
    noticia = {
        "autor": entry.author,
        "setor": format_categoria(categoria),
        "titulo": entry.title,
        "body": entry.summary + '.',
        "link": entry.link,
        "data": str(
            datetime.fromtimestamp(
                mktime(entry.published_parsed), 
                tz = pytz.UTC
            )
        ),
        "imagem_url": get_imagem(entry.link)
    }

    response = requests.post(f"{COMUNICA_URL}/news/post/", json = noticia, headers = {
        "Authorization": f"Bearer {token}"
    })

    print(response.status_code)

