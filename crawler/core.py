from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from .fetcher import fetch_url
from .parser import extract_links, extract_title, extract_emails
import time
import logging

logging.basicConfig(filename="logs/osint.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

class Crawler:
    def __init__(self, domain, max_depth=2, max_workers=8, delay=0.5):
        self.domain = domain
        self.base_netloc = urlparse(domain).netloc or domain
        self.max_depth = max_depth
        self.delay = delay
        self.max_workers = max_workers
        self.visited = set()
        self.results = []

    def _is_same_domain(self, url):
        return urlparse(url).netloc.endswith(self.base_netloc)

    def crawl(self):
        to_crawl = {(self.domain, 0)}
        while to_crawl:
            batch = list(to_crawl)
            to_crawl = set()
            with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
                futures = {ex.submit(self._fetch_and_parse, url, depth): (url, depth) for url, depth in batch}
                for fut in as_completed(futures):
                    url, depth = futures[fut]
                    links = fut.result() or []
                    if depth + 1 <= self.max_depth:
                        for l in links:
                            if l not in self.visited and self._is_same_domain(l):
                                to_crawl.add((l, depth + 1))
            # polite delay between rounds
            time.sleep(self.delay)
        return self.results

    def _fetch_and_parse(self, url, depth):
        if url in self.visited:
            return []
        self.visited.add(url)
        status, html, headers = fetch_url(url)
        if status is None:
            logging.info(f"Failed to fetch {url}")
            return []
        title = extract_title(html)
        emails = list(extract_emails(html))
        self.results.append({
            "url": url,
            "status": status,
            "title": title,
            "server": headers.get("Server") if headers else None,
            "emails": emails
        })
        links = extract_links(url, html)
        # keep only same-domain links
        links = [l for l in links if self._is_same_domain(l)]
        return links
