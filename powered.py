#!/usr/bin/env python
import re
import sys
import time
import serial
import struct
from datetime import datetime

import urlparse
import BaseHTTPServer
import ConfigParser

config = ConfigParser.ConfigParser()
config.read((
    'powered.conf',
    sys.path[0] + '/powered.conf',
    '/etc/powered.conf'
))

PORT = config.getint('powered', 'tcpport')
DEV = config.get('powered', 'serialport')

SUMMARY_VARS = ['I1', 'I2', 'I3', 'K1', 'K2', 'K3', 'KA', 'KV', 'KW',
                'P1', 'P2', 'P3', 'Q1', 'Q2', 'Q3', 'QA', 'V1', 'V2', 'V3', 'F']

class PactMeter:

    def __init__(self, dev='/dev/ttyS0'):
        self.dev = dev
        self.open()

    def open(self):
        self.s = serial.Serial(self.dev, 1200, timeout=1)

    def close(self):
        self.s.close()

    def writeline(self, str):
        self.s.write(str + '\r')

    def readline(self):

        res = []
        while True:
            c = self.s.read(1)
            if not c: break # TODO: raise exception?
            if c == '\r': break
            res.append(c)

        return ''.join(res)

    def parse(self, code, ret):
        fromhex  = lambda x: int(x, 16)
        fromtime = lambda x: datetime.strptime(x, '%H:%M:%S').time()
        frompack = lambda x: struct.unpack('<II', x)
        oddfloat = lambda x, s: float(x)

        parsers = [
          ('F=(\d+\.\d+)',                float),
          ('R=(\d\d:\d\d:\d\d)',          fromtime),
          ('S([0-9A-Z]{9})',              str),
          ('s=(.{8})',                    frompack),
          ('B[AVWvw]([0-9A-F]{6})',       fromhex),
          ('[IiLPpV][123]([+-]\d+\.\d+)', float),
          ('K[123AVW]([+-]\d+\.\d+)',     float),
          ('Q[123A]=(\d+\.\d+)([+-])',    oddfloat),
          ('U[AVWvw]=(\d{7})',            int),
          ('X[0-9A-F]{2}=([0-9A-F]{6})',  fromhex),
        ]

        for pattern, parser in parsers:
            m = re.match(pattern, ret)
            if m:
                return parser(*m.groups())

        

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    # Disable logging DNS lookups
    def address_string(self):
        return str(self.client_address[0])

    def do_GET(self):
        self.url = urlparse.urlparse(self.path)
        self.params = urlparse.parse_qs(self.url.query)

        def html_ok():
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_index(path, args):
            html_ok()
            self.wfile.write('Usage: /UA (temporarily)')

        def do_meter(code):
            html_ok()
            self.wfile.flush()

            meter.writeline(code)
            ret = meter.readline()
            print 'Meter returned: %s' % ret
            val = meter.parse(code, ret)
            self.wfile.write(val)
            self.wfile.write('\n')

	def do_summary():
	    html_ok()
            for var in SUMMARY_VARS:
                meter.writeline(var)
                ret = meter.readline()
                val = meter.parse(var, ret)
                self.wfile.write("%s:%s " % (var, val))
            self.wfile.write('\n')

        dispatches = [
            ('^/$',                do_index),
            ('^/summary$',         do_summary), 
            ('^/([FRSs])$',        do_meter),
            ('^/(B[AVWvw])$',      do_meter),
            ('^/([IiLPpV][123])$', do_meter),
            ('^/(K[123AVW])$',     do_meter),
            ('^/(Q[123A])$',       do_meter),
            ('^/([Uu][AVWvw])$',   do_meter),
            ('^/(X[0-9A-F]{2})$',  do_meter),
        ]
        for pattern, dispatch in dispatches:
            m = re.match(pattern, self.path)
            if m:
                dispatch(*m.groups())
                break

        else:
            #self.send_error(500)
            self.send_response(500)
            self.end_headers()
            self.wfile.write('Bad request, should be in the format /UA\n')




meter = PactMeter(DEV)
httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
httpd.serve_forever()

