# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os, re
from urllib.parse import urlparse

import requests
import scrapy

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class WprbotPipeline:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['url'] in self.urls_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.urls_seen.add(adapter['url'])

        data = {
            'post_title': item['title'],
            'post_content': item['content'],
            'post_status': 'publish',
            'post_author': 1,
            'post_type': 'post',
            'meta_input': {
                'custom_permalink': item['url'],
                'mfn-meta-seo-description': item['meta_desc'],
                'mfn-meta-seo-keywords': item['meta_keywords'],
            }
        }
        headers = {'Content-Type': 'application/json'}
        requests.post(f'https://{spider.base_domain}/wp-json/custom-api/v1/create-entity',
                      json=data, headers=headers)
        return item


class WprbotImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        url = re.split('/web/[0-9A-Za-z_\-]+/', request.url)[-1]
        print('======', url, '===>', 'uploads' + urlparse(url).path)
        return 'uploads/' + urlparse(url).path
