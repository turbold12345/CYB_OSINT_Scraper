from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

def extract_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # normalize
        link = urljoin(base_url, href)
        links.add(link)
    return links

def extract_title(html):
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""

def extract_emails(html):
    return set(EMAIL_REGEX.findall(html or ""))
