# -*- coding: utf-8 -*-
from uamobile import detect, Context

def test_crawler():
    def func(ip, useragent):
        device = detect({'HTTP_USER_AGENT': useragent,
                         'REMOTE_ADDR'    : ip})
        assert device.is_docomo()
        assert device.is_crawler()
        assert device.is_bogus()

    for ip, useragent in (
        ('60.43.36.253', 'DoCoMo/2.0 SO902i(c100;TB;W20H10) (symphonybot1.froute.jp; +http://search.froute.jp/howto/crawler.html)'),
        ('203.143.121.217', 'DoCoMo/2.0 SO902i(c100;TB;W20H10) (symphonybot1.froute.jp; +http://search.froute.jp/howto/crawler.html)'),
        # DeNA
        ('202.238.103.126', 'DoCoMo/2.0 N902iS(c100;TB;W24H12)(compatible; moba-crawler; http://crawler.dena.jp/)'),
        ('202.213.221.97', 'DoCoMo/2.0 N902iS(c100;TB;W24H12)(compatible; moba-crawler; http://crawler.dena.jp/)'),
        # Crawler whose IP is valid but the useragent contains FOMA hardware ID
        ('60.43.36.253', 'DoCoMo/2.0 M702iS(c100;TB;W24H13;ser333333033303333;icc8981100000333333333F)'),
        # Google
        ('209.85.238.17', 'DoCoMo/1.0/N505i/c20/TB/W20H10 (compatible; Googlebot-Mobile/2.1; +http://www.google.com/bot.html)'),
        ('72.14.199.1', 'DoCoMo/1.0/N505i/c20/TB/W20H10 (compatible; Googlebot-Mobile/2.1; +http://www.google.com/bot.html)'),
        # Yahoo
        ('124.83.159.146', 'DoCoMo/2.0 SH902i (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)'),
        ('124.83.159.148', 'DoCoMo/2.0 SH902i (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)'),
        ('124.83.159.152', 'DoCoMo/2.0 SH902i (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)'),
        ('124.83.159.160', 'DoCoMo/2.0 SH902i (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)'),
        ('124.83.159.176', 'DoCoMo/2.0 SH902i (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)'),
        ('124.83.159.184', 'DoCoMo/2.0 SH902i (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)'),
        # livedoor
        ('203.104.254.1', 'DoCoMo/1.0/N505i/c20/TB/W20H10 (compatible; LD_mobile_bot; +http://helpguide.livedoor.com/help/search/qa/grp627)'),
        # goo
        ('210.150.10.32', 'DoCoMo/2.0 P900i(c100;TB;W24H11)(compatible; ichiro/mobile goo; +http://help.goo.ne.jp/door/crawler.html)'),
        ):
        yield func, ip, useragent

def test_not_crawler():
    def func(ip, useragent):
        device = detect({'HTTP_USER_AGENT': useragent,
                         'REMOTE_ADDR'    : ip})
        assert device.is_docomo()
        assert device.is_bogus()
        assert device.is_crawler() is False

    for ip, ua in (
        ('66.249.70.39', 'DoCoMo/1.0/N505i/c20/TB/W20H10 (compatible; Googlebot-Mobile/2.1; +http://www.google.com/bot.html)'),
        ):
        yield func, ip, ua


def test_extra_ip():
    ctxt1 = Context(extra_crawler_ips=['192.168.0.0/24'])
    ua = detect({'HTTP_USER_AGENT': 'Mozilla/3.0(WILLCOM;KYOCERA/WX310K/2;1.2.7.17.000000/0.1/C100) Opera 7.0',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 },
                context=ctxt1)
    assert ua.is_willcom()
    assert ua.is_crawler() is True
    assert ua.is_bogus() is True

    ctxt2 = Context(extra_crawler_ips=[])
    ua = detect({'HTTP_USER_AGENT': 'Mozilla/3.0(WILLCOM;KYOCERA/WX310K/2;1.2.7.17.000000/0.1/C100) Opera 7.0',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 },
                context=ctxt2)
    assert ua.is_willcom()
    assert ua.is_crawler() is False
    assert ua.is_bogus() is True
