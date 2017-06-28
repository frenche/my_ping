#!/usr/bin/python

import argparse, sys, socket, string, IN

class Ping:
    def __init__(self, target, port, timeout, df, size):
      self.sock = None
      self.target = target
      self.port = port
      self.timeout = timeout
      self.df = df
      self.data = (string.ascii_letters *
                    (size/len(string.ascii_letters) +1))[:size]

    def set_socket_opt(self):
      self.sock.settimeout(self.timeout)
      # Ideally we'd want PROBE instead of DO if available
      pmtud = IN.IP_PMTUDISC_DO if self.df else IN.IP_PMTUDISC_DONT
      self.sock.setsockopt(socket.IPPROTO_IP, IN.IP_MTU_DISCOVER, pmtud)

    def send(self):
      return False

class PingUDP(Ping):
    def __init__(self, target, port, timeout, df, size):
      # Resolve peer now, to have a consistent address
      resolved = socket.gethostbyname(target)
      Ping.__init__(self, resolved, port, timeout, df, size)
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.set_socket_opt()

    def send(self):
      if self.sock.sendto(self.data, (self.target, self.port)) != len(self.data):
        raise BaseException('failed to send all data')

      ret, peer = self.sock.recvfrom(len(self.data))
      if ret != self.data:
        raise BaseException('failed to receive all data')

      if (peer !=  (self.target, self.port)):
        raise BaseException('received data from wrong peer')

      return True

class PingTCP(Ping):
    def __init__(self, target, port, timeout, df, size):
      Ping.__init__(self, target, port, timeout, df, size)

    def send(self):
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.set_socket_opt()
      self.sock.connect((self.target, self.port))

      if self.sock.send(self.data) != len(self.data):
        raise BaseException('failed to send all data')

      self.sock.shutdown(socket.SHUT_WR)

      if self.data != self.sock.recv(len(self.data)):
        raise BaseException('failed to receive all data')

      self.sock.close()

      return True

def ping_factory(proto, target, port, timeout, df, size):
  if proto == 'tcp':
    return PingTCP(target, port, timeout, df, size)
  if proto == 'udp':
    return PingUDP(target, port, timeout, df, size)
  raise BaseException('unsupported protocol')

def parse_args():
  parser = argparse.ArgumentParser(description='Ping client over TCP/UDP')
  parser.add_argument('target', default = 'localhost', help = "Target host")
  parser.add_argument('--count', default = '4', type=int, help = "Number of ping request")
  parser.add_argument('--protocol', default='udp', help = "Protocol to use")
  parser.add_argument('--port', default = 5555, type=int, help = "Port to use")
  parser.add_argument('--timeout', default = 15, type=int, help = "Timeout in seconds")
  parser.add_argument('--df', default = False, action='store_true', help = "Set DF flag")
  parser.add_argument('--size', default = 32, type=int, help = "The size of data")

  return vars(parser.parse_args())

if __name__ == '__main__':
  args = parse_args()

  ping = ping_factory(args['protocol'], args['target'], args['port'],
                      args['timeout'], args['df'], args['size'])

  for i in range(1, args['count'] + 1):
    print "Ping number", i, ":", "Ok" if ping.send() else "Failed"
