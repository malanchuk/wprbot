import os
import logging

from scrapy.utils.job import job_dir
from scrapy.utils.request import referer_str, request_fingerprint
from scrapy.dupefilters import RFPDupeFilter


class WprbotDupeFilter(RFPDupeFilter):
    """Request Fingerprint duplicates filter"""
    all_urls = []

    def __getid(self, url):
        url = url.split('.com')[-1].strip(':80').strip('/').split('#')[0]
        return url

    def request_seen(self, request):
        fp = self.__getid(request.url)
        if fp in self.fingerprints:
            print(f'===> {fp} ignored as duplicate', )
            return True
        else:
            print('====================', fp)
        if request.meta.get('redirect_urls'):
            self.fingerprints.add(fp)
        else:
            if request.url in self.all_urls:
                self.fingerprints.add(fp)
            self.all_urls.append(request.url)
        if self.file:
            self.file.write(fp + os.linesep)
