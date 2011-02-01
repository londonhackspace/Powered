#!/usr/bin/env python
import serial
s = None

def open():
  global s
  s = serial.Serial('/dev/ttyS0', 1200, timeout=1)

def close():
  s.close()

def testLine(str, max=100):

  s.write(str)
  s.write('\r')

  res = []
  while True:
    r = s.read(max)
    if not r: break
    res.append(' '.join(['%02x' % ord(x) for x in r]))

  return '\n'.join(res)

def getLine(str):

  s.write(str)
  res = []
  while True:
    c = s.read(1)
    if not c: break
    res.append(c)
    if c == '\r': break

  return ''.join(res)
 
def ascii(s):
  return ''.join([chr(int(x, 16)) for x in s.split(' ')])

if False:
  open()
  print testLine('\0' * 20) # '\0' * 9 + '\r'
  print testLine('\0' * 20) # '\0' * 9 + '\r'
  print testLine('\0' * 10) # '\0' * 10 + '\r'
  print testLine('\0' * 1)  # '\0' + '\r'
  close()

if False:
  open()
  for i in range(20, 30):
    print i
    print testLine('\0' * i)
  close()

  # '\0' * i + '\r' if i < 11
  # '\0' * (i - 11) + '\r' if i >= 11
  # '\0' * (i - 22) + '\r' if i >= 22

  # Seems to use packets of 11 chars


if False:
  open()
  print testLine('\xff' * 20) # '\x8c' * 5
  print testLine('\x01' * 20) # '\x01' * 9
  print testLine('\x80' * 20) # '\xfc'

  print testLine('\x96' * 20) # '\xff'
  print testLine('\xa5' * 20) # '\xa5' * 10
  close()

  # Seems to be PDU based

if False:
  for x in range(256):
    open()
    r = testLine(chr(x))
    if r != '%02x 0d' % x:
      print '%02x %s' % (x, repr(chr(x)))
      if not r:
        print 'blank'
      else:
        print '%s %s' % (r, repr(ascii(r)))
    close()

  # 0d '\r'
  # 0d '\r'
  # 0d '\r'
  #
  # 46 'F'
  # 46 3d 34 39 2e 39 37 39 0d 'F=49.979\r'
  # 46 3d 34 39 2e 39 38 36 0d 'F=49.986\r'
  # 46 3d 34 39 2e 39 36 37 0d 'F=49.967\r'
  #
  # 4e 'N'
  #
  # ff '\xff'
  # ff '\xff'
  #
  # 52 'R'
  # 52 3d 31 34 3a 35 30 3a 33 32 0d 'R=14:50:32\r'
  # 52 3d 31 35 3a 30 30 3a 34 30 0d 'R=15:00:40\r'
  # 52 3d 31 35 3a 32 31 3a 30 31 0d 'R=15:21:01\r'
  #
  # 53 'S'
  # 53 50 39 39 41 30 31 38 36 39 0d 'SP99A01869\r'
  # 53 50 39 39 41 30 31 38 36 39 0d 'SP99A01869\r'
  # 53 50 39 39 41 30 31 38 36 39 0d 'SP99A01869\r'
  #
  # 73 's'
  # 73 3d 9e 01 05 a6 00 00 00 00 0d 's=\x9e\x01\x05\xa6\x00\x00\x00\x00\r'
  # 73 3d 9e 01 05 a6 00 00 00 00 0d 's=\x9e\x01\x05\xa6\x00\x00\x00\x00\r'
  # 73 3d 9e 01 05 a6 00 00 00 00 0d 's=\x9e\x01\x05\xa6\x00\x00\x00\x00\r'
  #
  # 75 'u'
  # 55 0d 'U\r'
  # 55 0d 'U\r'
  # 55 0d 'U\r'
  #
  # 78 'x'
  # ff '\xff'
  # ff '\xff'
  # ff '\xff'
  #
  # 80 '\x80'
  # fc '\xfc'
  # fc '\xfc'
  # fc '\xfc'
  #
  # 81 '\x81'
  # ff '\xff'
  # ff '\xff'
  # ff '\xff'
  #
  # 84 '\x84'
  # 83 0d 84 '\x83\r\x84'
  # 83 0d 84 '\x83\r\x84'
  # 83 0d 84 '\x83\r\x84'
  #
  # 87 '\x87'
  # ff '\xff'
  # ff '\xff'
  # ff '\xff'
  #
  # All others between 130 and 0xfa return nothing
  #
  # fe '\xfe'
  # fa 0d fb 0d fc 0d fd 0d fe 0d '\xfa\r\xfb\r\xfc\r\xfd\r\xfe\r'
  #
  # ff '\xff'
  # 8c '\x8c'

  # So looks like an ASCII protocol, lines up to 10 chars,
  # but with funniness on a few high chars (programming?)

  # See documentation on wiki

if False:

  import pdb;pdb.set_trace()
  open()
  r = getLine('\x82\r') # '\x82\r'
  print repr(r)

  r = getLine('\x83\x01\x23\r') # '\x83\x01\x23' after a delay
  print repr(r)
  r = getLine('\x83\x01\x23\x45\x67\x88\xab\r') # '\x83\x01\x23' after a delay
  print repr(r)
  r = getLine('\x84\r') # ''
  print repr(r)
  r = getLine('\x84\x01\x23\r') # '\x84\x01\x23\r'
  print repr(r)
  r = getLine('\x84\x01\x23\x45\x67\x89\xab\r') # '\x84\x01\x23\x45'
  print repr(r)
  r = getLine('\xfa\x01\x23\x45\x67\x89\xab\xcd\xef\x01\r')
  print repr(r)

  r = getLine('\xfb\r') # '\xfb'
  print repr(r)
  r = getLine('\xfc\r') # '\xfc'
  print repr(r)
  r = getLine('\xfd\r') # '\xfd'
  print repr(r)
  r = getLine('\xfe\r') # '\xfa\x8c\x05\x0a\x9e\x72\x00\x02\x3f\xe4'
  print repr(r)
  close()

  # All the multi-bytes probably end in \r

if False:

  import time

  open()
  start = time.time()

  for i in range(0, 100):
    r = getLine('UA\r') # 12.4657409191
    #r = getLine('UA\r') # 12.4215011597
    #r = getLine('F\r') # 14.2507390976
    #r = getLine('F\r') # 14.1550590992
    #r = getLine('X00\r') # 16.90279603
    #r = getLine('X00\r') # 16.7112660408
    #r = getLine('AAAAAAAAAA\r') # 24.0108280182

  end = time.time()
  close()

  print end - start

if True:
  open()
  for i in range(0x0, 0xff):
    print getLine('X%02X\r' % i)

if False:

  import time
  open()

  try:
    while True:
      o = []
      for i in range(0x30, 0x40):
        r = getLine('X%02X\r' % i)
        o.append(r)

      print '\n' * 30
      print '\n'.join(o)
      time.sleep(1)

  except:
    close()
    raise
