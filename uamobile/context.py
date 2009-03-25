# -*- coding: utf-8 -*-
from uamobile.cidr import IP, get_ip
from uamobile.factory.docomo import *
from uamobile.factory.ezweb import *
from uamobile.factory.softbank import *
from uamobile.factory.willcom import *

def normalize_carrier_name(carrier):
    return carrier.lower()

class Context(object):
    def __init__(self, proxy_ips=None,
                 extra_docomo_ips=None, extra_ezweb_ips=None, extra_softbank_ips=None, extra_willcom_ips=None,
                 extra_crawler_ips=None,
                 docomo_factory=None, ezweb_factory=None, softbank_factory=None, willcom_factory=None):
        # extra IPs
        self._extra_ips = {}
        for carrier, ips in (('docomo', extra_docomo_ips),
                             ('ezweb', extra_ezweb_ips),
                             ('softbank', extra_softbank_ips),
                             ('willcom', extra_willcom_ips),
                             ('crawler', extra_crawler_ips),
                             ('nonmobile', None),
                             ):
            extra = self._extra_ips.setdefault(carrier, [])
            if not ips:
                # extra_ip is None or empty sequence
                continue

            if not isinstance(ips, (list, tuple)):
                ips = [ips]
            for addr in ips:
                self.add_ip(carrier, addr)

        # factary classes
        self.docomo_factory = docomo_factory or DoCoMoUserAgentFactory
        self.ezweb_factory = ezweb_factory or EZwebUserAgentFactory
        self.softbank_factory = softbank_factory or SoftBankUserAgentFactory
        self.willcom_factory = willcom_factory or WillcomUserAgentFactory

        if proxy_ips:
            if not isinstance(proxy_ips, (list, tuple)):
                proxy_ips = [proxy_ips]
        self._proxy_ips = proxy_ips

    def get_proxy_ips(self):
        hosts = []
        if self._proxy_ips:
            for addr in self._proxy_ips:
                try:
                    hosts.append(IP(addr))
                except ValueError:
                    raise ValueError('"%s" is not valid reverse proxy address' % addr)

        return hosts

    def get_ip(self, carrier):
        carrier = normalize_carrier_name(carrier)
        return get_ip(carrier) + self._extra_ips[carrier]

    def add_ip(self, carrier, ip):
        carrier = normalize_carrier_name(carrier)
        self._extra_ips[carrier].append(IP(ip))
