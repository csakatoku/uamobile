# -*- coding: utf-8 -*-
from tests import msg
from uamobile import *
from uamobile.willcom import WillcomUserAgent
from uamobile.factory.willcom import WillcomUserAgentFactory

def test_detect_fast():
    assert detect_fast('Mozilla/3.0(WILLCOM;SANYO/WX310SA/2;1/1/C128) NetFront/3.3,61.198.142.127') == 'willcom'

def test_useragent():
    def inner(useragent, name, vendor, model, model_version, browser_version, cache_size):
        ua = detect({'HTTP_USER_AGENT': useragent})

        assert ua.is_willcom()
        assert ua.carrier == 'WILLCOM'
        assert ua.short_carrier == 'W'
        assert ua.name == name
        assert ua.vendor == vendor
        assert ua.model == model, ua.model
        assert ua.model_version == model_version, ua.model_version
        assert ua.browser_version == browser_version, '%r expected, actual %r' % (browser_version, ua.browser_version)
        if cache_size is not None:
            assert ua.cache_size == cache_size
        else:
            assert ua.cache_size is None
        assert ua.display is not None
        assert ua.serialnumber is None
        assert ua.supports_cookie() == True

    for args in DATA:
        yield tuple([inner] + list(args))


def test_display_default():
    ua = detect({'HTTP_USER_AGENT':'Mozilla/3.0(WILLCOM;KYOCERA/WX310K/2;1.2.7.17.000000/0.1/C100) Opera 7.0'})
    assert ua.display.width != 0
    assert ua.display.height != 0
    assert ua.display.color
    assert ua.display.depth
    assert ua.display.is_vga() is False
    assert ua.display.is_qvga() is True

def test_strip_serialnumber():
    value = 'Mozilla/3.0(WILLCOM;KYOCERA/WX310K/2;1.2.7.17.000000/0.1/C100) Opera 7.0'
    ua = detect({'HTTP_USER_AGENT': value})
    assert ua.strip_serialnumber() == value


def test_is_bogus():
    def func(ip, expected):
        ua = detect({'HTTP_USER_AGENT': 'Mozilla/3.0(WILLCOM;SANYO/WX310SA/2;1/1/C128) NetFront/3.3,61.198.142.127',
                     'REMOTE_ADDR'    : ip,
                     })
        assert ua.is_willcom()
        res = ua.is_bogus()
        assert res == expected, '%s expected, actual %s' % (expected, res)

    for ip, expected in (
        ('210.230.128.224', True),
        ('61.198.128.0', False),
        ):
        yield func, ip, expected

def test_extra_ip():
    ctxt1 = Context(extra_willcom_ips=['192.168.0.0/24'])
    ua = detect({'HTTP_USER_AGENT': 'Mozilla/3.0(WILLCOM;KYOCERA/WX310K/2;1.2.7.17.000000/0.1/C100) Opera 7.0',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 },
                context=ctxt1)
    assert ua.is_willcom()
    assert ua.is_bogus() is False

    ctxt2 = Context(extra_willcom_ips=[])
    ua = detect({'HTTP_USER_AGENT': 'Mozilla/3.0(WILLCOM;KYOCERA/WX310K/2;1.2.7.17.000000/0.1/C100) Opera 7.0',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 },
                context=ctxt2)
    assert ua.is_willcom()
    assert ua.is_bogus() is True


def test_my_factory():
    class MyWillcomUserAgent(WillcomUserAgent):
        def get_my_attr(self):
            return self.environ.get('HTTP_X_DOCOMO_UID')

    class MyWillcomUserAgentFactory(WillcomUserAgentFactory):
        device_class = MyWillcomUserAgent

    context = Context(willcom_factory=MyWillcomUserAgentFactory)
    ua = detect({'HTTP_USER_AGENT'  : 'Mozilla/3.0(WILLCOM;KYOCERA/WX300K/2;2.0.10.11.000000/0.1/C100) Opera/7.0',
                 'REMOTE_ADDR'      : '192.168.0.1',
                 'HTTP_X_DOCOMO_UID': 'spam',
                 },
                context=context)
    assert ua.is_willcom()
    assert isinstance(ua, MyWillcomUserAgent)
    assert ua.get_my_attr() == 'spam'


#########################
# Test data
#########################

# ua, name, vendor, model, model_version, browser_version, cache_size
DATA = (('Mozilla/3.0(DDIPOCKET;JRC/AH-J3001V,AH-J3002V/1.0/0100/c50)CNF/2.0', 'WILLCOM', 'JRC', 'AH-J3001V,AH-J3002V', '1.0', '0100', 50),
        ('Mozilla/3.0(DDIPOCKET;KYOCERA/AH-K3001V/1.7.2.70.000000/0.1/C100) Opera 7.0', 'WILLCOM', 'KYOCERA', 'AH-K3001V', '1.7.2.70.000000', '0.1', 100),
        ('Mozilla/3.0(DDIPOCKET;JRC/AH-J3003S/1.0/0100/c50)CNF/2.0', 'WILLCOM', 'JRC', 'AH-J3003S', '1.0', '0100', 50),
        ('Mozilla/3.0(WILLCOM;SANYO/WX310SA/2;1/1/C128) NetFront/3.3,61.198.142.127', 'WILLCOM', 'SANYO', 'WX310SA', '2;1', '1', 128),

        # IE on W-zero3
        ('Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; SHARP/WS007SH; PPC; 480x640)', 'WILLCOM', 'SHARP', 'WS007SH', None, 'MSIE 4.01', None),

        # Opera on W-zero3
        ('Mozilla/4.0 (compatible; MSIE 6.0; Windows CE; SHARP/WS007SH; PPC; 480x640) Opera 8.60 [ja]', 'WILLCOM', 'SHARP', 'WS007SH', None, 'MSIE 6.0', None),
)
