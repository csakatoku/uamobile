# -*- coding: utf-8 -*-
import os, csv
from uamobile import detect

TEST_FILE = os.path.join(os.path.dirname(__file__), 'data', 'ke-tai_list.csv')
DATA = list(csv.reader(file(TEST_FILE, 'rb')))[2:]

def test_useragent():
    def softbank(ua, tp):
        assert ua.short_carrier == 'S'
        if tp == '3GC':
            assert ua.is_3g()
        elif tp.startswith('C'):
            assert ua.is_type_c()
        elif tp.startswith('P'):
            assert ua.is_type_p()
        elif tp.startswith('W'):
            assert ua.is_type_w()

    def docomo(ua, tp, html_version):
        assert ua.short_carrier == 'D'
        assert ua.is_foma() == (tp == 'FOMA')
        assert ua.html_version == html_version, '"%s" expected, actual "%s"' % (html_version,
                                                                                ua.html_version)

    def au(ua):
        assert ua.short_carrier == 'E'

    for row in DATA:
        carrier = {'DoCoMo'  : 'D',
                   'au'      : 'E',
                   'SoftBank': 'S',
                   'Vodafone': 'S',
                   }[row[1]]

        useragent = row[4].strip()
        if carrier == 'S':
            useragent = useragent.replace('[/Serial]', '')
        ua = detect({'HTTP_USER_AGENT':useragent})

        if carrier == 'S':
            yield (softbank, ua, row[5])
        elif carrier == 'E':
            if 'UP. Browser' in useragent:
                # I'm not sure these are valid data.
                continue
            yield (au, ua)
        elif carrier == 'D':
            yield (docomo, ua, row[5], row[6])

