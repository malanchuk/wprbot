import re

from twisted.web._newclient import ResponseNeverReceived
from scrapy.downloadermiddlewares.retry import RetryMiddleware

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from wprbot.items import WprbotItem


RetryMiddleware.EXCEPTIONS_TO_RETRY += (ResponseNeverReceived,)


class WaybackSpider(CrawlSpider):
    name = 'waybackmachine'

    custom_settings = {
        # 'CLOSESPIDER_ITEMCOUNT': 10,
    }

    def __init__(self, start_url, base_domain=None, content_xpath=None, *args, **kwargs):
        self.start_urls = [start_url]
        self.base_domain = base_domain.split('//')[-1].split('www.')[-1]
        self.content_xpath = content_xpath
        domain_re = self.base_domain.replace('.', '\.')
        self.rules = [Rule(LinkExtractor(allow=domain_re), callback='parse_page', follow=True)]

        super(WaybackSpider, self).__init__(*args, **kwargs)

    def parse_page(self, response):
        item = WprbotItem()
        item['url'] = response.url.split('.com')[-1].strip(':80').strip('/')
        if not item['url']:
            item['url'] = 'index.html'

        item['title'] = response.xpath('//title/text()').get()
        item['meta_title'] = response.xpath('//meta[@name="title"]/@content').get()
        item['meta_keywords'] = response.xpath('//meta[@name="keywords"]/@content').get()
        item['meta_desc'] = response.xpath('//meta[@name="description"]/@content').get()

        src = " ".join(response.xpath(self.content_xpath).getall())
        src = re.sub('<script[^>]+>.*?</script>', '', src, flags=re.DOTALL)
        src = re.sub('https://web.archive.org', '', src)
        src = re.sub('http://web.archive.org', '', src)
        src = re.sub('/web/[0-9A-Za-z_\-]+/http', 'https', src)
        src = re.sub('web/[0-9A-Za-z_\-]+/http', 'https', src)

        domain_re = self.base_domain.replace('.', '\.')

        src = re.sub('src=\".+%s/' % domain_re,
                     'src="https://www.%s/wp-content/uploads/' % self.base_domain, src)
        src = re.sub('background=\".+%s/' % domain_re,
                     'background="https://www.%s/wp-content/uploads/' % self.base_domain, src)
        src = re.sub('url=\".+%s/' % domain_re,
                     'url="https://www.%s/wp-content/uploads/' % self.base_domain, src)

        # case of cloud storage
        domain_re = 'cloudfront\.net|amazonaws\.com|thesn\.net'
        src = re.sub('src=\".+%s/' % domain_re,
                     'src="https://www.%s/wp-content/uploads/' % self.base_domain, src)
        src = re.sub('background=\".+%s/' % domain_re,
                     'background="https://www.%s/wp-content/uploads/' % self.base_domain, src)
        src = re.sub('url=\".+%s/' % domain_re,
                     'url="https://www.%s/wp-content/uploads/' % self.base_domain, src)

        item['content'] = src
        item['image_urls'] = response.xpath('//img/@src').getall()[4:]

        return item
