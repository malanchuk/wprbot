# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WprbotItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    meta_title = scrapy.Field()
    meta_keywords = scrapy.Field()
    meta_desc = scrapy.Field()
    content = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
