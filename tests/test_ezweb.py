# -*- coding: utf-8 -*-
from tests import msg, MockWSGIEnviron as Environ
from uamobile import detect, EZweb

def test_netfront_nonmobile_mode():
    ua = detect({'HTTP_USER_AGENT':'KDDI-TS3A UP.Browser/6.2.0.11.2.1 (GUI) MMP/2.0, Mozilla/4.08 (MobilePhone; NMCS/3.3) NetFront/3.3'})
    assert ua.is_ezweb()
    assert ua.model == 'TS3A'
    assert ua.version == '6.2.0.11.2.1 (GUI)'
    assert ua.server == 'MMP/2.0'

def test_yahooo_crawler():
    ua = detect({'HTTP_USER_AGENT':'KDDI-CA23 UP.Browser/6.2.0.5 (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)'})
    assert ua.is_ezweb()

def test_no_subscription_id():
    ua = detect({'HTTP_USER_AGENT': 'KDDI-SA35 UP.Browser/6.2.0.9.1 (GUI) MMP/2.0'})
    assert ua.serialnumber is None

def test_display():
    env = {'HTTP_USER_AGENT': 'KDDI-SA35 UP.Browser/6.2.0.9.1 (GUI) MMP/2.0',
           'HTTP_X_UP_DEVCAP_MAX_PDU': '131072',
           'HTTP_X_UP_DEVCAP_MULTIMEDIA': '9300941123301120',
           'HTTP_X_UP_DEVCAP_SCREENPIXELS': '240,268',
           'HTTP_X_SSL': 'off',
           'HTTP_X_UP_DEVCAP_SOFTKEYSIZE': '6',
           'HTTP_X_UP_DEVCAP_SCREENDEPTH': '16,RGB565',
           'HTTP_X_UP_DEVCAP_NUMSOFTKEYS': '2',
           'HTTP_X_UP_PROXY_BA_REALM': 'realm',
           'HTTP_X_UP_DEVCAP_QVGA': '1',
           'HTTP_X_UP_DEVCAP_SCREENCHARS': '23,12',
           'HTTP_X_UP_DEVCAP_CC': '1',
           'HTTP_X_UP_DEVCAP_TITLEBAR': '1',
           'HTTP_X_UP_DEVCAP_ISCOLOR': '1',
           'HTTP_X_UP_SUBNO': '00000000000000_ef.ezweb.ne.jp' }
    ua = detect(env)
    assert ua.display.width == 240, "%s expected, result %r" % (240, ua.display.width)
    assert ua.display.height == 268, "%s expected, result %r" % (268, ua.display.height)
    assert ua.display.color == True
    assert ua.display.is_vga() == False
    assert ua.display.is_qvga() == True

def test_display_error():
    base_env = {'HTTP_USER_AGENT': 'KDDI-SA35 UP.Browser/6.2.0.9.1 (GUI) MMP/2.0',
                'HTTP_X_UP_DEVCAP_SCREENPIXELS': '240,268',
                'HTTP_X_UP_DEVCAP_SCREENDEPTH': '16,RGB565',
                'HTTP_X_UP_DEVCAP_ISCOLOR': '1' }

    # No ISCOLOR
    env = dict(base_env)
    del env['HTTP_X_UP_DEVCAP_ISCOLOR']
    ua = detect(env)
    assert ua.display.width == 240
    assert ua.display.height == 268
    assert ua.display.depth
    assert ua.display.color == False

    # invalid SCREENPIXELS
    env = dict(base_env)
    del env['HTTP_X_UP_DEVCAP_SCREENPIXELS']
    ua = detect(env)
    assert ua.display.width == 0
    assert ua.display.height == 0
    assert ua.display.color
    assert ua.display.depth

    env = dict(base_env)
    env['HTTP_X_UP_DEVCAP_SCREENPIXELS'] = '240,egg'
    ua = detect(env)
    assert ua.display.width == 0
    assert ua.display.height == 0
    assert ua.display.color
    assert ua.display.depth

    env = dict(base_env)
    env['HTTP_X_UP_DEVCAP_SCREENPIXELS'] = '240,268,1'
    ua = detect(env)
    assert ua.display.width == 0
    assert ua.display.height == 0
    assert ua.display.color
    assert ua.display.depth

    # invalid SCREENDEPTH
    env = dict(base_env)
    del env['HTTP_X_UP_DEVCAP_SCREENDEPTH']
    ua = detect(env)
    assert ua.display.width == 240
    assert ua.display.height == 268
    assert ua.display.color
    assert ua.display.depth == 0

    env = dict(base_env)
    env['HTTP_X_UP_DEVCAP_SCREENDEPTH'] = 'spam'
    ua = detect(env)
    assert ua.display.width == 240
    assert ua.display.height == 268
    assert ua.display.color
    assert ua.display.depth == 0

def test_useragent_ezweb():
    def inner(useragent, version, model, device_id, server, xhtml_compliant, comment, is_wap1, is_wap2):
        ua = detect(Environ(useragent))
        assert isinstance(ua, EZweb)
        assert ua.carrier == 'EZweb'
        assert ua.short_carrier == 'E'
        assert ua.is_docomo() == False
        assert ua.is_ezweb()
        assert ua.is_softbank() == False
        assert ua.is_vodafone() == False
        assert ua.is_jphone() == False
        assert ua.is_willcom() == False
        assert ua.model == model, msg(ua, ua.model, model)
        assert ua.version == version, msg(ua, ua.version, version)
        assert ua.device_id == device_id, msg(ua, ua.device_id, device_id)
        assert ua.server == server, msg(ua, ua.server, server)
        assert ua.comment == comment, msg(ua, ua.comment, comment)
        assert ua.is_xhtml_compliant() == xhtml_compliant
        assert ua.is_wap1() == is_wap1
        assert ua.is_wap2() == is_wap2
        assert ua.display is not None
        assert ua.supports_cookie() == True

    for args in DATA:
        yield ([inner] + list(args))

#########################
# Test data
#########################

DATA = (
    # ua, version, model, device_id, server, xhtml_compliant, comment, is_wap1, is_wap2
    ('UP.Browser/3.01-HI01 UP.Link/3.4.5.2', '3.01', 'HI01', 'HI01', 'UP.Link/3.4.5.2', False, None, True, False),
    ('KDDI-TS21 UP.Browser/6.0.2.276 (GUI) MMP/1.1', '6.0.2.276 (GUI)', 'TS21', 'TS21', 'MMP/1.1', True, None, False, True),
    ('UP.Browser/3.04-TS14 UP.Link/3.4.4 (Google WAP Proxy/1.0)', '3.04', 'TS14', 'TS14', 'UP.Link/3.4.4', False, 'Google WAP Proxy/1.0', True, False),
    ('UP.Browser/3.04-TST4 UP.Link/3.4.5.6', '3.04', 'TST4', 'TST4', 'UP.Link/3.4.5.6', False, None, True, False),
    ('KDDI-KCU1 UP.Browser/6.2.0.5.1 (GUI) MMP/2.0', '6.2.0.5.1 (GUI)', 'KCU1', 'KCU1', 'MMP/2.0', True, None, False, True),
    ('KDDI-TS2A UP.Browser/6.2.0.9 (GUI) MMP/2.0', '6.2.0.9 (GUI)', 'TS2A', 'TS2A', 'MMP/2.0', True, None, False, True),
)
