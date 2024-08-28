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
        loader.add_xpath('title', '//h1[@class="c-detail__title"]/text()')
        loader.add_xpath('subtitle', '//p[@class="c-detail__subtitle"]/text()')
        loader.add_xpath('category', '//meta[@property="article:section"]/@content')
        loader.add_xpath('publication_date', '//p[contains(@class, "c-detail__info__more")][1]/a/time/@datetime')
        loader.add_xpath('updated_date', '//p[contains(@class, "c-detail__info__more")][2]/time/@datetime')
        loader.add_xpath('author', '//div[@class="c-detail__author__name"]/a/text()')
        loader.add_xpath('location', '//span[@class="c-detail__author__location"]/text()')
        loader.add_xpath('tags', '//ul[@class="c-detail__tags__list"]/li/a/text()')
        loader.add_xpath('content', '//div[@class="c-detail__body"]//p[@class="paragraph"]/text()')
        loader.add_xpath('images', '//div[@class="c-detail__media__thumb"]/picture/source[1]/@srcset')
        loader.add_xpath('image_caption', '//figcaption[@class="c-detail__media__txt"]/p/span[1]/text()')
        loader.add_xpath('image_author', '//figcaption[@class="c-detail__media__txt"]/p/span[2]/text()')

        yield loader.load_item()
