import re
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from wprbot.items import WprbotItem


class Romantic4everSpider(CrawlSpider):
    name = 'crossingtheoceansea'

    start_urls = ['https://web.archive.org/web/20190211145029/http://crossingtheoceansea.com/']
    rules = [Rule(LinkExtractor(allow='crossingtheoceansea\.com'), callback='parse_page', follow=True)]

    custom_settings = {
        # 'CLOSESPIDER_ITEMCOUNT': 10,
    }

    def parse_page(self, response):
        item = WprbotItem()
        item['url'] = response.url.split('.com')[-1].strip(':80').strip('/')
        if not item['url']:
            item['url'] = 'index.html'

        item['title'] = response.xpath('//title/text()').get()
        item['meta_title'] = response.xpath('//meta[@name="title"]/@content').get()
        item['meta_keywords'] = response.xpath('//meta[@name="keywords"]/@content').get()
        item['meta_desc'] = response.xpath('//meta[@name="description"]/@content').get()

        src = " ".join(response.xpath('//div[@id="wrapper"]').getall())
        src = re.sub('<script[^>]+>.*?</script>', '', src, flags=re.DOTALL)
        src = re.sub('https://web.archive.org', '', src)
        src = re.sub('/web/[0-9A-Za-z_\-]+/http', 'https', src)
        src = re.sub('web/[0-9A-Za-z_\-]+/http', 'https', src)
        src = re.sub('src=\".+crossingtheoceansea\.com/', 'src="https://www.crossingtheoceansea.com/wp-content/uploads/', src)
        src = re.sub('background=\".+crossingtheoceansea\.com/',
                     'background="https://www.crossingtheoceansea.com/wp-content/uploads/', src)
        src = re.sub('url=\".+crossingtheoceansea\.com/',
                     'url="https://www.crossingtheoceansea.com/wp-content/uploads/', src)

        item['content'] = src

        return item
