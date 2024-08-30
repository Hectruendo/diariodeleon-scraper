import logging

from scrapy.http import Request
from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc
from scrapy.utils.sitemap import Sitemap, sitemap_urls_from_robots

logger = logging.getLogger(__name__)


class CustomSitemapSpider(SitemapSpider):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._url_list = []
        self._pending_sitemap_requests = 0

    def _parse_sitemap(self, response):
        if response.url.endswith("/robots.txt"):
            for url in sitemap_urls_from_robots(response.text, base_url=response.url):
                self._pending_sitemap_requests += 1
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                logger.warning(
                    "Ignoring invalid sitemap: %(response)s",
                    {"response": response},
                    extra={"spider": self},
                )
                for r in self._check_sitemap_completion():
                    yield r

            s = Sitemap(body)
            it = self.sitemap_filter(s)

            if s.type == "sitemapindex":
                for loc in iterloc(it, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        self._pending_sitemap_requests += 1
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == "urlset":
                # Collect URLs and their lastmod dates
                for entry in it:
                    loc = entry.get("loc")
                    lastmod = entry.get("lastmod")
                    if loc:
                        self._url_list.append((loc, lastmod))

            # Decrement pending sitemap request counter
            for r in self._check_sitemap_completion():
                yield r

    def _check_sitemap_completion(self):
        """Check if all sitemapindex requests have been processed, and if so, process the URL set."""
        self._pending_sitemap_requests -= 1
        logger.info(
            "Pending sitemap requests: %(pending)s",
            {"pending": self._pending_sitemap_requests},
            extra={"spider": self},
        )
        if self._pending_sitemap_requests == 0:
            # Sort the URL list by lastmod in descending order and yield requests
            self._url_list.sort(key=lambda x: x[1], reverse=True)
            for loc, _ in self._url_list:
                for r, c in self._cbs:
                    if r.search(loc):
                        yield Request(loc, callback=c)
                        break
