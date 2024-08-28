import scrapy
from scrapy.spiders import SitemapSpider


class DiariodeleonSpider(SitemapSpider):
    name = 'diariodeleon'
    allowed_domains = ['diariodeleon.es']
    sitemap_urls = ['https://www.diariodeleon.es/sitemap-index.xml']

    # Optional: specify the sitemap rules if you want to target specific URLs
    # Uncomment and modify the following line if needed
    # sitemap_rules = [('/some-regex-pattern/', 'parse_page')]

    def parse(self, response):
        # This is the default callback method for the matched URLs.
        # You can customize this method to parse the content of the pages.
        
        # Example: extract the title of the page
        title = response.xpath('//title/text()').get()
        
        # Example: print the URL and title
        self.logger.info(f'URL: {response.url}')
        self.logger.info(f'Title: {title}')
        
        # You can return the data as a dictionary or further process it
        yield {
            'url': response.url,
            'title': title
        }
