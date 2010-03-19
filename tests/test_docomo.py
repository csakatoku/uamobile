# -*- coding: utf-8 -*-
from tests import msg
from uamobile import *
from uamobile.docomo import DoCoMoUserAgent
from uamobile.factory.docomo import DoCoMoUserAgentFactory

def test_detect_fast():
    assert detect_fast('DoCoMo/2.0 SH01A(c100;TB;W24H16)') == 'docomo'

def test_useragent_docomo():
    def inner(useragent, version, html_version, model, cache_size,
              is_foma, vendor, series, options=None, display=None, supports_cookie=False):

        ua = detect({'HTTP_USER_AGENT':useragent})
        assert ua.is_docomo()
        assert ua.is_ezweb() == False
        assert ua.is_softbank() == False
        assert ua.is_vodafone() == False
        assert ua.is_jphone() == False
        assert ua.is_willcom() == False
        assert ua.is_nonmobile() == False, ua

        assert ua.version == version
        assert ua.model == model, (ua, model)
        assert ua.html_version == html_version, msg(ua, ua.html_version, html_version)
        assert ua.cache_size == cache_size, (ua, cache_size)
        assert ua.is_foma() == is_foma, (ua, is_foma)
        assert ua.vendor == vendor, (ua, vendor)
        assert ua.series == series, msg(ua, ua.series, series)
        assert ua.display is not None
        if display:
            assert (ua.display.width, ua.display.height) == display, (ua.display.width, ua.display.height)
        assert ua.supports_cookie() == supports_cookie

        if options:
            for k, v in options.items():
                if k == 'status':
                    assert ua.status == v, msg(ua, ua.status, v)
                elif k == 'serial_number':
                    assert ua.serialnumber == v, msg(ua, ua.serialnumber, v)
                elif k == 'card_id':
                    assert ua.card_id == v, msg(ua, ua.card_id, v)
                elif k == 'bandwidth':
                    assert ua.bandwidth == v, msg(ua, ua.bandwidth, v)
                elif k == 'comment':
                    assert ua.comment == v, msg(ua, ua.comment, v)
                elif k == 'is_gps':
                    assert ua.is_gps() == v, msg(ua, ua.is_gps(), v)

    for args in DATA:
        yield tuple([inner] + list(args))

def test_ue_version():
    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 SH905i(c100;TB;W24H16)'})
    assert ua.is_docomo()
    assert ua.ue_version is None

    ua = detect({'HTTP_USER_AGENT'  : 'DoCoMo/2.0 F08A3(c500;TB;W24H16)',
                 'HTTP_X_UE_VERSION': '2'})
    assert ua.is_docomo()
    assert ua.ue_version == '2'

def test_display_default():
    # the following User-Agent doesn't exist at least in spring 2009
    ua = detect({'HTTP_USER_AGENT':'DoCoMo/2.0 SH99A(c100;TB;W24H16)'})
    assert ua.display.width != 0
    assert ua.display.height != 0
    assert ua.display.color
    assert ua.display.depth
    assert ua.display.is_vga() is False
    assert ua.display.is_qvga() is True

def test_display_bytes():
    ua = detect({'HTTP_USER_AGENT':'DoCoMo/1.0/F505i/c20/TB/W20H10'})
    assert ua.display.width_bytes == 20
    assert ua.display.height_bytes == 10

    ua = detect({'HTTP_USER_AGENT':'DoCoMo/2.0 SO905i(c100;TB;W24H18)'})
    assert ua.display.width_bytes == 24
    assert ua.display.height_bytes == 18

def test_guid():
    ua = detect({'HTTP_USER_AGENT':'DoCoMo/2.0 SO905i(c100;TB;W24H18)', 'HTTP_X_DCMGUID':'FFFFFFF'})
    assert ua.guid == 'FFFFFFF'

    ua = detect({'HTTP_USER_AGENT':'DoCoMo/2.0 SO905i(c100;TB;W24H18)'})
    assert ua.guid is None

def test_strip_serialnumber():
    value = 'DoCoMo/2.0 N904i(c100;TB;W24H16)'
    ua = detect({'HTTP_USER_AGENT': value})
    assert ua.strip_serialnumber() == value

    value = 'DoCoMo/1.0/SO213i/c10/TB/serSSSSS555555'
    ua = detect({'HTTP_USER_AGENT': value})
    assert ua.strip_serialnumber() == 'DoCoMo/1.0/SO213i/c10/TB'

    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 N702iD(c100;TB;W24H12;ser356623000314657;icc8981100000327921096F)'})
    assert ua.strip_serialnumber() == 'DoCoMo/2.0 N702iD(c100;TB;W24H12)', repr(ua.strip_serialnumber())

    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 N702iD(c100;ser356623000314657;TB;icc8981100000327921096F;W24H12)'})
    assert ua.strip_serialnumber() == 'DoCoMo/2.0 N702iD(c100;TB;W24H12)', repr(ua.strip_serialnumber())

    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 N702iD(icc8981100000327921096F;c100;TB;W24H12;ser356623000314657)'})
    assert ua.strip_serialnumber() == 'DoCoMo/2.0 N702iD(c100;TB;W24H12)', repr(ua.strip_serialnumber())

def test_not_matching_error():
    def func(ua):
        device = detect({'HTTP_USER_AGENT': ua})
        assert device.is_docomo()

    # No parenthis
    yield (func, 'DoCoMo/2.0 SO905i(c100;TB;W24H18')

    # invalid comment
    ua = detect({'HTTP_USER_AGENT':'DoCoMo/2.0 SO905i()'})
    assert ua.is_docomo()
    assert ua.serialnumber is None
    assert ua.card_id is None

    ua = detect({'HTTP_USER_AGENT':'DoCoMo/2.0 N902iS(ser0123456789abcdf;)'})
    assert ua.is_docomo()
    assert ua.serialnumber is not None
    assert ua.card_id is None

    # Invalid Cache Size
    yield (func, 'DoCoMo/1.0/F505i/ca/TB/W20H10')
    yield (func, 'DoCoMo/2.0 SO905i(ca;TB;W24H18')

    # Invalid State
    yield (func, 'DoCoMo/2.0 SO905i(c100;XX;W24H18')

    # Invalid Display width
    yield (func, 'DoCoMo/2.0 SO905i(c100;XX;WspamHegg')

    # Invalid serial number
    ua = detect({'HTTP_USER_AGENT':'DoCoMo/2.0 N902iS(c100;TB;W24H12;ser0123456789abcd;icc8888888888888888888F)'})
    assert ua.is_docomo()
    assert ua.serialnumber is None
    assert ua.card_id is not None

    # Invalid card id
    ua = detect({'HTTP_USER_AGENT':'DoCoMo/2.0 N902iS(c100;TB;W24H12;ser0123456789abcdf;icc8888888888888888888)'})
    assert ua.is_docomo()
    assert ua.serialnumber is not None
    assert ua.card_id is None

    # Is this OK???
    detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 SO905i(c100;TB)'})
    detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 SO905i(c100)'})

    # This is OK
    detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 N902iS(c100;TB;W24H12;ser0123456789abcdf;icc8888888888888888888F)'})

    # This useragent does not exist in the real world, pass our test
    detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 N902iS(ser0123456789abcdf;icc8888888888888888888F;c100;TB;W24H12)'})
    detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 N902iS(ser0123456789abcdf;icc8888888888888888888F;c100)'})
    detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 N902iS(ser0123456789abcdf;icc8888888888888888888F)'})
    detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 N902iS(ser0123456789abcdf)'})

def test_crawler():
    def func(agent):
        ua = detect({'HTTP_USER_AGENT':agent})
        assert ua.is_docomo()

    data = ('DoCoMo/2.0 N902iS(c100;TB;W24H12)(compatible; moba-crawler; http://crawler.dena.jp/)',
            'DoCoMo/2.0 SH902i (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)'
            'DoCoMo/2.0 P900i(c100;TB;W24H11)(compatible; ichiro/mobile goo; +http://help.goo.ne.jp/door/crawler.html)',
            'DoCoMo/1.0/N505i/c20/TB/W20H10 (compatible; LD_mobile_bot; +http://helpguide.livedoor.com/help/search/qa/grp627)',
            'DoCoMo/2.0 SO902i(c100;TB;W20H10) (symphonybot1.froute.jp; +http://search.froute.jp/howto/crawler.html)',
            )
    for agent in data:
        yield (func, agent)

def test_is_bogus():
    context = Context(proxy_ips='127.0.0.1')
    def func(remote_addr, forwarded_for, expected):
        ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                     'REMOTE_ADDR' : ip,
                     'HTTP_X_FORWARDED_FOR': forwarded_for,
                     },
                    context=context)
        assert ua.is_docomo()
        res = ua.is_bogus()
        assert res == expected, '%s expected, actual %s' % (expected, res)

    for ip, expected in (
        ('210.153.84.0', False),
        ('210.230.128.224', True),
        ):
        yield func, ip, None, expected

    for ip, f, expected in (
        # untrusted proxy address
        ('192.168.0.1', '210.153.84.0', True),
        ('192.168.0.1', '210.230.128.224', True),
        ):
        yield func, ip, f, expected

    for ip, f, expected in (
        ('127.0.0.1', '210.153.84.0', False),
        ('127.0.0.1', '210.230.128.224', True),

        ('127.0.0.1', '210.153.84.0, 192.168.0.2', False),
        ('127.0.0.1', '210.230.128.224, 192.168.0.2', True),
        ):
        yield func, ip, f, expected


def test_is_bogus_multiple_proxies():
    context = Context(proxy_ips=['192.168.0.0/24', '192.168.1.0/24'])
    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 'HTTP_X_FORWARDED_FOR': '210.153.84.0',
                 },
                context=context)
    assert ua.is_docomo()
    assert ua.is_bogus() is False

    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                 'REMOTE_ADDR'    : '192.168.1.1',
                 'HTTP_X_FORWARDED_FOR': '210.153.84.0',
                 },
                context=context)
    assert ua.is_docomo()
    assert ua.is_bogus() is False

    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                 'REMOTE_ADDR'    : '192.168.2.1',
                 'HTTP_X_FORWARDED_FOR': '210.153.84.0',
                 },
                context=context)
    assert ua.is_docomo()
    assert ua.is_bogus() is True


def test_is_bogus_error():
    context = Context(proxy_ips=['127.0.0.1'])
    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                 'REMOTE_ADDR'    : 'unknown',
                 },
                context=context)
    assert ua.is_docomo()
    assert ua.is_bogus()

    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                 'REMOTE_ADDR'    : '127.0.0.1',
                 'HTTP_X_FORWARDED_FOR': 'unknown,210.153.84.0',
                 },
                context=context)
    assert ua.is_docomo()
    assert ua.is_bogus()

def test_extra_ip():
    ctxt1 = Context(extra_docomo_ips=['192.168.0.0/24'])
    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 },
                context=ctxt1)
    assert ua.is_docomo()
    assert ua.is_bogus() is False

    ctxt2 = Context(extra_docomo_ips=[])
    ua = detect({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                 'REMOTE_ADDR'    : '192.168.0.1',
                 },
                context=ctxt2)
    assert ua.is_docomo()
    assert ua.is_bogus() is True


def test_my_factory():
    class MyDoCoMoUserAgent(DoCoMoUserAgent):
        def get_uid(self):
            return self.environ.get('HTTP_X_DOCOMO_UID')

    class MyDoCoMoUserAgentFactory(DoCoMoUserAgentFactory):
        device_class = MyDoCoMoUserAgent

    context = Context(docomo_factory=MyDoCoMoUserAgentFactory)
    ua = detect({'HTTP_USER_AGENT'  : 'DoCoMo/2.0 P01A(c100;TB;W24H15)',
                 'REMOTE_ADDR'      : '192.168.0.1',
                 'HTTP_X_DOCOMO_UID': 'spam',
                 },
                context=context)
    assert ua.is_docomo()
    assert isinstance(ua, MyDoCoMoUserAgent)
    assert ua.get_uid() == 'spam'


#########################
# Test data
#########################

DATA = (
# ua, version, html_version, model, cache_size, is_foma, vendor, series, options
('DoCoMo/1.0/D501i', '1.0', '1.0', 'D501i', 5, False, 'D', '501i'),
('DoCoMo/1.0/D502i', '1.0', '2.0', 'D502i', 5, False, 'D', '502i'),
('DoCoMo/1.0/D502i/c10', '1.0', '2.0', 'D502i', 10, False, 'D', '502i'),
('DoCoMo/1.0/D210i/c10', '1.0', '3.0', 'D210i', 10, False, 'D', '210i'),
('DoCoMo/1.0/SO503i/c10', '1.0', '3.0', 'SO503i', 10, False, 'SO', '503i'),
('DoCoMo/1.0/D211i/c10', '1.0', '3.0', 'D211i', 10, False, 'D', '211i'),
('DoCoMo/1.0/SH251i/c10', '1.0', '3.0', 'SH251i', 10, False, 'SH', '251i'),
('DoCoMo/1.0/R692i/c10', '1.0', '3.0', 'R692i', 10, False, 'R', '692i'),
('DoCoMo/2.0 P2101V(c100)', '2.0', '3.0', 'P2101V', 100, True, 'P', 'FOMA'),
('DoCoMo/2.0 N2001(c10)', '2.0', '3.0', 'N2001', 10, True, 'N', 'FOMA'),
               ('DoCoMo/2.0 N2002(c100)', '2.0', '3.0', 'N2002', 100, True, 'N', 'FOMA'),
               ('DoCoMo/2.0 D2101V(c100)', '2.0', '3.0', 'D2101V', 100, True, 'D', 'FOMA'),
               ('DoCoMo/2.0 P2002(c100)', '2.0', '3.0', 'P2002', 100, True, 'P', 'FOMA'),
               ('DoCoMo/2.0 MST_v_SH2101V(c100)', '2.0', '3.0', 'SH2101V', 100, True, 'SH', 'FOMA'),
               ('DoCoMo/2.0 T2101V(c100)', '2.0', '3.0', 'T2101V', 100, True, 'T', 'FOMA'),
               ('DoCoMo/1.0/D504i/c10', '1.0', '4.0', 'D504i', 10, False, 'D', '504i'),
               ('DoCoMo/1.0/D504i/c30/TD', '1.0', '4.0', 'D504i', 30, False, 'D', '504i', { 'status':'TD' }),
               ('DoCoMo/1.0/D504i/c10/TJ', '1.0', '4.0', 'D504i', 10, False, 'D', '504i', { 'status':'TJ' }),
               ('DoCoMo/1.0/F504i/c10/TB', '1.0', '4.0', 'F504i', 10, False, 'F', '504i', { 'status':'TB' }),
               ('DoCoMo/1.0/D251i/c10', '1.0', '4.0', 'D251i', 10, False, 'D', '251i'),
               ('DoCoMo/1.0/F251i/c10/TB', '1.0', '4.0', 'F251i', 10, False, 'F', '251i', { 'status':'TB' }),
               ('DoCoMo/1.0/F671iS/c10/TB', '1.0', '4.0', 'F671iS', 10, False, 'F', '671i', {'status':'TB'}),
('DoCoMo/1.0/P503i/c10/serNMABH200331', '1.0', '3.0', 'P503i', 10, False, 'P', '503i', {'serial_number':'NMABH200331' }),
('DoCoMo/2.0 N2001(c10;ser0123456789abcde;icc01234567890123456789)', '2.0', '3.0', 'N2001', 10, 1, 'N', 'FOMA', {'serial_number':'0123456789abcde', 'card_id' :'01234567890123456789'}),
               ('DoCoMo/1.0/eggy/c300/s32/kPHS-K', '1.0', '3.2', 'eggy', 300, False, None, None, {'bandwidth' : 32 }),
               ('DoCoMo/1.0/P751v/c100/s64/kPHS-K', '1.0', '3.2', 'P751v', 100, False, 'P', None, {'bandwidth' :64}),
               ('DoCoMo/1.0/P209is (Google CHTML Proxy/1.0)', '1.0', '2.0', 'P209is', 5, False, 'P', '209i', {'comment' :'Google CHTML Proxy/1.0'}),
               ('DoCoMo/1.0/F212i/c10/TB', '1.0', '4.0', 'F212i', 10, False, 'F', '212i', { 'status':'TB' }),
               ('DoCoMo/2.0 F2051(c100;TB)', '2.0', '4.0', 'F2051', 100, True, 'F', 'FOMA', { 'status':'TB' }),
               ('DoCoMo/2.0 N2051(c100;TB)', '2.0', '4.0', 'N2051', 100, True, 'N', 'FOMA', { 'status':'TB' }),
               ('DoCoMo/2.0 P2102V(c100;TB)', '2.0', '4.0', 'P2102V', 100, True, 'P', 'FOMA', { 'status':'TB' }),
               ('DoCoMo/1.0/N211iS/c10', '1.0', '3.0', 'N211iS', 10, False, 'N', '211i'),
               ('DoCoMo/1.0/P211iS/c10', '1.0', '3.0', 'P211iS', 10, False, 'P', '211i'),
               ('DoCoMo/1.0/N251iS/c10/TB', '1.0', '4.0', 'N251iS', 10, False, 'N', '251i', { 'status':'TB' }),
               ('DoCoMo/1.0/F661i/c10/TB', '1.0', '4.0', 'F661i', 10, False, 'F', '661i', {'status' :'TB', 'is_gps' :True}),
               ('DoCoMo/1.0/D505i/c20/TC/W20H10', '1.0', '5.0', 'D505i', 20, False, 'D', '505i', { 'status':'TC' }),
               ('DoCoMo/1.0/SO505i/c20/TB/W21H09', '1.0', '5.0', 'SO505i', 20, False, 'SO', '505i', { 'status':'TB' }),
               ('DoCoMo/2.0 N2701(c100;TB)', '2.0', '4.0', 'N2701', 100, True, 'N', 'FOMA', { 'status':'TB' }),
               ('DoCoMo/1.0/SH505i/c20/TB/W24H12', '1.0', '5.0', 'SH505i', 20, False, 'SH', '505i', { 'status':'TB' }),
               ('DoCoMo/1.0/N505i/c20/TB/W20H10', '1.0', '5.0', 'N505i', 20, False, 'N', '505i', { 'status':'TB' }),
('DoCoMo/2.0 F2102V(c100;TB)', '2.0', '4.0', 'F2102V', 100, True, 'F', 'FOMA', { 'status':'TB' }),
('DoCoMo/2.0 N2102V(c100;TB)', '2.0', '4.0', 'N2102V', 100, True, 'N', 'FOMA', { 'status':'TB' }),
('DoCoMo/1.0/F505i/c20/TB/W20H10', '1.0', '5.0', 'F505i', 20, False, 'F', '505i', { 'status':'TB' }),
('DoCoMo/1.0/P505i/c20/TB/W20H10', '1.0', '5.0', 'P505i', 20, False, 'P', '505i', { 'status':'TB' }),
('DoCoMo/1.0/F672i/c10/TB', '1.0', '4.0', 'F672i', 10, False, 'F', '672i', { 'status':'TB' }),
('DoCoMo/1.0/SH505i2/c20/TB/W24H12', '1.0', '5.0', 'SH505i', 20, False, 'SH', '505i', { 'status':'TB' }),
               ('DoCoMo/1.0/D252i/c10/TB/W25H12', '1.0', '5.0', 'D252i', 10, False, 'D', '252i', { 'status':'TB' }),
               ('DoCoMo/1.0/SH252i/c20/TB/W24H12', '1.0', '5.0', 'SH252i', 20, False, 'SH', '252i', { 'status':'TB' }),
               ('DoCoMo/1.0/D505iS/c20/TB/W20H10', '1.0', '5.0', 'D505iS', 20, False, 'D', '505i', { 'status':'TB' }),
('DoCoMo/1.0/P505iS/c20/TB/W20H10', '1.0', '5.0', 'P505iS', 20, False, 'P', '505i', { 'status':'TB' }),
('DoCoMo/1.0/P252i/c10/TB/W22H10', '1.0', '5.0', 'P252i', 10, False, 'P', '252i', { 'status':'TB' }),
('DoCoMo/1.0/N252i/c10/TB/W22H10', '1.0', '5.0', 'N252i', 10, False, 'N', '252i', { 'status':'TB' }),
('DoCoMo/1.0/N505iS/c20/TB/W20H10', '1.0', '5.0', 'N505iS', 20, False, 'N', '505i', { 'status':'TB' }),
('DoCoMo/1.0/SO505iS/c20/TB/W20H10', '1.0', '5.0', 'SO505iS', 20, False, 'SO', '505i', { 'status':'TB' }),
('DoCoMo/1.0/SH505iS/c20/TB/W24H12', '1.0', '5.0', 'SH505iS', 20, False, 'SH', '505i', { 'status':'TB' }),
('DoCoMo/1.0/F505iGPS/c20/TB/W20H10', '1.0', '5.0', 'F505iGPS', 20, False, 'F', '505i', { 'status':'TB' }),
('DoCoMo/2.0 F900i(c100;TB;W22H12)', '2.0', '5.0', 'F900i', 100, True, 'F', '900i', { 'status':'TB' }),
('DoCoMo/2.0 N900i(c100;TB;W24H12)', '2.0', '5.0', 'N900i', 100, True, 'N', '900i', { 'status':'TB' }),
('DoCoMo/2.0 P900i(c100;TB;W24H11)', '2.0', '5.0', 'P900i', 100, True, 'P', '900i', { 'status':'TB' }),
('DoCoMo/2.0 SH900i(c100;TB;W24H12)', '2.0', '5.0', 'SH900i', 100, True, 'SH', '900i', { 'status':'TB' }),
('DoCoMo/1.0/D506i/c20/TB/W20H10', '1.0', '5.0', 'D506i', 20, False, 'D', '506i', { 'status':'TB' }),
('DoCoMo/1.0/P651ps', '1.0', '2.0', 'P651ps', 5, False, 'P', '651'),
('DoCoMo/1.0/SO213i/c10/TB', '1.0', '4.0', 'SO213i', 10, False, 'SO', '213i', { 'status':'TB' }),
('DoCoMo/2.0 F880iES(c100;TB;W20H08)', '2.0', '5.0', 'F880iES', 100, True, 'F', '880i', { 'status':'TB' }),
('DoCoMo/1.0/SO213iS/c10/TB', '1.0', '4.0', 'SO213iS', 10, False, 'SO', '213i', { 'status':'TB' }),
('DoCoMo/1.0/P253i/c10/TB/W22H10', '1.0', '5.0', 'P253i', 10, False, 'P', '253i', { 'status':'TB' }),
('DoCoMo/1.0/P213i/c10/TB/W22H10', '1.0', '5.0', 'P213i', 10, False, 'P', '213i', { 'status':'TB' }),
('DoCoMo/2.0 N900iG(c100;TB;W24H12)', '2.0', '5.0', 'N900iG', 100, True, 'N', '900i', { 'status':'TB' }, (240, 269)),
('DoCoMo/2.0 F901iC(c100;TB;W23H12)', '2.0', '5.0', 'F901iC', 100, True, 'F', '901i', { 'status':'TB' }, (230, 240)),
('DoCoMo/1.0/SO506iS/c20/TB/W20H10', '1.0', '5.0', 'SO506iS', 20, False, 'SO', '506i', { 'status':'TB' }, (240, 256)),
('DoCoMo/2.0 SH901iS(c100;TB;W24H12)', '2.0', '5.0', 'SH901iS', 100, True, 'SH', '901i', { 'status':'TB' }, (240, 252)),
('DoCoMo/2.0 F901iS(c100;TB;W23H12)', '2.0', '5.0', 'F901iS', 100, True, 'F', '901i', { 'status':'TB' }, (230, 240)),
('DoCoMo/2.0 D901iS(c100;TB;W23H12)', '2.0', '5.0', 'D901iS', 100, True, 'D', '901i', { 'status':'TB' }, (230, 240)),
('DoCoMo/2.0 P901iS(c100;TB;W24H12)', '2.0', '5.0', 'P901iS', 100, True, 'P', '901i', { 'status':'TB' }, (240, 270)),
('DoCoMo/2.0 N901iS(c100;TB;W24H12)', '2.0', '5.0', 'N901iS', 100, True, 'N', '901i', { 'status':'TB' }, (240, 270)),
('DoCoMo/2.0 SH851i(c100;TB;W24H12)', '2.0', '5.0', 'SH851i', 100, True, 'SH', '851i', { 'status':'TB' }, (240, 252)),
('DoCoMo/1.0/SO213iWR/c10/TB', '1.0', '4.0', 'SO213iWR', 10, False, 'SO', '213i', { 'status':'TB' }, (120, 112)),
('DoCoMo/2.0 SA700iS(c100;TB;W24H12)', '2.0', '5.0', 'SA700iS', 100, True, 'SA', '700i', { 'status':'TB' }, (240, 252)),
('DoCoMo/2.0 P851i(c100;TB;W24H12)', '2.0', '5.0', 'P851i', 100, True, 'P', '851i', { 'status':'TB' }, (240, 270)),
('DoCoMo/2.0 D701iWM(c100;TB;W23H12)', '2.0', '5.0', 'D701iWM', 100, True, 'D', '701i', { 'status':'TB' }, (230, 240)),
('DoCoMo/2.0 SH902i(c100;TB;W24H12)', '2.0', '6.0', 'SH902i', 100, True, 'SH', '902i', { 'status':'TB' }, (240, 240)),
('DoCoMo/2.0 NM850iG(c100;TB;W22H10)', '2.0', '4.0', 'NM850iG', 100, True, 'NM', '850i', { 'status':'TB' }, (176, 144)),
('DoCoMo/2.0 N703imyu(c100;TB;W24H12)', '2.0', '7.0', 'N703imyu', 100, True, 'N', '703i', { 'status':'TB' }, (240, 270)),
('DoCoMo/2.0 P703imyu(c100;TB;W24H12)', '2.0', '6.0', 'P703imyu', 100, True, 'P', '703i', { 'status':'TB' }, (240, 270)),
('DoCoMo/2.0 SH904i(c100;TB;W24H16)', '2.0', '7.0', 'SH904i', 100, True, 'SH', '904i', { 'status':'TB' }, (240, 320)),
('DoCoMo/2.0 N904i(c100;TB;W30H20)', '2.0', '7.0', 'N904i', 100, True, 'N', '904i', { 'status':'TB' }, (240, 352)),
('DoCoMo/2.0 N704imyu(c100;TB;W24H12)', '2.0', '7.0', 'N704imyu', 100, True, 'N', '704i', { 'status':'TB' }, (240, 270)),
('DoCoMo/2.0 SH905i(c100;TB;W24H16)', '2.0', '7.1', 'SH905i', 100, True, 'SH', '905i', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 D905i(c100;TB;W24H17)', '2.0', '7.1', 'D905i', 100, True, 'D', '905i', {'status':'TB'}, (240, 352)),
('DoCoMo/2.0 N905i(c100;TB;W24H16)', '2.0', '7.1', 'N905i', 100, True, 'N', '905i', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 P905i(c100;TB;W24H15)', '2.0', '7.1', 'P905i', 100, True, 'P', '905i', {'status':'TB'}, (240, 350)),
('DoCoMo/2.0 F905i(c100;TB;W24H17)', '2.0', '7.1', 'F905i', 100, True, 'F', '905i', {'status':'TB'}, (240, 352)),
('DoCoMo/2.0 SO905i(c100;TB;W24H18)', '2.0', '7.1', 'SO905i', 100, True, 'SO', '905i', {'status':'TB'}, (240, 368)),
('DoCoMo/2.0 N905imyu(c100;TB;W24H16)', '2.0', '7.1', 'N905imyu', 100, True, 'N', '905i', {'status':'TB'}, (240, 320)),

# Added 2008/2/27
('DoCoMo/2.0 SO905iCS(c100;TB;W24H18)', '2.0', '7.1', 'SO905iCS', 100, True, 'SO', '905i', {'status':'TB'}, (240, 368)),
('DoCoMo/2.0 F905iBiz(c100;TB;W24H17)', '2.0', '7.1', 'F905iBiz', 100, True, 'F', '905i', {'status':'TB'}, (240, 352)),

('DoCoMo/2.0 P705i(c100;TB;W24H15)', '2.0', '7.1', 'P705i', 100, True, 'P', '705i', {'status':'TB'}, (240, 350)),
('DoCoMo/2.0 P705imyu(c100;TB;W24H15)', '2.0', '7.1', 'P705imyu', 100, True, 'P', '705i', {'status':'TB'}, (240, 350)),
('DoCoMo/2.0 N705i(c100;TB;W24H16)', '2.0', '7.1', 'N705i', 100, True, 'N', '705i', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 N705imyu(c100;TB;W24H16)', '2.0', '7.1', 'N705imyu', 100, True, 'N', '705i', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 SO705i(c100;TB;W24H16)', '2.0', '7.1', 'SO705i', 100, True, 'SO', '705i', {'status':'TB'}, (240, 320)),

# Added 2008/5/28
('DoCoMo/2.0 P906i(c100;TB;W24H15)', '2.0', '7.2', 'P906i', 100, True, 'P', '906i', {'status':'TB'}, (240, 350)),
('DoCoMo/2.0 SO906i(c100;TB;W24H18)', '2.0', '7.2', 'SO906i', 100, True, 'SO', '906i', {'status':'TB'}, (240, 368)),
('DoCoMo/2.0 SH906i(c100;TB;W24H16)', '2.0', '7.2', 'SH906i', 100, True, 'SH', '906i', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 N906imyu(c100;TB;W24H16)', '2.0', '7.2', 'N906imyu', 100, True, 'N', '906i', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 F906i(c100;TB;W24H17)', '2.0', '7.2', 'F906i', 100, True, 'F', '906i', {'status':'TB'}, (240, 352)),

# Added 2008/11/8
('DoCoMo/2.0 F01A(c100;TB;W24H17)', '2.0', '7.2', 'F01A', 100, True, 'F', '01A', {'status':'TB'}, (240, 352)),
('DoCoMo/2.0 P01A(c100;TB;W24H15)', '2.0', '7.2', 'P01A', 100, True, 'P', '01A', {'status':'TB'}, (240, 350)),
('DoCoMo/2.0 N01A(c100;TB;W24H16)', '2.0', '7.2', 'N01A', 100, True, 'N', '01A', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 N02A(c100;TB;W24H16)', '2.0', '7.2', 'N02A', 100, True, 'N', '02A', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 N03A(c100;TB;W24H16)', '2.0', '7.2', 'N03A', 100, True, 'N', '03A', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 SH01A(c100;TB;W24H16)', '2.0', '7.2', 'SH01A', 100, True, 'SH', '01A', {'status':'TB'}, (240, 320)),

# Added 2009/5/21
('DoCoMo/2.0 P02A(c100;TB;W24H15)', '2.0', '7.2', 'P02A', 100, True, 'P', '02A', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 P03A(c100;TB;W24H15)', '2.0', '7.2', 'P03A', 100, True, 'P', '03A', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 P04A(c100;TB;W24H15)', '2.0', '7.2', 'P04A', 100, True, 'P', '04A', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 P05A(c100;TB;W24H15)', '2.0', '7.2', 'P05A', 100, True, 'P', '05A', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 P06A(c100;TB;W20H13)', '2.0', '7.2', 'P06A', 100, True, 'P', '06A', {'status':'TB'}, (240, 320)),
('DoCoMo/2.0 P07A(c500;TB;W24H15)', '2.0', '7.2', 'P07A', 500, True, 'P', '07A', {'status':'TB'}, (240, 320), True),
('DoCoMo/2.0 N06A(c500;TB;W24H16)', '2.0', '7.2', 'N06A', 500, True, 'N', '06A', {'status':'TB'}, (240, 320), True),

# Added 2009/5/26
('DoCoMo/2.0 N06A2(c500;TB;W24H16)', '2.0', '7.2', 'N06A2', 500, True, 'N', '06A2', {'status':'TB'}, (240, 320), True),

# Added 2009/5/27
('DoCoMo/2.0 N06A3(c500;TB;W24H16)', '2.0', '7.2', 'N06A3', 500, True, 'N', '06A3', {'status':'TB'}, (240, 320), True),
('DoCoMo/2.0 P07A3(c500;TB;W24H15)', '2.0', '7.2', 'P07A3', 500, True, 'P', '07A3', {'status':'TB'}, (240, 320), True),

# Added 2009/6/5
('DoCoMo/2.0 F09A3(c500;TB;W24H16)', '2.0', '7.2', 'F09A3', 500, True, 'F', '09A3', {'status':'TB'}, (240, 320), True),

# Added 2009/6/18
('DoCoMo/2.0 SH05A3(c500;TB;W24H14)', '2.0', '7.2', 'SH05A3', 500, True, 'SH', '05A3', {'status':'TB'}, (240, 320), True),
('DoCoMo/2.0 SH06A3(c500;TB;W24H14)', '2.0', '7.2', 'SH06A3', 500, True, 'SH', '06A3', {'status':'TB'}, (240, 320), True),

# Added 2009/7/2
('DoCoMo/2.0 P10A(c100;TB;W24H15)', '2.0', '7.2', 'P10A', 100, True, 'P', '10A', {'status':'TB'}, (240, 320), False),
)
