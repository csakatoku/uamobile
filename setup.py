from setuptools import setup, find_packages
import sys, os

version = '0.10'

setup(name='uamobile',
      version=version,
      description="WSGIUserAgentMobile - mobile user agent string parser for WSGI applications",
      long_description="""\
WSGIUserAgentMobile is HTTP mobile user agent string parser. It'll be useful in parsing HTTP_USER_AGENT strings of (mainly Japanese) mobile devices.

This library is ported from similar libraries in Perl and PHP and owes a lot to them.

HTTP-MobileAgent? http://search.cpan.org/~kurihara/HTTP-MobileAgent-0.26/lib/HTTP/MobileAgent.pm

PEAR::Net_UserAgent_Mobile? http://pear.php.net/package/Net_UserAgent_Mobile
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Chihio Sakatoku',
      author_email='csakatoku@mac.com',
      url='http://code.google.com/p/wsgiuseragentmobile/',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite='nose.collector'
      )
