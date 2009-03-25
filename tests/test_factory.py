# -*- coding: utf-8 -*-
from uamobile import Context
from uamobile.factory.docomo import *
from uamobile.factory.ezweb import *
from uamobile.factory.softbank import *
from uamobile.factory.willcom import *

context = Context()

def test_docomo1():
    factory = DoCoMoUserAgentFactory()
    device = factory.create({'HTTP_USER_AGENT': 'DoCoMo/2.0 P01A(c100;TB;W24H15)'}, context)

    assert device.is_docomo()
    assert device.version == '2.0'
    assert device.model == 'P01A'
    assert device.cache_size == 100, device.cache_size
    assert device.status == 'TB'
    assert device.serialnumber is None
    assert device.card_id is None

def test_docomo2():
    factory = DoCoMoUserAgentFactory()
    device = factory.create({'HTTP_USER_AGENT': 'DoCoMo/2.0 P703i(c100;TB;W24H12;ser0123456789abcdf;icc01234567890123456789)'}, context)

    assert device.is_docomo()
    assert device.version == '2.0'
    assert device.model == 'P703i'
    assert device.cache_size == 100, device.cache_size
    assert device.status == 'TB'
    assert device.serialnumber == '0123456789abcdf'
    assert device.card_id == '01234567890123456789'

def test_ezweb1():
    factory = EZwebUserAgentFactory()
    device = factory.create({'HTTP_USER_AGENT': 'KDDI-TS2A UP.Browser/6.2.0.9 (GUI) MMP/2.0'}, context)

    assert device.is_ezweb()
    assert device.xhtml_compliant is True

def test_softbank_3g():
    factory = SoftBankUserAgentFactory()
    device = factory.create({'HTTP_USER_AGENT': 'SoftBank/1.0/913SH/SHJ001 Browser/NetFront/3.4 Profile/MIDP-2.0 Configuration/CLDC-1.1'}, context)

    assert device.is_softbank()
    assert device.model == '913SH'
    assert device.vendor == 'SH'
    assert device.vendor_version == 'J001'
    assert device.is_3g()

def test_willcom():
    factory = WillcomUserAgentFactory()
    device = factory.create({'HTTP_USER_AGENT': 'Mozilla/3.0(WILLCOM;SANYO/WX310SA/2;1/1/C128) NetFront/3.3,61.198.142.127'}, context)

    assert device.is_willcom()
    assert device.model == 'WX310SA'
    assert device.vendor == 'SANYO'
    assert device.cache_size == 128
