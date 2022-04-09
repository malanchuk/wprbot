import re

from scrapy import Request
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

    def __init__(
            self,
            start_url,
            base_domain=None,
            content_xpath=None,
            meta_title_xpath=None,
            meta_keywords_xpath=None,
            meta_desc_xpath=None,
            *args, **kwargs
    ):
        self.start_urls = [start_url]
        self.base_domain = base_domain.split('//')[-1].split('www.')[-1]
        self.content_xpath = content_xpath
        self.meta_title_xpath = meta_title_xpath or '//meta[@name="title"]/@content'
        self.meta_keywords_xpath = meta_keywords_xpath or '//meta[@name="keywords"]/@content'
        self.meta_desc_xpath = meta_desc_xpath or '//meta[@name="description"]/@content'
        domain_re = self.base_domain.replace('.', '\.')
        self.rules = [Rule(LinkExtractor(allow=domain_re), callback='parse_page', follow=True)]

        super(WaybackSpider, self).__init__(*args, **kwargs)

    def parse_page(self, response, **kwargs):
        item = WprbotItem()
        item['url'] = response.url.split('.com')[-1].strip(':80').strip('/')
        if not item['url']:
            item['url'] = 'index.html'

        item['title'] = response.xpath('//title/text()').get()

        item['meta_title'] = response.xpath(self.meta_title_xpath).get()
        item['meta_keywords'] = response.xpath(self.meta_keywords_xpath).get()
        item['meta_desc'] = response.xpath(self.meta_desc_xpath).get()

        src = " ".join(response.xpath(self.content_xpath).getall())
        src = re.sub('<script[^>]*>.*?</script>', '', src, flags=re.DOTALL)
        src = re.sub('https://web.archive.org', '', src)
        src = re.sub('http://web.archive.org', '', src)
        src = re.sub('/web/[0-9A-Za-z_\-]+/http', 'https', src)
        src = re.sub('web/[0-9A-Za-z_\-]+/http', 'https', src)
        src = re.sub('httpss:', 'https:', src)

        domain_re = self.base_domain.replace('.', '\.')

        src = re.sub('src=\".+%s/' % domain_re,
                     'src="https://www.%s/wp-content/uploads/' % self.base_domain, src)
        src = re.sub('background=\".+%s/' % domain_re,
                     'background="https://www.%s/wp-content/uploads/' % self.base_domain, src)
        src = re.sub('url=\".+%s/' % domain_re,
                     'url="https://www.%s/wp-content/uploads/' % self.base_domain, src)

        # case of cloud storage
        domain_re = 'cloudfront\.net|amazonaws\.com|thesn\.net|bestbetting\.com'
        src = re.sub('src=\".+(%s)/' % domain_re,
                     'src="https://www.%s/wp-content/uploads/' % self.base_domain, src)
        src = re.sub('background=\".+(%s)/' % domain_re,
                     'background="https://www.%s/wp-content/uploads/' % self.base_domain, src)
        src = re.sub('url=\".+(%s)/' % domain_re,
                     'url="https://www.%s/wp-content/uploads/' % self.base_domain, src)

        item['content'] = src
        image_urls = []
        for url in response.xpath('//img/@src').getall()[4:]:
            if not url.startswith('http'):
                url = 'http://web.archive.org' + url
            image_urls.append(url)
        item['image_urls'] = image_urls

        # for href in response.xpath("//a/@href").getall():
        #     if self.base_domain in href:
        #         if not href.startswith("http"):
        #             href = 'https://web.archive.org' + href
        #         yield Request(href, callback=self.parse_start_url)

        if item['title'] in ["Wayback Machine", "Internet Archive logo"]:
            print('!!!! Bad page', response.url)
            return

        yield item
