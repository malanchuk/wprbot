import os
import logging

from scrapy.utils.job import job_dir
from scrapy.utils.request import referer_str, request_fingerprint
from scrapy.dupefilters import RFPDupeFilter


class WprbotDupeFilter(RFPDupeFilter):
    """Request Fingerprint duplicates filter"""

    def __getid(self, url):
        url = url.split('.com')[-1].strip(':80').strip('/')
        print('====================', url)
        return url

    def request_seen(self, request):
        fp = self.__getid(request.url)
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)
