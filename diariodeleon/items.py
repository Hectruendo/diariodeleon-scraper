import scrapy
from scrapy.loader.processors import MapCompose, Join, TakeFirst
import re


class DiariodeleonItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    subtitle = scrapy.Field()
    category = scrapy.Field()
    publication_date = scrapy.Field()
    updated_date = scrapy.Field()
    author = scrapy.Field()
    location = scrapy.Field()
    keywords = scrapy.Field()
    content = scrapy.Field()
    image = scrapy.Field()

    category = scrapy.Field()  # New field for category

def split_by_comma(value):
    if value:
        return [item.strip() for item in value.split(',')]
    return []

class DiariodeleonItemLoader(scrapy.loader.ItemLoader):
    default_output_processor = TakeFirst()

    # Processors for specific fields
    content_in = MapCompose(str.strip)  # Remove leading/trailing spaces from content
    content_out = Join('\n')  # Join paragraphs with a newline

    keywords_out = MapCompose(split_by_comma)  # Strip whitespace from each tag

    # Publication date processor to clean up the date format
    publication_date_in = MapCompose(lambda x: re.sub(r'\s*\|\s*', ' ', x))
    updated_date_in = MapCompose(lambda x: re.sub(r'\s*\|\s*', ' ', x))

    def add_content_length(self, body):
        self.add_value('content_length', len(body))
