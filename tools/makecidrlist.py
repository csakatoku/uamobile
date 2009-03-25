#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import optparse
import pickle
import pprint

try:
    import simplejson
    has_json = True
except ImportError:
    has_json = False

try:
    import yaml
    has_yaml = True
except ImportError:
    has_yaml = False

from uamobile.utils import scraper

def main():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--carrier", dest="carrier",
                      help="mobile jp carrier. docomo/ezweb/softbank/willcom")
    parser.add_option("-o", "--filename", dest="filename", default=None,
                      help="the output filename. if None, use sys.stdout")
    parser.add_option("-f", "--format", dest="format", default='json',
                      help="the output format. json/pickle/yaml/python")
    opts, args = parser.parse_args()

    if opts.carrier is None:
        parser.print_help()
        sys.exit(1)

    if opts.filename:
        output = open(opts.filename, "w")
    else:
        output = sys.stdout

    if opts.format == 'pickle':
        dump_func = lambda result: pickle.dump(result, output)
    elif opts.format == 'json':
        if not has_json:
            print "To use 'json' format, you need simplejson"
            sys.exit(1)
        dump_func = lambda result: simplejson.dump(result, output, ensure_ascii=False, indent=2)
    elif opts.format == 'yaml':
        if not has_yaml:
            print "To use 'yaml' format, you need PyYAML"
            sys.exit(1)
        dump_func = lambda result: yaml.dump([list(x) for x in result], output)
    elif opts.format == 'python':
        dump_func = lambda result: output.write("DATA = %s\n" % pprint.pformat(result, indent=2))
    else:
        # unsupported format
        print "unsupported format %s" % opts.format
        parser.print_help()
        sys.exit(1)

    dump_func(scraper.scrape_cidr(opts.carrier))

if __name__ == '__main__':
    main()
