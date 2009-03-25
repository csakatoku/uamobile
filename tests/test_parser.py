# -*- coding: utf-8 -*-
from uamobile import parser

DOCOMO = (
    ('DoCoMo/1.0/R692i/c10',
     { 'version': '1.0',
       'model'  : 'R692i',
       'c'      : 10,
       'series' : '692i',
       'html_version': '3.0',
      }),

    ('DoCoMo/1.0/P209is (Google CHTML Proxy/1.0)',
     { 'version': '1.0',
       'model'  : 'P209is',
       'series' : '209i',
       'html_version': '2.0',
       }),

    ('DoCoMo/2.0 N2001(c10;ser0123456789abcde;icc01234567890123456789)',
     { 'version': '2.0',
       'model'  : 'N2001',
       'c': 10,
       'ser'    : '0123456789abcde',
       'icc'    : '01234567890123456789',
       'series' : 'FOMA',
       'html_version': '3.0',
       },
     ),

    ('DoCoMo/2.0 P703i(c100;TB;W24H12;ser0123456789abcdf;icc01234567890123456789)',
     { 'version': '2.0',
       'model'  : 'P703i',
       'c': 100,
       'status' : 'TB',
       'ser'    : '0123456789abcdf',
       'icc'    : '01234567890123456789',
       'display_bytes': (24, 12),
       'series' : '703i',
       'html_version': '7.0',
       },
     ),

    ('DoCoMo/2.0 N902iS(c100;TB;W24H12)(compatible; moba-crawler; http://crawler.dena.jp/)',
     { 'version': '2.0',
       'model'  : 'N902iS',
       'c': 100,
       'status' : 'TB',
       'display_bytes': (24, 12),
       'series' : '902i',
       'html_version': '6.0',
       },
     ),
)

EZWEB = (
    ('KDDI-TS21 UP.Browser/6.0.2.276 (GUI) MMP/1.1',
     { 'xhtml_compliant': True,
       'device_id'      : 'TS21',
       'name'           : 'UP.Browser',
       'version'        : '6.0.2.276 (GUI)',
       'server'         : 'MMP/1.1',
       },
     ),
    ('KDDI-TS3A UP.Browser/6.2.0.11.2.1 (GUI) MMP/2.0, Mozilla/4.08 (MobilePhone; NMCS/3.3) NetFront/3.3',
     { 'xhtml_compliant': True,
       'device_id'      : 'TS3A',
       'name'           : 'UP.Browser',
       'version'        : '6.2.0.11.2.1 (GUI)',
       'server'         : 'MMP/2.0',
       },
     ),
    ('UP.Browser/3.01-HI01 UP.Link/3.4.5.2',
     { 'xhtml_compliant': False,
       'device_id'      : 'HI01',
       'name'           : 'UP.Browser',
       'version'        : '3.01',
       'server'         : 'UP.Link/3.4.5.2',
       }),
)

SOFTBANK = (
    ('Vodafone/1.0/V705SH (compatible; Y!J-SRD/1.0; http://help.yahoo.co.jp/help/jp/search/indexing/indexing-27.html)',
     { 'packet_compliant': True,
       'version'         : '1.0',
       'model'           : 'V705SH',
       'vendor'          : None,
       'vendor_version'  : None,
       'serialnumber'    : None,
       'java_info'       : {}
       },
     ),

    ('Vodafone/1.0/V802SE/SEJ001/SN123456789012345 Browser/SEMC-Browser/4.1 Profile/MIDP-2.0 Configuration/CLDC-1.1',
     { 'packet_compliant': True,
       'version'         : '1.0',
       'model'           : 'V802SE',
       'vendor'          : 'SE',
       'vendor_version'  : 'J001',
       'serialnumber'    : '123456789012345',
       'java_info'       : { 'Profile': 'MIDP-2.0',
                             'Configuration': 'CLDC-1.1',
                             }
       },
     ),

    ('Vodafone/1.0/V702NK/NKJ001 Series60/2.6 Nokia6630/2.39.148 Profile/MIDP-2.0 Configuration/CLDC-1.1',
     { 'packet_compliant': True,
       'version'         : '1.0',
       'model'           : 'V702NK',
       'vendor'          : 'NK',
       'vendor_version'  : 'J001',
       'serialnumber'    : None,
       'java_info'       : { 'Profile': 'MIDP-2.0',
                             'Configuration': 'CLDC-1.1',
                             }
       },
     ),

    ('J-PHONE/4.0/J-SH51/SNJSHA3029293 SH/0001aa Profile/MIDP-1.0 Configuration/CLDC-1.0 Ext-Profile/JSCL-1.1.0',
     { 'packet_compliant': True,
       'version'         : '4.0',
       'model'           : 'J-SH51',
       'vendor'          : 'SH',
       'vendor_version'  : '0001aa',
       'serialnumber'    : 'JSHA3029293',
       'java_info'       : { 'Profile': 'MIDP-1.0',
                             'Configuration': 'CLDC-1.0',
                             'Ext-Profile'  : 'JSCL-1.1.0',
                             }
       },
     ),

    ('J-PHONE/2.0/J-DN02',
     { 'packet_compliant': False,
       'version'         : '2.0',
       'model'           : 'J-DN02',
       'vendor'          : 'DN',
       },
     ),

    ('MOT-V980/80.2F.2E. MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1',
     { 'packet_compliant': True,
       'vendor'          : 'MOT',
       'vendor_version'  : '80.2F.2E.',
       'java_info'       : { 'Profile': 'MIDP-2.0',
                             'Configuration': 'CLDC-1.1',
                             }
       },
     ),
)

WILLCOM = (
    ('Mozilla/3.0(WILLCOM;SANYO/WX310SA/2;1/1/C128) NetFront/3.3,61.198.142.127',
     { 'vendor'         : 'SANYO',
       'model'          : 'WX310SA',
       'model_version'  : '2;1',
       'browser_version': '1',
       'cache_size'     : 128,
       },
     ),

    ('Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; SHARP/WS007SH; PPC; 480x640)',
     { 'vendor': 'SHARP',
       'model' : 'WS007SH',
       'browser_version': 'MSIE 4.01',
       'os'  : 'Windows CE',
       'arch': 'PPC',
       },
     ),
)

def _test_func(p, ua, params):
    res = p.parse(ua)
    assert isinstance(res, dict)
    for k, v in params.items():
        assert res.get(k) == v, '%r expected, actual %r' % (v, res.get(k))

def test_docomo_parser():
    p = parser.DoCoMoUserAgentParser()
    for ua, params in DOCOMO:
        yield _test_func, p, ua, params

def test_ezweb_parser():
    p = parser.EZwebUserAgentParser()
    for ua, params in EZWEB:
        yield _test_func, p, ua, params

def test_softbank_parser():
    p = parser.SoftBankUserAgentParser()
    for ua, params in SOFTBANK:
        yield _test_func, p, ua, params

def test_willcom_parser():
    p = parser.WillcomUserAgentParser()
    for ua, params in WILLCOM:
        yield _test_func, p, ua, params
