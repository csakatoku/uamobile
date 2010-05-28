# -*- coding: utf-8 -*-
from uamobile import detect

def test_flash():
    def func(version, ua):
        device = detect({'HTTP_USER_AGENT': ua})
        assert device.flash_version == version, device.flash_version
        assert device.supports_flash() == (version is not None)

    for version, ua in DATA:
        yield func, version, ua

DATA = (
    # docomo
    ('1.0', 'DoCoMo/1.0/D506i/c20/TB/W16H08'),
    ('1.1', 'DoCoMo/2.0 L03B(c100;TB;W24H16)'),
    ('1.1', 'DoCoMo/2.0 SH902i(c100;TB;W24H12)'),
    ('3.0', 'DoCoMo/2.0 P06A(c100;TB;W20H13)'),
    ('3.1', 'DoCoMo/2.0 P07A3(c500;TB;W24H15)'),

    # kddi
    (None, 'KDDI-KC3W UP.Browser/6.2_7.2.7.1.K.4.303 (GUI) MMP/2.0'),
    ('2.0', 'KDDI-KC3R UP.Browser/6.2_7.2.7.1.K.4.303 (GUI) MMP/2.0'),
    ('1.1', 'KDDI-HI33 UP.Browser/6.2.0.7.3.129 (GUI) MMP/2.0'),
    (None, 'KDDI-TS25 UP.Browser/6.0.8.3 (GUI) MMP/1.1'),

    # softbank
    ('3.0', 'SoftBank/1.0/943SH/SHJ001 Browser/NetFront/3.5 Profile/MIDP-2.0 Configuration/CLDC-1.1'),
    ('2.0', 'SoftBank/1.0/840P/PJP10 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1'),
    ('2.0', 'SoftBank/1.0/840Pe/PJP10 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1'),
    (None, 'SoftBank/1.0/740SC/SCJ001 Browser/NetFront/3.3'),
    ('1.1', 'Vodafone/1.0/V804SH/SHJ001 Browser/UP.Browser/7.0.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1 Ext-J-Profile/JSCL-1.3.2 Ext-V-Profile/VSCL-2.0.0'),
    ('1.1', 'Vodafone/1.0/V703SHf/SHJ001 Browser/UP.Browser/7.0.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1 Ext-J-Profile/JSCL-1.2.2 Ext-V-Profile/VSCL-2.0.0'),
    (None, 'Vodafone/1.0/V702NK2/NKJ001 Nokia6680/4.04.28 Profile/MIDP-2.0 Configuration/CLDC-1.1'),
    (None, 'MOT-V980/80.2F.2E. MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1'),

    # willcom
    (None, 'Mozilla/3.0(WILLCOM;SANYO/WX310SA/2;1/1/C128) NetFront/3.3'),

    # nonmobile
    ('3.1', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.1.249.1064 Safari/532.5'),
)

