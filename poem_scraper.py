import random
import re

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.poemas-del-alma.com"

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_html(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text


def normalize_url(url):
    if url.startswith("/"):
        return f"{BASE_URL}{url}"
    return url


def is_poem_url(url):
    return bool(
        re.search(r"poemas-del-alma\.com/[^\s#?]+\.htm$", url)
        or re.search(r"poemas-del-alma\.com/blog/mostrar-poema-\d+$", url)
    )


def extract_poem_links():
    links = set()
    html = fetch_html(f"{BASE_URL}/sitemap.php?pag={random.randint(1, 51)}")
    soup = BeautifulSoup(html, "html.parser")

    for anchor in soup.find_all("a", href=True):
        link = anchor["href"]
        link = normalize_url(link)
        if is_poem_url(link):
            links.add(link)

    return sorted(links)


def extract_title_and_author(html):
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1")
    author_tag = soup.find("h2")

    title = title_tag.get_text(" ", strip=True) if title_tag else "Sin título"
    author = author_tag.get_text(" ", strip=True) if author_tag else "Autor desconocido"

    return title, author


def extract_poem_text(html, author_name):
    soup = BeautifulSoup(html, "html.parser")
    poem_entry = soup.select_one("div.poem-entry")

    if poem_entry is None:
        return ""

    return str(poem_entry)

def get_poem():
    poem_urls = extract_poem_links()
    
    if not poem_urls:
        print("No se encontraron poemas en los sitemaps.")
        return

    selected_url = random.choice(poem_urls)

    try:
        html = fetch_html(selected_url)
    except requests.RequestException as error:
        print(f"No se pudo abrir el poema elegido: {error}")
        return

    title, author = extract_title_and_author(html)
    poem_text = extract_poem_text(html, author)
    poem_text = poem_text if poem_text else "No se pudo extraer el texto del poema."
    poem_text = poem_text.replace("<br/><br/>", "\n").replace("<br><br>", "\n").replace("<br/>", "").replace("<br>", "").replace("<p>", "").replace("</p>", "\n").replace("<i>", "*").replace("</i>", "*")
    poem_text = poem_text.split('<div class="likebox">')[0].strip()
    poem_text = poem_text.replace('<div class="poem-entry" id="contentfont">', "").strip()

    return f"## {title}\n{author}\n >>> {poem_text}"