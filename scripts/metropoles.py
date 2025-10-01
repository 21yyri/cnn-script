import feedparser, requests, os, pytz
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
from time import mktime


def get_imagem(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    return soup.select('img.img-fluid.center-image')[0].get("src")


load_dotenv()

COMUNICA_URL = "http://localhost:8000/api"
METROPOLES_URL = "https://metropoleonline.com.br/rss/latest-posts"

feed = feedparser.parse(METROPOLES_URL)
if feed.status != 200:
    raise requests.exceptions.ConnectionError()

token = requests.post(f"{COMUNICA_URL}/login/", json = {
    "username": os.getenv("MATRICULA"),
    "password": os.getenv("SENHA")
}).json().get("Token")


for news in feed.entries:
    noticia = {
        "titulo": news.title,
        "body": news.summary + '.',
        "link": news.link,
        "data": str(datetime.fromtimestamp(
            mktime(news.published_parsed),
            pytz.UTC)
        ),
        "imagem_url": get_imagem(news.link)
    }

    response = requests.post(
        f"{COMUNICA_URL}/news/post/", 
        json = noticia, headers = {
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(response.status_code)
