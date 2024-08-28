import scrapy
from scrapy.loader.processors import Join
from scrapy.spiders import SitemapSpider

from diariodeleon.items import DiariodeleonItem, DiariodeleonItemLoader


class DiariodeleonSpider(SitemapSpider):
    name = 'diariodeleon'
    allowed_domains = ['diariodeleon.es']
    sitemap_urls = ['https://www.diariodeleon.es/sitemap-index.xml']

    # Optional: specify the sitemap rules if you want to target specific URLs
    # Uncomment and modify the following line if needed
    # sitemap_rules = [('/some-regex-pattern/', 'parse_page')]

    def parse(self, response):
        loader = DiariodeleonItemLoader(item=DiariodeleonItem(), response=response)

        loader.add_value('url', response.url)
        loader.add_xpath('title', '//meta[@name="title"]/@content')
        loader.add_xpath('subtitle', '//meta[@name="description"]/@content')
        loader.add_xpath('author', '//meta[@name="author"]/@content')
        loader.add_xpath('category', '//meta[@property="article:section"]/@content')
        loader.add_xpath('publication_date', '//meta[@property="article:published_time"]/@content')
        loader.add_xpath('updated_date', '//meta[@property="article:modified_time"]/@content')
        loader.add_xpath('keywords', '//meta[@name="keywords"]/@content')
        loader.add_xpath('image', '//meta[@property="og:image"]/@content')
        loader.add_xpath('location', '//span[@class="c-detail__author__location"]/text()')
        loader.add_xpath('content', '//div[@class="c-detail__body"]//p[@class="paragraph"]/text()')

        yield loader.load_item()
