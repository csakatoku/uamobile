# -*- coding: utf-8 -*-
from tests import msg, MockWSGIEnviron as Environ
from uamobile import detect, EZweb

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

        assert ua.is_cookie_available() == True
        
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
