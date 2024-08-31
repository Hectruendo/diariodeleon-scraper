import logging
import time
from scrapy import signals
from datetime import datetime

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
        self.total_urls = 0

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Create the spider instance
        spider = super(CustomSitemapSpider, cls).from_crawler(crawler, *args, **kwargs)

        # Connect the signal
        crawler.signals.connect(spider.log_error, signal=signals.spider_error)

        return spider

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
                        # last mode has format: 2018-05-01T06:00:01+02:00, convert it to timestamp for sorting later as such: self._url_list.sort(key=lambda x: x[1], reverse=True)
                        if lastmod:
                            lastmod = time.mktime(time.strptime(lastmod, "%Y-%m-%dT%H:%M:%S%z"))
                        else:
                            lastmod = 0

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
            logger.info(
                f"Sitemap index processed, sorting URLs by lastmod and yielding requests, total URLs: {len(self._url_list)}",
                extra={"spider": self}
            )
            logger.info(
                f"First date: {datetime.fromtimestamp(self._url_list[-1][1])}, Last date: {datetime.fromtimestamp(self._url_list[0][1])}",
                extra={"spider": self}
            )
            self.total_urls = len(self._url_list)
            for index, (loc, _) in enumerate(self._url_list):
                for r, c in self._cbs:
                    if r.search(loc):
                        yield Request(
                            loc,
                            callback=c,
                            priority=self.total_urls - index,
                            # errback=self.log_error,
                            # meta={'handle_httpstatus_all': True}
                        )
                        break

    def log_error(self, failure):
        # Extract the URL from the failure object
        request = failure.request
        url = request.url

        # Get the current date in YYYYMMDD format
        date_str = datetime.now().strftime("%Y%m%d%H%M%S")

        # Log the URL to a file with the date in its name
        with open(f'results/failed_urls_{date_str}.txt', 'a') as f:
            f.write(url + '\n')
