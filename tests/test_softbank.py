# -*- coding: utf-8 -*-
from tests import msg
from uamobile import *
from uamobile.softbank import SoftBankUserAgent
from uamobile.factory.softbank import SoftBankUserAgentFactory

def test_detect_fast():
    assert detect_fast('SoftBank/1.0/816SH/SHJ001 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1') == 'softbank'

def test_msname():
    ua = detect({'HTTP_USER_AGENT'     : 'SoftBank/1.0/824SH/SHJ001 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1',
                 'HTTP_X_JPHONE_SMAF'  : '64/pcm/grf/rs',
                 'HTTP_X_JPHONE_MSNAME': '824SH',
                 })
    assert ua.msname == '824SH'

def test_smaf():
    ua = detect({'HTTP_USER_AGENT'     : 'SoftBank/1.0/824SH/SHJ001 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1',
                 'HTTP_X_JPHONE_SMAF'  : '64/pcm/grf/rs',
                 'HTTP_X_JPHONE_MSNAME': '824SH',
                 })
    assert ua.smaf == '64/pcm/grf/rs'

def test_display():
    env = {'HTTP_USER_AGENT': 'Vodafone/1.0/V904SH/SHJ003/SN000000000000000 Browser/VF-NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1',
           'HTTP_X_JPHONE_MSNAME': 'V904SH',
           'HTTP_X_JPHONE_COLOR': 'C262144',
           'HTTP_X_SSL': 'off',
           'HTTP_X_JPHONE_REGION': '44020',
           'HTTP_X_JPHONE_DISPLAY': '480*640',
           'HTTP_X_JPHONE_UID': 'xxxxxxxxxxxxxxxx',
           'HTTP_X_JPHONE_SMAF': '128/pcm/grf/rs',
           'HTTP_X_WAP_PROFILE': 'http://www.sharp-mobile.com/UAProf/V904SH_SHJ001_3g.xml'
           }
    ua = detect(env)
    assert ua.display.width == 480
    assert ua.display.height == 640
    assert ua.display.color == True
    assert ua.display.depth == 262144, "%s expected, result %r" % (262144, ua.display.color)
    assert ua.display.is_qvga() == True
    assert ua.display.is_vga() == True

def test_display_error():
    base_env = {'HTTP_USER_AGENT': 'Vodafone/1.0/V904SH/SHJ003/SN000000000000000 Browser/VF-NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1',
                'HTTP_X_JPHONE_COLOR': 'C262144',
                'HTTP_X_JPHONE_DISPLAY': '480*640'
           }

    def func(ua, width, height, color, depth):
        assert ua.display.width == width, repr(ua.display.width)
        assert ua.display.height == height
        assert ua.display.color == color
        assert ua.display.depth == depth

    # Invalid COLOR
    env = dict(base_env)
    del env['HTTP_X_JPHONE_COLOR']
    ua = detect(env)
    yield (func, ua, 480, 640, False, 0)

    env = dict(base_env)
    env['HTTP_X_JPHONE_COLOR'] = 'spam'
    ua = detect(env)
    yield (func, ua, 480, 640, False, 0)

    env = dict(base_env)
    env['HTTP_X_JPHONE_COLOR'] = ''
    ua = detect(env)
    yield (func, ua, 480, 640, False, 0)

    # Invalid DISPLAY
    env = dict(base_env)
    del env['HTTP_X_JPHONE_DISPLAY']
    ua = detect(env)
    yield (func, ua, None, None, True, 262144)

    env = dict(base_env)
    env['HTTP_X_JPHONE_DISPLAY'] = '480'
    ua = detect(env)
    yield (func, ua, None, None, True, 262144)

    env = dict(base_env)
    env['HTTP_X_JPHONE_DISPLAY'] = '480*spam'
    ua = detect(env)
    yield (func, ua, None, None, True, 262144)

def test_strip_serialnumber():
    value = 'SoftBank/1.0/816SH/SHJ001 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1'
    ua = detect({'HTTP_USER_AGENT': value})
    assert ua.strip_serialnumber() == value

    ua = detect({'HTTP_USER_AGENT':
                     'Vodafone/1.0/V904SH/SHJ003/SN000000000000000 Browser/VF-NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1'})
    res = ua.strip_serialnumber()
    assert res == 'Vodafone/1.0/V904SH/SHJ003 Browser/VF-NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1', repr(res)

def test_jphone_uid():
    useragent = 'Vodafone/1.0/V904SH/SHJ003/SN000000000000000 Browser/VF-NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1'
    ua = detect({'HTTP_USER_AGENT': useragent,
                 'HTTP_X_JPHONE_UID': 'xxxxxxxxxxxxxxxx' })
    assert ua.jphone_uid == 'xxxxxxxxxxxxxxxx'

    ua = detect({'HTTP_USER_AGENT': useragent })
    assert ua.jphone_uid is None

def test_useragent_softbank():
    def inner(useragent, version, model, packet_compliant,
              serial_number=None, vendor=None, vendor_version=None, java_infos=None):
        ua = detect({'HTTP_USER_AGENT': useragent})

        assert ua.carrier == 'SoftBank'
        assert ua.short_carrier == 'S'

        assert ua.is_docomo() == False
        assert ua.is_ezweb() == False
        assert ua.is_softbank()
        assert ua.is_vodafone()
        assert ua.is_jphone()
        assert ua.is_willcom() == False
        assert ua.is_nonmobile() == False
        assert ua.display is not None

        if serial_number:
            assert ua.serialnumber == serial_number, msg(ua, ua.serialnumber, serial_number)
            assert ua.version == version
            assert ua.model == model, msg(ua, ua.model, model)
            assert ua.packet_compliant == packet_compliant

            assert ua.vendor == vendor, msg(ua, ua.vendor, vendor)
            assert ua.vendor_version == vendor_version, msg(ua, ua.vendor_version, vendor_version)

    for args in DATA:
        yield tuple([inner] + list(args))

def test_jphone_2_0():
    ua = detect({'HTTP_USER_AGENT'      :'J-PHONE/2.0/J-DN02',
                 'HTTP_X_JPHONE_COLOR'  : 'G4',
                 'HTTP_X_JPHONE_DISPLAY': '116*112',
                 })
    assert isinstance(ua.version, basestring)
    assert not ua.is_3g(), 'Invalid generation'
    assert ua.is_type_c(), 'Invalid type %s' % ua.version
    assert not ua.is_type_p(), 'Invalid type %s'  % ua.version
    assert not ua.is_type_w(), 'Invalid type' % ua.version
    assert ua.supports_cookie() == False
    assert ua.vendor == 'DN', ua.vendor
    assert not ua.display.color
    assert ua.display.width == 116
    assert ua.display.height == 112

def test_jphone_3_0():
    ua = detect({'HTTP_USER_AGENT':'J-PHONE/3.0/J-PE03_a'})
    assert not ua.is_3g(), 'Invalid generation'
    assert ua.is_type_c(), 'Invalid type %s' % ua.version
    assert not ua.is_type_p(), 'Invalid type %s'  % ua.version
    assert not ua.is_type_w(), 'Invalid type' % ua.version
    assert ua.supports_cookie() == False
    assert ua.vendor == 'PE', ua.vendor

def test_jphone_4_0():
    ua = detect({'HTTP_USER_AGENT':'J-PHONE/4.0/J-SH51/SNJSHA3029293 SH/0001aa Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0'})
    assert not ua.is_type_c(), 'Invalid type %s' % ua.version
    assert ua.is_type_p(), 'Invalid type %s'  % ua.version
    assert not ua.is_type_w(), 'Invalid type' % ua.version
    assert ua.supports_cookie() == False
    assert ua.vendor == 'SH'

def test_jphone_5_0():
    ua = detect({'HTTP_USER_AGENT':'J-PHONE/5.0/V801SA'})
    assert not ua.is_type_c(), 'Invalid type %s' % ua.version
    assert not ua.is_type_p(), 'Invalid type %s'  % ua.version
    assert ua.is_type_w(), 'Invalid type' % ua.version
    assert ua.supports_cookie() == True
    assert ua.vendor == 'SA'

def test_vodafone_1_0():
    ua = detect({'HTTP_USER_AGENT':'Vodafone/1.0/V702NK/NKJ001 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1'})
    assert ua.is_3g(), 'Invalid generation'
    assert not ua.is_type_c(), 'Invalid type %s' % ua.version
    assert not ua.is_type_p(), 'Invalid type %s'  % ua.version
    assert not ua.is_type_w(), 'Invalid type' % ua.version
    assert ua.supports_cookie() == True

def test_yahoo_crawler():
    def func(useragent, is_3g, model, cookie):
        ua = detect({'HTTP_USER_AGENT': useragent})
        assert ua.is_softbank()
        assert ua.is_3g() == is_3g, 'Invalid generation'
        assert not ua.is_type_p(), 'Invalid type %s'  % ua.version
        assert not ua.is_type_w(), 'Invalid type' % ua.version
        assert ua.model == model
        assert ua.supports_cookie() == cookie

    for u, model, is_3g, cookie in (
        ('J-PHONE/2.0/J-SH03 (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)', False, 'J-SH03', False),
        ('Vodafone/1.0/V705SH (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)', True, 'V705SH', True),
        ):
        yield func, u, model, is_3g, cookie

def test_crawler():
    def func(useragent):
        ua = detect({'HTTP_USER_AGENT':useragent})
        assert ua.is_softbank()
    for useragent in ('Vodafone/1.0/V802SH/SHJ002 Browser/UP.Browser/7.0.2.1 (compatible; ichiro/mobile goo; +http://help.goo.ne.jp/door/crawler.html)',
                      'J-PHONE/3.0/J-SH10 (compatible; LD_mobile_bot; +http://helpguide.livedoor.com/help/search/qa/grp627)',
                      'SoftBank/1.0/913SH/SHJ001/SN000123456789000 Browser/NetFront/3.4 Profile/MIDP-2.0 (symphonybot1.froute.jp; +http://search.froute.jp/howto/crawler.html)',
                      ):
        yield func, useragent

def test_s_appli():
    ua = detect({'HTTP_USER_AGENT': 'SoftBank/1.0/831SH/SHJ001 Java/Java/1.0 Profile/MIDP-2.0 Configuration/CLDC-1.1'})
    assert ua.is_softbank()
    assert ua.is_3g()
    assert ua.model == '831SH'

def test_mobile_widget():
    ua = detect({'HTTP_USER_AGENT': 'SoftBank/1.0/831SH/SHJ001 Widgets/Widgets/1.0'})
    assert ua.is_softbank()
    assert ua.is_3g()
    assert ua.model == '831SH'

def test_flash_lite():
    ua = detect({'HTTP_USER_AGENT': 'SoftBank/1.0/831SH/SHJ001 Flash/Flash-Lite/3.0'})
    assert ua.is_softbank()
    assert ua.is_3g()
    assert ua.model == '831SH'

def test_error_agents():
    def tester(useragent):
        ua = detect({'HTTP_USER_AGENT':useragent})
        assert ua.is_softbank()

    for datum in ERRORS:
        yield tester, datum


def test_is_bogus():
    def func(ip, expected):
        ua = detect({'HTTP_USER_AGENT': 'SoftBank/1.0/705P/PJP10 Browser/Teleca-Browser/3.1 Profile/MIDP-2.0 Configuration/CLDC-1.1',
                     'REMOTE_ADDR'    : ip,
                     })
        assert ua.is_softbank()
        res = ua.is_bogus()
        assert res == expected, '%s expected, actual %s' % (expected, res)

    for ip, expected in (
        ('210.230.128.224', True),
        ('123.108.236.0', False),
        ):
        yield func, ip, expected


def test_extra_ip():
    ctxt1 = Context(extra_softbank_ips=['192.168.0.0/24'])
    ua = detect({'HTTP_USER_AGENT': 'SoftBank/1.0/816SH/SHJ001 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 },
                context=ctxt1)
    assert ua.is_softbank()
    assert ua.is_bogus() is False

    ctxt2 = Context(extra_softbank_ips=[])
    ua = detect({'HTTP_USER_AGENT': 'SoftBank/1.0/816SH/SHJ001 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 },
                context=ctxt2)
    assert ua.is_softbank()
    assert ua.is_bogus() is True


def test_my_factory():
    class MySoftBankUserAgent(SoftBankUserAgent):
        def get_my_attr(self):
            return self.environ.get('HTTP_X_DOCOMO_UID')

    class MySoftBankUserAgentFactory(SoftBankUserAgentFactory):
        device_class = MySoftBankUserAgent

    context = Context(softbank_factory=MySoftBankUserAgentFactory)
    ua = detect({'HTTP_USER_AGENT'  : 'SoftBank/1.0/812SH/SHJ001/SN333333333333333 Browser/NetFront/3.3 Profile/MIDP-2.0 Configuration/CLDC-1.1',
                 'REMOTE_ADDR'      : '192.168.0.1',
                 'HTTP_X_DOCOMO_UID': 'spam',
                 },
                context=context)
    assert ua.is_softbank()
    assert isinstance(ua, MySoftBankUserAgent)
    assert ua.get_my_attr() == 'spam'


#########################
# Test data
#########################

DATA = (
# ua, version, model, packet_compliant, serial_number, vendor, vendor_version, java_infos
    ('J-PHONE/2.0/J-DN02', '2.0', 'J-DN02', False),
    ('J-PHONE/3.0/J-PE03_a', '3.0', 'J-PE03_a', False),
    ('J-PHONE/4.0/J-SH51/SNJSHA3029293 SH/0001aa Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0', '4.0', 'J-SH51', True, 'JSHA3029293', 'SH', '0001aa', { 'Profile':'MIDP-1.0', 'Configuration':'CLDC-1.0', 'Ext-Profile':'JSCL-1.1.0' }),
    ('J-PHONE/4.0/J-SH51/SNXXXXXXXXX SH/0001a Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0', '4.0', 'J-SH51', True, 'XXXXXXXXX', 'SH', '0001a', {'Profile' : 'MIDP-1.0', 'Configuration' : 'CLDC-1.0', 'Ext-Profile' : 'JSCL-1.1.0'}),
    ('J-PHONE/5.0/V801SA SA/0001JP Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0', '5.0', 'V801SA', True),
    ('Vodafone/1.0/V702NK/NKJ001 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1', '1.0', 'V702NK', True, None, 'NK', 'NKJ001', {'Profile' : 'MIDP-1.0', 'Configuration' : 'CLDC-1.0'}),

    # TODO check whether this serial number is valid.
    ('Vodafone/1.0/V702NK/NKJ001/SN123456789012345 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1', '1.0', 'V702NK', True, '123456789012345', 'NK', 'J001', {'Profile' : 'MIDP-1.0', 'Configuration' : 'CLDC-1.0'}),

    # TODO cehck whether this serial number is valid
    ('Vodafone/1.0/V802SE/SEJ001/SN123456789012345 Browser/SEMC-Browser/4.1 Profile/MIDP-2.0 Configuration/CLDC-1.1', '1.0', 'V802SE', True, '123456789012345', 'SE', 'J001', {'Profile' : 'MIDP-2.0', 'Configuration' : 'CLDC-1.1'}),
    ('Vodafone/1.0/V902SH/SHJ001 Browser/UP.Browser/7.0.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1 Ext-J-Profile/JSCL-1.2.2 Ext-V-Profile/VSCL-2.0.0', '1.0', 'V902SH', True, None, 'SH', 'J001', {'Profile' : 'MIDP-2.0', 'Configuration' : 'CLDC-1.1'}),
    ('Vodafone/1.0/V802N/NJ001 Browser/UP.Browser/7.0.2.1.258 Profile/MIDP-2.0 Configuration/CLDC-1.1 Ext-J-Profile/JSCL-1.2.2 Ext-V-Profile/VSCL-2.0.0', '1.0', 'V802N', True, None, 'N', 'J001', {'Profile' : 'MIDP-2.0', 'Configuration' : 'CLDC-1.1'}),
    ('MOT-V980/80.2F.2E. MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1', '', 'V980', True, None, 'MOT', '80.2F.2E.', {'Profile' : 'MIDP-2.0', 'Configuration' : 'CLDC-1.1'}),
    ('J-PHONE/3.0/V301SH', '3.0', 'V301SH', False),
    ('J-PHONE/3.0/V301T', '3.0', 'V301T', False),
    ('SoftBank/1.0/705P/PJP10 Browser/Teleca-Browser/3.1 Profile/MIDP-2.0 Configuration/CLDC-1.1', '1.0', '705P', True, None, 'P', 'JP10', {'Profile' : 'MIDP-2.0', 'Configuration' : 'CLDC-1.1'}),
    ('SoftBank/1.0/DM001SH/SHJ001/SN123456789012345 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1', '1.0', 'DM001SH', True, '123456789012345', 'SH', 'J001', {'Profile': 'MIDP-2.0', 'Configuration': 'CLDC-1.1'}),
)

ERRORS = ('J-PHONE/4.0/J-SH51_a/ZNJSHA5081372 SH/0001aa Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0',
          #'Vodafone/1.0/V702NK',
          'Vodafone/1.0/V702NK/NKJ001/123456789012345 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1',
          )
