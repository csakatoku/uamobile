#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import optparse
import pprint
from importlib import import_module

try:
    import json
    has_json = True
except ImportError:
    try:
        import simplejson as json
        has_json = True
    except ImportError:
        has_json = False

try:
    import yaml
    has_yaml = True
except ImportError:
    has_yaml = False


def main():
    parser = optparse.OptionParser()
    parser.add_option("-m", "--module", dest="module", default=None,
                      help="the scraper module. cidr/model/flash")
    parser.add_option("-c", "--carrier", dest="carrier",
                      help="mobile jp carrier. docomo/ezweb/softbank/willcom")
    parser.add_option("-o", "--filename", dest="filename", default=None,
                      help="the output filename. if None, use sys.stdout")
    parser.add_option("-f", "--format", dest="format", default='json',
                      help="the output format. json/yaml/python")
    opts, args = parser.parse_args()

    if opts.carrier is None or opts.module is None:
        parser.print_help()
        sys.exit(1)

    try:
        scraper = import_module('uamobile.scrapers.%s' % opts.module)
    except ImportError:
        print "no scaper module '%s'" % opts.module
        parser.print_help()
        sys.exit(1)

    if opts.format == 'json':
        if not has_json:
            print "To use 'json' format, you need json or simplejson module"
            sys.exit(1)
        dump_func = lambda result: json.dumps(result, ensure_ascii=False, indent=2)
    elif opts.format == 'yaml':
        if not has_yaml:
            print "To use 'yaml' format, you need PyYAML"
            sys.exit(1)
        dump_func = lambda result: yaml.dump(result)
    elif opts.format == 'python':
        dump_func = lambda result: "DATA = %s\n" % pprint.pformat(result, indent=2)
    else:
        # unsupported format
        print "unsupported format %s" % opts.format
        parser.print_help()
        sys.exit(1)

    name = { 'kddi'      : 'EZWebScraper',
             'ezweb'     : 'EZWebScraper',
             'thirdforce': 'SoftBankScraper',
             'softbank'  : 'SoftBankScraper',
             'docomo'    : 'DoCoMoScraper',
             'willcom'   : 'WillcomScraper',
             }.get(opts.carrier.lower())
    cls = getattr(scraper, name, None)
    if cls is None:
        print "scraper not found for the carrier '%s'" % opts.carrier
        sys.exit(1)

    content = dump_func(cls().scrape())

    if opts.filename:
        output = open(opts.filename, "w")
    else:
        output = sys.stdout

    output.write(content)
    output.write("\n")
    output.close()


if __name__ == '__main__':
    main()
